import { useEffect, useState } from "react";

type Props = {
  aisData: { vessel_id: string }[];
  loading: boolean;
  selectedVessel: string | null;
  onSelectVessel: (vessel: string | null) => void;
};

export default function VesselSelector({ aisData, loading, selectedVessel, onSelectVessel }: Props) {
  const [vessels, setVessels] = useState<string[]>([]);

  useEffect(() => {
    // Compute unique vessels from the loaded AIS data
    const unique = Array.from(new Set(aisData.map((r) => r.vessel_id)));
    setVessels(unique);
  }, [aisData]);

  return (
    <select
      value={selectedVessel || ""}
      onChange={(e) => onSelectVessel(e.target.value || null)}
      disabled={loading || !vessels.length}
    >
      <option value="">All Vessels</option>
      {vessels.map((v) => (
        <option key={v} value={v}>{v}</option>
      ))}
    </select>
  );
}
