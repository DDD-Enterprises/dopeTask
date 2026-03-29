# Bundle Review Guide

This guide describes how supervisors, agents, and reviewers should interact with Dopetask proof bundles.

## Standard Review Protocol

To ensure efficiency and standardization, follow these steps exactly when reviewing a completed Task Packet.

### Step 1: Open the Bundle
Always begin by opening the canonical proof bundle: `*_PROOF_BUNDLE.json`.
Do not open full traces, logs, or archives first.

### Step 2: Read the Top-Level
Review the `summary`, `status`, and `acceptance_checks` to grasp the high-level outcome. 
- Did the packet succeed?
- Are there any `failed` acceptance checks?
- What are the `key_caveats`?

### Step 3: Check Validation Metrics
Review the `validation` section. 
- Were sufficient scenarios evaluated?
- What do the `coverage_notes` reveal about gaps?

### Step 4: Drill Down (Only If Necessary)
If (and only if) you need forensic detail, locate the relevant filename in `artifacts.supporting`.
- For a small number of supporting artifacts, you will find them next to the bundle.
- For a large number, locate the `*_PROOF_ARCHIVE.zip` (referenced in `artifacts.archive`) and extract the specific file needed.

### Step 5: Avoid Archive Reliance
The zip must never be used as the canonical proof surface. If the bundle lacks the summary detail necessary to make a basic judgment without opening the archive, then the bundle itself is deficient and needs improvement.
