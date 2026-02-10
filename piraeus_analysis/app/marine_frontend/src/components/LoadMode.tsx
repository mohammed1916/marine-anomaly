// marine_frontend/src/components/LoadMode.tsx
import { useState } from "react";

type LoadMode = "index" | "time";

interface LoadModeSelectorProps {
  loading: boolean;
  minTimestamp: number;
  maxTimestamp: number;
  onLoadByIndex: (startIdx: number, endIdx: number) => void;
  onLoadByTime: (startTime: number, endTime: number) => void;
}

export default function LoadModeSelector({
  loading,
  minTimestamp,
  maxTimestamp,
  onLoadByIndex,
  onLoadByTime,
}: LoadModeSelectorProps) {
  const [loadMode, setLoadMode] = useState<LoadMode>("index");
  const [startIdx, setStartIdx] = useState(0);
  const [endIdx, setEndIdx] = useState(100);
  const [timeRange, setTimeRange] = useState<[number, number]>([
    minTimestamp,
    maxTimestamp,
  ]);

  // Keep timeRange synced with min/max changes
  if (timeRange[0] < minTimestamp || timeRange[1] > maxTimestamp) {
    setTimeRange([minTimestamp, maxTimestamp]);
  }

  return (
      <div style={{ marginBottom: "1rem", fontFamily: "sans-serif", color: "#eee", backgroundColor: "#1e1e1e", padding: "1rem", borderRadius: "12px" }}>
        {/* Mode toggle */}
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.75rem" }}>
          {(["index", "time"] as LoadMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setLoadMode(mode)}
              disabled={loading}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "8px",
                border: loadMode === mode ? "2px solid #1e90ff" : "1px solid #555",
                backgroundColor: loadMode === mode ? "#2c2c2c" : "#333",
                color: loadMode === mode ? "#1e90ff" : "#ccc",
                cursor: loading ? "not-allowed" : "pointer",
                fontWeight: loadMode === mode ? "600" : "400",
                flex: 1,
                transition: "all 0.2s",
              }}
            >
              {mode === "index" ? "By Index" : "By Time"}
            </button>
          ))}
        </div>

        {/* Index loader */}
        {loadMode === "index" && (
          <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginBottom: "0.5rem" }}>
            <input
              type="number"
              value={startIdx}
              onChange={(e) => setStartIdx(Number(e.target.value))}
              disabled={loading}
              placeholder="Start index"
              style={{
                width: "6rem",
                padding: "0.4rem 0.5rem",
                borderRadius: "6px",
                border: "1px solid #555",
                backgroundColor: "#2c2c2c",
                color: "#eee",
                outline: "none",
              }}
            />
            <input
              type="number"
              value={endIdx}
              onChange={(e) => setEndIdx(Number(e.target.value))}
              disabled={loading}
              placeholder="End index"
              style={{
                width: "6rem",
                padding: "0.4rem 0.5rem",
                borderRadius: "6px",
                border: "1px solid #555",
                backgroundColor: "#2c2c2c",
                color: "#eee",
                outline: "none",
              }}
            />
            <button
              onClick={() => onLoadByIndex(startIdx, endIdx)}
              disabled={loading}
              style={{
                padding: "0.5rem 1rem",
                borderRadius: "8px",
                border: "none",
                backgroundColor: "#1e90ff",
                color: "#fff",
                cursor: loading ? "not-allowed" : "pointer",
                fontWeight: 600,
              }}
            >
              Load Rows
            </button>
          </div>
        )}

        {/* Time window loader */}
        {loadMode === "time" && (
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ minWidth: "5rem", fontWeight: 500 }}>Start:</span>
              <input
                type="range"
                min={minTimestamp}
                max={timeRange[1]}
                value={timeRange[0]}
                onChange={(e) => setTimeRange([Number(e.target.value), timeRange[1]])}
                disabled={loading}
                style={{ flexGrow: 1 }}
              />
              <span style={{ width: "10rem", textAlign: "right", fontSize: "0.85rem" }}>
                {new Date(timeRange[0]).toLocaleString()}
              </span>
            </div>

            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span style={{ minWidth: "5rem", fontWeight: 500 }}>End:</span>
              <input
                type="range"
                min={timeRange[0]}
                max={maxTimestamp}
                value={timeRange[1]}
                onChange={(e) => setTimeRange([timeRange[0], Number(e.target.value)])}
                disabled={loading}
                style={{ flexGrow: 1 }}
              />
              <span style={{ width: "10rem", textAlign: "right", fontSize: "0.85rem" }}>
                {new Date(timeRange[1]).toLocaleString()}
              </span>
            </div>

            <button
              onClick={() => onLoadByTime(timeRange[0], timeRange[1])}
              disabled={loading}
              style={{
                marginTop: "0.25rem",
                padding: "0.5rem 1rem",
                borderRadius: "8px",
                border: "none",
                backgroundColor: "#28a745",
                color: "#fff",
                fontWeight: 600,
                cursor: loading ? "not-allowed" : "pointer",
                alignSelf: "flex-start",
              }}
            >
              Load Time Window
            </button>
          </div>
        )}
      </div>


  );
}
