import math
import unittest
from fource_cuc import (
    CUCDeepNetwork,
    CUCInstruction,
    CUCVirtualMachine,
    Phasor,
    branch_contradictions,
    coa_star,
    fuse_group,
)


class TestFourceCUCCore(unittest.TestCase):
    def test_pfa_order_invariance(self):
        z1 = Phasor(2.0, 0.0)
        z2 = Phasor(3.0, math.pi / 3.0)
        z3 = Phasor(1.5, math.pi / 2.0)
        fused_abc, r_abc = fuse_group([z1, z2, z3], beta=2.0)
        fused_cba, r_cba = fuse_group([z3, z2, z1], beta=2.0)
        self.assertAlmostEqual(r_abc, r_cba, places=8)
        self.assertAlmostEqual(fused_abc.A, fused_cba.A, places=8)

    def test_contradiction_branching(self):
        items = ["e1", "e2", "e3", "e4"]
        scores = {
            ("e1", "e2"): 0.1,
            ("e1", "e3"): 0.8,
            ("e2", "e3"): 0.7,
            ("e1", "e4"): 0.75,
            ("e2", "e4"): 0.85,
            ("e3", "e4"): 0.2,
        }
        ctr = lambda a, b: scores.get((a, b), scores.get((b, a), 0.1))
        self.assertEqual(branch_contradictions(items, ctr, theta_ctr=0.6), [["e1", "e2"], ["e3", "e4"]])

    def test_coa_star_box_projection(self):
        res = coa_star(8.0, 5.0, lambda a, b: a + b, lambda x: max(0.0, min(10.0, x)))
        self.assertEqual(res, 10.0)

    def test_cuc_vm_execution(self):
        program = [
            CUCInstruction("LOAD", {"carriers": [
                Phasor(0.95, 0.12), Phasor(0.90, 0.24),
                Phasor(0.60, -2.40), Phasor(0.55, -2.10),
            ]}),
            CUCInstruction("COMPOSE", {"phasor": Phasor(1.05, 0.05)}),
            CUCInstruction("PROJECT", {"bounds": (0.1, 1.0)}),
            CUCInstruction("BRANCH", {"theta_ctr": 0.35}),
            CUCInstruction("STABILIZE", {"steps": 12, "kappa": 0.45}),
            CUCInstruction("SELECT"),
            CUCInstruction("HALT"),
        ]
        state = CUCVirtualMachine().run(program)
        self.assertTrue(state.halted)
        self.assertEqual(state.selected_basin, "H1")

    def test_deep_cuc_network_convergence(self):
        net = CUCDeepNetwork([
            (4, ["Hidden_Low", "Hidden_High"]),
            (2, ["Class_Stable", "Class_Unstable"]),
        ])
        x_stable = [Phasor(0.95, 0.10), Phasor(0.90, 0.15), Phasor(0.92, 0.12), Phasor(0.94, 0.08)]
        x_unstable = [Phasor(0.90, 2.20), Phasor(0.88, 2.35), Phasor(0.91, 2.10), Phasor(0.89, 2.25)]
        for _ in range(15):
            net.train_step(x_stable, ["Hidden_Low"], "Class_Stable", lr=0.30)
            net.train_step(x_unstable, ["Hidden_High"], "Class_Unstable", lr=0.30)

        pred_s, _, _ = net.forward(x_stable)
        pred_u, _, _ = net.forward(x_unstable)
        self.assertEqual(pred_s, "Class_Stable")
        self.assertEqual(pred_u, "Class_Unstable")


if __name__ == "__main__":
    unittest.main()
