# Portability Checklist

Use this before treating the workspace as ready for GitHub inheritance.

## Documentation

- `README.md` explains repo role and entry order
- central re-entry brief exists
- stable core contract exists
- skill lifecycle contract exists
- setup and config docs exist

## Path Audit

- no critical behavior depends only on `/Users/tom/...` style paths
- machine-specific paths are documented
- environment-variable override route is documented

## Runtime Commands

- `./scripts/brain.sh doctor` runs
- `./scripts/brain.sh capabilities` runs
- `./scripts/brain.sh refresh` runs
- continuity command expectations are documented

## Artifact Boundary

- caches and browser output are ignored
- scratch folders are excluded or intentionally retained
- runtime telemetry is not being mistaken for portable contract

## Promotion Discipline

- stable vs experimental boundaries are documented
- no experimental feature is presented as already globally safe
- any outward promotion is backed by local evidence
