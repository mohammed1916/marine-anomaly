import { useState, useRef, useEffect } from "react";

type FileSelectorProps = {
  files: { name: string }[];
  selectedFile: string | null;
  setSelectedFile: (f: string) => void;
  loading: boolean;
  onClick: () => void;
};

export default function FileSelector({
  files,
  selectedFile,
  setSelectedFile,
  loading,
  onClick,
}: FileSelectorProps) {
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // close dropdown on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  return (
    <div
      ref={containerRef}
      style={{
        position: "relative",
        width: "100%",
        userSelect: "none",
        fontFamily: "sans-serif",
      }}
    >
      {/* flex container for dropdown + button */}
      <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
        {/* Dropdown */}
        <div
          onClick={() => !loading && setOpen(!open)}
          style={{
            flex: 1, // takes full width minus button
            padding: "0.5rem 0.75rem",
            borderRadius: "8px",
            border: "1px solid #555",
            backgroundColor: "#2c2c2c",
            color: "#eee",
            cursor: loading ? "not-allowed" : "pointer",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          {selectedFile || "Select file"}
          <span
            style={{
              transform: open ? "rotate(180deg)" : "rotate(0deg)",
              transition: "0.2s",
            }}
          >
            ▼
          </span>
        </div>

        {/* Refresh button */}
        <button
          onClick={onClick}
          disabled={loading}
          style={{
            padding: "0.5rem",
            borderRadius: "8px",
            backgroundColor: "#444",
            color: "#eee",
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
            transition: "background 0.2s",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#555")}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = "#444")}
        >
          🔄
        </button>
      </div>

      {/* Dropdown list */}
      {open && (
        <div
          style={{
            position: "absolute",
            top: "calc(100% + 4px)",
            left: 0,
            right: 0,
            backgroundColor: "#2c2c2c",
            border: "1px solid #555",
            borderRadius: "8px",
            maxHeight: "200px",
            overflowY: "auto",
            zIndex: 10,
          }}
        >
          {files.map((f) => (
            <div
              key={f.name}
              onClick={() => {
                setSelectedFile(f.name);
                setOpen(false);
              }}
              style={{
                padding: "0.5rem 0.75rem",
                cursor: "pointer",
                backgroundColor: selectedFile === f.name ? "#444" : "#2c2c2c",
                color: "#eee",
                transition: "background 0.2s",
              }}
              onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "#555")}
              onMouseLeave={(e) =>
                (e.currentTarget.style.backgroundColor =
                  selectedFile === f.name ? "#444" : "#2c2c2c")
              }
            >
              {f.name}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
