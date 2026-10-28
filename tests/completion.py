#!/usr/bin/env python3
"""Exercise the real Readline prompt through a pseudo-terminal."""
import errno
import os
from pathlib import Path
import pty
import select
import subprocess
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent


def check(typed, expected, *, root=False):
    with tempfile.TemporaryDirectory() as directory:
        home = Path(directory)
        (home / ".ssh").mkdir()
        options = home / ".ssh-wrapper"
        options.mkdir()
        history = options / ("ssh-root_history" if root else "ssh-wrapper_history")
        history.write_text("alice@wrtest-history -p 2222\nwrtest-recent\n")
        (home / ".ssh" / "known_hosts").write_text(
            "# comment\n"
            "wrtest-known,wrtest-alias ssh-ed25519 KEY\n"
            "[wrtest-port]:2222 ssh-ed25519 KEY\n"
            "[2001:db8::42]:2222 ssh-ed25519 KEY\n"
            "@cert-authority wrtest-cert ssh-ed25519 KEY\n"
            "@revoked wrtest-revoked ssh-ed25519 KEY\n"
            "wrtest-wild* ssh-ed25519 KEY\n"
            "|1|HASH|HASH ssh-ed25519 KEY\n"
        )
        (home / ".ssh" / "config").write_text(
            "Host wrtest-cfg wrtest-cfgalias\n  HostName example.org\n"
            "Host wrtest-cfgwild-*\n  User x\n"
        )
        (home / ".ssh" / "known_hosts2").write_text("wrtest-legacy ssh-rsa KEY\n")
        command = ROOT / "ssh-wrapper"
        if root:
            command = home / "ssh-root"
            command.symlink_to(ROOT / "ssh-wrapper")
        master, slave = pty.openpty()
        process = subprocess.Popen(
            [str(command)], stdin=slave, stdout=slave, stderr=slave,
            env=dict(os.environ, HOME=str(home), TERM="xterm",
                     TERM_SESSION_ID="completion-test"),
        )
        os.close(slave)
        output = b""
        deadline = time.monotonic() + 5
        # Answer each prompt only after it appears: sending everything at once
        # is racy because Readline may discard type-ahead (seen with bash 5).
        steps = [(b"Host: ", typed + b"\n"), (b"[y/a/N]", b"n\n"), (b"Screen:", b"q")]
        try:
            while time.monotonic() < deadline:
                if select.select([master], [], [], 0.1)[0]:
                    try:
                        data = os.read(master, 65536)
                    except OSError as error:
                        if error.errno != errno.EIO:
                            raise
                        break
                    if not data:
                        break
                    output += data
                    if steps and steps[0][0] in output:
                        # q exits before any SSH connection is started.
                        os.write(master, steps.pop(0)[1])
                        output = b""
                if process.poll() is not None:
                    break
            assert process.wait(timeout=2) == 0, output
            assert history.read_text().splitlines()[-1] == expected, output
            assert not list(options.glob("hosts.*")), "temporary host list leaked"
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            os.close(master)
    print("ok   - host completion:", repr(typed))


for prefix, expected in [
    (b"wrtest-hist\t", "wrtest-history"),
    (b"bob@wrtest-kno\t", "bob@wrtest-known"),
    (b"wrtest-ali\t", "wrtest-alias"),
    (b"wrtest-por\t", "wrtest-port"),
    (b"2001:db8::4\t", "2001:db8::42"),
    (b"wrtest-cer\t", "wrtest-cert"),
    (b"wrtest-leg\t", "wrtest-legacy"),
    (b"wrtest-cfga\t", "wrtest-cfgalias"),
    (b"bob@wrtest-cfga\t", "bob@wrtest-cfgalias"),
    (b"wrtest-cfgw\t", "wrtest-cfgw"),
    (b"wrtest-rev\t", "wrtest-rev"),
    (b"wrtest-wil\t", "wrtest-wil"),
    (b"\x1b[A", "wrtest-recent"),
]:
    check(prefix, expected)
check(b"wrtest-hist\t", "wrtest-history", root=True)
