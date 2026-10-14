# Release checklist

Status is recorded separately in `VERIFICATION.md`. Source-publication approvals below are specific to the 2026-10-14 release. Deployment checks are a reusable checklist for each new machine/session; an unchecked deployment item does not imply that the documented offline baseline failed.

## Source and rights

- [x] Owner approved public repository `z3247124509-sketch/notion-local-sandbox`.
- [x] Owner approved MIT for project-owned code, documentation, Skill, tests and synthetic fixtures, with `z3247124509-sketch` attribution.
- [x] Inspect all publication manifest entries; publish only the explicit 27 text files.
- [ ] Preserve required notices if any upstream code is added later.
- [ ] Finish exact wheel/image license and NOTICE audit before distributing binaries.
- [x] No company source, PRD, prototypes, media, conversations, logs, real host paths,
      active tunnel domains, tokens, credentials, `.env`, Docker config or old state.

## Reproducibility and isolation

- [ ] Recheck official metadata and pinned image/wheel identities for linux/arm64.
- [ ] Build both standalone images with separately approved download/execution scope.
- [ ] Inspect effective non-root UID, read-only root, cap drop, no-new-privileges,
      default seccomp, resource caps, exact mounts, network modes and no host ports.
- [ ] Confirm control has no external route; gateway has no project/host/socket mount.
- [ ] Run immutable self-test inside the actual control image.
- [ ] Real MCP initialize/list/read/write/check succeeds with dedicated bearer.
- [ ] Missing/wrong/duplicate authentication, traversal, links and unknown checks fail.
- [ ] Assert secrets absent from process arguments, container config/env and logs.

## Explicit external approvals

- [ ] User approves dedicated token generation if needed; user enters values locally.
- [ ] User approves exact public endpoint/provider, exposure duration and synthetic data.
- [ ] User authorizes the Notion connection in its UI; write/check tools ask each time.
- [ ] Verify access using the intended personal Agent or Custom Agent separately.
- [ ] Record quota/cost constraints without spending credits beyond the approved test.
- [ ] Verify stop removes reachability; explicit purge deletes only session volumes.

## Publication

- [x] Document actual test result, remaining limitations and supported architecture.
- [x] Confirm final manifest, archive integrity and privacy scan after final edits.
- [x] Review final README and license; owner approved this exact repository creation/publication.
- [x] Publish from the explicit source manifest, without the parent workspace or old Git history.
- [x] No automatic releases, package registry publication or hosted endpoint.

After the source write, verify GitHub visibility, repository owner/name, default branch commit, complete file tree and hashes, rendered README, and MIT license detection. Report that remote result separately; a local manifest alone is not proof of publication.
