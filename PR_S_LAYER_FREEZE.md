# Freeze: canonical State-of-Mind (S) layer semantics

Summary
-------

This PR establishes the canonical S-layer semantics for the repository. It
introduces `registry/s_layer.yaml` and the accompanying `docs/S_LAYER_SPEC.md`.

Files added
-----------
- `registry/s_layer.yaml` — canonical label registry and runtime mappings
- `docs/S_LAYER_SPEC.md` — specification and audit instructions

Rationale
---------

Freezing the S-layer means we define an authoritative semantic checkpoint. The
goal is architectural discipline: after the freeze, implementations must
conform to these semantics and mismatches are resolved through audits, not ad-
hoc code edits.

Verification checklist for reviewer (please do before I commit locally)
---------------------------------------------------------------
- Confirm `registry/s_layer.yaml` labels match `docs/S_LAYER_SPEC.md`.
- Check `runtime_mapping` target names are the intended canonical attributes.
- Validate the YAML parses (e.g., with `python -c "import yaml; yaml.safe_load(open('registry/s_layer.yaml'))"`).

Do not merge
-----------

Please do not merge this PR. Treat the branch/PR as the frozen semantic
checkpoint. After the PR exists, perform the Runtime Reconciliation Audit (see
below) and produce a mismatch report before allowing any implementation changes
that alter semantics.

Runtime Reconciliation Audit (next phase)
----------------------------------------
1. Inspect `state_inference.py` and `state_manager.py` for names and labels used
   at runtime.
2. Compare those attributes against `registry/s_layer.yaml`'s `runtime_mapping`.
3. Record every mismatch as an item in the audit report (no code changes).
4. Produce a small guidance document mapping canonical labels → runtime fields
   and proposed migration steps. That guidance may be turned into tasks after
   the audit is reviewed.

Local commit steps (for me)
---------------------------
The intended local sequence (I will not run these without your OK):

```powershell
cd e:\psypredictor
git checkout -b freeze/s-layer
git add registry/s_layer.yaml docs/S_LAYER_SPEC.md PR_S_LAYER_FREEZE.md
git commit -m "freeze: establish canonical S-layer semantics"
git push -u origin freeze/s-layer
```

PR creation (after push)
------------------------

```powershell
gh pr create `
  --title "Freeze canonical State-of-Mind (S) layer semantics" `
  --body-file PR_S_LAYER_FREEZE.md
```

Notes
-----
- The freeze is intentionally conservative: it does not change runtime code.
- After the PR is visible we can use it as the authoritative semantic checkpoint
  for the audit described above.
PR: Freeze S-layer semantic registry (draft)

Summary
- Adds a freeze-ready semantic registry for the State-of-Mind (S) layer and a one-page S-layer specification.
- Freezes five canonical S nodes and records mappings for seven nodes removed from S.
- No runtime code changes included; this PR is semantic/documentation-only.

Files added/changed
- registry/s_layer.yaml (new): freeze-ready YAML registry containing the five S nodes and removed_mappings.
- docs/S_LAYER_SPEC.md (new): one-page human-readable specification and freeze record.

Rationale
- The S-layer audit completed an evidence-first boundary review and determined a minimal canonical S set that satisfies form-generation, situation-removal, and layer-purity tests.
- We record mapping targets for nodes that failed the S tests so later runtime/taxonomy reconciliation can be precise.

Review checklist
- [ ] Confirm wording guardrails in `docs/S_LAYER_SPEC.md` are acceptable.
- [ ] Confirm the five canonical node definitions are sufficiently precise and episode-limited.
- [ ] Confirm the removed node mappings align with intended downstream layers (Mood/Feeling/Trait/Cognition).
- [ ] Verify no runtime code is modified in this PR.

Testing guidance
- No automated runtime tests required for this documentation-only change.
- Suggested manual checks for reviewers:
  - Scan `registry/s_layer.yaml` for wording or boundary leakage.
  - Confirm `docs/S_LAYER_SPEC.md` matches governance expectations for freeze artifacts.

Next steps after merge
1. Prepare a mapping proposal that maps runtime `state_inference.py` labels and `StateManager` active state instances to the canonical S nodes and to other layers where appropriate.
2. Implement runtime changes in small, reviewable PRs referencing this freeze artifact.

Notes
- This PR intentionally avoids any runtime mapping or changes. The purpose is to establish the semantic freeze artifact to guide later implementation.
