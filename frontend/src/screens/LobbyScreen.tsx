import { useEffect, useState } from "react";
import { avatarSrc } from "../avatar";
import { getRoomStatus, startRoom } from "../api"
import type { Identity, RoomStatus } from "../types";

interface Props {
    roomId: string;
    identity: Identity;
    onGameStart: () => void;
}

const POLL_INTERVAL_MS = 2000;

export function LobbyScreen({ roomId, identity, onGameStart }: Props) {
    const [status, setStatus] = useState<RoomStatus | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [starting, setStarting] = useState<boolean>(false);

    useEffect(() => {
        let cancelled = false;

        async function poll() {
            try {
                const next = await getRoomStatus(roomId);
                if (cancelled) return;
                setStatus(next);
                setError(null);
                if (next.started) onGameStart();
            } catch (err) {
                if (!cancelled) setError (err instanceof Error ? err.message : "Unknown error.");
            }
        }

        poll();
        const interval = setInterval(poll, POLL_INTERVAL_MS);
        return () => {
            cancelled = true;
            clearInterval(interval);
        };
    }, [roomId, onGameStart]);

    const isOwner = status?.owner_id === identity.uuid;
    const canStart = isOwner && (status?.players.length ?? 0) >= 2;

    async function handleStart() {
        setStarting(true);
        setError(null);
        try {
            await startRoom(roomId, identity.uuid);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Unknown error.");
        } finally {
            setStarting(false);
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-base-200 p-4">
            <div className="card w-full max-w-lg bg-base-100 shadow-xl">
                <div className="card-body gap-6">
                    <div className="text-center">
                        <p className="text-sm text-base-content/60">Code de la room</p>
                        <div className="flex items-center justify-center gap-2">
                            <span className="font-mono text-3xl font-bold tracking-widest">{roomId}</span>
                            <button
                                type="button"
                                className="btn btn-ghost btn-sm"
                                onClick={() => navigator.clipboard.writeText(roomId)}
                            >
                                Copier
                            </button>
                        </div>
                    </div>
        
                    {!status && !error && (
                        <div className="flex justify-center py-8">
                            <span className="loading loading-spinner loading-lg" />
                        </div>
                    )}
        
                    {status && (
                        <ul className="flex flex-col gap-2">
                            {status.players.map((player) => (
                                <li
                                    key={player.id}
                                    className="flex flex-wrap items-center gap-3 rounded-box bg-base-200 p-3"
                                >
                                    <div className="avatar">
                                        <div className="w-10 rounded-full">
                                            <img src={avatarSrc(player.avatar)} alt="" />
                                        </div>
                                    </div>
                                    <div className="flex min-w-0 flex-1 flex-col">
                                        <span className="flex items-center gap-2 truncate font-semibold">
                                            {player.username}
                                            {player.id === identity.uuid && (
                                                <span className="badge badge-sm badge-outline">vous</span>
                                            )}
                                            {player.id === status.owner_id && (
                                                <span className="badge badge-sm badge-primary">hôte</span>
                                            )}
                                        </span>
                                        <span className="text-xs text-base-content/60">
                                            {player.games_won} victoire{player.games_won !== 1 ? "s" : ""} /{" "}
                                            {player.games_played} partie{player.games_played !== 1 ? "s" : ""}
                                        </span>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    )}
        
                    {error && <p className="text-sm text-error">{error}</p>}
        
                    <div className="divider" />
        
                    {isOwner ? (
                        <>
                            <button
                                type="button"
                                className="btn btn-primary w-full"
                                disabled={!canStart || starting}
                                onClick={handleStart}
                            >
                                {starting ? <span className="loading loading-spinner loading-xs" /> : "Démarrer la partie"}
                            </button>
                            {!canStart && (
                                <p className="text-center text-sm text-base-content/60">
                                    Il faut au moins 2 joueurs pour démarrer.
                                </p>
                            )}
                        </>
                    ) : (
                        <p className="text-center text-sm text-base-content/60">
                            En attente de l'hôte pour démarrer la partie...
                        </p>
                    )}
                </div>
            </div>
        </div>
    )
}