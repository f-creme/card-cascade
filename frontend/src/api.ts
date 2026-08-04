import type { CreateRoomResponse, JoinRoomResponse, RoomStatus, ScoresResponse, UserProfile } from "./types";

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

export async function getRoomStatus(roomId: string): Promise<RoomStatus> {
    const response = await fetch(`${API_URL}/rooms/${roomId}`);
    return parseOrThrow<RoomStatus>(response);
}

export async function startRoom(roomId: string, playerId: string): Promise<void> {
    const response = await fetch(`${API_URL}/rooms/${roomId}/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_id: playerId }),
    });
    await parseOrThrow<{ status: string }>(response);
}

export async function getRoomScores(roomId: string): Promise<ScoresResponse> {
    const response = await fetch(`${API_URL}/rooms/${roomId}/scores`);
    return parseOrThrow<ScoresResponse>(response);
}