// marine_frontend/src/components/SpeedLegend.tsx
export type SpeedRange = {
  min: number;
  max: number | null;
  color: string;
  label: string;
};

export const SPEED_RANGES: SpeedRange[] = [
  { min: 0,  max: 2,  color: "#bc2fd2", label: "0 – 2 kn" },
  { min: 2,  max: 5,  color: "#2c7bb6", label: "2 – 5 kn" },
  { min: 5,  max: 10, color: "#ffffbf", label: "5 – 10 kn" },
  { min: 10, max: 20, color: "#fdae61", label: "10 – 20 kn" },
  { min: 20, max: null, color: "#67d1d1", label: "≥ 20 kn" },
];

export function colorBySpeed(speed?: number): string {
  /**
   * Return color for speed using SPEED_RANGES.
   */
  if (speed == null) return "#999999";

  for (const r of SPEED_RANGES) {
    if (r.max === null && speed >= r.min) return r.color;
    if (r.max !== null && speed >= r.min && speed < r.max) return r.color;
  }
  return "#999999";
}

export function SpeedLegend() {
  /**
   * Leaflet legend overlay explaining speed ranges.
   */
  return (
    <div
      style={{
        position: "absolute",
        bottom: "20px",
        right: "20px",
        background: "white",
        padding: "8px 10px",
        borderRadius: "4px",
        boxShadow: "0 0 6px rgba(0,0,0,0.3)",
        fontSize: "12px",
        lineHeight: "16px",
      }}
    >
      <strong style={{ color: "#333"}}>Speed (knots)</strong>
      {SPEED_RANGES.map((r) => (
        <div key={r.label} style={{ display: "flex", alignItems: "center" }}>
          <div
            style={{
              width: "12px",
              height: "12px",
              background: r.color,
              marginRight: "6px",
            }}
          />
          <span style={{ color: "#333"}}>{r.label}</span>
        </div>
      ))}
    </div>
  );
}
