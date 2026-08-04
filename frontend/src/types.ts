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

export type Color = "pink" | "gray" | "green" | "red" | "blue" | "orange" | "brown";

export interface NumberCard {
  id: string;
  kind: "number";
  value: number;
  color: Color;
}

export interface DrawCard {
  id: string;
  kind: "draw";
  amount: number;
}

export interface DoubleCard {
  id: string;
  kind: "double";
}

export interface SecondChanceCard {
  id: string;
  kind: "second_chance";
}

export interface BlockCard {
  id: string;
  kind: "block";
}

export interface Block3Card {
  id: string;
  kind: "block3";
}

export type Card = NumberCard | DrawCard | DoubleCard | SecondChanceCard | BlockCard | Block3Card;

export interface PublicPlayer {
  id: string;
  username: string;
  avatar: string | null;
  hand_count: number;
  has_left: boolean;
}

export interface DrawChain {
  total: number;
  has_double: boolean;
  pending_color: Color;
}

export interface PlayerView {
  player_id: string;
  hand: Card[];
  players: PublicPlayer[];
  current_player_index: number;
  draw_pile_count: number;
  discard_pile: Card[];
  announced_color: Color | null;
  draw_chain: DrawChain | null;
  pending_skips: Record<string, number>;
  second_chance_pile: Card[];
  winner_id: string | null;
  has_drawn: boolean;
  second_chances_played: number;
}

export type Action =
  | { kind: "play_card"; player_id: string; card_id: string }
  | { kind: "play_pair"; player_id: string; card_id_1: string; card_id_2: string; top_card_id: string }
  | {
      kind: "play_special";
      player_id: string;
      card_id: string;
      announced_color?: Color;
      skip_targets?: string[];
    }
  | { kind: "draw"; player_id: string }
  | { kind: "pass"; player_id: string }
  | { kind: "leave"; player_id: string };