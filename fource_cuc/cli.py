import argparse
import sys
from pathlib import Path
from .compiler import execute_cuc_source


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="fource-cuc",
        description="Fource/CUC Virtual Machine & Assembly Runner",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run_cmd = sub.add_parser("run", help="Compile and execute a .cuc assembly file")
    run_cmd.add_argument("file", help="Path to .cuc source file")

    args = parser.parse_args(argv)

    if args.command == "run":
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File not found: {path}", file=sys.stderr)
            return 1

        source = path.read_text(encoding="utf-8")
        state = execute_cuc_source(source)

        print("=== FOURCE-CUC VM EXECUTION TRACE ===")
        for line in state.trace:
            print(" ", line)

        print("\n=== BASIN DISTORTION SPECTRUM ===")
        for bname, sc in state.scores.items():
            marker = " <-- WINNER" if bname == state.selected_basin else ""
            print(
                f"  {bname}: r_lock={sc.C_phi_group:.4f} | "
                f"C_total={sc.C_total:.4f} | E_total={sc.E_total:.4f}{marker}"
            )

        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
