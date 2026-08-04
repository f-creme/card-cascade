import { useMemo } from "react";

export interface ConfettiToken {
  type: "color" | "emoji";
  value: string; // css color or emoji
}

interface Props {
  tokens: ConfettiToken[];
  count?: number;
}

export function Confetti({ tokens, count = 90 }: Props) {
  const particles = useMemo(() => {
    if (tokens.length === 0) return [];
    return Array.from({ length: count }, (_, i) => ({
      id: i,
      token: tokens[i % tokens.length],
      left: Math.random() * 100,
      delay: Math.random() * 1.2,
      duration: 2.5 + Math.random() * 2,
      rotate: Math.random() * 360,
      size: 10 + Math.random() * 10,
    }));
  }, [tokens, count]);

  return (
    <div className="pointer-events-none fixed inset-0 z-[70] overflow-hidden">
      {particles.map((p) => (
        <span
          key={p.id}
          className="absolute -top-[5%] animate-confetti-fall"
          style={{
            left: `${p.left}%`,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
          }}
        >
          {p.token.type === "emoji" ? (
            <span style={{ fontSize: p.size }}>{p.token.value}</span>
          ) : (
            <span
              className="block rounded-sm"
              style={{
                width: p.size,
                height: p.size,
                backgroundColor: p.token.value,
                transform: `rotate(${p.rotate}deg)`,
              }}
            />
          )}
        </span>
      ))}
    </div>
  );
}