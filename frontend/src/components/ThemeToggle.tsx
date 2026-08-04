import { Moon, Sun } from "lucide-react";
import { useTheme } from "../hooks/useTheme";

export function ThemeToggle() {
  const { mode, toggle } = useTheme();

  return (
    <button
      type="button"
      className="btn btn-circle btn-ghost"
      onClick={toggle}
      aria-label={mode === "dark" ? "Passer au thème clair" : "Passer au thème sombre"}
    >
      {mode === "dark" ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
}