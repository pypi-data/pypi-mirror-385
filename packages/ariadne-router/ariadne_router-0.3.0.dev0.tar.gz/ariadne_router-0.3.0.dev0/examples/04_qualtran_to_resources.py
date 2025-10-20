from __future__ import annotations

from examples._util import write_report


def main() -> None:
    try:
        import qualtran  # noqa: F401

        from ariadne.ft.resource_estimator import estimate_with_azure

        # Placeholder: load QIR/Broombridge and call estimate (requires Azure workspace)
        est = estimate_with_azure("path/to/qir.ll", code="surface")
        report = f"Azure estimate (stub): {est}"
    except Exception as e:
        report = f"Qualtran/Azure unavailable or not configured: {e}"
    path = write_report("04_qualtran_to_resources", f"# Resource Estimation\n\n{report}\n")
    print(f"Wrote report to {path}")


if __name__ == "__main__":
    main()
