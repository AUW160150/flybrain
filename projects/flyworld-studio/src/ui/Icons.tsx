export function FlyMark({ size = 28 }: { size?: number }) {
  return <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
    <path d="M14 16C5 3 1 11 6 18c3 3 7 2 8-2Zm4 0C27 3 31 11 26 18c-3 3-7 2-8-2Z" stroke="currentColor" strokeWidth="1.3" />
    <ellipse cx="16" cy="20" rx="3" ry="8" fill="currentColor" /><circle cx="16" cy="9" r="3.4" fill="currentColor" />
    <path d="m11 20-6 5m16-5 6 5M13 7l-3-4m9 4 3-4" stroke="currentColor" strokeWidth="1.2" />
  </svg>;
}
export function Crosshair() {
  return <svg width="19" height="19" viewBox="0 0 20 20" fill="none" aria-hidden="true"><circle cx="10" cy="10" r="5.5" stroke="currentColor" /><path d="M10 1v5m0 8v5M1 10h5m8 0h5" stroke="currentColor" /></svg>;
}
