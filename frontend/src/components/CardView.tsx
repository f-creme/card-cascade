import { useRef, useState } from "react";
import { createPortal } from "react-dom";
import type { Card, Color } from "../types";

export const COLOR_CLASSES: Record<Color, string> = {
  pink: "bg-pink-400",
  gray: "bg-gray-400",
  green: "bg-green-500",
  red: "bg-red-500",
  blue: "bg-blue-500",
  orange: "bg-orange-500",
  brown: "bg-amber-800",
};

const CARD_BACK_SRC = "/cards/back.PNG";

function cardImageSrc(card: Card): string {
  switch (card.kind) {
    case "number":
      return `/cards/number-${card.value}.PNG`;
    case "draw":
      return `/cards/draw-${card.amount}.PNG`;
    case "double":
      return "/cards/double.PNG";
    case "second_chance":
      return "/cards/second-chance.PNG";
    case "block":
      return "/cards/block.PNG";
    case "block3":
      return "/cards/block3.PNG";
  }
}

function cardLabel(card: Card): string {
  switch (card.kind) {
    case "number":
      return `Carte ${card.value}`;
    case "draw":
      return `Pioche +${card.amount}`;
    case "double":
      return "Double (x2)";
    case "second_chance":
      return "Seconde chance";
    case "block":
      return "Bloc";
    case "block3":
      return "Bloc 3 fois";
  }
}

const SPECIAL_DESCRIPTIONS: Partial<Record<Card["kind"], string>> = {
  draw: "Le joueur suivant pioche ce nombre de cartes, ou pose une autre carte de ce type pour continuer la chaîne. Se pose sur une carte numérotée (ou sur une chaîne déjà en cours). Nécessite d'annoncer une couleur.",
  double:
    "Double la main du joueur qui devra finalement piocher au bout de la chaîne. Se combine avec les cartes +X. Nécessite d'annoncer une couleur.",
  second_chance:
    "Jouable à tout moment durant ton tour : tu pioches une carte de plus, dans l'espoir qu'elle soit jouable.",
  block: "Le joueur suivant passe son tour. Se pose sur une carte numérotée. Nécessite d'annoncer une couleur.",
  block3:
    "Distribue 3 tours passés entre les joueurs de ton choix. Se pose sur une carte numérotée. Nécessite d'annoncer une couleur.",
};

interface Props {
  card: Card;
  onClick?: () => void;
  disabled?: boolean;
  selected?: boolean;
}

export function CardView({ card, onClick, disabled, selected }: Props) {
  const clickable = !!onClick && !disabled;
  const description = SPECIAL_DESCRIPTIONS[card.kind];

  const buttonRef = useRef<HTMLButtonElement>(null);
  const [tooltipPos, setTooltipPos] = useState<{ top: number; left: number } | null>(null);

  function showTooltip() {
    if (!description || !buttonRef.current) return;
    const rect = buttonRef.current.getBoundingClientRect();
    setTooltipPos({ top: rect.top, left: rect.left + rect.width / 2 });
  }

  function hideTooltip() {
    setTooltipPos(null);
  }

  return (
    <>
      <button
        ref={buttonRef}
        type="button"
        disabled={!clickable}
        onClick={onClick}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        className={`aspect-[600/1130] w-20 shrink-0 overflow-hidden rounded-lg shadow-md transition sm:w-28 ${
          selected ? "z-10 -translate-y-4 ring-4 ring-primary" : ""
        } ${clickable ? "cursor-pointer hover:z-10 hover:-translate-y-2 hover:scale-105" : "cursor-default opacity-90"}`}
      >
        <img src={cardImageSrc(card)} alt={cardLabel(card)} className="h-full w-full object-cover" />
      </button>

      {description &&
        tooltipPos &&
        createPortal(
          <div
            className="pointer-events-none fixed z-[100] w-56 -translate-x-1/2 -translate-y-full"
            style={{ top: tooltipPos.top - 8, left: tooltipPos.left }}
          >
            <div className="rounded-lg bg-neutral p-3 text-xs leading-snug text-neutral-content shadow-xl">
              <p className="mb-1 font-semibold">{cardLabel(card)}</p>
              <p>{description}</p>
            </div>
            <div className="mx-auto -mt-1 h-2 w-2 rotate-45 bg-neutral" />
          </div>,
          document.body,
        )}
    </>
  );
}

export function CardBack({ count, onClick }: { count: number; onClick?: () => void }) {
  return (
    <button
      type="button"
      disabled={!onClick}
      onClick={onClick}
      className={`relative aspect-[600/1130] w-20 shrink-0 overflow-hidden rounded-lg shadow-md transition sm:w-28 ${
        onClick ? "cursor-pointer hover:z-10 hover:-translate-y-2 hover:scale-105" : "cursor-default opacity-60"
      }`}
    >
      <img src={CARD_BACK_SRC} alt="Pioche" className="h-full w-full object-cover" />
      <span className="absolute bottom-1 right-1 rounded-full bg-neutral px-2 py-0.5 text-sm font-bold text-neutral-content shadow">
        {count}
      </span>
    </button>
  );
}