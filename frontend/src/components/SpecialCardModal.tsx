import { useState } from "react";
import type { Card, Color, PublicPlayer } from "../types";

const COLOR_OPTIONS: { value: Color; label: string; className: string }[] = [
  { value: "pink", label: "Rose", className: "bg-pink-400" },
  { value: "gray", label: "Gris", className: "bg-gray-400" },
  { value: "green", label: "Vert", className: "bg-green-500" },
  { value: "red", label: "Rouge", className: "bg-red-500" },
  { value: "blue", label: "Bleu", className: "bg-blue-500" },
  { value: "orange", label: "Orange", className: "bg-orange-500" },
  { value: "brown", label: "Marron", className: "bg-amber-800" },
];

interface Props {
  card: Card;
  opponents: PublicPlayer[];
  onConfirm: (announcedColor: Color, skipTargets?: string[]) => void;
  onCancel: () => void;
}

export function SpecialCardModal({ card, opponents, onConfirm, onCancel }: Props) {
  const needsTargets = card.kind === "block3";
  const [step, setStep] = useState<"targets" | "color">(needsTargets ? "targets" : "color");
  const [targets, setTargets] = useState<string[]>([]);

  function addTarget(id: string) {
    if (targets.length >= 3) return;
    setTargets([...targets, id]);
  }

  function removeLastTarget() {
    setTargets(targets.slice(0, -1));
  }

  return (
    <div className="modal modal-open">
      <div className="modal-box">
        {step === "targets" && (
          <>
            <h3 className="text-lg font-bold">À qui distribuer les 3 passages de tour ?</h3>
            <p className="py-2 text-sm text-base-content/60">
              Clique sur un joueur pour lui donner un passage (tu peux cliquer plusieurs fois sur le même).
            </p>
            <div className="flex flex-wrap gap-2 py-2">
              {opponents.map((player) => (
                <button
                  key={player.id}
                  type="button"
                  className="btn btn-outline btn-sm"
                  disabled={targets.length >= 3}
                  onClick={() => addTarget(player.id)}
                >
                  {player.username}
                  {targets.filter((t) => t === player.id).length > 0 &&
                    ` (${targets.filter((t) => t === player.id).length})`}
                </button>
              ))}
            </div>
            <p className="text-sm">Choisis : {targets.length} / 3</p>
            <div className="modal-action">
              <button type="button" className="btn" onClick={onCancel}>
                Annuler
              </button>
              <button
                type="button"
                className="btn btn-ghost"
                disabled={targets.length === 0}
                onClick={removeLastTarget}
              >
                Retirer le dernier
              </button>
              <button
                type="button"
                className="btn btn-primary"
                disabled={targets.length !== 3}
                onClick={() => setStep("color")}
              >
                Suivant
              </button>
            </div>
          </>
        )}

        {step === "color" && (
          <>
            <h3 className="text-lg font-bold">Quelle couleur annoncer ?</h3>
            <div className="grid grid-cols-4 gap-3 py-4">
              {COLOR_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  className={`h-14 rounded-lg ${option.className} text-xs font-semibold text-white shadow hover:scale-105 transition`}
                  onClick={() => onConfirm(option.value, needsTargets ? targets : undefined)}
                >
                  {option.label}
                </button>
              ))}
            </div>
            <div className="modal-action">
              {needsTargets && (
                <button type="button" className="btn" onClick={() => setStep("targets")}>
                  Retour
                </button>
              )}
              <button type="button" className="btn" onClick={onCancel}>
                Annuler
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}