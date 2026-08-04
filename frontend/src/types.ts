export interface UserProfile {
    uuid: string;
    username: string;
    avatar: string | null;
    games_played: number;
    games_won: number;
}

export interface Identity {
    uuid: string;
    username: string;
    avatar: string;
}

export interface LobbyPlayer {
    id: string;
    username: string;
}

export interface JoinRoomResponse {
    owner_id: string;
    players: LobbyPlayer[];
}

export interface CreateRoomResponse {
    room_id: string;
}

export interface LobbyPlayerWithStats {
    id: string;
    username: string;
    avatar: string;
    games_played: number;
    games_won: number;
}

export interface RoomStatus {
    owner_id: string;
    started: boolean;
    players: LobbyPlayerWithStats[];
}