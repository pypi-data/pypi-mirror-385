from __future__ import annotations
import argparse
from pathlib import Path
from typing import List, Set, Tuple

from .circular_import_detector import CircularImportDetector


def _resolve_changed_modules(detector: CircularImportDetector, repo_root: Path, filenames: List[str]) -> Set[str]:
    """Map staged filenames to module names using the detector's index; fallback heuristics if needed."""
    changed: Set[str] = set()
    # Normalize known index
    inv: Dict[Path, str] = {Path(fp).resolve(): mod for mod, fp in detector.module_to_file.items()}
    for f in filenames:
        p = (repo_root / f).resolve() if not Path(f).is_absolute() else Path(f).resolve()
        mod = inv.get(p)
        if mod:
            changed.add(mod)
            continue
        # Fallback: derive module name like detector does
        try:
            scan_root = detector.scan_root
            if p.is_relative_to(scan_root):
                rel = p.relative_to(scan_root)
                parts = list(rel.parts)
                if parts[-1] == "__init__.py":
                    parts = parts[:-1]
                else:
                    parts[-1] = parts[-1][:-3]
                parts = [q for q in parts if q and q != "."]
                if parts:
                    changed.add(".".join(parts))
        except Exception:
            pass
    return changed


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Pre-commit hook for circular imports")
    ap.add_argument("filenames", nargs="*")         # provided by pre-commit when pass_filenames: true
    ap.add_argument("--repo-root", default=".")
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    det = CircularImportDetector(str(repo_root))
    has_cycles, groups = det.detect_circular_imports()

    # If pre-commit didn’t pass any python files, allow commit.
    if not args.filenames:
        return 0

    # Build set of changed absolute paths
    changed_paths: Set[Path] = set()
    for f in args.filenames:
        p = Path(f)
        p = (repo_root / p).resolve() if not p.is_absolute() else p.resolve()
        changed_paths.add(p)

    # Keep only groups where at least one edge is created by a changed file
    filtered = []
    for comp in groups:
        # real edges inside this SCC
        edges_in_group: Set[Tuple[str, str]] = {
            (u, v) for u in comp for v in det.module_graph.get(u, ())
            if v in comp
        }
        # does any edge originate in a changed file?
        keep = False
        for (u, v) in edges_in_group:
            for (fp, _lineno, _raw) in det.edge_meta.get((u, v), ()):
                if Path(fp).resolve() in changed_paths:
                    keep = True
                    break
            if keep:
                break
        if keep:
            filtered.append(comp)

    if filtered:
        # Reuse the detector’s formatter (we’ll improve it next).
        print(det.format_cycles(filtered))
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
