# ssh-wrapper
Wrapper around ssh to simplify dealing with lot of session.

At the `Host:` prompt, press Tab to complete hostnames from the wrapper's
history, the `Host` aliases of `~/.ssh/config` (wildcards ignored) and SSH's
`~/.ssh/known_hosts`, `~/.ssh/known_hosts2`,
`/etc/ssh/ssh_known_hosts` and `/etc/ssh/ssh_known_hosts2`. Completion also
works after `user@`; arrow keys recall previous connections. Entries with a
port such as `[host]:2222` contribute the hostname; specify the port with
`-p 2222`. Hashed, wildcard and revoked entries are ignored.

If you invoke the script with the name 'ssh-root' (ie: as a symlink) it will connect as root@<HOST>.
  
If used as a command iTerm2.app profile it remeber the host it was connected per iTerm session. So if you close and reopen iTerm ssh-wrapper automatically reconnect all hosts in their windows.

Before every interactive SSH connection, `ssh-wrapper` asks for one character:
`r` to recover the `screen` session associated with the current iTerm window,
`c` to create a new session, `l` to choose from the remote session list, `s`
for a normal shell, or `q` to exit.  The same menu is shown after a dropped
session. Recovering creates the named session when it is unavailable. Creating
a session falls back to a normal shell if `screen` cannot start; choosing from
an empty list falls back to creating a new session. The list includes the time
and Attached/Detached status reported by `screen -ls`. New `screen` windows
explicitly start the remote user's login shell.

When the ssh-agent is forwarded, `screen`/`tmux` sessions use the stable
symlink `~/.ssh-wrapper/agent.sock` on the remote host as `SSH_AUTH_SOCK`,
refreshed on every reconnect, so `ssh-add -l` keeps working in long-lived
sessions. Sessions created before this change must be recreated once.

## Files in `~/.ssh-wrapper`

| File | Purpose |
|---|---|
| `ssh-wrapper_history`, `ssh-root_history` | Host history (one entry per host) |
| `session.<iTerm id>` | Host and ssh arguments of an iTerm session, used to reconnect; removed on exit, stale ones are deleted after 30 days |
| `<host>.def-fwd-ssh-agent` | Always forward the ssh-agent to `<host>` |
| `multiplexer` | Contents `screen`, `tmux` or `auto` (default: `screen` if present, otherwise `tmux`) |
| `multiplex` / `<host>.multiplex` | Create it to enable SSH connection sharing (`ControlMaster`, 10 minutes `ControlPersist`) for all hosts or for one host. Needs `MaxSessions` > 1 on the server |

The public key used for `authorized_keys` is the first found among
`id_ed25519`, `id_ecdsa` and `id_rsa`. With `tmux`, the menu behaves like with
`screen`; the prefix key is the tmux default (`Ctrl-b`).

## Development

```
shellcheck ssh-wrapper tests/run.sh
tests/run.sh
python3 tests/completion.py
```
