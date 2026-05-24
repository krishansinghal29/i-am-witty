import { createContext, useContext, type ReactNode } from 'react';

function getOrCreateSessionUid(): string {
  const stored = localStorage.getItem('sessionUid');
  if (stored) return stored;
  const newUid = crypto.randomUUID();
  localStorage.setItem('sessionUid', newUid);
  return newUid;
}

const uid = getOrCreateSessionUid();

interface UserContextValue {
  uid: string;
  isAnonymous: boolean;
}

const UserContext = createContext<UserContextValue>({ uid, isAnonymous: true });

export const UserProvider = ({ children }: { children: ReactNode }) => (
  <UserContext.Provider value={{ uid, isAnonymous: true }}>
    {children}
  </UserContext.Provider>
);

export const useUser = () => useContext(UserContext);
