# BUNDLE REVIEW GUIDE

## For Supervisors and Reviewers

To review a completed Task Packet, follow this deterministic sequence:

### 1. The Bundle Review (Mandatory)
Open `TP-<ID>_PROOF_BUNDLE.json`.
- **Check Status**: Ensure it is `VALIDATED`.
- **Review Summary**: Read the results and findings.
- **Audit Acceptance**: Verify all critical acceptance checks are listed in `passed`.
- **Verify Decision**: Evaluate the confidence and rationale for the final decision.

### 2. The Artifact Audit (Optional)
If the summary mentions specific findings in primary artifacts, check those files directly if they are outside the zip.

### 3. The Forensic Drill-down (As Needed)
If you require deep evidence (logs, traces, raw data), locate the `*_PROOF_ARCHIVE.zip`.
- Check the `PROOF_ARCHIVE_MANIFEST.json` inside the zip.
- Locate the relevant trace or log file.

## Why Bundle-First?
Bundle-first review reduces cognitive load by abstracting raw execution traces into strategic summaries. It ensures that the "Why" and "What Happened" are clear before looking at the "How".
