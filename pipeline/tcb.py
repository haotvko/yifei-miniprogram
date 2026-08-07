#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-contained wrapper around the CloudBase tcb CLI for automation.

Why this exists
---------------
The default `tcb login` (device/web flow) issues temporary STS credentials that
expire after ~2 hours, and the CLI does NOT auto-refresh them. That forced a
human to re-authorize in the browser on every cross-day automation run.

The fix used here: log in ONCE with a CloudBase *environment API Key*
(`tcb env apikey create ...`, then `tcb login --cloudbase-api-key <key> -e <envId>`).
The CLI then auto-exchanges the env API key for fresh STS credentials whenever
they expire -- no browser, no refresh token, no human in the loop.

This wrapper:
  1. Checks whether the stored tcb credential is still fresh.
  2. If not, re-logs in using the stored env API key (or Tencent Cloud
     permanent key from env vars as a fallback).
  3. Then execs the requested tcb command unchanged.

Usage (drop-in replacement for `tcb ...`):
  python pipeline/tcb.py db nosql execute -c '[...]' -e cloud1-xxxx
  python pipeline/tcb.py env apikey list -e cloud1-xxxx

Secrets (never committed; .workbuddy/ is git-ignored):
  .workbuddy/secrets/cloudbase_env_apikey.json -> {"apiKey": "...", "envId": "..."}
"""
import json
import os
import sys
import time
import subprocess

# ---- managed runtimes (no user env pollution) ----
NODE_EXE = r"C:\Users\admin\.workbuddy\binaries\node\versions\22.22.2\node.exe"
TCB_CLI = r"C:\Users\admin\.workbuddy\binaries\node\workspace\node_modules\@cloudbase\cli\bin\tcb"

AUTH_PATH = os.path.expanduser(r"~\.config\.cloudbase\auth.json")
SECRET_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".workbuddy", "secrets", "cloudbase_env_apikey.json"
)
CLOUDBASERC = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cloudbaserc.json"
)

BUFFER_SECONDS = int(os.environ.get("TCB_REFRESH_BUFFER", "600"))


def no_proxy_env():
    env = os.environ.copy()
    for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
              "ALL_PROXY", "all_proxy"]:
        env.pop(k, None)
    return env


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def credential_expired():
    auth = load_json(AUTH_PATH)
    if not auth:
        return True
    cred = auth.get("credential", {})
    exp = int(cred.get("tmpExpired") or cred.get("accessTokenExpired") or 0)
    if exp <= 0:
        return True
    return exp < int(time.time() * 1000) + BUFFER_SECONDS * 1000


def default_env_id():
    rc = load_json(CLOUDBASERC)
    return rc.get("envId") if rc else None


def ensure_login():
    # Already fresh? Nothing to do.
    if not credential_expired():
        return

    secret = load_json(SECRET_FILE)
    env_id = None
    api_key = None
    if secret:
        api_key = secret.get("apiKey")
        env_id = secret.get("envId") or default_env_id()

    # Preferred: CloudBase environment API key (auto-refreshing).
    if api_key and env_id:
        print("[tcb] credential expired/empty; re-login via CloudBase env API key",
              file=sys.stderr)
        rc = subprocess.run(
            [NODE_EXE, TCB_CLI, "login", "--cloudbase-api-key", api_key,
             "-e", env_id],
            env=no_proxy_env(),
        )
        if rc.returncode == 0:
            return
        print("[tcb] env API key login failed, falling back", file=sys.stderr)

    # Fallback: Tencent Cloud permanent key from env vars.
    sid = os.environ.get("TCB_SECRET_ID")
    skey = os.environ.get("TCB_SECRET_KEY")
    if sid and skey:
        print("[tcb] re-login via Tencent Cloud permanent key", file=sys.stderr)
        rc = subprocess.run(
            [NODE_EXE, TCB_CLI, "login", "--apiKeyId", sid, "--apiKey", skey],
            env=no_proxy_env(),
        )
        if rc.returncode == 0:
            return

    print(
        "[tcb] FATAL: no valid credential and no API key configured.\n"
        "       Bootstrap once:\n"
        "       1) tcb login  (one-time browser device authorization)\n"
        "       2) tcb env apikey create yifei-automation -e <envId>\n"
        "       3) save the returned ApiKey to .workbuddy/secrets/cloudbase_env_apikey.json\n"
        "          {\"apiKey\": \"<token>\", \"envId\": \"<envId>\"}\n"
        "       After that this wrapper self-renews and never needs a browser.",
        file=sys.stderr,
    )
    sys.exit(2)


def main():
    if len(sys.argv) < 2:
        print("usage: tcb.py <tcb args...>", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    # These subcommands do not need (and must not force) a fresh login.
    skip = {"--help", "-h", "--version", "-v", "login", "logout"}
    if args[0] in skip or "--help" in args:
        cmd = [NODE_EXE, TCB_CLI] + args
        rc = subprocess.run(cmd, env=no_proxy_env())
        sys.exit(rc.returncode)

    ensure_login()

    cmd = [NODE_EXE, TCB_CLI] + sys.argv[1:]
    rc = subprocess.run(cmd, env=no_proxy_env())
    sys.exit(rc.returncode)


if __name__ == "__main__":
    main()
