"""Top-down pygame renderer: arena, named flies, per-fly activity LEDs and the focus fly's spike raster."""
import math
import os
import time
import numpy as np
import pygame

from .render_panda import HELP, GOAL
from .game import hud_status
from .world import behaviour_word
from .profiles import FLY_PROFILES, FOOD_COLOR, FOCUS_COLOR, EYE_WHITE, EYE_PUPIL, LED_GROUPS, LED_LABELS, rgb255
from .activity import led_levels, raster_image, BG
from .garden import FLOWER_COLORS, GRASS, GRASS_DARK, FENCE, TRUNK, LEAF, ROCK, flower_field, grass_texture

LEFT_W, RIGHT_W = 330, 300


class PygameRenderer:
    def __init__(self, game, size=(1280, 800)):
        self.game = game
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("flyworld (top-down)")
        self.font = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 12)
        self.font_b = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 13, bold=True)
        self.w, self.h = size
        side = min(self.h - 60, self.w - LEFT_W - RIGHT_W - 20)
        self.scale = side / (2 * game.wp.arena_half)
        self.cx, self.cy = LEFT_W + side // 2 + 10, 30 + side // 2
        self.arena_right = LEFT_W + side + 20
        self.keys = set()
        self.acc = game.dt
        self.clock = pygame.time.Clock()
        self.lawn = self._make_lawn(side)
        clear = [(o.pos, o.radius) for o in game.world.obstacles] + [(fd.pos, fd.radius) for fd in game.world.foods]
        self.flowers = flower_field(game.wp.arena_half, keep_clear=clear)

    def _make_lawn(self, side):
        tile = grass_texture(128)
        surf = pygame.surfarray.make_surface(np.transpose(tile, (1, 0, 2)))
        lawn = pygame.Surface((side, side))
        for x in range(0, side, 128):
            for y in range(0, side, 128):
                lawn.blit(surf, (x, y))
        return lawn

    def _draw_garden(self):
        g, s = self.game, self.screen
        half = g.wp.arena_half
        x0, y0 = self.to_px(-half, half)
        s.blit(self.lawn, (x0, y0))
        for p, ci, sz in self.flowers:
            px, py = self.to_px(*p)
            pygame.draw.circle(s, rgb255(FLOWER_COLORS[ci]), (px, py), max(2, int(2.5 * sz)))
            pygame.draw.circle(s, (255, 230, 120), (px, py), 1)
        x1, y1 = self.to_px(half, -half)
        pygame.draw.rect(s, rgb255(FENCE), (x0, y0, x1 - x0, y1 - y0), 3)
        for o in g.world.obstacles:
            px, py = self.to_px(*o.pos); r = int(o.radius * self.scale)
            if o.kind == "tree":
                pygame.draw.circle(s, rgb255(TRUNK), (px, py), max(2, r // 3))
                pygame.draw.circle(s, rgb255(LEAF), (px, py), r)
                pygame.draw.circle(s, (60, 130, 50), (px - r // 3, py - r // 3), r // 2)
            elif o.kind == "bush":
                for dx, dy, rr in ((0, 0, 1.0), (-0.5, 0.2, 0.7), (0.5, 0.3, 0.7), (0.1, -0.5, 0.65)):
                    pygame.draw.circle(s, rgb255(LEAF), (px + int(dx * r), py + int(dy * r)), int(r * rr))
            else:
                pygame.draw.ellipse(s, rgb255(ROCK), (px - r, py - int(r * 0.75), 2 * r, int(r * 1.5)))
                pygame.draw.ellipse(s, (120, 120, 118), (px - r, py - int(r * 0.75), 2 * r, int(r * 1.5)), 2)
        for fd in g.world.foods:
            if fd.amount <= 0:
                continue
            px, py = self.to_px(*fd.pos)
            r = max(4, int(fd.radius * self.scale * (0.45 + 0.55 * fd.amount / 5)))
            col, acc = rgb255(fd.color), rgb255(fd.accent)
            if fd.kind == "grapes":
                for dx, dy in ((0, 0), (-0.5, -0.4), (0.5, -0.4), (-0.25, 0.45), (0.25, 0.45), (0, -0.85)):
                    pygame.draw.circle(s, col, (px + int(dx * r), py + int(dy * r)), max(2, r // 2))
                pygame.draw.line(s, acc, (px, py - r), (px + r // 3, py - int(r * 1.5)), 2)
            elif fd.kind == "watermelon":
                pygame.draw.circle(s, col, (px, py), r)
                pygame.draw.circle(s, acc, (px, py), max(2, int(r * 0.7)))
                for k in range(4):
                    pygame.draw.circle(s, (30, 20, 20), (px + int(math.cos(k * 1.6) * r * 0.35), py + int(math.sin(k * 1.6) * r * 0.35)), 1)
            elif fd.kind == "cherries":
                for dx in (-0.45, 0.45):
                    pygame.draw.circle(s, col, (px + int(dx * r), py + r // 4), max(2, int(r * 0.55)))
                    pygame.draw.line(s, acc, (px + int(dx * r), py), (px, py - r), 2)
            else:                                   # kiwi slice
                pygame.draw.circle(s, col, (px, py), r)
                pygame.draw.circle(s, acc, (px, py), max(2, int(r * 0.8)))
                pygame.draw.circle(s, (245, 245, 225), (px, py), max(1, r // 4))
            lab = self.font.render(fd.kind, True, (235, 240, 235))
            s.blit(lab, (px - lab.get_width() // 2, py + r + 2))

    def to_px(self, x, y):
        return int(self.cx + x * self.scale), int(self.cy - y * self.scale)

    # ----- drawing -----
    def _draw_fly(self, f, focus):
        s = self.screen
        px, py = self.to_px(*f.pos)
        r = max(3, int(f.radius * self.scale))
        col = rgb255(f.color)
        if f.jumping:
            pygame.draw.circle(s, (255, 255, 255), (px, py), r + 3, 2)
        c, sn = math.cos(f.heading), math.sin(f.heading)
        if f.style == "jigglypuff":         # round body, ears, big eyes, wings
            R = int(r * 1.5)
            flap = 0.6 + 0.4 * abs(math.sin(time.perf_counter() * (18 if abs(f.speed) > 0.3 or f.jumping else 3)))
            for side in (-1, 1):
                wx, wy = px + int(-sn * side * R * 1.3), py + int(-c * side * R * 1.3)
                pygame.draw.ellipse(s, (235, 240, 255), (wx - int(R * 0.9 * flap), wy - R // 2, int(R * 1.8 * flap), R))
            for side in (-1, 1):            # ears
                ex, ey = px + int(-sn * side * R * 0.8 - c * R * 0.3), py + int(-c * side * R * 0.8 + sn * R * 0.3)
                pygame.draw.polygon(s, col, [(ex - R // 3, ey), (ex + R // 3, ey), (ex - int(sn * side * R * 0.7), ey - int(c * side * R * 0.7))])
            pygame.draw.circle(s, col, (px, py), R)
            for side in (-1, 1):            # eyes
                ex, ey = px + int(c * R * 0.45 - sn * side * R * 0.45), py - int(sn * R * 0.45 + c * side * R * 0.45)
                pygame.draw.circle(s, rgb255(EYE_WHITE), (ex, ey), max(3, R // 3))
                pygame.draw.circle(s, rgb255(EYE_PUPIL), (ex + int(c * 2), ey - int(sn * 2)), max(2, R // 6))
            pygame.draw.circle(s, (200, 60, 120), (px + int(c * R * 0.85), py - int(sn * R * 0.85)), max(1, R // 8))   # mouth
            pygame.draw.arc(s, (230, 100, 160), (px - R // 2, py - R - R // 4, R, R // 2), 0, math.pi, 2)   # curl
            if f is focus:
                pygame.draw.circle(s, rgb255(FOCUS_COLOR), (px, py), R + 6, 2)
            lab = self.font.render(f.name, True, col)
            s.blit(lab, (px - lab.get_width() // 2, py + R + 4))
            return
        if f.sex == "female":               # longer body with a pointed abdomen
            tail = (px - int(c * r * 1.6), py + int(sn * r * 1.6))
            pygame.draw.polygon(s, col, [(px + int(-sn * r * 0.8), py + int(-c * r * 0.8)), (px + int(sn * r * 0.8), py + int(c * r * 0.8)), tail])
            pygame.draw.circle(s, col, (px, py), r)
        else:                               # rounder body with a dark tip
            pygame.draw.circle(s, col, (px, py), r)
            pygame.draw.circle(s, (40, 30, 30), (px - int(c * r * 0.8), py + int(sn * r * 0.8)), max(2, r // 2))
        pygame.draw.circle(s, (230, 60, 60), (px + int(c * r * 1.1), py - int(sn * r * 1.1)), max(2, r // 2))   # head
        pygame.draw.line(s, (255, 240, 220), (px, py), (px + int(c * r * 1.8), py - int(sn * r * 1.8)), 2)
        if f is focus:
            pygame.draw.circle(s, rgb255(FOCUS_COLOR), (px, py), r + 6, 2)
        lab = self.font.render(f.name, True, col)
        s.blit(lab, (px - lab.get_width() // 2, py + r + 4))

    def _draw(self):
        g, s = self.game, self.screen
        s.fill((20, 24, 30))
        self._draw_garden()
        focus = g.world.flies[g.panel.focus]
        for f in g.world.flies:
            self._draw_fly(f, focus)
        # left column: brain panel of the focus fly
        rates = g.last_rates.get(focus.id, {})
        sizes = {k: len(v) for k, v in g.brain.groups.items()}
        y = 6
        for line in g.panel.lines(rates, sizes, focus.name)[:34]:
            s.blit(self.font.render(line, True, (230, 240, 255)), (6, y)); y += 15
        y += 8
        if g.mode == "shepherd":
            for line in GOAL.split("\n"):
                s.blit(self.font.render(line, True, (200, 220, 190)), (6, y)); y += 15
        s.blit(self.font_b.render(hud_status(g), True, (255, 245, 160)), (6, y + 6))
        # right column: activity LEDs per fly
        rx, ry = self.arena_right + 6, 30
        s.blit(self.font_b.render("neurons firing now", True, (230, 240, 255)), (rx, ry - 22))
        lw = (RIGHT_W - 76) // len(LED_GROUPS)
        for i, lab in enumerate(LED_LABELS):
            t = self.font.render(lab[:4], True, (150, 160, 175))
            t = pygame.transform.rotate(t, 90)
            s.blit(t, (rx + 70 + i * lw, ry))
        ry += 38
        for f in g.world.npcs:
            col = rgb255(f.color)
            s.blit(self.font_b.render(f.name, True, col), (rx, ry))
            s.blit(self.font.render(behaviour_word(f), True, (200, 205, 215)), (rx, ry + 14))
            for i, lvl in enumerate(led_levels(g.last_rates.get(f.id, {}))):
                c = tuple(int(BG[k] + (col[k] - BG[k]) * lvl) for k in range(3))
                pygame.draw.rect(s, c, (rx + 70 + i * lw, ry + 2, lw - 2, 24))
            ry += 34
        # raster of the focus fly
        if focus.kind == "npc" and g.last_ring is not None:
            brain, b, ring, ptr = g.brain_for(focus.id)
            img, rows = raster_image(brain, b, ring, ptr, focus.color)
            surf = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
            rh = 12
            surf = pygame.transform.scale(surf, (RIGHT_W - 62, rh * len(rows)))
            s.blit(self.font_b.render(f"{focus.name}: last 200 ms", True, rgb255(focus.color)), (rx, ry + 4))
            ry += 22
            s.blit(surf, (rx + 56, ry))
            for i, name in enumerate(rows):
                s.blit(self.font.render(name[:7], True, (150, 160, 175)), (rx, ry + i * rh - 1))
        s.blit(self.font.render(HELP, True, (170, 180, 190)), (6, self.h - 38))
        hud = f"{focus.name} brain: {'whole-CNS' if g.focus_whole else 'sub-circuit'}  tick {g.tick_ms[-1] if g.tick_ms else 0:.0f} ms  speed {focus.speed:.1f}  {behaviour_word(focus)}  eaten {focus.eaten:.1f} hits {focus.hits}"
        s.blit(self.font.render(hud, True, (255, 230, 128)), (6, self.h - 20))
        if g.round["state"] != "playing":
            big = pygame.font.SysFont("menlo,monaco,couriernew,monospace", 64, bold=True)
            msg = "YOU WIN" if g.round["state"] == "won" else "TIME UP"
            t = big.render(msg, True, (255, 255, 180)); s.blit(t, (self.cx - t.get_width() // 2, self.cy - 40))
        pygame.display.flip()

    # ----- input and loop -----
    def _handle(self, ev):
        g = self.game
        if ev.type == pygame.QUIT:
            return False
        if ev.type == pygame.KEYDOWN:
            k = ev.key
            if k == pygame.K_ESCAPE: return False
            if k == pygame.K_TAB: g.panel.cycle_focus(-1 if ev.mod & pygame.KMOD_SHIFT else 1)
            elif k == pygame.K_LEFTBRACKET: g.panel.move_cursor(-1)
            elif k == pygame.K_RIGHTBRACKET: g.panel.move_cursor(1)
            elif k == pygame.K_s: g.panel.toggle_stim()
            elif k == pygame.K_x: g.panel.toggle_silence()
            elif k in (pygame.K_EQUALS, pygame.K_PLUS, pygame.K_KP_PLUS): g.panel.adjust_amp(0.05)
            elif k in (pygame.K_MINUS, pygame.K_KP_MINUS): g.panel.adjust_amp(-0.05)
            elif k == pygame.K_w: g.toggle_whole()
            elif k == pygame.K_r: g.restart()
            self.keys.add(k)
        if ev.type == pygame.KEYUP:
            self.keys.discard(ev.key)
        return True

    def step_frames(self, n):
        """Advance n rendered frames (fixed 30 Hz game ticks inside). Returns False if the user quit."""
        g = self.game
        for _ in range(n):
            for ev in pygame.event.get():
                if not self._handle(ev):
                    return False
            v = g.wp.big_speed * ((pygame.K_UP in self.keys) - (pygame.K_DOWN in self.keys))
            om = math.radians(g.wp.big_turn_deg) * ((pygame.K_LEFT in self.keys) - (pygame.K_RIGHT in self.keys))
            g.big_cmd = (v, om)
            self.acc += self.clock.tick(60) / 1000.0
            k = 0
            while self.acc >= g.dt and k < 2:
                g.tick(g.dt); self.acc -= g.dt; k += 1
            if k == 2:
                self.acc = 0.0
            self._draw()
        return True

    def frame_array(self):
        return np.transpose(pygame.surfarray.array3d(self.screen), (1, 0, 2)).copy()

    def save(self, path):
        pygame.image.save(self.screen, path)

    def close(self):
        pygame.quit()

    def run(self, frames=None, screenshot=None, min_fps=0.0):
        n = 0
        t0 = time.perf_counter()
        while frames is None or n < frames:
            if not self.step_frames(1):
                break
            n += 1
        fps = n / max(time.perf_counter() - t0, 1e-9)
        ok = fps >= min_fps
        if screenshot:
            self.save(screenshot)
            size = os.path.getsize(screenshot)
            ok = ok and size > 10_000
            print(f"screenshot {screenshot} {size} bytes")
        print(f"RENDER fps={fps:.1f} frames={n}")
        print("RENDER OK" if ok else "RENDER FAIL")
        self.close()
        return 0 if ok else 1
