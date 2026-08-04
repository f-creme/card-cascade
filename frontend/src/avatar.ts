export interface AvatarOption {
    id: string;
    src: string;
}

export const AVATAR_OPTIONS: AvatarOption[] = [
    { id: "avatar-1", src: "/avatars/avatar-1.png"},
    { id: "avatar-2", src: "/avatars/avatar-2.png"},
    { id: "avatar-3", src: "/avatars/avatar-3.png"},
    { id: "avatar-4", src: "/avatars/avatar-4.png"},
    { id: "avatar-5", src: "/avatars/avatar-5.png"},
    { id: "avatar-6", src: "/avatars/avatar-6.png"},
    { id: "avatar-7", src: "/avatars/avatar-7.png"},
    { id: "avatar-8", src: "/avatars/avatar-8.png"},
]

export function avatarSrc(avatarId: string | null): string {
    return AVATAR_OPTIONS.find((a) => a.id === avatarId)?.src ?? AVATAR_OPTIONS[0].src;
}