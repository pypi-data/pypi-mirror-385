from __future__ import annotations

from examples._util import estimate_sv_bytes, write_report


def fmt_bytes(n: int) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if n < 1024:
            return f"{n:.2f} {unit}"
        n /= 1024
    return f"{n:.2f} PiB"


def main() -> None:
    rows = []
    for n in (29, 30, 31):
        b_single = estimate_sv_bytes(n, complex_bytes=8)
        b_double = estimate_sv_bytes(n, complex_bytes=16)
        rows.append((n, b_single, b_double))

    lines = ["# State-vector memory estimates (complex64 vs complex128)\n"]
    for n, bs, bd in rows:
        lines.append(f"- n={n}: single={fmt_bytes(bs)}, double={fmt_bytes(bd)}")

    lines.append("\nNote: We avoid executing large SV sims here to keep examples fast.")
    path = write_report("01_sv_limits", "\n".join(lines))
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
