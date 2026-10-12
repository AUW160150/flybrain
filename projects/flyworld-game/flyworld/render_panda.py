"""panda3d renderer: arena, flies, chase camera behind the big fly, brain panel HUD, key bindings."""
import math
import os
import sys
import time
from panda3d.core import (loadPrcFileData, CardMaker, NodePath, AmbientLight, DirectionalLight, Vec3, Vec4,
                          TextNode, Filename, LineSegs, WindowProperties, Fog, TextureStage)
from .garden import (FLOWER_COLORS, SKY, GRASS, FENCE, TRUNK, LEAF, ROCK, flower_field, grass_texture)

loadPrcFileData("", "window-title flyworld\nwin-size 1280 800\nsync-video 1\ntextures-power-2 none")
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import Texture, TextNode as _TN
import numpy as np
from .game import hud_status
from .world import behaviour_word
from .profiles import FOOD_COLOR, FOCUS_COLOR, EYE_WHITE, EYE_PUPIL, LED_GROUPS, LED_LABELS, RASTER_GROUPS
from .activity import led_levels, raster_image, BG

HELP = "arrows: drive big fly | Tab: focus fly | [ ]: group | S: stim | X: silence | +/-: amp | W: whole-CNS | R: restart | H: help | Esc: quit"
GOAL = "Shepherd: herd the six flies onto the fruit (grapes, watermelon, cherries, kiwi).\nThey flee when you loom at them, and stop to eat when they smell it.\nOr drive their brains from the panel. Clear all food before time runs out."


