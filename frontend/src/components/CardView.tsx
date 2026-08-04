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

function labelAndColor(card: Card): { label: string; colorClass: string } {
  switch (card.kind) {
    case "number":
      return { label: String(card.value), colorClass: COLOR_CLASSES[card.color] };
    case "draw":
      return { label: `+${card.amount}`, colorClass: "bg-slate-700" };
    case "double":
      return { label: "x2", colorClass: "bg-slate-900" };
    case "second_chance":
      return { label: "2nde ch.", colorClass: "bg-violet-600" };
    case "block":
      return { label: "Bloc", colorClass: "bg-rose-800" };
    case "block3":
      return { label: "Bloc x3", colorClass: "bg-rose-950" };
  }
}

interface Props {
  card: Card;
  onClick?: () => void;
  disabled?: boolean;
}

export function CardView({ card, onClick, disabled }: Props) {
  const { label, colorClass } = labelAndColor(card);
  const clickable = !!onClick && !disabled;

  return (
    <button
      type="button"
      disabled={!clickable}
      onClick={onClick}
      className={`flex h-20 w-14 shrink-0 items-center justify-center rounded-lg text-sm font-bold text-white shadow transition sm:h-24 sm:w-16 ${colorClass} ${
        clickable ? "cursor-pointer hover:-translate-y-1" : "cursor-default opacity-90"
      }`}
    >
      {label}
    </button>
  );
}

export function CardBack({ count, onClick }: { count: number; onClick?: () => void }) {
  return (
    <button
      type="button"
      disabled={!onClick}
      onClick={onClick}
      className={`flex h-20 w-14 shrink-0 items-center justify-center rounded-lg border-2 border-base-100 bg-neutral text-sm font-bold text-neutral-content shadow sm:h-24 sm:w-16 ${
        onClick ? "cursor-pointer hover:-translate-y-1" : "cursor-default opacity-60"
      }`}
    >
      {count}
    </button>
  );
}