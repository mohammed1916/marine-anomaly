// marine_frontend/src/components/LoadingButton.tsx
import { useState, useEffect, ReactNode } from "react";

type LoadingButtonProps = {
  onClick: () => void;
  loading: boolean;
  children: ReactNode; // accept button label
};

export function LoadingButton({ onClick, loading, children }: LoadingButtonProps) {
  const [dots, setDots] = useState("");

  useEffect(() => {
    if (!loading) {
      setDots("");
      return;
    }
    const interval = setInterval(() => {
      setDots((prev) => (prev.length < 3 ? prev + "." : ""));
    }, 500);
    return () => clearInterval(interval);
  }, [loading]);

  return (
    <button onClick={onClick} disabled={loading}>
      {loading ? `Loading${dots}` : children}
    </button>
  );
}
