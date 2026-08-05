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

interface Props {
  card: Card;
  onClick?: () => void;
  disabled?: boolean;
  selected?: boolean;
}

export function CardView({ card, onClick, disabled, selected }: Props) {
  const clickable = !!onClick && !disabled;

  return (
    <button
      type="button"
      disabled={!clickable}
      onClick={onClick}
      className={`aspect-[600/1130] w-20 shrink-0 overflow-hidden rounded-lg shadow-md transition sm:w-28 ${
        selected ? "z-10 -translate-y-4 ring-4 ring-primary" : ""
      } ${clickable ? "cursor-pointer hover:z-10 hover:-translate-y-2 hover:scale-110" : "cursor-default opacity-60"}`}
    >
      <img src={cardImageSrc(card)} alt={cardLabel(card)} className="h-full w-full object-cover" />
    </button>
  );
}

export function CardBack({ count, onClick }: { count: number; onClick?: () => void }) {
  return (
    <button
      type="button"
      disabled={!onClick}
      onClick={onClick}
      className={`relative aspect-[600/1130] w-20 shrink-0 overflow-hidden rounded-lg shadow-md sm:w-28 ${
        onClick ? "cursor-pointer hover:-translate-y-2 hover:scale-110" : "cursor-default opacity-60"
      }`}
    >
      <img src={CARD_BACK_SRC} alt="Pioche" className="h-full w-full object-cover" />
      <span className="absolute bottom-1 right-1 rounded-full bg-neutral px-2 py-0.5 text-sm font-bold text-neutral-content shadow">
        {count}
      </span>
    </button>
  );
}