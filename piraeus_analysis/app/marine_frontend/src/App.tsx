import { useState, useEffect } from "react";
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

function App() {
  const [aisData, setAisData] = useState<AISRow[]>([]);

  useEffect(() => {
    // Fetch first 100 rows from FastAPI
    const fetchData = async () => {
      const res = await fetch(`http://localhost:8000/rows/?start=0&end=100`);
      const rows: AISRow[] = await res.json();
      setAisData(rows);
    };
    fetchData();
  }, []);

  // Center map at mean location
  const center: LatLngExpression = aisData.length > 0 ? [
    aisData.reduce((sum, r) => sum + r.lat, 0) / (aisData.length || 1),
    aisData.reduce((sum, r) => sum + r.lon, 0) / (aisData.length || 1),
  ] : [0, 0];

  return (
    <div style={{ height: "100vh" }}>
      <MapContainer center={center} zoom={12} style={{ height: "100%" }}>
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        {aisData.map((row, idx) => (
          <CircleMarker
            key={idx}
            center={[row.lat, row.lon]}
            radius={3}
            pathOptions={{ color: "red", fill: true }}
          />
        ))}
      </MapContainer>
    </div>
  );
}

export default App;
