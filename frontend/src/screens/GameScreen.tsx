import { useGameSocket } from "../hooks/useGameSocket";
import { CardBack, CardView } from "../components/CardView";
import type { Identity } from "../types";

interface Props {
  roomId: string;
  identity: Identity;
}

export function GameScreen({ roomId, identity }: Props) {
  const { view, serverError, connected } = useGameSocket(roomId, identity.uuid);

  if (!view) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-base-200">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  const opponents = view.players.filter((p) => p.id !== view.player_id);
  const topDiscard = view.discard_pile[view.discard_pile.length - 1];

  return (
    <div className="flex min-h-screen flex-col bg-base-200">
      <header className="flex items-center justify-between bg-base-100 px-4 py-2 shadow">
        <span className="font-mono text-sm">
          Room {roomId} {!connected && <span className="text-error">(déconnecté)</span>}
        </span>
      </header>

      <div className="flex gap-2 overflow-x-auto p-3">
        {opponents.map((player) => {
          const playerIndex = view.players.findIndex((p) => p.id === player.id);
          const isTheirTurn = playerIndex === view.current_player_index;
          return (
            <div
              key={player.id}
              className={`flex shrink-0 flex-col items-center gap-1 rounded-box p-2 ${
                isTheirTurn ? "bg-primary text-primary-content" : "bg-base-100"
              } ${player.has_left ? "opacity-40" : ""}`}
            >
              <span className="text-sm font-semibold">{player.username}</span>
              <span className="text-xs">
                {player.has_left ? "a quitté" : `${player.hand_count} carte${player.hand_count !== 1 ? "s" : ""}`}
              </span>
            </div>
          );
        })}
      </div>

      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-4">
        <div className="flex items-center gap-6">
          <div className="flex flex-col items-center gap-1">
            <CardBack count={view.draw_pile_count} />
            <span className="text-xs text-base-content/60">Pioche</span>
          </div>

          {topDiscard && (
            <div className="flex flex-col items-center gap-1">
              <CardView card={topDiscard} />
              <span className="text-xs text-base-content/60">Défausse</span>
            </div>
          )}

          {view.second_chance_pile.length > 0 && (
            <div className="flex flex-col items-center gap-1">
              <CardBack count={view.second_chance_pile.length} />
              <span className="text-xs text-base-content/60">2ndes chances</span>
            </div>
          )}
        </div>

        {serverError && <p className="text-sm text-error">{serverError}</p>}
      </div>

      <div className="flex flex-col gap-3 bg-base-100 p-3 shadow-inner">
        <div className="flex gap-2 overflow-x-auto px-2 pb-2">
          {view.hand.map((card) => (
            <CardView key={card.id} card={card} />
          ))}
        </div>
      </div>
    </div>
  );
}