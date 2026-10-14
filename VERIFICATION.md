# Verification — 2026-10-14

## Passed

- 24 standard-library tests, immutable synthetic self-test and Skill validator.
- Both linux/arm64 images built offline from existing identity-checked parents and 67 hash-matched wheels; no new pulls.
- Real MCP Streamable HTTP over Unix socket, protocol 2025-03-26. Exact tools: list_files, read_file, write_file, run_check.
- Read, create, readback, implicit-overwrite rejection, compare-and-replace, traversal/absolute-path rejection, fixed-check enforcement, sample_json and self_test; unauthenticated 401 and wrong-path 404.
- The same protocol checks passed through the gateway's loopback HTTP proxy, also with network=none and IPC mounted read-only. No tunnel process was started.
- Actual control settings: UID/GID 10001, readonly root, network none, no host ports/binds, capabilities dropped, no-new-privileges, only IPC and synthetic data volumes.
- New gateway binary executes offline and reports ngrok 3.39.8.
- Actual launcher received SIGTERM, exited 0 and left no session container. Dedicated synthetic test volumes were cleaned after testing.

Control image: sha256:5a72c3f396b00f0c806e6cd803376d6dedc0e0614796cb1ae2995ae42d3ed7db
Gateway image: sha256:9b4c1b92dba28cd53b2cf48167a2733ca0110a9aad150fabe90e084071e44f8b

Real startup testing found dormant tunnel devices in Docker's network=none namespace. The corrected check allows only known, down tunnel devices and rejects external routes, unexpected/up interfaces, effective capabilities or missing no-new-privileges. Regression tests cover these denials.

## Not exercised

New credentials, OAuth, public ngrok authentication/tunnel, cloud Notion connection/model calls, personal-Agent Bearer compatibility, AMD64 and other kernels, and binary redistribution.

The deterministic public test token is not a secret and was used only in offline containers. Existing workbench services were not changed. These results prove local build/protocol behavior, not cloud Notion success.

## License and package evidence

All 27 publication files, 67 dependency results, 180 Rust metadata versions, 105 Debian package records, Python/pip and ngrok boundaries are documented in docs/PROVENANCE.md and docs/dependency-license-inventory.json. Binary-only gaps are named individually; the source ZIP contains none of those binaries.

The package uses a fixed 27-file allowlist and per-file hashes. A privacy scan checks known private identifiers, home paths, domains and ZIP integrity without accessing secret stores. No wheels, images, binaries, logs, company data or credentials are distributed. The owner approved public source publication at z3247124509-sketch/notion-local-sandbox with an MIT license for project-owned files. The publication changes add LICENSE and update documentation/packaging; the runtime code and dependency pins remain identical to the offline-tested version. This source-publication approval does not authorize a public service or Notion calls.
