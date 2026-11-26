import re
from typing import Any, Dict, List
from .algebra import Phasor
from .vm import CUCInstruction, CUCVirtualMachine, CUCMachineState


def _parse_kv(tokens: List[str]) -> Dict[str, Any]:
    """Parse key=value tokens into typed Python arguments."""
    args: Dict[str, Any] = {}
    for tok in tokens:
        if "=" not in tok:
            continue
        k, _, v = tok.partition("=")
        if "," in v:
            args[k] = tuple(float(x) for x in v.split(","))
        elif v.isdigit():
            args[k] = int(v)
        else:
            try:
                args[k] = float(v)
            except ValueError:
                args[k] = v
    return args


def compile_cuc_source(source: str) -> List[CUCInstruction]:
    """Compile human-readable .cuc assembly text into CUCVirtualMachine bytecode."""
    program: List[CUCInstruction] = []

    for lineno, raw_line in enumerate(source.splitlines(), start=1):
        code_part, _, _ = raw_line.partition("#")
        line = code_part.strip()
        if not line:
            continue

        op_part, _, rest_part = line.partition(" ")
        op = op_part.strip().upper()
        rest = rest_part.strip()

        if op == "LOAD":
            pairs = re.findall(r"\(\s*([+-]?\d*\.?\d+)\s*,\s*([+-]?\d*\.?\d+)\s*\)", rest)
            if not pairs:
                raise SyntaxError(f"Line {lineno}: LOAD requires (A, phi) phasor pairs.")
            carriers = [Phasor(float(a), float(phi)) for a, phi in pairs]
            program.append(CUCInstruction("LOAD", {"carriers": carriers}))

        elif op == "COMPOSE":
            kv = _parse_kv(rest.split())
            p = Phasor(kv.get("A", 1.0), kv.get("phi", 0.0))
            program.append(CUCInstruction("COMPOSE", {"phasor": p, "beta": kv.get("beta", 1.5)}))

        elif op == "PROJECT":
            kv = _parse_kv(rest.split())
            program.append(CUCInstruction("PROJECT", {"bounds": kv.get("bounds", (0.1, 1.0))}))

        elif op == "BRANCH":
            kv = _parse_kv(rest.split())
            program.append(CUCInstruction("BRANCH", {"theta_ctr": kv.get("theta", 0.35)}))

        elif op == "STABILIZE":
            kv = _parse_kv(rest.split())
            program.append(CUCInstruction("STABILIZE", {
                "steps": int(kv.get("steps", 10)),
                "kappa": float(kv.get("kappa", 0.45)),
            }))

        elif op in ("SELECT", "HALT"):
            program.append(CUCInstruction(op))

        else:
            raise SyntaxError(f"Line {lineno}: Unknown CUC opcode '{op}'.")

    return program


def execute_cuc_source(source: str) -> CUCMachineState:
    """Compile and run a .cuc program in one call."""
    return CUCVirtualMachine().run(compile_cuc_source(source))
