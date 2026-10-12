"""Brain panel state: which fly is in focus, which group the cursor is on, what is stimulated or silenced."""
from .groups import panel_order


class PanelState:
    def __init__(self, n_npc, amp=0.15, groups=None):
        self.n_npc = n_npc
        self.focus = 1                        # fly id; NPCs are 1..n_npc (the big fly has no brain in v1)
        self.names = [n for n in panel_order() if groups is None or (n in groups and len(groups[n]) > 0)]
        self.cursor = 0
        self.amp = amp
        self.stim = set()                     # {(fly_id, group)}
        self.clamp = set()
        self.messages = []

    # ----- navigation -----
    def cycle_focus(self, step=1):
        self.focus = ((self.focus - 1 + step) % self.n_npc) + 1

    def move_cursor(self, step):
        self.cursor = (self.cursor + step) % len(self.names)

    @property
    def current(self):
        return self.names[self.cursor]

    def toggle_stim(self, group=None, fly=None):
        key = (fly or self.focus, group or self.current)
        if key in self.stim:
            self.stim.remove(key)
        else:
            self.stim.add(key)
            self.clamp.discard(key)

    def toggle_silence(self, group=None, fly=None):
        key = (fly or self.focus, group or self.current)
        if key in self.clamp:
            self.clamp.remove(key)
        else:
            self.clamp.add(key)
            self.stim.discard(key)

    def adjust_amp(self, d):
        self.amp = float(min(0.5, max(0.0, self.amp + d)))

    # ----- application -----
    def stim_for(self, fly_id):
        return {g: self.amp for (f, g) in self.stim if f == fly_id}

    def clamp_for(self, fly_id):
        return [g for (f, g) in self.clamp if f == fly_id]

    def lines(self, rates=None, sizes=None, focus_name=None):
        """Text lines for the on-screen panel."""
        who = focus_name or f"fly {self.focus}"
        out = [f"brain of {who}   amp {self.amp:.2f}   [Tab] fly  [ ] cursor  S stim  X silence  +/- amp  W whole-CNS"]
        for i, n in enumerate(self.names):
            mark = ">" if i == self.cursor else " "
            st = "STIM" if (self.focus, n) in self.stim else "    "
            cl = "SILENT" if (self.focus, n) in self.clamp else "      "
            r = f"{rates[n]:6.1f} Hz" if rates and n in rates else "        "
            sz = f"n={sizes[n]:5d}" if sizes and n in sizes else ""
            out.append(f"{mark} {n:9s} {sz} {r} {st} {cl}")
        return out
