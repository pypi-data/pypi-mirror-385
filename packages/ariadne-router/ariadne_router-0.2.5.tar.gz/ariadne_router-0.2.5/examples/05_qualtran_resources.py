from __future__ import annotations

from examples._util import write_report


def main() -> None:
    from ariadne.ft.resource_estimator import azure_estimate_table

    table = azure_estimate_table("path/to/program")
    lines = [
        "# Azure Resource Estimates\n",
        "(If Azure not configured, showing 'unavailable' records)\n",
    ]
    for code, est in table.items():
        lines.append(f"- {code}: qubits={est.logical_qubits}, runtime={est.runtime_sec}s, notes={est.notes}")
    path = write_report("05_qualtran_resources", "\n".join(lines))
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
