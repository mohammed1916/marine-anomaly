#include <cudf/table/table.hpp>
#include <cudf/io/csv.hpp>
#include <cudf/column/column.hpp>
#include <cudf/strings/convert/convert_datetime.hpp>
#include <cudf/sorting.hpp>
#include <cudf/transform.hpp>
#include <cudf/types.hpp>
#include <cudf/encode.hpp>
#include <cudf/stream_compaction.hpp>

#include <rmm/device_uvector.hpp>
#include <rmm/mr/device/pool_memory_resource.hpp>
#include <rmm/mr/device/per_device_resource.hpp>
#include <rmm/cuda_stream_view.hpp>

#include <cuda_runtime.h>
#include <thrust/sequence.h>

#include <iostream>
#include <vector>
#include <map>
#include <cmath>
#include <string>
#include <cnpy.h> // For saving .npy

// ------------------------------
// Config and metadata
// ------------------------------
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
// CUDA kernel: sliding windows + clamp + NaN
// ------------------------------
__global__
void fused_mask_clamp_window_kernel(
    const int* vessel_id,
    const float* lat,
    const float* lon,
    float* speed,
    float* course,
    const float* ts,
    int N,
    int window_size,
    float* out_windows,
    int* out_vids
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N - window_size + 1) return;

    int vid = vessel_id[idx];
    if (vessel_id[idx + window_size - 1] != vid) return; // same vessel

    int base = idx * window_size * 5;
    bool valid_window = true;

    for (int j = 0; j < window_size; ++j) {
        int r = idx + j;

        float s = speed[r];
        float c = course[r];

        // NaN check + clamp
        if (isnan(s) || isnan(c)) {
            valid_window = false;
            break;
        }

        speed[r]  = fminf(fmaxf(s, 0.0f), 100.0f);
        course[r] = fminf(fmaxf(c, 0.0f), 360.0f);

        // write sliding window
        out_windows[base + j * 5 + 0] = lat[r];
        out_windows[base + j * 5 + 1] = lon[r];
        out_windows[base + j * 5 + 2] = speed[r];
        out_windows[base + j * 5 + 3] = course[r];
        out_windows[base + j * 5 + 4] = ts[r];
    }

    out_vids[idx] = valid_window ? vid : -1;
}

// ------------------------------
// Save .npy file helper
// ------------------------------
void save_npy(const std::string& filename, const std::vector<float>& data,
              int num_windows, int window_size, int features) {
    // reshape flat vector into [num_windows, window_size, features] automatically handled by .npy
    cnpy::npy_save(filename, &data[0], {num_windows, window_size, features}, "w");
}

void save_vids(const std::string& filename, const std::vector<int>& vids) {
    cnpy::npy_save(filename, &vids[0], {static_cast<int>(vids.size())}, "w");
}

// ------------------------------
// Main GPU processing
// ------------------------------
void process_month_gpu(int year, int month, const AISConfig& cfg) {
    std::string file_path = cfg.root + "/unipi_ais_dynamic_" + std::to_string(year) +
                            "/unipi_ais_dynamic_" + MONTH_ABBR[month] + std::to_string(year) + ".csv";

    auto options = cudf::io::csv_reader_options::builder(cudf::io::source_info(file_path))
                   .header(0)
                   .use_cols(cols_alias)
                   .byte_range_size(cfg.chunk_size);

    auto table = cudf::io::read_csv(options);

    // rename t -> timestamp
    auto col_names = table->view().column_names();
    for (auto &n : col_names) if (n == "t") n = "timestamp";

    // cast timestamp -> float
    auto ts_col = table->view().column(cudf::column_view::find_column(table->view(), "timestamp"));
    auto ts_float = cudf::cast(ts_col, cudf::data_type(cudf::type_id::FLOAT32));

    // dictionary encode vessel_id -> int
    auto encoded = cudf::dictionary::encode(table->view().column("vessel_id"));
    auto vessel_id_col = encoded->get_dictionary_column();

    // gather relevant columns
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
    int num_windows = N - cfg.window_size + 1;
    if (num_windows <= 0) return;

    rmm::device_uvector<float> windows(num_windows * cfg.window_size * 5, rmm::cuda_stream_default);
    rmm::device_uvector<int> vids(num_windows, rmm::cuda_stream_default);

    int threads = 256;
    int blocks = (num_windows + threads - 1) / threads;

    fused_mask_clamp_window_kernel<<<blocks, threads>>>(
        sorted.column(0).data<int>(),   // vessel_id
        sorted.column(1).data<float>(), // lat
        sorted.column(2).data<float>(), // lon
        sorted.column(3).data<float>(), // speed
        sorted.column(4).data<float>(), // course
        sorted.column(5).data<float>(), // timestamp
        N,
        cfg.window_size,
        windows.data(),
        vids.data()
    );
    cudaError_t err = cudaGetLastError();
    if (err != cudaSuccess) std::cerr << "Kernel error: " << cudaGetErrorString(err) << "\n";

    cudaDeviceSynchronize();

    // copy back to CPU
    std::vector<float> host_windows(windows.size());
    cudaMemcpy(host_windows.data(), windows.data(), windows.size() * sizeof(float), cudaMemcpyDeviceToHost);

    std::vector<int> host_vids(vids.size());
    cudaMemcpy(host_vids.data(), vids.data(), vids.size() * sizeof(int), cudaMemcpyDeviceToHost);

    // save as .npy files
    save_npy(cfg.root + "/windows_" + std::to_string(year) + "_" + MONTH_ABBR[month] + ".npy",
             host_windows, num_windows, cfg.window_size, 5);
    save_vids(cfg.root + "/vids_" + std::to_string(year) + "_" + MONTH_ABBR[month] + ".npy",
              host_vids);

    std::cout << "Processed month " << MONTH_ABBR[month] << " " << year
              << " | Generated windows: " << num_windows << "\n";
}

// ------------------------------
// Main
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

    std::cout << "GPU preprocessing completed.\n";
    return 0;
}
