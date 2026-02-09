// import { useEffect, useRef, useState } from "react";
// import Select from "react-select";
// import Plot from 'react-plotly.js';


// type ParquetFile = {
//   name: string;
// };

// type AnalysisRow = {
//   t: number;
//   vessel_id: string;
//   lat: number;
//   lon: number;
// };

// type LoadMode = "manual" | "auto";

// type SelectOption = {
//   value: string;
//   label: string;
// };

// export default function MultiParquetAnalysis() {
//   const [files, setFiles] = useState<ParquetFile[]>([]);
//   const [selectedOptions, setSelectedOptions] = useState<SelectOption[]>([]);
//   const [data, setData] = useState<AnalysisRow[]>([]);
//   const [uniqueVesselCount, setUniqueVesselCount] = useState(0);
//   const [uniqueStats, setUniqueStats] = useState<Record<string, number>>({});
//   const vesselSetRef = useRef(new Set<string>());

//   const [loadMode, setLoadMode] = useState<LoadMode>("manual");
//   const [loading, setLoading] = useState(false);
//   const [progress, setProgress] = useState(0);
//   const [controller, setController] = useState<AbortController | null>(null);

//   /** Fetch parquet files */
//   const fetchFiles = async () => {
//     const res = await fetch("http://localhost:8000/files");
//     if (!res.ok) return;
//     const list: ParquetFile[] = await res.json();
//     setFiles(list);
//   };

//   useEffect(() => {
//     fetchFiles();
//   }, []);

//   /** Load selected files */
//   const loadSelected = async () => {
//   vesselSetRef.current.clear();
//   setUniqueVesselCount(0);
//   setUniqueStats({}); // reset per-file stats

//   if (selectedOptions.length === 0 || loading) return;

//   setLoading(true);
//   setData([]);
//   setProgress(0);

//   const fileNames = selectedOptions.map((o) => o.value);
//   const abortCtrl = new AbortController();
//   setController(abortCtrl);

//   try {
//     const res = await fetch(
//       `http://localhost:8000/analysis-multi/stream?${fileNames
//         .map((f) => `files=${encodeURIComponent(f)}`)
//         .join("&")}`,
//       { signal: abortCtrl.signal }
//     );

//     const reader = res.body!.getReader();
//     const decoder = new TextDecoder();
//     let buffer = "";
//     let rows: AnalysisRow[] = [];

//     // Temporary object to track unique vessels per file
//     const perFileVessels: Record<string, Set<string>> = {};

//     while (true) {
//       const { value, done } = await reader.read();
//       if (done) break;

//       buffer += decoder.decode(value, { stream: true });
//       const lines = buffer.split("\n");
//       buffer = lines.pop() || ""; // keep incomplete line

//       for (const line of lines) {
//         if (!line.trim()) continue;
//         try {
//           const msg = JSON.parse(line);

//           const vesselId = msg.row.vessel_id;
//           const file = msg.row.file || "unknown"; // backend must send file info

//           // Track per-file unique vessels
//           if (!perFileVessels[file]) perFileVessels[file] = new Set();
//           perFileVessels[file].add(vesselId);

//           // Update uniqueStats state for plotting
//           const statsUpdate: Record<string, number> = {};
//           for (const [f, vessels] of Object.entries(perFileVessels)) {
//             statsUpdate[f] = vessels.size;
//           }
//           setUniqueStats(statsUpdate);

//           // Update global unique vessel count progressively
//           if (!vesselSetRef.current.has(vesselId)) {
//             vesselSetRef.current.add(vesselId);
//             setUniqueVesselCount(vesselSetRef.current.size);
//           }

//           setProgress(msg.progress);
//           rows.push(msg.row);

//           if (rows.length % 50 === 0) setData([...rows]); // batch update
//         } catch (e) {
//           console.error("Failed to parse line:", line, e);
//         }
//       }
//     }

//     // final update
//     if (buffer.trim()) {
//       try {
//         const msg = JSON.parse(buffer);
//         rows.push(msg.row);
//       } catch (e) {
//         console.error("Failed to parse last line:", buffer, e);
//       }
//     }

