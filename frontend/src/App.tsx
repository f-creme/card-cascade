import { useCallback, useState } from "react";
import { useIdentity } from "./hooks/useIdentity";
import { IdentityScreen } from "./screens/IdentityScreen";
import { LobbyScreen } from "./screens/LobbyScreen";
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

  return (
    <div className="flex min-h-screen items-center justify-center bg-base-200">
      <p className="text-lg">
        Partie lancée dans la room <span className="font-mono font-bold">{roomId}</span> !
      </p>
    </div>
  );
}

export default App;