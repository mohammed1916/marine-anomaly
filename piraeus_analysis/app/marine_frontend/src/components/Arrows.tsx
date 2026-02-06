import { Polyline } from "react-leaflet";

/** 
 * Convert angle in degrees to a short line for an arrow
 * 0° = north, 90° = east
 */
export function computeArrow(lat: number, lon: number, angle: number, length = 0.002): [number, number][] {
  const rad = (angle * Math.PI) / 180;
  const dLat = length * Math.cos(rad);
  const dLon = length * Math.sin(rad);
  return [
    [lat, lon],           // arrow base
    [lat + dLat, lon + dLon], // arrow tip
  ];
}