//     setData([...rows]);
//   } catch (e) {
//     if ((e as any).name === "AbortError") {
//       console.log("Load aborted");
//     } else {
//       console.error(e);
//     }
//   } finally {
//     setLoading(false);
//     setController(null);
//   }
// };



//   /** Auto-load on selection */
//   useEffect(() => {
//     if (loadMode === "auto" && selectedOptions.length > 0) {
//       loadSelected();
//     }
//   }, [selectedOptions, loadMode]);

//   const options: SelectOption[] = files.map((f) => ({
//     value: f.name,
//     label: f.name,
//   }));

//   return (
//     <div>
//       <h2>Multi-Parquet Analysis</h2>

//       {/* Controls */}
//       <div style={{ display: "flex", gap: "0.5rem", marginBottom: "0.5rem" }}>
//         <button onClick={fetchFiles} disabled={loading}>
//           🔄 Refresh files
//         </button>

//         <label>
//           <input
//             type="radio"
//             checked={loadMode === "manual"}
//             onChange={() => setLoadMode("manual")}
//           />
//           Manual
//         </label>

//         <label>
//           <input
//             type="radio"
//             checked={loadMode === "auto"}
//             onChange={() => setLoadMode("auto")}
//           />
//           Auto on select
//         </label>
//       </div>

//     {/* React multi-select */}
//     <Select
//         isMulti
//         options={options}
//         value={selectedOptions}
//         onChange={(v) => setSelectedOptions(v as SelectOption[])}
//         isDisabled={loading}
//         placeholder="Select parquet files (months)…"
//         styles={{
//             control: (base) => ({
//             ...base,
//             backgroundColor: "#1e1e1e",
//             borderColor: "#444",
//             color: "#fff",
//             }),
//             menu: (base) => ({
//             ...base,
//             backgroundColor: "#1e1e1e",
//             }),
//             option: (base, state) => ({
//             ...base,
//             backgroundColor: state.isFocused ? "#333" : "#1e1e1e",
//             color: "#fff",
//             }),
//             multiValue: (base) => ({
//             ...base,
//             backgroundColor: "#333",
//             }),
//             multiValueLabel: (base) => ({
//             ...base,
//             color: "#fff",
//             }),
//             placeholder: (base) => ({
//             ...base,
//             color: "#aaa",
//             }),
//             singleValue: (base) => ({
//             ...base,
//             color: "#fff",
//             }),
//         }}
//         />


//       {/* Manual load */}
//       {loadMode === "manual" && (
//         <button
//           onClick={loadSelected}
//           disabled={loading || selectedOptions.length === 0}
//           style={{ marginTop: "0.5rem" }}
//         >
//           Load selected files
//         </button>
//       )}

//     <button
//         onClick={() => controller?.abort()}
//         disabled={!loading}
//         style={{ marginTop: "0.5rem", marginLeft: "0.5rem" }}
//         >
//         ⏹ Stop
//     </button>

//         {/* Status */}
//         <div style={{ marginTop: "0.5rem" }}>
//             {loading
//                 ? "Loading…"
//                 : `Files: ${selectedOptions.length}, Rows: ${data.length}`}
//         </div>
//         {loading && (
//             <div style={{ marginTop: "0.5rem" }}>
//                 <progress value={progress} max={100} style={{ width: "100%" }} />
//                 <span>{progress}%</span>
//             </div>
//         )}

//         <div style={{ marginTop: "0.5rem" }}>
//             Unique vessels: {uniqueVesselCount}
//         </div>

//         <div>

      

//       {loading && <div>Loading unique vessels…</div>}

//       {Object.keys(uniqueStats).length > 0 && (
//         <Plot
//             data={[{
//             x: Object.keys(uniqueStats),
//             y: Object.values(uniqueStats),
//             type: "scatter",
//             mode: "lines+markers",
//             marker: { color: "blue" },
//             }]}
//             layout={{
//             title: "Unique vessels per file",
//             xaxis: { title: "File", tickangle: -45 },
//             yaxis: { title: "Unique vessels" },
//             margin: { b: 120 },
//             }}
//             style={{ width: "100%", height: "400px" }}
//         />
//         )}

//     </div>


//     </div>
//   );
// }
