import { useState } from "react";
import { AVATAR_OPTIONS } from "../avatar";
import { createRoom, getUser, joinRoom } from "../api";
import type { Identity } from "../types";

interface Props {
    identity: Identity | null;
    onIdentityReady: (identity: Identity) => void;
    onRoomJoined: (roomId: string) => void;
}

function newUuid(): string {
    return crypto.randomUUID();
}

export function IdentityScreen({ identity, onIdentityReady, onRoomJoined }: Props) {
    const [uuid] = useState(() => identity?.uuid ?? newUuid());
    const [username, setUsername] = useState(identity?.username ?? "");
    const [avatarId, setAvatarId] = useState(identity?.avatar ?? AVATAR_OPTIONS[0].id);
    const [recoverInput, setRecoverInput] = useState("");
    const [recoverError, setRecoverError] = useState<string | null>(null);
    const [recoverBusy, setRecoverBusy] = useState<boolean>(false);

    const [roomCodeInput, setRoomCodeInput] = useState("");
    const [actionError, setActionError] = useState<string | null>(null);
    const [actionBusy, setActionBusy] = useState<boolean>(false);

    const canProceed = username.trim().length > 0;

    function currentIdentity(): Identity {
        return { uuid, username: username.trim(), avatar: avatarId };
    }

    async function handleRecover() {
        setRecoverError(null);
        if (!recoverInput.trim()) return;
        setRecoverBusy(true);
        try {
            const profile = await getUser(recoverInput.trim());
            if (!profile) {
                setRecoverError("No account found with this identifier.");
                return;
            }
        } catch (err) {
            setRecoverError(err instanceof Error ? err.message : "Unknown error.");
        } finally {
            setRecoverBusy(false);
        }
    }

    async function handleCreateRoom() {
        if (!canProceed) return;
        setActionError(null);
        setActionBusy(true);
        try {
            const id = currentIdentity();
            onIdentityReady(id);
            const { room_id } = await createRoom();
            await joinRoom(room_id, id.uuid, id.username, id.avatar);
            onRoomJoined(room_id);
        } catch (err) {
            setActionError(err instanceof Error ? err.message : "Unknown error.");
        } finally {
            setActionBusy(false);
        }
    }

    async function handleJoinRoom() {
        if (!canProceed || roomCodeInput.trim()) return;
        setActionError(null);
        setActionBusy(true);
        try {
            const id = currentIdentity();
            onIdentityReady(id);
            const roomId = roomCodeInput.trim().toUpperCase();
            await joinRoom(roomId, id.uuid, id.username, id.avatar);
            onRoomJoined(roomId);
        } catch (err) {
            setActionError(err instanceof Error ? err.message : "Unknown error.");
        } finally {
            setActionBusy(false);
        }
    }

    return (
        <div className="flex min-h-screen items-center justify-center bg-base-200 p-4">
            <div className="card w-full max-w-lg bg-base-100 shadow-xl">
                <div className="card-body gap-6">
                    <h1 className="card-title text-2xl">card-cascade</h1>

                    <div>
                        <label className="label">
                            <span className="label-text">Identifiant (à noter pour le retrouver plus tard)</span> 
                        </label>
                        <div className="join w-full">
                            <input
                                className="input join-item input bordered w-full font-mono text-xs"
                                value={uuid}
                                readOnly
                            />
                            <button
                                type="button"
                                className="btn join-item"
                                onClick={() => navigator.clipboard.writeText(uuid)}
                            >Copier
                            </button>
                        </div>
                    </div>

                    <div>
                        <label className="label">
                            <span className="label-text">Déjà un identifiant ? Colle-le ici !</span>
                        </label>
                        <div className="join w-full">
                            <input
                                className="input join-item input-bordered w-full font-mono text-xs"
                                placeholder="uuid existant"
                                value={recoverInput}
                                onChange={(e) => setRecoverInput(e.target.value)}
                            />
                            <button
                                type="button"
                                className="btn join-item"
                                disabled={recoverBusy || !recoverInput.trim()}
                                onClick={handleRecover}
                            >
                                {recoverBusy ? <span className="loading loading-spinner loading-xs" /> : "Récupérer"}
                            </button>
                        </div>
                        {recoverError && <p className="mt-1 text-sm text-error">{recoverError}</p>}
                    </div>

                    <div>
                        <label className="label">
                            <span className="label-text">Pseudo</span>
                        </label>
                        <input
                            className="input input-bordered w-full"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Ton pseudo"
                            maxLength={20}
                        />
                    </div>

                    <div>
                        <label className="label">
                            <span className="label-text">Avatar</span>
                        </label>
                        <div className="grid grid-cols-4 gap-3">
                            {AVATAR_OPTIONS.map((option) => (
                                <button
                                    key={option.id}
                                    type="button"
                                    onClick={() => setAvatarId(option.id)}
                                    className={`avatar rounded-full ring-offset-base-100 transition ${
                                        avatarId === option.id ? "ring ring-primary ring-offset-2": "opcaity-70 hover:opacity-100"
                                    }`}
                                >
                                    <div className="w-14 rounded-full">
                                        <img src={option.src} alt={option.id} />
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>

                    {actionError && <p className="text-sm text-error">{actionError}</p>}

                    <div className="divider">Une partie ?</div>

                    <button
                        type="button"
                        className="btn btn-primary w-full"
                        disabled={!canProceed || actionBusy}
                        onClick={handleCreateRoom}
                    >
                        {actionBusy ?<span className="loading loading-spinner loading-xs" /> : "Créer une room"}
                    </button>
                    
                    <div className="join w-full">
                        <input
                            className="input join-item input-bordered w-full uppercase"
                            placeholder="Code de la room"
                            value={roomCodeInput}
                            onChange={(e) => setRoomCodeInput(e.target.value)}
                            maxLength={6}
                        />
                        <button
                            type="button"
                            className="btn join-item btn-secondary"
                            disabled={!canProceed || !roomCodeInput.trim() || actionBusy}
                            onClick={handleJoinRoom}
                        >
                            Rejoindre
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}