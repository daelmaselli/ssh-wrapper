#!/bin/bash
# End-to-end tests: ssh, screen, tmux and ssh-add are replaced by fakes that
# record their arguments, and the "remote" command runs locally.
cd "$(dirname "$0")/.." || exit 1
root=$PWD
fail=0
ORIG_PATH=$PATH

setup() {
  PATH=$ORIG_PATH
  tmp=$(mktemp -d) || exit 1
  mkdir "$tmp/bin" "$tmp/home"
  export HOME="$tmp/home" TERM_SESSION_ID="w0t0p0:TEST-ID" LOG="$tmp/log"
  : > "$LOG"
  cat > "$tmp/bin/ssh" <<'FAKE'
#!/bin/sh
echo "ssh $*" >> "$LOG"
for last; do :; done
case "$*" in *" true"|*"cat >>"*) exit 0 ;; esac
sh -c "$last"
FAKE
  cat > "$tmp/bin/ssh-add" <<'FAKE'
#!/bin/sh
exit 0
FAKE
  for m in "$@"; do
    # shellcheck disable=SC2016  # $LOG and $* expand inside the fake
    printf '#!/bin/sh\necho "%s $*" >> "$LOG"\n' "$m" > "$tmp/bin/$m"
  done
  chmod +x "$tmp/bin"/*
  # Expose only the real tools the script needs, hiding any real screen/tmux.
  for t in sh bash awk sed tr tail grep mv mkdir chmod find touch rm cat date \
           id hostname basename mktemp true; do
    ln -s "$(command -v "$t")" "$tmp/bin/$t" 2>/dev/null
  done
  PATH="$tmp/bin"
  export PATH
}

check() {
  if grep -q -- "$2" "$LOG"; then echo "ok   - $1"; else
    echo "FAIL - $1 (expected '$2')"; sed 's/^/       /' "$LOG"; fail=1; fi
}

run() { printf "%s" "$1" | "$root/ssh-wrapper" >/dev/null 2>&1; }

setup screen
run $'myhost\nn\nrq'
check "recover uses screen -xRR" "screen -c .* -q -e \^Bb -xRR -S ssh_wrapper_TEST-ID"
check "ssh runs with -t" "ssh -t myhost"

setup tmux
run $'myhost\nn\nrq'
check "falls back to tmux" "tmux -f .* new-session -A -s ssh_wrapper_TEST-ID"

setup screen tmux
mkdir -p "$HOME/.ssh-wrapper"; echo tmux > "$HOME/.ssh-wrapper/multiplexer"
run $'myhost\nn\nrq'
check "multiplexer file overrides auto" "tmux -f"

setup screen
mkdir -p "$HOME/.ssh-wrapper"; touch "$HOME/.ssh-wrapper/multiplex"
run $'myhost\nn\nrq'
check "multiplex adds ControlMaster" "ControlMaster=auto"

setup screen
run $'myhost\nn\ncq'
check "create uses a timestamped name" "-S ssh_wrapper_TEST-ID_[0-9]\{8\}-[0-9]\{6\}"

setup screen
run $'myhost\nn\nsq'
if grep -q '^screen' "$LOG"; then echo "FAIL - shell must not start screen"; fail=1; else echo "ok   - shell skips screen"; fi

setup screen
mkdir -p "$HOME/.ssh-wrapper"
echo "ssh oldhost" > "$HOME/.ssh-wrapper/session.TEST-ID"
run $'rq'
check "legacy session file is restored with -t" "ssh -t oldhost"

exit $fail
