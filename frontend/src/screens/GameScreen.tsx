import { useState } from "react";
import { useGameSocket } from "../hooks/useGameSocket";
import { CardBack, CardView } from "../components/CardView";
import { SpecialCardModal } from "../components/SpecialCardModal";
import type { Card, Color, Identity } from "../types";

interface Props {
  roomId: string;
  identity: Identity;
}

export function GameScreen({ roomId, identity }: Props) {
  const { view, serverError, connected, send } = useGameSocket(roomId, identity.uuid);
  const [pendingSpecial, setPendingSpecial] = useState<Card | null>(null);

  if (!view) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-base-200">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  const myIndex = view.players.findIndex((p) => p.id === view.player_id);
  const isMyTurn = view.current_player_index === myIndex && !view.winner_id;
  const opponents = view.players.filter((p) => p.id !== view.player_id);
  const topDiscard = view.discard_pile[view.discard_pile.length - 1];

  function handleCardClick(card: Card) {
    if (!isMyTurn) return;
    if (card.kind === "number") {
      send({ kind: "play_card", player_id: identity.uuid, card_id: card.id });
    } else if (card.kind === "second_chance") {
      send({ kind: "play_special", player_id: identity.uuid, card_id: card.id });
    } else {
      // draw, double, block, block3 : a color must be announced first
      setPendingSpecial(card);
    }
  }

  function handleConfirmSpecial(announcedColor: Color, skipTargets?: string[]) {
    if (!pendingSpecial) return;
    send({
      kind: "play_special",
      player_id: identity.uuid,
      card_id: pendingSpecial.id,
      announced_color: announcedColor,
      skip_targets: skipTargets,
    });
    setPendingSpecial(null);
  }

  function handleDraw() {
    if (!isMyTurn) return;
    send({ kind: "draw", player_id: identity.uuid });
  }

  function handlePass() {
    if (!isMyTurn) return;
    send({ kind: "pass", player_id: identity.uuid });
  }

  return (
    <div className="flex min-h-screen flex-col bg-base-200">
      {/* Header */}
      <header className="flex items-center justify-between bg-base-100 px-4 py-2 shadow">
        <span className="font-mono text-sm">
          Room {roomId} {!connected && <span className="text-error">(déconnecté)</span>}
        </span>
      </header>

      {/* Opponents */}
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

      {/* Central zone */}
      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-4">
        {view.draw_chain && (
          <div className="alert alert-warning max-w-sm py-2 text-sm">
            Chaîne de pioche active : +{view.draw_chain.total}
            {view.draw_chain.has_double ? " et x2" : ""} — pose une carte pioche ou pioche.
          </div>
        )}
        {view.announced_color && !view.draw_chain && (
          <p className="text-sm text-base-content/70">
            Couleur en cours : <span className="font-semibold">{view.announced_color}</span>
          </p>
        )}

        <div className="flex items-center gap-6">
          <div className="flex flex-col items-center gap-1">
            <CardBack count={view.draw_pile_count} onClick={isMyTurn ? handleDraw : undefined} />
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

        <p className="text-lg font-semibold">
          {isMyTurn ? "À toi de jouer" : `Tour de ${view.players[view.current_player_index]?.username}`}
        </p>

        {serverError && <p className="text-sm text-error">{serverError}</p>}
      </div>

      {/* Actions + hand of player */}
      <div className="flex flex-col gap-3 bg-base-100 p-3 shadow-inner">
        <div className="flex justify-center gap-2">
          <button type="button" className="btn btn-sm" disabled={!isMyTurn} onClick={handleDraw}>
            Piocher
          </button>
          <button type="button" className="btn btn-sm" disabled={!isMyTurn} onClick={handlePass}>
            Passer
          </button>
        </div>

        <div className="flex gap-2 overflow-x-auto px-2 pb-2">
          {view.hand.map((card) => (
            <CardView key={card.id} card={card} onClick={() => handleCardClick(card)} disabled={!isMyTurn} />
          ))}
        </div>
      </div>

      {pendingSpecial && (
        <SpecialCardModal
          card={pendingSpecial}
          opponents={opponents.filter((p) => !p.has_left)}
          onConfirm={handleConfirmSpecial}
          onCancel={() => setPendingSpecial(null)}
        />
      )}
    </div>
  );
}