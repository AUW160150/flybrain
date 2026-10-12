import math
import numpy as np
from flyworld.encoders import SensoryEncoder, hemifield, binocular


def test_hemifield():
    assert hemifield(0.0) == (0.5, 0.5)
    wl, wr = hemifield(math.pi / 2)
    assert wl == 1.0 and wr == 0.0
    assert binocular(0.0) == (1.0, 1.0) and binocular(math.pi / 2) == (1.0, 0.0)


def test_looming_ahead_is_symmetric_and_grows():
    e = SensoryEncoder()
    fly = (np.array([0.0, 0.0]), 0.0)
    a1 = e.encode(1, *fly, [(9, np.array([6.0, 0.0]), 0.9, "big")], 1 / 30)
    a2 = e.encode(1, *fly, [(9, np.array([4.0, 0.0]), 0.9, "big")], 1 / 30)
    assert not any(k.startswith("LC4") for k in a1)              # no expansion on the first frame
    assert a2["LC4_L"] == a2["LC4_R"] > 0 and a2["LPLC2_L"] > 0


def test_looming_on_left_is_lateralized():
    e = SensoryEncoder()
    fly = (np.array([0.0, 0.0]), 0.0)
    e.encode(1, *fly, [(9, np.array([3.0, 3.0]), 0.9, "big")], 1 / 30)
    a = e.encode(1, *fly, [(9, np.array([2.0, 2.0]), 0.9, "big")], 1 / 30)
    assert a["LC4_L"] > a.get("LC4_R", 0.0)


def test_receding_object_gives_no_loom():
    e = SensoryEncoder()
    fly = (np.array([0.0, 0.0]), 0.0)
    e.encode(1, *fly, [(9, np.array([3.0, 0.0]), 0.9, "big")], 1 / 30)
    a = e.encode(1, *fly, [(9, np.array([5.0, 0.0]), 0.9, "big")], 1 / 30)
    assert not any(k.startswith("LC") for k in a)
    assert "ORN_DA1" in a


def test_food_and_taste():
    e = SensoryEncoder()
    a = e.encode(1, np.array([0.0, 0.0]), 0.0, [(200, np.array([2.0, 2.0]), 0.5, "food")], 1 / 30, on_food=True)
    assert a["ORN_DM1_L"] > a["ORN_DM1_R"] > 0 and a["LB3c_L"] == 0.2
    far = e.encode(1, np.array([0.0, 0.0]), 0.0, [(200, np.array([15.0, 0.0]), 0.5, "food")], 1 / 30)
    assert far == {}


def test_amplitudes_capped():
    e = SensoryEncoder()
    objs = [(i, np.array([1.2, 0.0]), 0.9, "big") for i in range(20)]
    e.encode(1, np.array([0.0, 0.0]), 0.0, [(i, np.array([6.0, 0.0]), 0.9, "big") for i in range(20)], 1 / 30)
    a = e.encode(1, np.array([0.0, 0.0]), 0.0, objs, 1 / 30)
    assert max(a.values()) <= 0.25
