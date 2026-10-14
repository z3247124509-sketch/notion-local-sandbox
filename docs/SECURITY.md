# Security boundary

Only synthetic data belongs in this review/demo. Requests and returned text can be
seen by Notion and the tunnel provider; a valid bearer can invoke all four tools.
There is no per-user authorization or server-side human-approval receipt.

The control container is offline, non-root, read-only except for one synthetic data
volume, IPC and bounded temporary storage. The gateway has network access and IPC
only; it has no project data mount, host mount, Docker socket, keychain or SSH keys.
The local launcher has Docker authority and is a trusted part of the system.
Container isolation reduces exposure; it does not protect against a compromised
Docker daemon, local administrator, host kernel or malicious replacement image.

File paths use descriptor-relative opens and reject traversal, symlinks, hardlinks,
non-regular files and oversized/non-UTF-8 text. The MCP process serializes file
operations. Resource caps and a 100-file limit bound normal remote usage. Nothing
from the writable workspace is imported or executed.

Secrets are supplied by the user through hidden local input. The control receives
only a bearer digest; the gateway receives an ngrok token and writes it only to
tmpfs with 0600 permissions. The token still exists in process memory and transit
through local pipes. Docker logs and raw gateway output are disabled. Do not promise
forensic erasure from host RAM, swap or vendor systems.

The public endpoint is explicitly opt-in and stays active until stopped. No default
TTL, auto-start, OAuth server or token generator is included. `--approved-public-session`
is a guard against accidents, not proof of human authorization; the operator/assistant
must obtain the actual approval before invoking it. `.env.example` is documentation
only and must never be filled with real secrets.

The launcher stops only session-labelled resources whose names match its session
record. A hard-killed launcher can leave containers alive: verify stop rather than
assuming a closed terminal disconnected the endpoint. Deleting volumes is separate.

Changes that require a new review: arbitrary commands, workspace-code execution,
new host mounts, networking for control/runners, third-party model delegation,
credential persistence, automatic restart, sharing an Agent, or publishing artifacts.

Report issues with a synthetic reproducer. This review package has no public issue
tracker/contact yet; do not post private material or secrets while choosing one.
