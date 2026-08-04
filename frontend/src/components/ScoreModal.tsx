import { useEffect, useState } from "react";
import { getRoomScores } from "../api";
import { avatarSrc } from "../avatar";
import { Confetti, type ConfettiToken } from "./Confetti";
import type { ScoreEntry } from "../types";

interface Props {
  roomId: string;
  myId: string;
  onBackToMenu: () => void;
}

const MOCKING_EMOJIS = ["😂🫵", "🫠", "🙄", "👎"];
const MEDAL_COLORS = ["#FFD700", "#C0C0C0", "#CD7F32"]; // or, argent, bronze

function buildMyConfettiTokens(ranking: ScoreEntry[], myId: string): ConfettiToken[] {
  const myIndex = ranking.findIndex((entry) => entry.id === myId);
  if (myIndex === -1) return [];

  const isLastPlace = myIndex === ranking.length - 1;

  // le dernier a toujours des emojis, même s'il est 2e ou 3e
  if (isLastPlace) {
    return MOCKING_EMOJIS.map((emoji) => ({ type: "emoji", value: emoji }));
  }
  if (myIndex < 3) {
    return [{ type: "color", value: MEDAL_COLORS[myIndex] }];
  }
  return MOCKING_EMOJIS.map((emoji) => ({ type: "emoji", value: emoji }));
}

export function ScoreModal({ roomId, myId, onBackToMenu }: Props) {
  const [scores, setScores] = useState<ScoreEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getRoomScores(roomId)
      .then((data) => {
        if (!cancelled) setScores(data.ranking);
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Erreur inconnue.");
      });
    return () => {
      cancelled = true;
    };
  }, [roomId]);

  const podium = scores?.slice(0, 3) ?? [];
  const confettiTokens = scores ? buildMyConfettiTokens(scores, myId) : [];

  return (
    <div className="modal modal-open">
      {scores && <Confetti tokens={confettiTokens} />}

      <div className="modal-box max-w-2xl">
        <h2 className="mb-4 text-center text-2xl font-bold">Partie terminée !</h2>

        {error && <p className="text-center text-sm text-error">{error}</p>}

        {!scores && !error && (
          <div className="flex justify-center py-8">
            <span className="loading loading-spinner loading-lg" />
          </div>
        )}

        {scores && (
          <>
            {/* Podium */}
            <div className="mb-6 flex items-end justify-center gap-3">
              {podium[1] && <PodiumSpot entry={podium[1]} place={2} isMe={podium[1].id === myId} />}
              {podium[0] && <PodiumSpot entry={podium[0]} place={1} isMe={podium[0].id === myId} />}
              {podium[2] && <PodiumSpot entry={podium[2]} place={3} isMe={podium[2].id === myId} />}
            </div>

            {/* Tableau complet */}
            <div className="overflow-x-auto">
              <table className="table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th></th>
                    <th>Joueur</th>
                    <th>Score</th>
                    <th>Cartes restantes</th>
                  </tr>
                </thead>
                <tbody>
                  {scores.map((entry, index) => (
                    <tr key={entry.id} className={entry.id === myId ? "font-semibold" : ""}>
                      <td>{index + 1}</td>
                      <td>
                        <div className="avatar">
                          <div className="w-8 rounded-full">
                            <img src={avatarSrc(entry.avatar)} alt="" />
                          </div>
                        </div>
                      </td>
                      <td>
                        {entry.username}
                        {entry.id === myId ? " (vous)" : ""}
                      </td>
                      <td>{entry.score}</td>
                      <td>{entry.cards_remaining}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        <div className="modal-action justify-center">
          <button type="button" className="btn btn-primary" onClick={onBackToMenu}>
            Retour au menu
          </button>
        </div>
      </div>
    </div>
  );
}

function PodiumSpot({ entry, place, isMe }: { entry: ScoreEntry; place: 1 | 2 | 3; isMe: boolean }) {
  const heights: Record<1 | 2 | 3, string> = { 1: "h-24", 2: "h-16", 3: "h-12" };
  const medals: Record<1 | 2 | 3, string> = { 1: "🥇", 2: "🥈", 3: "🥉" };

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="avatar">
        <div className={`w-12 rounded-full ${place === 1 ? "ring ring-primary ring-offset-2" : ""}`}>
          <img src={avatarSrc(entry.avatar)} alt="" />
        </div>
      </div>
      <span className="max-w-20 truncate text-xs font-semibold">
        {entry.username}
        {isMe ? " (vous)" : ""}
      </span>
      <div className={`flex ${heights[place]} w-16 flex-col items-center justify-start rounded-t-box bg-base-200 pt-1`}>
        <span className="text-xl">{medals[place]}</span>
      </div>
    </div>
  );
}