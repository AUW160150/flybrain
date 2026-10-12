import math
from flyworld.decoder import MotorDecoder
from flyworld.config import DecoderParams

Z = {k: 0.0 for k in ["DNp01", "DNp01_L", "DNp01_R", "DNp09", "MDN", "DNa01_L", "DNa01_R", "DNa02_L", "DNa02_R", "DNg11", "MN9", "DN_all"]}


def run(d, rates, n=60, dnp01=0, on_food=False, idle=False):
    if not idle:
        d.p.idle_s = 1e9
    cmd = None
    for _ in range(n):
        cmd = d.update({**Z, **rates}, dnp01, 1 / 30, on_food)
    return cmd


def test_forward_and_backward():
    assert run(MotorDecoder(), {"DNp09": 100.0}).v > 2.0
    assert run(MotorDecoder(), {"MDN": 100.0}).v < -1.0
    assert run(MotorDecoder(), {"DNp09": 5.0}).v == 0.0


def test_turn_sign_and_dead_zone():
    assert run(MotorDecoder(), {"DNa02_R": 100.0}).omega < 0      # right drive -> clockwise (negative omega)
    assert run(MotorDecoder(), {"DNa02_L": 100.0}).omega > 0
    assert run(MotorDecoder(), {"DNa02_L": 3.0}).omega == 0.0


def test_turn_bias_removes_walk_coupled_asymmetry():
    d = MotorDecoder(calib={"turn_bias_per_dnp09_hz": 0.4})
    cmd = run(d, {"DNp09": 100.0, "DNa02_L": 40.0})
    assert abs(cmd.omega) < 1e-6 and cmd.v > 2.0


def test_jump_and_cooldown():
    d = MotorDecoder()
    c1 = d.update({**Z, "DNp01_L": 200.0}, 3, 1 / 30)
    assert c1.jump and c1.jump_turn < 0 and c1.v == d.p.jump_speed   # threat on the left -> turn right
    c2 = d.update({**Z, "DNp01_L": 200.0}, 3, 1 / 30)
    assert not c2.jump
    for _ in range(int(d.p.jump_dur_s * 30) + 2):
        d.update({**Z}, 0, 1 / 30)
    assert d.update({**Z}, 3, 1 / 30).jump is False               # still cooling down
    for _ in range(int(d.p.jump_cooldown_s * 30) + 2):
        d.update({**Z}, 0, 1 / 30)
    assert d.update({**Z}, 3, 1 / 30).jump is True


def test_groom_hysteresis_and_eat():
    d = MotorDecoder()
    assert run(d, {"DNg11": 30.0, "DNp09": 100.0}).groom and d.v_actual < 0.5
    assert run(d, {"DNg11": 15.0}).groom                            # stays on between thresholds
    assert not run(d, {"DNg11": 5.0}).groom
    assert run(MotorDecoder(), {"MN9": 50.0}, on_food=True).eat
    assert not run(MotorDecoder(), {"MN9": 50.0}, on_food=False).eat


def test_idle_wander_after_silence():
    d = MotorDecoder(DecoderParams(idle_s=0.5))
    cmd = run(d, {}, n=60, idle=True)
    assert cmd.idle and cmd.v > 0
