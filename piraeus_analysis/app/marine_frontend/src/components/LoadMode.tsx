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
    <div style={{ marginBottom: "1rem" }}>
      {/* Mode selection */}
      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
        <label>
          <input
            type="radio"
            checked={loadMode === "index"}
            onChange={() => setLoadMode("index")}
          />
          By index
        </label>

        <label>
          <input
            type="radio"
            checked={loadMode === "time"}
            onChange={() => setLoadMode("time")}
          />
          By time
        </label>
      </div>

      {/* Index loader */}
      {loadMode === "index" && (
        <div style={{ display: "flex", gap: "0.5rem", marginTop: "0.5rem" }}>
          <input
            type="number"
            value={startIdx}
            onChange={(e) => setStartIdx(Number(e.target.value))}
            disabled={loading}
            placeholder="Start index"
          />
          <input
            type="number"
            value={endIdx}
            onChange={(e) => setEndIdx(Number(e.target.value))}
            disabled={loading}
            placeholder="End index"
          />
          <button onClick={() => onLoadByIndex(startIdx, endIdx)} disabled={loading}>
            Load rows
          </button>
        </div>
      )}

      {/* Time window loader */}
      {loadMode === "time" && (
        <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
          <label>
            Start: {new Date(timeRange[0]).toLocaleString()}
            <input
              type="range"
              min={minTimestamp}
              max={timeRange[1]}
              value={timeRange[0]}
              onChange={(e) =>
                setTimeRange([Number(e.target.value), timeRange[1]])
              }
              disabled={loading}
            />
          </label>

          <label>
            End: {new Date(timeRange[1]).toLocaleString()}
            <input
              type="range"
              min={timeRange[0]}
              max={maxTimestamp}
              value={timeRange[1]}
              onChange={(e) =>
                setTimeRange([timeRange[0], Number(e.target.value)])
              }
              disabled={loading}
            />
          </label>

          <button onClick={() => onLoadByTime(timeRange[0], timeRange[1])} disabled={loading}>
            Load Time Window
          </button>
        </div>
      )}
    </div>
  );
}
