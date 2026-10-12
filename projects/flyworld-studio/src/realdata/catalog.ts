import { z } from 'zod';
import { BROWSER_LIMITS, SCIENTIFIC_LABELS } from './schema';

export const catalogSchema = z.object({
  format: z.literal('FLYWORLD_PACKAGE_CATALOG'), schemaVersion: z.literal(1), dataset: z.object({ name: z.string(), version: z.string(), uuid: z.string() }),
  generatedAt: z.string(), packages: z.array(z.object({
    id: z.string(), name: z.string(), file: z.string().regex(/^malecns-[a-z0-9-]+\.json$/),
    scientificLabel: z.enum(SCIENTIFIC_LABELS), nodes: z.number().int().nonnegative().max(BROWSER_LIMITS.maxNodes),
    edges: z.number().int().nonnegative().max(BROWSER_LIMITS.maxEdges), bytes: z.number().int().positive().max(BROWSER_LIMITS.maxPackageBytes),
    sha256: z.string().regex(/^[a-f0-9]{64}$/),
  }).strict()).max(50),
}).strict();
export type CatalogEntry = z.infer<typeof catalogSchema>['packages'][number];
