import { expect, type Page } from '@playwright/test';

/** Use a genuine unobstructed canvas click in every camera/layout, never force. */
export async function activateViewport(page: Page) {
  const viewport = page.locator('[data-world-viewport]');
  await viewport.scrollIntoViewIfNeeded();
  const position = await viewport.evaluate(element => {
    const rect = element.getBoundingClientRect();
    for (const [u, v] of [[0.08, 0.68], [0.12, 0.8], [0.45, 0.65], [0.5, 0.5], [0.9, 0.85]]) {
      const x = rect.width * u, y = rect.height * v;
      const hit = document.elementFromPoint(rect.left + x, rect.top + y);
      if (hit && element.contains(hit) && !hit.closest('button,input,a,[role="button"]')) return { x, y };
    }
    throw new Error('No unobstructed viewport point: inspect the overlay/layout before clicking.');
  });
  await viewport.click({ position, timeout: 5000 });
  await expect(viewport).toBeFocused();
}
