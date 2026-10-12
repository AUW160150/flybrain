import { create } from 'zustand';

export const usePerformance = create<{
  fps: number | null; visibleMeshes: number; drawCalls: number; activeHighlights: number;
}>(() => ({ fps: null, visibleMeshes: 0, drawCalls: 0, activeHighlights: 0 }));
