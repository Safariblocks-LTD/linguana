'use client';

import { ReactNode } from 'react';

// Simplified provider - no heavy dependencies
export function Web3Provider({ children }: { children: ReactNode }) {
  return <>{children}</>;
}
