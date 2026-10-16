# ssh-wrapper
Wrapper around ssh to simplify dealing with lot of session.

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
