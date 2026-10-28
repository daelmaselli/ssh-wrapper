# Changelog

## Unreleased

### Behaviour changes
- **Key selection**: the key used by the "add to authorized_keys" step and
  loaded with `ssh-add` is no longer always `~/.ssh/id_rsa`. The first
  existing one among `id_ed25519`, `id_ecdsa`, `id_rsa` (in this order) is
  used. If only `id_rsa` exists, nothing changes. If you also have an
  `id_ed25519`, that one is now preferred. Normal ssh authentication is
  unaffected: ssh/ssh-agent still try every available key.
- **tmux**: when `screen` is missing on the remote host, `tmux` is used.
  Force one with `~/.ssh-wrapper/multiplexer` (`screen`, `tmux`, `auto`).
- **Session names**: new sessions are named `<base>_YYYYMMDD-HHMMSS`
  instead of a Unix timestamp.
- **Multiplexing** (opt-in): `~/.ssh-wrapper/multiplex` or
  `~/.ssh-wrapper/<host>.multiplex` enables `ControlMaster`/`ControlPersist`.
- **ssh failures**: the exit status is printed when ssh ends non-zero.
- **Menu on EOF**: a closed terminal quits instead of looping on the default.
- **Host history**: one entry per host (most recent last).
- **Cleanup**: `session.*` files older than 30 days are deleted;
  `~/.ssh-wrapper` is set to mode 700.
- Removed `ssh -K` (macOS-only, GSSAPI keychain) from the key check.

### Fixes
- Quoted all variables (hosts, paths with spaces); removed tcsh leftovers
  (`set noglog`, `eval resize`).
- `ssh-add -l` is checked by exit status instead of matching its message.
- `ssh_copy_id_func` returns explicit results; the `-A` agent-forwarding
  prompt is no longer skipped by a stale `$?`.
- The public key is appended to `authorized_keys` through stdin instead of
  being embedded in the remote command.
- Session files store one ssh argument per line (old single-line files are
  still read).

### Development
- `tests/run.sh` (fake ssh/screen/tmux), `shellcheck` and a GitHub Actions
  workflow.
