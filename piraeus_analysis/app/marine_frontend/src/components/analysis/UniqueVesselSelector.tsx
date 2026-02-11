// marine_frontend/src/components/UniqueVesselSelector.tsx
import { useState } from "react";
import Plot from "react-plotly.js";

type ParquetFile = { name: string };

interface Props {
  files: ParquetFile[];
  loading: boolean;
}

interface FileSelection {
  id: number;
  file: string | null;
}

export default function UniqueVesselSelector({ files, loading }: Props) {
  const [selections, setSelections] = useState<FileSelection[]>([
    { id: 1, file: null },
  ]);
  const [progress, setProgress] = useState<number>(0);
  const [results, setResults] = useState<Record<string, number>>({});

  const _MONTH_MAP: Record<string, number> = {
    jan: 1, feb: 2, mar: 3, apr: 4,
    may: 5, jun: 6, jul: 7, aug: 8,
    sep: 9, oct: 10, nov: 11, dec: 12,
  };

  /** Add a new file selection field */
  const addField = () => {
    setSelections([...selections, { id: Date.now(), file: null }]);
  };

  /** Update the selected file in a field */
  const updateField = (id: number, value: string) => {
    setSelections(
      selections.map((s) => (s.id === id ? { ...s, file: value } : s))
    );
  };

  /** Remove a file selection field */
  const removeField = (id: number) => {
    setSelections(selections.filter((s) => s.id !== id));
  };

  /** Currently selected files */
  const selectedFiles = selections
    .map((s) => s.file)
    .filter((f): f is string => f !== null);

  /** Available files for a select field (exclude selections in other fields) */
  const availableFiles = (currentId: number) => {
    const selectedOther = selections
      .filter((s) => s.id !== currentId)
      .map((s) => s.file)
      .filter((f): f is string => f !== null);
    return files.filter((f) => !selectedOther.includes(f.name));
  };

  /** Fetch unique vessels from backend streaming */
  const fetchUniqueVessels = async () => {
    if (selectedFiles.length === 0) return;
    setProgress(0);
    setResults({});
    const controller = new AbortController();

    const res = await fetch(`http://localhost:8000/unique-vessels-multi`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ files: selectedFiles }),
      signal: controller.signal,
    });

    const reader = res.body!.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        if (!line.trim()) continue;
        const msg = JSON.parse(line); // { file: string, unique_vessels: number, progress: number }
        setResults((prev) => ({ ...prev, [msg.file]: msg.unique_vessels }));
        setProgress(msg.progress);
      }
    }
  };

  /** Clean file labels by removing prefix and extension */
  const cleanLabels = (stats: Record<string, number>) => {
    const cleaned: Record<string, number> = {};
    for (const [k, v] of Object.entries(stats)) {
      const label = k.replace("unipi_ais_dynamic_", "").replace(".parquet", "");
      cleaned[label] = v;
    }
    return cleaned;
  };

  /** Sort stats chronologically based on month/year in filename */
  const sortStatsChronologically = (stats: Record<string, number>) => {
    const entries = Object.entries(stats);
    entries.sort((a, b) => {
      const re = /_(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)(\d{4})/i;
      const ma = a[0].match(re);
      const mb = b[0].match(re);
      if (!ma || !mb) return 0;

      const monthA = _MONTH_MAP[ma[1].toLowerCase()];
      const yearA = parseInt(ma[2], 10);
      const monthB = _MONTH_MAP[mb[1].toLowerCase()];
      const yearB = parseInt(mb[2], 10);

      return yearA !== yearB ? yearA - yearB : monthA - monthB;
    });
    return Object.fromEntries(entries);
  };

  // Compute cleaned and sorted results once
  const cleanedAndSortedResults =
    Object.keys(results).length > 0
      ? sortStatsChronologically(cleanLabels(results))
      : {};

  return (
    <div>
      <h2>Unique Vessel Analysis</h2>

      {selections.map((s) => (
        <div key={s.id} style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
          <select
            value={s.file || ""}
            onChange={(e) => updateField(s.id, e.target.value)}
            disabled={loading}
          >
            <option value="">Select file…</option>
            {availableFiles(s.id).map((f) => (
              <option key={f.name} value={f.name}>{f.name}</option>
            ))}
          </select>
          <button onClick={() => removeField(s.id)} disabled={loading}>🗑️</button>
        </div>
      ))}

      <div style={{ marginBottom: "1rem" }}>
        <button onClick={addField} disabled={loading}>➕ Add file</button>
        <button onClick={fetchUniqueVessels} disabled={loading || selectedFiles.length === 0}>
          Find Unique Vessels
        </button>
      </div>

      <div style={{ marginTop: "1rem" }}>
        Progress: {progress}%
        {Object.keys(cleanedAndSortedResults).length > 0 && (
          <Plot
            data={[{
              x: Object.keys(cleanedAndSortedResults),
              y: Object.values(cleanedAndSortedResults),
              type: "bar"
            }]}
            layout={{
              title: "Unique vessels per file",
              xaxis: { title: "File" },
              yaxis: { title: "Count" },
              margin: { b: 120 } // room for long x labels
            }}
            style={{ width: "100%", height: "400px" }}
          />
        )}
      </div>
    </div>
  );
}
