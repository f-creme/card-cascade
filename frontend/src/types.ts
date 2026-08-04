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