**How We Prove Equivalence**

- Primary method: MQT QCEC (`mqt.qcec.verify`) on pairs of circuits before/after semantics‑preserving optimizations.
- Fallback: Small‑circuit statevector comparison ignoring global phase.
- Mitigation passes (ZNE, CDR, PEC, VD) change semantics and are skipped for QCEC.

Artifacts
- Each semantics‑preserving pass writes a JSON artifact to `reports/qcec/` with: pass name, before/after circuit hashes, QCEC availability, result, and message. Peephole rules include H•H and adjacent CX cancellation.

Segmentation and Equivalence
- Deferred‑measurement rewriting is applied only to Clifford‑eligible branches and preserves semantics; when successful, segments validated by QCEC or empirical TVD ≤ 0.05 vs. Aer.
