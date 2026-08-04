import { useEffect, useState } from "react";
import { useGameSocket } from "../hooks/useGameSocket";
import { CardBack, CardView, COLOR_CLASSES } from "../components/CardView";
import { SpecialCardModal } from "../components/SpecialCardModal";
import { ScoreModal } from "../components/ScoreModal";
import { avatarSrc } from "../avatar";
import type { Card, Color, Identity, NumberCard } from "../types";

interface Props {
  roomId: string;
  identity: Identity;
  onLeave: () => void;
}

export function GameScreen({ roomId, identity, onLeave }: Props) {
  const { view, serverError, connected, send } = useGameSocket(roomId, identity.uuid);
  const [pendingSpecial, setPendingSpecial] = useState<Card | null>(null);
  const [pairMode, setPairMode] = useState(false);
  const [selectedForPair, setSelectedForPair] = useState<string[]>([]);

  const myIndex = view ? view.players.findIndex((p) => p.id === view.player_id) : -1;
  const isMyTurn = !!view && view.current_player_index === myIndex && !view.winner_id;

  // Si ce n'est plus (ou plus jamais eu) mon tour, on quitte proprement le mode paire
  useEffect(() => {
    if (!isMyTurn) {
      setPairMode(false);
      setSelectedForPair([]);
    }
  }, [isMyTurn]);

  if (!view) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-base-200">
        <span className="loading loading-spinner loading-lg" />
      </div>
    );
  }

  const opponents = view.players.filter((p) => p.id !== view.player_id && !p.has_left);
  const topDiscard = view.discard_pile[view.discard_pile.length - 1];
  const selectedCards = view.hand.filter((c) => selectedForPair.includes(c.id)) as NumberCard[];

  function handleCardClick(card: Card) {
    if (!isMyTurn) return;

    if (pairMode) {
      if (card.kind !== "number") return; // seules les cartes numérotées forment une paire
      setSelectedForPair((prev) => {
        if (prev.includes(card.id)) return prev.filter((id) => id !== card.id);
        if (prev.length >= 2) return prev;
        return [...prev, card.id];
      });
      return;
    }

    if (card.kind === "number") {
      send({ kind: "play_card", player_id: identity.uuid, card_id: card.id });
    } else if (card.kind === "second_chance") {
      send({ kind: "play_special", player_id: identity.uuid, card_id: card.id });
    } else {
      // draw, double, block, block3 : il faut d'abord annoncer une couleur (et parfois des cibles)
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

  function handleConfirmPair(topCardId: string) {
    if (selectedForPair.length !== 2) return;
    const [cardId1, cardId2] = selectedForPair;
    send({
      kind: "play_pair",
      player_id: identity.uuid,
      card_id_1: cardId1,
      card_id_2: cardId2,
      top_card_id: topCardId,
    });
    setSelectedForPair([]);
    setPairMode(false);
  }

  function togglePairMode() {
    setPairMode((prev) => !prev);
    setSelectedForPair([]);
  }

  function handleDraw() {
    if (!isMyTurn) return;
    send({ kind: "draw", player_id: identity.uuid });
  }

  function handlePass() {
    if (!isMyTurn) return;
    send({ kind: "pass", player_id: identity.uuid });
  }

  function handleLeaveClick() {
    send({ kind: "leave", player_id: identity.uuid });
    onLeave();
  }

  return (
    <div className="flex min-h-screen flex-col bg-base-200">
      {/* En-tête */}
      <header className="flex items-center justify-between bg-base-100 px-4 py-2 shadow">
        <span className="font-mono text-sm">
          Room {roomId} {!connected && <span className="text-error">(déconnecté)</span>}
        </span>
        <button type="button" className="btn btn-error btn-outline btn-sm" onClick={handleLeaveClick}>
          Quitter
        </button>
      </header>

      {/* Tous les joueurs, dans l'ordre du tour, soi-même compris */}
      <div className="flex gap-3 overflow-x-auto p-3">
        {view.players.map((player, index) => {
          const isTheirTurn = index === view.current_player_index;
          const isMe = player.id === view.player_id;
          return (
            <div
              key={player.id}
              className={`flex shrink-0 flex-col items-center gap-1 rounded-box p-2 ${
                isTheirTurn ? "bg-primary text-primary-content" : "bg-base-100"
              } ${player.has_left ? "opacity-40" : ""}`}
            >
              <div className="avatar">
                <div className="w-10 rounded-full">
                  <img src={avatarSrc(player.avatar)} alt="" />
                </div>
              </div>
              <span className="max-w-20 truncate text-xs font-semibold">
                {player.username}
                {isMe ? " (vous)" : ""}
              </span>
              <span className="text-xs">
                {player.has_left
                  ? "a quitté"
                  : `${player.hand_count} carte${player.hand_count !== 1 ? "s" : ""}`}
              </span>
            </div>
          );
        })}
      </div>

      {/* Zone centrale */}
      <div className="flex flex-1 flex-col items-center justify-center gap-4 p-4">
        {view.draw_chain && (
          <div className="alert alert-warning max-w-sm py-2 text-sm">
            Chaîne de pioche active : +{view.draw_chain.total}
            {view.draw_chain.has_double ? " et x2" : ""} — pose une carte pioche ou pioche.
          </div>
        )}
        {view.announced_color && !view.draw_chain && (
          <div className="flex items-center gap-2 text-sm text-base-content/70">
            <span>Couleur en cours :</span>
            <span className={`inline-block h-4 w-4 rounded-full ${COLOR_CLASSES[view.announced_color]}`} />
          </div>
        )}

        <div className="flex flex-wrap items-center justify-center gap-4">
          <button type="button" className="btn btn-sm" disabled={!isMyTurn} onClick={handleDraw}>
            Piocher
          </button>

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

            {/* Emplacement toujours réservé, même vide, pour que rien ne saute au premier coup */}
            <div className="flex w-14 flex-col items-center gap-1 sm:w-16">
              {view.second_chance_pile.length > 0 && (
                <>
                  <CardBack count={view.second_chance_pile.length} />
                  <span className="text-xs text-base-content/60">2ndes chances</span>
                </>
              )}
            </div>
          </div>

          <button type="button" className="btn btn-sm" disabled={!isMyTurn} onClick={handlePass}>
            Passer
          </button>
        </div>

        <p className="text-lg font-semibold">
          {isMyTurn ? "À toi de jouer" : `Tour de ${view.players[view.current_player_index]?.username}`}
        </p>

        {serverError && <p className="text-sm text-error">{serverError}</p>}
      </div>

      {/* Main du joueur */}
      <div className="flex flex-col gap-2 bg-base-100 p-3 shadow-inner">
        <div className="flex items-center justify-center gap-2">
          <button
            type="button"
            className={`btn btn-xs ${pairMode ? "btn-secondary" : "btn-outline"}`}
            disabled={!isMyTurn}
            onClick={togglePairMode}
          >
            {pairMode ? "Annuler la paire" : "Jouer une paire (2 cartes)"}
          </button>
        </div>

        {pairMode && selectedForPair.length < 2 && (
          <p className="text-center text-xs text-base-content/60">
            Choisis 2 cartes numérotées dont la somme correspond au sommet de la défausse
            ({selectedForPair.length}/2 sélectionnée{selectedForPair.length !== 1 ? "s" : ""}).
          </p>
        )}

        {pairMode && selectedForPair.length === 2 && (
          <div className="flex flex-col items-center gap-2">
            <p className="text-xs text-base-content/60">Quelle carte doit se retrouver au-dessus ?</p>
            <div className="flex gap-3">
              {selectedCards.map((card) => (
                <button
                  key={card.id}
                  type="button"
                  className="btn btn-sm"
                  onClick={() => handleConfirmPair(card.id)}
                >
                  {card.value}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2 overflow-x-auto px-2 pb-2">
          {view.hand.map((card) => (
            <CardView
              key={card.id}
              card={card}
              onClick={() => handleCardClick(card)}
              disabled={!isMyTurn || (pairMode && card.kind !== "number")}
              selected={selectedForPair.includes(card.id)}
            />
          ))}
        </div>
      </div>

      {pendingSpecial && (
        <SpecialCardModal
          card={pendingSpecial}
          opponents={opponents}
          onConfirm={handleConfirmSpecial}
          onCancel={() => setPendingSpecial(null)}
        />
      )}

      {view.winner_id && (
        <ScoreModal roomId={roomId} myId={identity.uuid} onBackToMenu={onLeave} />
      )}
    </div>
  );
}