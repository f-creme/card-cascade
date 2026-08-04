import { useCallback, useEffect, useState } from "react";
import type { Identity } from "../types";

const STORAGE_KEY = "card-cascade:identity";

function readStoredIdentity(): Identity | null {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    try {
        return JSON.parse(raw) as Identity;
    } catch {
        return null;
    }
}

export function useIdentity() {
    const [identity, setIdentityState] = useState<Identity | null>(() => readStoredIdentity());

    useEffect(() => {
        if (identity) {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(identity));
        }
    }, [identity]);

    const setIdentity = useCallback((next: Identity) => {
        setIdentityState(next);
    }, []);

    const clearIdentity = useCallback(() => {
        localStorage.removeItem(STORAGE_KEY);
        setIdentityState(null);
    }, []);

    return { identity, setIdentity, clearIdentity };
}