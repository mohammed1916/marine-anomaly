#include <cudf/table/table.hpp>
#include <cudf/io/csv.hpp>
#include <cudf/column/column.hpp>
#include <cudf/strings/convert/convert_datetime.hpp>
#include <cudf/sorting.hpp>
#include <cudf/transform.hpp>
#include <cudf/types.hpp>
#include <cudf/encode.hpp>
#include <cudf/stream_compaction.hpp>
#include <cudf/strings/string_view.cuh>

#include <rmm/device_uvector.hpp>
#include <rmm/mr/device/pool_memory_resource.hpp>
#include <rmm/mr/device/per_device_resource.hpp>
#include <rmm/cuda_stream_view.hpp>

#include <cuda_runtime.h>
#include <thrust/sequence.h>

#include <iostream>
#include <vector>
#include <map>

static std::map<int, std::string> MONTH_ABBR = {
    {1,"jan"}, {2,"feb"}, {3,"mar"}, {4,"apr"}, {5,"may"}, {6,"jun"},
    {7,"jul"}, {8,"aug"}, {9,"sep"}, {10,"oct"}, {11,"nov"}, {12,"dec"}
};

static std::vector<std::pair<int, std::vector<int>>> DATA_PERIODS = {
    {2017, {5,6,7,8,9,10,11,12}},
    {2018, {1,2,3,4,5,6,7,8,9,10,11,12}},
    {2019, {1,2,3,4,5,6,7,8,9,10,11,12}}
};

static std::vector<std::string> cols_alias = {
    "t","timestamp","vessel_id","lon","lat","speed","course","heading"
};

struct AISConfig {
    std::string root;
    size_t chunk_size;
    int window_size;
};

// ------------------------------
// Combined mask + clamp kernel
// ------------------------------
__global__
void mask_clamp_kernel(
    float* speed, float* course,
    uint8_t* mask,
    int N
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N) return;

    float s = speed[idx];
    float c = course[idx];

    // NaN check
    bool valid = !(isnan(s) || isnan(c));
    mask[idx] = valid;

    if (valid) {
        // clamp
        speed[idx]  = min(max(s, 0.0f), 100.0f);
        course[idx] = min(max(c, 0.0f), 360.0f);
    }
}

// ------------------------------
// Sliding window kernel
// ------------------------------
__global__
void sliding_window_kernel(
    const int* vessel_id,
    const float* lat,
    const float* lon,
    const float* speed,
    const float* course,
    const float* ts,
    int N,
    int window_size,
    float* out_windows,
    int* out_vid
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N - window_size + 1) return;

    // check same vessel for full window
    int vid = vessel_id[idx];
    if (vessel_id[idx + window_size - 1] != vid) return;

    int base = idx * window_size * 5;

    for (int j = 0; j < window_size; ++j) {
        int r = idx + j;
        out_windows[base + j * 5 + 0] = lat[r];
        out_windows[base + j * 5 + 1] = lon[r];
        out_windows[base + j * 5 + 2] = speed[r];
        out_windows[base + j * 5 + 3] = course[r];
        out_windows[base + j * 5 + 4] = ts[r];
    }

    out_vid[idx] = vid;
}

// ------------------------------
// Main processing
// ------------------------------
void process_month_gpu(int year, int month, const AISConfig& cfg) {

    std::string file_path = cfg.root + "/unipi_ais_dynamic_" + std::to_string(year) +
                            "/unipi_ais_dynamic_" + MONTH_ABBR[month] + std::to_string(year) + ".csv";

    auto options = cudf::io::csv_reader_options::builder(
                       cudf::io::source_info(file_path))
                       .header(0)
                       .use_cols(cols_alias)
                       .byte_range_size(cfg.chunk_size);

    auto table = cudf::io::read_csv(options);

    // rename t -> timestamp if exists
    auto col_names = table->view().column_names();
    bool has_t = false;
    for (auto &n : col_names) if (n == "t") has_t = true;

    if (has_t) {
        for (auto &n : col_names) if (n == "t") n = "timestamp";
        table = cudf::table::concatenate({table->view()}, cudf::table::column_names(col_names));
    }

    // cast timestamp -> float seconds
    auto ts_col = table->view().column(cudf::column_view::find_column(table->view(), "timestamp"));
    auto ts_float = cudf::cast(ts_col, cudf::data_type(cudf::type_id::FLOAT32));

    // dictionary encode vessel_id -> int
    auto encoded = cudf::dictionary::encode(table->view().column("vessel_id"));
    auto vessel_id_col = encoded->get_dictionary_column();

    // gather table to include encoded vessel_id and ts_float
    auto gathered = cudf::table_view({
        vessel_id_col->view(),
        table->view().column(cudf::column_view::find_column(table->view(), "lat")),
        table->view().column(cudf::column_view::find_column(table->view(), "lon")),
        table->view().column(cudf::column_view::find_column(table->view(), "speed")),
        table->view().column(cudf::column_view::find_column(table->view(), "course")),
        ts_float->view()
    });

    // sort by vessel_id + timestamp
    auto sorted_order = cudf::sorted_order(
        {gathered.column(0), gathered.column(5)},
        {cudf::order::ASCENDING, cudf::order::ASCENDING}
    );
    auto sorted = cudf::gather(gathered, *sorted_order);

    int N = sorted.num_rows();

    // Create mask array
    rmm::device_uvector<uint8_t> mask(N, rmm::cuda_stream_default);

    // run combined mask+clamp kernel
    int threads = 256;
    int blocks = (N + threads - 1) / threads;
    mask_clamp_kernel<<<blocks, threads>>>(
        sorted.column(3).data<float>(), // speed
        sorted.column(4).data<float>(), // course
        mask.data(),
        N
    );
    cudaDeviceSynchronize();

    // apply boolean mask (compact)
    auto filtered = cudf::apply_boolean_mask(sorted, mask);

    // update N
    int Nf = filtered.num_rows();

    // allocate output windows
    int num_windows = Nf - cfg.window_size + 1;
    rmm::device_uvector<float> windows(num_windows * cfg.window_size * 5, rmm::cuda_stream_default);
    rmm::device_uvector<int> vids(num_windows, rmm::cuda_stream_default);

    // generate sliding windows
    int wblocks = (num_windows + threads - 1) / threads;
    sliding_window_kernel<<<wblocks, threads>>>(
        filtered.column(0).data<int>(),   // vessel_id
        filtered.column(1).data<float>(), // lat
        filtered.column(2).data<float>(), // lon
        filtered.column(3).data<float>(), // speed
        filtered.column(4).data<float>(), // course
        filtered.column(5).data<float>(), // timestamp
        Nf,
        cfg.window_size,
        windows.data(),
        vids.data()
    );
    cudaDeviceSynchronize();

    std::cout << "Generated " << num_windows << " windows on GPU\n";
}

// ------------------------------
int main() {
    AISConfig cfg;
    cfg.root = "../dataset/piraeus";
    cfg.chunk_size = 500000;
    cfg.window_size = 128;

    for (auto& [year, months] : DATA_PERIODS) {
        for (auto month : months) {
            process_month_gpu(year, month, cfg);
        }
    }

    std::cout << "GPU processing completed\n";
    return 0;
}
