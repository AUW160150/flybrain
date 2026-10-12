"""Parameter dataclasses and repository paths shared by every flyworld module."""
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATHS = {
    "whole_npz": ROOT / "processed/malecns_v1.0_traced_minw1.npz",
    "annotations": ROOT / "data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather",
    "circuit_npz": ROOT / "processed/circuit_npc.npz",
    "circuit_groups": ROOT / "processed/circuit_npc_groups.json",
    "groups_whole": ROOT / "processed/groups_whole.json",
    "calibration": ROOT / "processed/calibration.json",
    "runs": ROOT / "runs",
}


@dataclass
class LIFParams:
    dt: float = 1.0          # biological ms per step
    tau: float = 20.0        # membrane time constant, ms
    thr: float = 1.0         # spike threshold (dimensionless v)
    reset: float = 0.0
    refr_ms: int = 2         # absolute refractory period, steps
    gain: float = 0.005      # synaptic gain multiplying signed synapse counts
    min_w: int = 5           # keep edges with abs(synapse count) >= min_w
    noise: float = 0.0       # uniform noise amplitude added to drive each step
    governor_frac: float = 0.05   # activity fraction that counts as runaway
    governor_steps: int = 20      # consecutive runaway steps before damping


@dataclass
class DecoderParams:
    window_ms: int = 50       # spike-count window for rates
    ema_ms: float = 100.0     # EMA smoothing of rates, biological ms
    walk_thr: float = 10.0    # Hz below which DNp09/MDN drive is zero
    walk_sat: float = 100.0   # Hz at which drive saturates
    v_forward: float = 3.0    # units/s at saturation
    v_back: float = 2.0
    turn_deg: float = 180.0   # deg/s at saturation
    turn_scale: float = 50.0  # Hz scale inside tanh
    turn_dead: float = 10.0   # Hz dead zone on the L-R difference (looming asymmetries are >100 Hz)
    jump_window_ms: int = 20
    jump_cooldown_s: float = 0.5
    jump_turn_deg: float = 45.0
    jump_speed: float = 8.0
    jump_dur_s: float = 0.15
    groom_on: float = 20.0
    groom_off: float = 10.0
    eat_thr: float = 20.0
    idle_s: float = 2.0
    idle_speed: float = 0.4
    lowpass_s: float = 0.1


@dataclass
class WorldParams:
    arena_half: float = 20.0
    n_npc: int = 6
    n_food: int = 4
    n_obstacles: int = 5
    fly_radius: float = 0.3
    big_radius: float = 0.9
    food_radius: float = 0.75
    obstacle_radius: float = 1.2
    tick_hz: int = 30
    bio_ms_per_tick: int = 10
    bio_ms_per_tick_focus: int = 10   # same clock as the sub-circuit brains since propagation became event-driven
    sense_range: float = 8.0
    fov_deg: float = 150.0
    odour_range: float = 8.0
    odour_decay: float = 2.0      # units; measured: a stimulated fly stalls on the food patch at this value, 2.4 units short at 4.0
    da1_range: float = 6.0
    big_speed: float = 4.0
    big_turn_deg: float = 120.0
