import Dexie, { Table } from 'dexie';

export interface Clip {
  id: string;
  status: 'pending' | 'uploading' | 'uploaded' | 'failed';
  blob: Blob;
  dialect: string;
  duration: number;
  createdAt: Date;
  serverClipId?: string;
  metadata: Record<string, any>;
}

export interface AnnotationDraft {
  id: string;
  clipId: string;
  draftText: string;
  savedAt: Date;
}

export interface TxQueue {
  id: string;
  rewardId: string;
  signedTx: string;
  status: 'pending' | 'sent' | 'failed';
}

export class LinguanaDB extends Dexie {
  clips!: Table<Clip>;
  annotationDrafts!: Table<AnnotationDraft>;
  txQueue!: Table<TxQueue>;

  constructor() {
    super('LinguanaDB');
    this.version(1).stores({
      clips: 'id, status, dialect, createdAt',
      annotationDrafts: 'id, clipId, savedAt',
      txQueue: 'id, rewardId, status'
    });
  }
}

export const db = new LinguanaDB();
