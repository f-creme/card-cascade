import { useCallback, useState } from "react";
import { useIdentity } from "./hooks/useIdentity";
import { IdentityScreen } from "./screens/IdentityScreen";
import { LobbyScreen } from "./screens/LobbyScreen";
import { GameScreen } from "./screens/GameScreen";
import type { Identity } from "./types";

function App() {
  const { identity, setIdentity } = useIdentity();
  const [roomId, setRoomId] = useState<string | null>(null);
  const [gameStarted, setGameStarted] = useState(false);

  const handleIdentityReady = useCallback(
    (next: Identity) => setIdentity(next),
    [setIdentity],
  );

  const handleGameStart = useCallback(() => {
    setGameStarted(true);
  }, []);

  const handleLeaveGame = useCallback(() => {
    setRoomId(null);
    setGameStarted(false);
  }, []);

  if (!roomId || !identity) {
    return (
      <IdentityScreen
        identity={identity}
        onIdentityReady={handleIdentityReady}
        onRoomJoined={setRoomId}
      />
    );
  }

  if (!gameStarted) {
    return <LobbyScreen roomId={roomId} identity={identity} onGameStart={handleGameStart} />;
  }

  return <GameScreen roomId={roomId} identity={identity} onLeave={handleLeaveGame} />;
}

export default App;