class Panda3DRenderer:
    def __init__(self, game):
        self.game = game
        self.base = ShowBase()
        base = self.base
        base.disableMouse()
        base.setBackgroundColor(*SKY)
        self._lights()
        self._arena()
        self.nodes = {}
        self.wings = {}
        for fly in game.world.flies:
            self.nodes[fly.id] = self._fly_model(fly)
        self.food_nodes = {fd.id: self._food_model(fd) for fd in game.world.foods}
        self.marker = self._marker()
        self.keys = {"up": False, "down": False, "left": False, "right": False}
        self._bind_keys()
        font = base.loader.loadFont("cmtt12")
        self.panel_text = OnscreenText(text="", pos=(-1.58, 0.86), scale=0.042, align=TextNode.ALeft, fg=(0.9, 0.95, 1, 1),
                                       shadow=(0, 0, 0, 1), font=font, mayChange=True)
        self.hud_text = OnscreenText(text="", pos=(-1.58, -0.95), scale=0.045, align=TextNode.ALeft, fg=(1, 0.9, 0.5, 1),
                                     shadow=(0, 0, 0, 1), font=font, mayChange=True)
        self.help_text = OnscreenText(text=HELP, pos=(0, 0.95), scale=0.04, fg=(0.8, 0.8, 0.8, 1), shadow=(0, 0, 0, 1), font=font, mayChange=True)
        self.goal_text = OnscreenText(text=GOAL if game.mode == "shepherd" else "", pos=(0, -0.68), scale=0.036, fg=(0.85, 0.9, 0.8, 1), shadow=(0, 0, 0, 1), font=font, mayChange=True)
        self.round_text = OnscreenText(text="", pos=(0, -0.9), scale=0.05, fg=(1, 0.95, 0.6, 1), shadow=(0, 0, 0, 1), font=font, mayChange=True)
        self.banner = OnscreenText(text="", pos=(0, 0.3), scale=0.14, fg=(1, 1, 0.7, 1), shadow=(0, 0, 0, 1), font=font, mayChange=True)
        self.show_help = True
        self._build_activity_panel(font)
        self.frames = 0
        self.t_start = None
        self.acc = game.dt

    # ----- scene -----
    def _lights(self):
        base = self.base
        amb = AmbientLight("amb"); amb.setColor(Vec4(0.45, 0.45, 0.5, 1))
        sun = DirectionalLight("sun"); sun.setColor(Vec4(0.9, 0.85, 0.75, 1))
        sun_np = base.render.attachNewNode(sun); sun_np.setHpr(-30, -60, 0)
        base.render.setLight(base.render.attachNewNode(amb)); base.render.setLight(sun_np)

    def _arena(self):
        base = self.base
        half = self.game.wp.arena_half
        # sky: fog haze, sun and clouds
        fog = Fog("haze"); fog.setColor(*SKY); fog.setExpDensity(0.008); base.render.setFog(fog)
        sun = base.loader.loadModel("models/misc/sphere"); sun.reparentTo(base.render); sun.setScale(6)
        sun.setPos(60, 90, 70); sun.setColor(1.0, 0.95, 0.6, 1); sun.setLightOff(); sun.setFogOff()
        rng = np.random.default_rng(11)
        for _ in range(14):
            cx, cy = rng.uniform(-90, 90), rng.uniform(-90, 90)
            for k in range(4):
                c = base.loader.loadModel("models/misc/sphere"); c.reparentTo(base.render)
                c.setScale(rng.uniform(3, 6), rng.uniform(2, 4), rng.uniform(1.2, 2.2))
                c.setPos(cx + k * 3.5, cy + rng.uniform(-2, 2), rng.uniform(28, 36)); c.setColor(1, 1, 1, 1); c.setLightOff(); c.setFogOff()
        # lawn: mottled grass texture, extends beyond the fence
        tex = Texture("grass"); tile = grass_texture(128)
        tex.setup2dTexture(128, 128, Texture.T_unsigned_byte, Texture.F_rgb); tex.setRamImageAs(tile.tobytes(), "RGB")
        tex.setWrapU(Texture.WM_repeat); tex.setWrapV(Texture.WM_repeat)
        cm = CardMaker("ground"); cm.setFrame(-half * 4, half * 4, -half * 4, half * 4)
        ground = base.render.attachNewNode(cm.generate()); ground.setP(-90); ground.setTexture(tex); ground.setTexScale(TextureStage.getDefault(), 40, 40)
        # picket fence around the arena
        for i in range(-int(half), int(half) + 1):
            for (x, y) in ((i, -half), (i, half), (-half, i), (half, i)):
                post = base.loader.loadModel("models/box"); post.reparentTo(base.render); post.setTextureOff(1)
                post.setScale(0.12, 0.12, 0.7); post.setPos(x - 0.06, y - 0.06, 0); post.setColor(*FENCE, 1)
        rail = LineSegs(); rail.setColor(*FENCE, 1); rail.setThickness(3)
        for z in (0.3, 0.55):
            rail.moveTo(-half, -half, z)
            for (x, y) in ((half, -half), (half, half), (-half, half), (-half, -half)):
                rail.drawTo(x, y, z)
        base.render.attachNewNode(rail.create())
        # flowers
        clear = [(o.pos, o.radius) for o in self.game.world.obstacles] + [(fd.pos, fd.radius) for fd in self.game.world.foods]
        for p, ci, sz in flower_field(half, keep_clear=clear):
            stem = base.loader.loadModel("models/box"); stem.reparentTo(base.render); stem.setTextureOff(1)
            stem.setScale(0.04, 0.04, 0.35 * sz); stem.setPos(p[0], p[1], 0); stem.setColor(*LEAF, 1)
            petal = base.loader.loadModel("models/misc/sphere"); petal.reparentTo(base.render)
            petal.setScale(0.16 * sz, 0.16 * sz, 0.07 * sz); petal.setPos(p[0] + 0.02, p[1] + 0.02, 0.36 * sz); petal.setColor(*FLOWER_COLORS[ci], 1)
        # trees, bushes, rocks (collision radius unchanged)
        for o in self.game.world.obstacles:
            r = o.radius
            if o.kind == "tree":
                trunk = base.loader.loadModel("models/box"); trunk.reparentTo(base.render); trunk.setTextureOff(1)
                trunk.setScale(r * 0.4, r * 0.4, 2.4); trunk.setPos(o.pos[0] - r * 0.2, o.pos[1] - r * 0.2, 0); trunk.setColor(*TRUNK, 1)
                for (dx, dy, dz, sc) in ((0, 0, 3.0, 1.3), (-0.6, 0.3, 2.6, 0.9), (0.6, -0.2, 2.7, 0.9), (0.1, 0.6, 3.4, 0.8)):
                    crown = base.loader.loadModel("models/misc/sphere"); crown.reparentTo(base.render)
                    crown.setScale(r * sc); crown.setPos(o.pos[0] + dx * r, o.pos[1] + dy * r, dz); crown.setColor(*LEAF, 1)
            elif o.kind == "bush":
                for (dx, dy, sc) in ((0, 0, 1.0), (-0.55, 0.25, 0.7), (0.55, 0.3, 0.7), (0.1, -0.55, 0.65), (0, 0.1, 0.8)):
                    b = base.loader.loadModel("models/misc/sphere"); b.reparentTo(base.render)
                    b.setScale(r * sc, r * sc, r * sc * 0.8); b.setPos(o.pos[0] + dx * r, o.pos[1] + dy * r, r * sc * 0.5); b.setColor(*LEAF, 1)
            else:
                rock = base.loader.loadModel("models/misc/sphere"); rock.reparentTo(base.render)
                rock.setScale(r, r * 0.8, r * 0.55); rock.setPos(o.pos[0], o.pos[1], 0.1); rock.setColor(*ROCK, 1)

    def _fly_model(self, fly):
        base = self.base
        root = base.render.attachNewNode(f"fly{fly.id}")
        col = (*fly.color, 1)
        r = fly.radius
        self.wings.setdefault(fly.id, [])
        if fly.style == "jigglypuff":
            R = r * 1.5
            body = base.loader.loadModel("models/misc/sphere"); body.reparentTo(root); body.setScale(R); body.setZ(R); body.setColor(*col)
            for side in (-1, 1):
                eye = base.loader.loadModel("models/misc/sphere"); eye.reparentTo(root); eye.setScale(R * 0.32)
                eye.setPos(R * 0.72, side * R * 0.42, R * 1.25); eye.setColor(*EYE_WHITE, 1)
                pupil = base.loader.loadModel("models/misc/sphere"); pupil.reparentTo(root); pupil.setScale(R * 0.16)
                pupil.setPos(R * 0.98, side * R * 0.42, R * 1.28); pupil.setColor(*EYE_PUPIL, 1)
                ear = base.loader.loadModel("models/misc/sphere"); ear.reparentTo(root); ear.setScale(R * 0.25, R * 0.25, R * 0.5)
                ear.setPos(-R * 0.2, side * R * 0.7, R * 1.8); ear.setColor(*col)
                wing = base.loader.loadModel("models/misc/sphere"); wing.reparentTo(root)
                wing.setScale(R * 0.5, R * 0.9, R * 0.05); wing.setPos(-R * 0.1, side * R * 1.4, R * 1.1)
                wing.setColor(0.93, 0.95, 1.0, 0.7); wing.setTransparency(True)
                self.wings[fly.id].append((wing, side))
            for k in range(3):                       # curl on the forehead
                c = base.loader.loadModel("models/misc/sphere"); c.reparentTo(root); c.setScale(R * 0.18)
                c.setPos(R * (0.55 - 0.15 * k), 0, R * (1.95 + 0.12 * k)); c.setColor(*col)
            tn = _TN(f"label{fly.id}"); tn.setText(fly.name); tn.setTextColor(*col); tn.setAlign(_TN.ACenter)
            tn.setShadow(0.05, 0.05); tn.setShadowColor(0, 0, 0, 1)
            label = root.attachNewNode(tn); label.setBillboardPointEye(); label.setScale(0.4); label.setZ(R * 2.5 + 0.3); label.setLightOff()
            return root
        body = base.loader.loadModel("models/misc/sphere"); body.reparentTo(root)
        body.setScale(r, r * 0.6, r * 0.5); body.setZ(r * 0.5); body.setColor(*col)
        abdomen = base.loader.loadModel("models/misc/sphere"); abdomen.reparentTo(root)
        if fly.sex == "female":            # longer, pointed abdomen
            abdomen.setScale(r * 1.1, r * 0.5, r * 0.4); abdomen.setPos(-r * 0.9, 0, r * 0.45); abdomen.setColor(*col)
        else:                              # shorter, rounded, dark tip
            abdomen.setScale(r * 0.7, r * 0.55, r * 0.45); abdomen.setPos(-r * 0.7, 0, r * 0.45)
            abdomen.setColor(fly.color[0] * 0.35, fly.color[1] * 0.3, fly.color[2] * 0.3, 1)
        head = base.loader.loadModel("models/misc/sphere"); head.reparentTo(root)
        head.setScale(r * 0.45); head.setPos(r * 0.95, 0, r * 0.6); head.setColor(0.85, 0.2, 0.2, 1)
        for side in (-1, 1):
            wing = base.loader.loadModel("models/misc/sphere"); wing.reparentTo(root)
            wing.setScale(r * 0.7, r * 0.3, r * 0.04)
            wing.setPos(-r * 0.2, side * r * 0.45, r * 0.95); wing.setH(side * 20)
            wing.setColor(0.85, 0.9, 1.0, 0.55); wing.setTransparency(True)
            self.wings[fly.id].append((wing, side))
        tn = _TN(f"label{fly.id}"); tn.setText(fly.name); tn.setTextColor(*col); tn.setAlign(_TN.ACenter)
        tn.setShadow(0.05, 0.05); tn.setShadowColor(0, 0, 0, 1)
        label = root.attachNewNode(tn); label.setBillboardPointEye(); label.setScale(0.55 if fly.kind == "big" else 0.4)
        label.setZ(r * 2.2 + 0.3); label.setLightOff()
        return root

    def _food_model(self, fd):
        """A fruit patch: a root node scaled by remaining amount each frame."""
        base = self.base
        root = base.render.attachNewNode(f"food{fd.id}")
        root.setPos(fd.pos[0], fd.pos[1], 0)
        r = fd.radius
        col, acc = (*fd.color, 1), (*fd.accent, 1)
        def ball(scale, pos, color):
            m = base.loader.loadModel("models/misc/sphere"); m.reparentTo(root); m.setScale(*scale); m.setPos(*pos); m.setColor(*color); return m
        if fd.kind == "grapes":
            for (dx, dy, dz) in ((0, 0, 0.3), (-0.45, 0.1, 0.3), (0.45, -0.1, 0.3), (-0.2, 0.4, 0.3), (0.2, -0.4, 0.3), (0, 0.1, 0.8), (-0.3, -0.2, 0.75), (0.3, 0.25, 0.75), (0, 0, 1.2)):
                ball((r * 0.32,) * 3, (dx * r, dy * r, dz * r), col)
            ball((0.04, 0.04, 0.35), (0, 0, r * 1.5), acc)
        elif fd.kind == "watermelon":
            ball((r, r * 0.55, r * 0.5), (0, 0, r * 0.25), col)                      # rind
            ball((r * 0.8, r * 0.4, r * 0.42), (0, 0, r * 0.35), acc)                  # flesh
        elif fd.kind == "cherries":
            for dx in (-0.4, 0.4):
                ball((r * 0.4,) * 3, (dx * r, 0, r * 0.4), col)
                stem = base.loader.loadModel("models/box"); stem.reparentTo(root); stem.setTextureOff(1)
                stem.setScale(0.03, 0.03, r * 0.8); stem.setPos(dx * r * 0.6, 0, r * 0.7); stem.setColor(*acc); stem.setR(dx * 40)
        else:                                                                         # kiwi halves
            for dx in (-0.5, 0.5):
                ball((r * 0.45, r * 0.45, r * 0.22), (dx * r, 0, r * 0.2), col)
                ball((r * 0.36, r * 0.36, r * 0.2), (dx * r, 0, r * 0.26), acc)
                ball((r * 0.12, r * 0.12, r * 0.1), (dx * r, 0, r * 0.4), (0.96, 0.96, 0.9, 1))
        tn = _TN(f"foodlabel{fd.id}"); tn.setText(fd.kind); tn.setTextColor(1, 1, 1, 1); tn.setAlign(_TN.ACenter); tn.setShadow(0.05, 0.05); tn.setShadowColor(0, 0, 0, 1)
        label = root.attachNewNode(tn); label.setBillboardPointEye(); label.setScale(0.3); label.setZ(r * 1.8 + 0.3); label.setLightOff()
        return root

    def _marker(self):
        m = self.base.loader.loadModel("models/misc/sphere"); m.reparentTo(self.base.render)
        m.setScale(0.15); m.setColor(*FOCUS_COLOR, 1)
        return m

    def _build_activity_panel(self, font):
        """Right column: one row of LEDs per NPC fly, and a raster texture for the focus fly."""
        a2d = self.base.aspect2d
        for (l, r, b, t) in ((-1.62, -0.98, -0.55, 0.9), (0.58, 1.62, -0.5, 0.9), (-1.62, 1.62, -1.0, -0.6)):
            cm = CardMaker("backdrop"); cm.setFrame(l, r, b, t)
            bd = a2d.attachNewNode(cm.generate()); bd.setColor(0.02, 0.03, 0.05, 0.62); bd.setTransparency(True); bd.setBin("background", 0)
        self.led_nodes = {}
        x0, y0 = 0.62, 0.82
        self.led_w = (1.56 - x0 - 0.22) / len(LED_GROUPS)
        OnscreenText(text="neurons firing now", pos=(x0, y0 + 0.02), scale=0.036, align=TextNode.ALeft, fg=(0.9, 0.95, 1, 1), shadow=(0, 0, 0, 1), font=font)
        for i, lab in enumerate(LED_LABELS):
            OnscreenText(text=lab[:5], pos=(x0 + 0.22 + i * self.led_w + self.led_w / 2, y0 + 0.02), scale=0.024, fg=(0.75, 0.8, 0.9, 1), font=font, roll=-90, align=TextNode.ALeft)
        self.led_names = {}
        for row, fly in enumerate(self.game.world.npcs):
            y = y0 - 0.05 - row * 0.075
            self.led_names[fly.id] = OnscreenText(text=fly.name, pos=(x0, y - 0.01), scale=0.036, align=TextNode.ALeft, fg=(*fly.color, 1), shadow=(0, 0, 0, 1), font=font, mayChange=True)
            for i in range(len(LED_GROUPS)):
                cm = CardMaker(f"led{fly.id}_{i}")
                cm.setFrame(x0 + 0.22 + i * self.led_w, x0 + 0.22 + (i + 1) * self.led_w - 0.006, y - 0.04, y + 0.012)
                n = a2d.attachNewNode(cm.generate()); n.setColor(BG[0] / 255, BG[1] / 255, BG[2] / 255, 1)
                self.led_nodes[(fly.id, i)] = n
        # raster
        self.raster_rows = [g for g in RASTER_GROUPS if g in self.game.brain.out_index]
        self.raster_tex = Texture("raster")
        self.raster_tex.setup2dTexture(200, len(self.raster_rows), Texture.T_unsigned_byte, Texture.F_rgb)
        self.raster_tex.setMagfilter(Texture.FT_nearest); self.raster_tex.setMinfilter(Texture.FT_nearest)
        ry1 = y0 - 0.05 - len(self.game.world.npcs) * 0.075 - 0.05
        self.rrow = 0.03
        rh = self.rrow * len(self.raster_rows)
        cm = CardMaker("raster"); cm.setFrame(x0 + 0.22, 1.56, ry1 - rh, ry1)
        card = a2d.attachNewNode(cm.generate()); card.setTexture(self.raster_tex)
        self.raster_title = OnscreenText(text="", pos=(x0, ry1 + 0.015), scale=0.036, align=TextNode.ALeft, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1), font=font, mayChange=True)
        for i, name in enumerate(self.raster_rows):
            OnscreenText(text=name[:8], pos=(x0, ry1 - (i + 0.75) * self.rrow), scale=0.024, align=TextNode.ALeft, fg=(0.75, 0.8, 0.9, 1), font=font)

    def _update_activity_panel(self, focus):
        g = self.game
        for fly in g.world.npcs:
            col = fly.color
            self.led_names[fly.id].setText(f"{fly.name} {behaviour_word(fly)}")
            for i, lvl in enumerate(led_levels(g.last_rates.get(fly.id, {}))):
                self.led_nodes[(fly.id, i)].setColor(BG[0] / 255 + (col[0] - BG[0] / 255) * lvl, BG[1] / 255 + (col[1] - BG[1] / 255) * lvl, BG[2] / 255 + (col[2] - BG[2] / 255) * lvl, 1)
        if focus.kind == "npc" and g.last_ring is not None:
            brain, b, ring, ptr = g.brain_for(focus.id)
            img, rows = raster_image(brain, b, ring, ptr, focus.color, self.raster_rows)
            self.raster_tex.setRamImageAs(np.ascontiguousarray(img[::-1]).tobytes(), "RGB")
            self.raster_title.setText(f"{focus.name}: spikes, last 200 ms"); self.raster_title.setFg((*focus.color, 1))

    # ----- input -----
    def _bind_keys(self):
        b, g = self.base, self.game
        for k in self.keys:
            b.accept(f"arrow_{k}", self.keys.__setitem__, [k, True]); b.accept(f"arrow_{k}-up", self.keys.__setitem__, [k, False])
        b.accept("tab", lambda: g.panel.cycle_focus(1))
        b.accept("shift-tab", lambda: g.panel.cycle_focus(-1))
        b.accept("[", lambda: g.panel.move_cursor(-1)); b.accept("]", lambda: g.panel.move_cursor(1))
        b.accept("s", g.panel.toggle_stim); b.accept("x", g.panel.toggle_silence)
        b.accept("=", lambda: g.panel.adjust_amp(0.05)); b.accept("+", lambda: g.panel.adjust_amp(0.05)); b.accept("-", lambda: g.panel.adjust_amp(-0.05))
        b.accept("w", g.toggle_whole)
        b.accept("h", self._toggle_help)
        b.accept("r", g.restart)
        b.accept("escape", self._quit)

    def _toggle_help(self):
        self.show_help = not self.show_help
        self.help_text.setText(HELP if self.show_help else "")

    def _quit(self):
        self.base.taskMgr.stop()

    # ----- per frame -----
    def _frame(self, task):
        g = self.game
        if self.t_start is None:
            self.t_start = time.perf_counter()
        dt = g.dt
        v = g.wp.big_speed * ((1 if self.keys["up"] else 0) - (1 if self.keys["down"] else 0))
        om = math.radians(g.wp.big_turn_deg) * ((1 if self.keys["left"] else 0) - (1 if self.keys["right"] else 0))
        g.big_cmd = (v, om)
        self.acc += min(self.base.clock.getDt(), 0.1)
        n = 0
        while self.acc >= dt and n < 2:          # fixed 30 Hz game ticks, at most two per rendered frame
            g.tick(dt); self.acc -= dt; n += 1
        if n == 2:
            self.acc = 0.0
        for fly in g.world.flies:
            n = self.nodes[fly.id]
            n.setPos(fly.pos[0], fly.pos[1], 0.25 if fly.jumping else 0.0)
            n.setH(math.degrees(fly.heading))
            n.setP(15 if fly.groom else 0)
            rate = 22.0 if (abs(fly.speed) > 0.3 or fly.jumping) else 3.0
            for wing, side in self.wings.get(fly.id, []):
                wing.setR(side * (25 + 30 * math.sin(task.time * rate)))
        if set(self.nodes) != {f.id for f in g.world.flies} or any(fd.id not in self.food_nodes for fd in g.world.foods):
            pass   # ids are stable across restart (same layout ids), positions are re-read every frame
        for fd in g.world.foods:
            node = self.food_nodes[fd.id]
            node.setPos(fd.pos[0], fd.pos[1], 0)
            k = 0.3 + 0.7 * max(fd.amount, 0.0) / 5.0
            node.setScale(k if fd.amount > 0 else 0.001)
        focus = g.world.flies[g.panel.focus]
        self.marker.setPos(focus.pos[0], focus.pos[1], 0.9 + 0.1 * math.sin(4 * task.time))
        big = g.world.big
        cam = Vec3(big.pos[0] - 13 * math.cos(big.heading), big.pos[1] - 13 * math.sin(big.heading), 7.5)
        self.base.camera.setPos(cam); self.base.camera.lookAt(Vec3(big.pos[0] + 5 * math.cos(big.heading), big.pos[1] + 5 * math.sin(big.heading), 0.8))
        rates = g.last_rates.get(focus.id, {})
        sizes = {k: len(v) for k, v in g.brain.groups.items()}
        self.panel_text.setText("\n".join(g.panel.lines(rates, sizes, focus.name)[:34]))
        self._update_activity_panel(focus)
        st = "whole-CNS" if g.focus_whole else "sub-circuit"
        bio = g.wp.bio_ms_per_tick_focus if g.focus_whole else g.wp.bio_ms_per_tick
        tm = g.tick_ms[-1] if g.tick_ms else 0.0
        self.hud_text.setText(f"{focus.name} brain: {st}   bio x{bio/1000/dt:.2f}   tick {tm:.0f} ms   fps {self.base.clock.getAverageFrameRate():.0f}   "
                              f"speed {focus.speed:.1f}  {behaviour_word(focus)}  "
                              f"eaten {focus.eaten:.1f} hits {focus.hits}")
        self.round_text.setText(hud_status(g))
        st_round = g.round["state"]
        self.banner.setText("YOU WIN" if st_round == "won" else "TIME UP" if st_round == "lost" else "")
        self.frames += 1
        if self.max_frames and self.frames >= self.max_frames:
            self._finish()
            return task.done
        return task.cont

    def _finish(self):
        elapsed = time.perf_counter() - self.t_start
        fps = self.frames / max(elapsed, 1e-9)
        ok = fps >= self.min_fps
        if self.screenshot:
            self.base.graphicsEngine.renderFrame()
            self.base.win.saveScreenshot(Filename.fromOsSpecific(os.path.abspath(self.screenshot)))
            size = os.path.getsize(self.screenshot) if os.path.exists(self.screenshot) else 0
            ok = ok and size > 10_000
            print(f"screenshot {self.screenshot} {size} bytes")
        print(f"RENDER fps={fps:.1f} frames={self.frames} ticks={len(self.game.tick_ms)} mean_tick_ms={sum(self.game.tick_ms)/max(len(self.game.tick_ms),1):.1f}")
        self.result = 0 if ok else 1
        print("RENDER OK" if ok else "RENDER FAIL")
        self.base.taskMgr.stop()

    def run(self, frames=None, screenshot=None, min_fps=0.0):
        self.max_frames, self.screenshot, self.min_fps, self.result = frames, screenshot, min_fps, 0
        self.base.taskMgr.add(self._frame, "flyworld-frame")
        self.base.run()
        return self.result
