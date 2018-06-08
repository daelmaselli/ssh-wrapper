# ssh-wrapper
Wrapper around ssh to simplify dealing with lot of session.

If you invoke the script with the name 'ssh-root' (ie: as a symlink) it will connect as root@<HOST>.
  
If used as a command iTerm2.app profile it remeber the host it was connected per iTerm session. So if you close and reopen iTerm ssh-wrapper automatically reconnect all hosts in their windows.
