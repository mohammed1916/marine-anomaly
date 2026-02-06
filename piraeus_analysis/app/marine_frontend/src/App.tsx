// marine_frontend/src/App.tsx
import { useState, useEffect, useRef, Fragment } from "react";
import { MapContainer, TileLayer, CircleMarker, Polyline} from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { LatLngExpression } from "leaflet";
import {
  SpeedLegend,
  colorBySpeed,
  SPEED_RANGES,
  type SpeedRange,
} from "./components/SpeedLegend";

import { computeArrow } from "./components/Arrows";

type AISRow = {
  t: number;
  vessel_id: string;
  lon: number;
  lat: number;
  heading?: number;
  speed?: number;
  course?: number;
};

type ParquetFile = { name: string };

function App() {
  const [aisData, setAisData] = useState<AISRow[]>([]);
  const [files, setFiles] = useState<ParquetFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(
    localStorage.getItem("lastSelectedParquet")
  );

  const [startIdx, setStartIdx] = useState(0);
  const [endIdx, setEndIdx] = useState(100);

  const [showHeading, setShowHeading] = useState(true);
  const [showCourse, setShowCourse] = useState(true);

  const [showOnlyStopped, setShowOnlyStopped] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [timeRange, setTimeRange] = useState<[number, number] | null>(null);
  const [minTimestamp, setMinTimestamp] = useState(0);
  const [maxTimestamp, setMaxTimestamp] = useState(0);
  const controllerRef = useRef<AbortController | null>(null);

  /** Fetch available Parquet files */
  const fetchFiles = async () => {
    const res = await fetch("http://localhost:8000/files");
    if (!res.ok) return;
    const list: ParquetFile[] = await res.json();
    setFiles(list);
    if (!selectedFile && list.length > 0) {
      setSelectedFile(list[0].name);
    }
  };

  /** Stream AIS rows by index */
  const handleLoad = async () => {
    if (!selectedFile || loading) return;
    setLoading(true);
    setProgress(0);
    setAisData([]);

    const controller = new AbortController();
    controllerRef.current = controller;

    const res = await fetch(`http://localhost:8000/rows/stream?file=${encodeURIComponent(selectedFile)}&start=${startIdx}&end=${endIdx}`, {
      signal: controller.signal,
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop()!;

        for (const line of lines) {
          // console.log(line)
          const msg = JSON.parse(line);
          setProgress(msg.progress);
          setAisData((prev) => [...prev, msg.row]);
        }
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") throw e;
    } finally {
      setLoading(false);
    }

    localStorage.setItem("lastSelectedParquet", selectedFile);
  };

  /** Stream AIS rows by timestamp window */
  const handleLoadByTime = async () => {
    if (!selectedFile || loading) return;
    setLoading(true);
    setProgress(0);
    setAisData([]);

    const controller = new AbortController();
    controllerRef.current = controller;

    if (!timeRange){
      alert("no time range")
      return
    }
    const [start_ts, end_ts] = timeRange;

    const res = await fetch(
      `http://localhost:8000/rows/stream_time?file=${encodeURIComponent(selectedFile)}&start_ts=${start_ts}&end_ts=${end_ts}`,
      { signal: controller.signal }
    );

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop()!;

        for (const line of lines) {
          const msg = JSON.parse(line);
          setProgress(msg.progress);
          setAisData((prev) => [...prev, msg.row]);
        }
      }
    } catch (e) {
      if ((e as Error).name !== "AbortError") throw e;
    } finally {
      setLoading(false);
    }
  };

  const handleStop = () => {
    controllerRef.current?.abort();
    setLoading(false);
  };

  /** Filter AIS data */
  const filteredData = aisData.filter((r) => {
    if (showOnlyStopped && r.speed !== 0) return false;
    if (r.t < timeRange[0] || r.t > timeRange[1]) return false;
    console.log("r: ", r);
    return true;
  });


  /** Map center */
  const mapCenter: LatLngExpression =
    filteredData.length > 0
      ? [filteredData[0].lat, filteredData[0].lon]
      : [37.9402, 23.6465];

  useEffect(() => {
    fetchFiles();
  }, []);

  // Example: initialize min/max timestamps
  useEffect(() => {
    if (aisData.length > 0) {
      const ts = aisData.map((r) => r.t);
      setMinTimestamp(Math.min(...ts));
      setMaxTimestamp(Math.max(...ts));
      setTimeRange([Math.min(...ts), Math.max(...ts)]);
    }
  }, [aisData]);

  useEffect(() => {
    console.log("selectedFile: ", selectedFile);
    if (!selectedFile) return;

    fetch(
      `http://localhost:8000/rows/time_bounds?file=${encodeURIComponent(selectedFile)}`
    )
      .then(r => r.json())
      .then(({ min, max }) => {
        setMinTimestamp(min);
        setMaxTimestamp(max);
        setTimeRange([min, max]);
      });
  }, [selectedFile]);

  return (
    <div style={{ padding: "1rem", maxWidth: "900px", margin: "0 auto" }}>
      <h1 style={{ marginBottom: "2rem", textAlign: "center" }}>Marine AIS Data</h1>
      <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem" }}>
        <select
          value={selectedFile || ""}
          onChange={(e) => setSelectedFile(e.target.value)}
          disabled={loading}
        >
          {files.map((f) => (
            <option key={f.name} value={f.name}>
              {f.name}
            </option>
          ))}
        </select>

        <button onClick={fetchFiles} disabled={loading}>
          🔄
        </button>

        <input
          type="number"
          value={startIdx}
          onChange={(e) => setStartIdx(Number(e.target.value))}
          disabled={loading}
        />

        <input
          type="number"
          value={endIdx}
          onChange={(e) => setEndIdx(Number(e.target.value))}
          disabled={loading}
        />

        <button onClick={handleLoad} disabled={loading}>
          Load rows
        </button>


        <button onClick={handleLoadByTime} disabled={loading}>
          Load Time Window
        </button>

        {loading && (
          <>
            <progress value={progress} max={100} />
            <button onClick={handleStop}>Stop</button>
          </>
        )}

        <label style={{ marginLeft: "1rem" }}>
          <input
            type="checkbox"
            checked={showOnlyStopped}
            onChange={(e) => setShowOnlyStopped(e.target.checked)}
          />
          Show only speed = 0
        </label>
      </div>

      <label style={{ marginLeft: "1rem" }}>
        <input
          type="checkbox"
          checked={showHeading}
          onChange={(e) => setShowHeading(e.target.checked)}
        />
        Show Heading
      </label>

      <label style={{ marginLeft: "1rem" }}>
        <input
          type="checkbox"
          checked={showCourse}
          onChange={(e) => setShowCourse(e.target.checked)}
        />
        Show Course
      </label>



      <div style={{ marginBottom: "1rem" }}>
        {timeRange && (
          <>
            <label>
              Start: {timeRange[0]}
              <input
                type="range"
                min={minTimestamp}
                max={timeRange[1]}
                value={timeRange[0]}
                onChange={(e) =>
                  setTimeRange([Number(e.target.value), timeRange[1]])
                }
              />
            </label>

            <label>
              End: {timeRange[1]}
              <input
                type="range"
                min={timeRange[0]}
                max={maxTimestamp}
                value={timeRange[1]}
                onChange={(e) =>
                  setTimeRange([timeRange[0], Number(e.target.value)])
                }
              />
            </label>
          </>
        )}

      </div>

      <div style={{ height: "500px", width: "100%" }}>
        <MapContainer center={mapCenter} zoom={12} style={{ height: "100%" }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution="&copy; OpenStreetMap contributors"
          />
          {filteredData.map((row, i) => (
            <CircleMarker
              key={i}
              center={[row.lat, row.lon]}
              radius={3}
              pathOptions={{
                color: colorBySpeed(row.speed),
                fillColor: colorBySpeed(row.speed),
                fillOpacity: 0.9,
              }}
            />
          ))}
          {filteredData.map((row, i) => (
            <Fragment key={i}>
              <CircleMarker
                center={[row.lat, row.lon]}
                radius={3}
                pathOptions={{
                  color: colorBySpeed(row.speed),
                  fillColor: colorBySpeed(row.speed),
                  fillOpacity: 0.9,
                }}
              />

              {/* Heading arrow - Blue */}
              {showHeading && row.heading !== undefined && (
                <Polyline
                  positions={computeArrow(row.lat, row.lon, row.heading, 0.002)}
                  pathOptions={{ color: "blue", weight: 2 }}
                />
              )}

              {/* Course arrow - Red */}
              {showCourse && row.course !== undefined && (
                <Polyline
                  positions={computeArrow(row.lat, row.lon, row.course, 0.002)}
                  pathOptions={{ color: "red", weight: 2 }}
                />
              )}
            </Fragment>
          ))}

        </MapContainer>
        <SpeedLegend />
      </div>
    </div>
  );
}

export default App;
