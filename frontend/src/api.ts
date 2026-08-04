import type { CreateRoomResponse, JoinRoomResponse, UserProfile } from "./types";

const API_URL = import.meta.env.VITE_API_URL as string;

async function parseOrThrow<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const body = await response.json().catch(() => null);
        throw new Error(body?.detail ?? `Error ${response.status}`);
    }
    return response.json() as Promise<T>;
}

export async function getUser(uuid: string): Promise<UserProfile | null> {
    const response = await fetch(`${API_URL}/users/${uuid}`);
    if (response.status === 404) return null;
    return parseOrThrow<UserProfile>(response);
}

export async function createRoom(): Promise<CreateRoomResponse> {
    const response = await fetch(`${API_URL}/rooms`, { method: "POST" });
    return parseOrThrow<CreateRoomResponse>(response);
}

export async function joinRoom(
    roomId: string,
    playerId: string, 
    username: string,
    avatar: string,
): Promise<JoinRoomResponse> {
    const response = await fetch(`${API_URL}/rooms/${roomId}/join`, {
        method: "POST", 
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_id: playerId, username, avatar}),
    });
    return parseOrThrow<JoinRoomResponse>(response);
}

