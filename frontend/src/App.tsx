import { useCallback, useState } from "react";
import { useIdentity } from "./hooks/useIdentity";
import { IdentityScreen } from "./screens/IdentityScreen";
import type { Identity } from "./types";

function App() {
  const { identity, setIdentity } = useIdentity();
  const [roomId, setRoomId] = useState<string | null>(null);

  const handleIdentityReady = useCallback(
    (next: Identity) => setIdentity(next),
    [setIdentity],
  );

  if (!roomId) {
    return (
      <IdentityScreen
        identity={identity}
        onIdentityReady={handleIdentityReady}
        onRoomJoined={setRoomId}
      />
    );
  }

  // Écran de lobby : à construire à la prochaine étape.
  return (
    <div className="flex min-h-screen items-center justify-center bg-base-200">
      <p className="text-lg">
        Room <span className="font-mono font-bold">{roomId}</span> rejointe !
      </p>
    </div>
  );
}

export default App;