import { useCallback, useEffect, useRef, useState } from "react";
import type { Action, PlayerView } from "../types";

const WS_URL = import.meta.env.VITE_WS_URL as string;

export function useGameSocket(roomId: string, playerId: string) {
  const [view, setView] = useState<PlayerView | null>(null);
  const [serverError, setServerError] = useState<string | null>(null);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(`${WS_URL}/ws/${roomId}/${playerId}`);
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data as string);
      if ("error" in data) {
        setServerError(data.error as string);
        return;
      }
      setServerError(null);
      setView(data as PlayerView);
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [roomId, playerId]);

  const send = useCallback((action: Action) => {
    wsRef.current?.send(JSON.stringify(action));
  }, []);

  return { view, serverError, connected, send };
}