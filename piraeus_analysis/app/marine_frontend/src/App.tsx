import { useState, useEffect, useRef } from "react";
import { MapContainer, TileLayer, CircleMarker } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import type { LatLngExpression } from "leaflet";

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
  const [showOnlyStopped, setShowOnlyStopped] = useState(false);

  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
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

  /** Stream rows with progress */
  const handleLoad = async () => {
    if (!selectedFile || loading) return;

    setLoading(true);
    setProgress(0);
    setAisData([]);

    const controller = new AbortController();
    controllerRef.current = controller;

    const res = await fetch(
      "http://localhost:8000/rows/stream?start=0&end=100",
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

    localStorage.setItem("lastSelectedParquet", selectedFile);
  };

  const handleStop = () => {
    controllerRef.current?.abort();
    setLoading(false);
  };

  /** Filter AIS data */
  const filteredData = showOnlyStopped
    ? aisData.filter((r) => r.speed === 0)
    : aisData;

  /** Map center */
  const mapCenter: LatLngExpression =
    filteredData.length > 0
      ? [filteredData[0].lat, filteredData[0].lon]
      : [37.9402, 23.6465];

  useEffect(() => {
    fetchFiles();
  }, []);

  return (
    <div style={{ padding: "1rem", maxWidth: "900px", margin: "0 auto" }}>
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

        <button onClick={fetchFiles} disabled={loading}>🔄</button>

        <button onClick={handleLoad} disabled={loading}>Load</button>

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
              pathOptions={{ color: "red", fill: true }}
            />
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

export default App;
