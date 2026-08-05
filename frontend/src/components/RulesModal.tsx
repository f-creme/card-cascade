import { CardView, SPECIAL_DESCRIPTIONS } from "./CardView";
import type { Card } from "../types";

interface Props {
  onClose: () => void;
}

const SAMPLE_NUMBER_CARD: Card = { id: "sample-number", kind: "number", value: 7, color: "brown" };

const SAMPLE_SPECIAL_CARDS: Card[] = [
  { id: "sample-draw", kind: "draw", amount: 4 },
  { id: "sample-double", kind: "double" },
  { id: "sample-second-chance", kind: "second_chance" },
  { id: "sample-block", kind: "block" },
  { id: "sample-block3", kind: "block3" },
];

export function RulesModal({ onClose }: Props) {
  return (
    <div className="modal modal-open">
      <div className="modal-box max-w-2xl">
        <h2 className="mb-4 text-center text-2xl font-bold">Règles</h2>

        <div className="flex flex-col gap-5 text-sm">
          <section>
            <h3 className="mb-1 font-semibold">Objectif</h3>
            <p>Sois le·la premier·ère à te débarrasser de toutes tes cartes.</p>
          </section>

          <section className="flex items-center gap-4">
            <div className="shrink-0">
              <CardView card={SAMPLE_NUMBER_CARD} />
            </div>
            <p>
              Pose une carte dont le numéro est identique, à ±1, ou de la même couleur que le sommet de la
              défausse (ou la couleur annoncée après une carte spéciale).
            </p>
          </section>

          <section>
            <h3 className="mb-1 font-semibold">Une paire</h3>
            <p>
              Tu peux aussi poser 2 cartes numérotées dont la somme égale le sommet de la défausse (bouton
              "Jouer une paire").
            </p>
          </section>

          <section>
            <h3 className="mb-1 font-semibold">Piocher / Passer</h3>
            <p>Si tu ne peux (ou ne veux) rien jouer, pioche une carte. Une fois piochée, tu peux passer.</p>
          </section>

          <section>
            <h3 className="mb-2 font-semibold">Cartes spéciales</h3>
            <div className="flex flex-col gap-3">
              {SAMPLE_SPECIAL_CARDS.map((card) => (
                <div key={card.id} className="flex items-center gap-4">
                  <div className="shrink-0">
                    <CardView card={card} />
                  </div>
                  <p>{SPECIAL_DESCRIPTIONS[card.kind]}</p>
                </div>
              ))}
            </div>
          </section>
        </div>

        <div className="modal-action justify-center">
          <button type="button" className="btn btn-primary" onClick={onClose}>
            Fermer
          </button>
        </div>
      </div>
    </div>
  );
}