# fource-cuc-core

**Zero-Dependency Python Runtime for Fource / CUC Algebra, the CUC Virtual Machine (`CUC-VM`), and Phase-Locked Neural Networks**

Instead of treating scalar equality (`x = y`) as the primitive operation of computation, `fource-cuc-core` builds computation around **Coherence-Under-Constraint (`Compose → Project → Stabilize`)**:

1. **PFA (Phase / Fource Algebra):** Represents signals and weights as complex phasors $z = A e^{i\phi}$ and fuses groups via the order-invariant Kuramoto order parameter $r = \left|\frac{1}{n}\sum e^{i\phi_k}\right|$.
2. **CS (Coherence Semiring):** Converts multiplicative coherence $C_{\text{total}}$ into additive distortion energy $E_{\text{total}} = -\ln(C_{\text{total}} + \epsilon)$, partitioning contradictory inputs into separate hypothesis basins (`branch_contradictions`) and selecting the minimum-distortion basin ($k^* = \arg\min_k E_{\text{total},k}$).
3. **COA (CUC Operator Algebra):** Executes universal system transitions $x \star_K y = R\bigl(\Pi_K(x \otimes y)\bigr)$.

## Modules
* `fource_cuc.algebra`: Core PFA, CS, COA operators, contradiction branching, and `UnifiedCoherenceScore`.
* `fource_cuc.vm`: `CUCVirtualMachine` executing `LOAD`, `COMPOSE`, `PROJECT`, `BRANCH`, `STABILIZE`, `SELECT`, and `HALT`.
* `fource_cuc.neural`: `CUCPhaseLayer` and `CUCDeepNetwork` training via distortion-energy minimization.
* `docs/`: Interactive browser visualizer for stepping through CUC-VM opcodes and training the deep phase-locked network.

## License
Apache License, Version 2.0.
