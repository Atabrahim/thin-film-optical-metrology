"""Command line entry point for the reproducible V1 study."""

import argparse

from .workflow import run_workflow


def main():
    parser = argparse.ArgumentParser(
        description="Thin-film metrology and tolerance case studies"
    )
    parser.add_argument("config", help="V1 JSON configuration path")
    parser.add_argument(
        "--output", help="Override output directory (relative to current directory)"
    )
    parser.add_argument(
        "--no-figures", action="store_true", help="Skip optional Matplotlib output"
    )
    args = parser.parse_args()
    try:
        report = run_workflow(args.config, output_dir=args.output, figures=not args.no_figures)
    except (ValueError, OSError, RuntimeError, ImportError) as exc:
        parser.exit(2, f"thinfilm: {exc}\n")
    print(
        "Measured conditional thicknesses (nm):",
        report["measured"]["two_thickness"]["thickness_nm"],
    )
    print("Design optimum (nm):", report["tolerance"]["optimum_nm"])
    print("Reports generated. See report.json for assumptions and limitations.")


if __name__ == "__main__":
    main()
