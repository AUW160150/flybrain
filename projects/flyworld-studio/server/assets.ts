import { createHash } from 'node:crypto';
import { mkdir, readFile, writeFile, rename } from 'node:fs/promises';
import { join } from 'node:path';
import type { Receipt } from '../src/connectome/types';

export const BUCKET = 'https://storage.googleapis.com/flyem-male-cns/';
export const hash = (bytes: Uint8Array | string) => createHash('sha256').update(bytes).digest('hex');
export const assetKey = (url: string, range?: [number, number]) => hash(url + (range ? `#${range[0]}-${range[1]}` : ''));
export interface Asset { data: Buffer; receipt: Receipt }
export type GetAsset = (url: string, maxBytes?: number, range?: [number, number]) => Promise<Asset>;

/** Local server only. No credentials, arbitrary URLs, redirects or unbounded downloads. */
export function assetCache(directory: string): GetAsset {
  const pending = new Map<string, Promise<Asset>>();
  return (url, maxBytes = 16 * 1024 * 1024, range) => {
    if (!url.startsWith(BUCKET) || /[?#]/.test(url) || url.includes('..')) return Promise.reject(new Error('Unsupported official asset URL'));
    if (range && (!range.every(Number.isSafeInteger) || range[0] < 0 || range[1] <= range[0] || range[1]-range[0] > maxBytes)) return Promise.reject(new Error('Invalid byte range'));
    const key = assetKey(url, range);
    if (pending.has(key)) return pending.get(key)!;
    const operation = (async () => {
      const folder = join(directory, key);
      try {
        const receipt: Receipt = JSON.parse(await readFile(join(folder, 'receipt.json'), 'utf8'));
        const data = await readFile(join(folder, 'raw.bin'));
        if (receipt.url !== url || JSON.stringify(receipt.range) !== JSON.stringify(range) || receipt.bytes !== data.length || hash(data) !== receipt.sha256 || data.length > maxBytes) throw new Error('Asset cache integrity failure');
        return { data, receipt };
      } catch (error) { if ((error as NodeJS.ErrnoException).code !== 'ENOENT') throw error; }
      const response = await fetch(url, { redirect: 'error', signal: AbortSignal.timeout(25000), headers: range ? { Range: `bytes=${range[0]}-${range[1]-1}`, 'Accept-Encoding': 'identity' } : {} });
      if (response.status !== (range ? 206 : 200)) { await response.body?.cancel(); throw new Error(`Official source returned HTTP ${response.status}; no substitute data was used`); }
      if (range && !response.headers.get('content-range')?.startsWith(`bytes ${range[0]}-${range[1]-1}/`)) { await response.body?.cancel(); throw new Error('Official source returned a different byte range'); }
      if (Number(response.headers.get('content-length')) > maxBytes) { await response.body?.cancel(); throw new Error('Asset exceeds the download budget'); }
      const chunks: Buffer[] = []; let size = 0;
      const reader = response.body!.getReader();
      try {
        while (true) {
          const { done, value } = await reader.read(); if (done) break;
          size += value.byteLength;
          if (size > maxBytes) throw new Error('Asset exceeds the download budget');
          chunks.push(Buffer.from(value));
        }
      } finally { await reader.cancel(); }
      const data = Buffer.concat(chunks);
      if (range && data.length !== range[1]-range[0]) throw new Error('Truncated range response');
      const receipt: Receipt = { url, bytes: data.length, sha256: hash(data), retrievedAt: new Date().toISOString(), ...(range ? { range } : {}), etag: response.headers.get('etag') ?? undefined, generation: response.headers.get('x-goog-generation') ?? undefined };
      await mkdir(folder, { recursive: true });
      await writeFile(join(folder, 'raw.partial'), data); await rename(join(folder, 'raw.partial'), join(folder, 'raw.bin'));
      await writeFile(join(folder, 'receipt.partial'), JSON.stringify(receipt)); await rename(join(folder, 'receipt.partial'), join(folder, 'receipt.json'));
      return { data, receipt };
    })();
    pending.set(key, operation);
    void operation.finally(() => pending.delete(key)).catch(() => {});
    return operation;
  };
}
