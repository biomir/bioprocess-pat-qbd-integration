# Codex task — create and publish bioprocess PAT/QbD repository

Create a new **public** GitHub repository under `biomir` named:

`bioprocess-pat-qbd-integration`

Use this directory as the repository root.

## Required steps

1. Review for secrets, credentials, private health data, proprietary BioMIR implementation, and confidential employer/process information.
2. Confirm all process data and parameters are synthetic/non-proprietary.
3. Run `pip install -e ".[test]"`, `pytest -q`, and `python examples/run_reference.py`.
4. Create `biomir/bioprocess-pat-qbd-integration` as a public repository with default branch `main`.
5. Commit with: `Build bioprocess PAT/QbD integration reference`.
6. Push and verify GitHub Actions CI succeeds.
7. Report final commit SHA and CI status.

Do not introduce real manufacturing recipes, confidential employer methods/data, or BioMIR proprietary algorithms.
