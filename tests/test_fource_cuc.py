    def test_cuc_assembly_compiler(self):
        src = """
        # Multi-basin sensory fusion program
        LOAD (0.95, 0.12), (0.90, 0.24), (0.60, -2.40), (0.55, -2.10)
        COMPOSE A=1.05 phi=0.05 beta=1.5
        PROJECT bounds=0.1,1.0
        BRANCH theta=0.35
        STABILIZE steps=12 kappa=0.45
        SELECT
        HALT
        """
        state = execute_cuc_source(src)
        self.assertTrue(state.halted)
        self.assertEqual(state.selected_basin, "H1")
