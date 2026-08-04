import { useCallback, useEffect, useState } from "react";

const THEME_KEY = "card-cascade:theme-mode";
const LIGHT_THEME = "cupcake";
const DARK_THEME = "dark";

type ThemeMode = "light" | "dark";

function getInitialMode(): ThemeMode {
  const stored = localStorage.getItem(THEME_KEY);
  if (stored === "light" || stored === "dark") return stored;
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

export function useTheme() {
  const [mode, setMode] = useState<ThemeMode>(() => getInitialMode());

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", mode === "dark" ? DARK_THEME : LIGHT_THEME);
    localStorage.setItem(THEME_KEY, mode);
  }, [mode]);

  const toggle = useCallback(() => {
    setMode((current) => (current === "dark" ? "light" : "dark"));
  }, []);

  return { mode, toggle };
}