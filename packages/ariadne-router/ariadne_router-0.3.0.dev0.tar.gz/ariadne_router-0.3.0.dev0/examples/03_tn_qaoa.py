from __future__ import annotations

from examples._util import write_report


def main() -> None:
    try:
        import cotengra  # noqa: F401
        import quimb  # noqa: F401
    except Exception as e:
        path = write_report("03_tn_qaoa", f"TN libs unavailable: {e}\n")
        print(f"Wrote report to {path}")
        return

    # Planning-only stub with memory cap note
    qubits = 96
    mem_cap_gib = 24
    report = f"""
# TN QAOA with slicing (planning/execution note)

- Qubits: {qubits}
- Memory cap: {mem_cap_gib} GiB
- Concurrency: uses process pool for slices when available
"""
    path = write_report("03_tn_qaoa", report)
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
