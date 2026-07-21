# control-exec

The one deliberate exception to "the dashboard never writes." A dashboard
process needs a way to stop a runaway instance or pause a cron job — but it
must never get `docker.sock`, and it must never be able to run arbitrary
commands. `control-exec` is the narrow, allow-listed door for that: the
dashboard writes a request file, a host-side root process (this script,
never mounted into any instance container) is the only thing that acts on
it, through the instance's own `openclaw` CLI.

## Flow

```
<instance-dir>/control/
  command.json   # written by the dashboard, consumed (deleted) by control-exec
  log.jsonl      # append-only, written by control-exec: every attempt, accepted or not
  .processing    # transient lock file, present only while a request is running
```

1. Dashboard writes `command.json`, e.g.:
   ```json
   {"action": "stop_channel", "channel": "matrix", "requested_at": "...", "requested_by": "mue"}
   ```
2. A systemd path unit (`control-exec@<instance>.path`) watches for that
   file's existence via inotify and fires `control-exec@<instance>.service`.
3. `control_exec.py` validates the action against a fixed allow-list, runs
   the corresponding `openclaw` CLI call, appends the outcome to
   `log.jsonl`, and deletes `command.json` — accepted or refused, so a bad
   request can never re-trigger.

## Allowed actions

| action | effect | CLI call |
|---|---|---|
| `stop_channel` | disable a channel **live**, no gateway restart, keeps its config | `channels remove --channel <x>` |
| `resume_channel` | re-enable a previously stopped channel | `config set channels.<x>.enabled true` |
| `set_cron_enabled` | pause/resume a cron job | `cron edit <id> --enable\|--disable` |

Anything else is refused and logged, not silently ignored.

### Why `resume_channel` is `config set ... enabled true`, not `channels add`

`channels remove` (without `--delete`) only flips `<channel>.enabled` to
`false` — it does **not** erase `homeserver`/`userId`/credentials from
config. The exact inverse is flipping `enabled` back to `true`.

`channels add --channel matrix` looked like the obvious "re-add" call, but
in testing (CGR-55, 2026-07-21) it silently switched the account to
env-var-backed credential mode and **stripped `homeserver`/`userId` from
config** because the required `MATRIX_HOMESERVER`/`MATRIX_USER_ID` env vars
weren't present in the gateway's own `secrets/.env` — breaking the account
until those fields were restored by hand with `config set`. `config set
channels.<x>.enabled true` has none of that risk: it touches exactly one
field, hot-reloads without a restart, and relies on the credentials already
cached in the shared `state/openclaw.sqlite` (per openclaw's Matrix docs),
not on re-supplying them.

### Why commands need `y\n` piped on stdin

`channels remove`/`channels add` print an interactive confirmation prompt
regardless of TTY allocation; there is no `--yes`/`--force` flag. `run_cli`
disables pseudo-TTY allocation (`-T`) and feeds `"y\n"` on stdin
unconditionally — harmless for calls (like `config set`, `cron edit`) that
don't prompt at all.

## Install for an instance

```bash
sudo cp systemd/control-exec@.path systemd/control-exec@.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now control-exec@CGR-55.path
```

The `%i` instance name must match the instance's directory name under
`/opt/continuants/instances/`.

Test manually before relying on the path unit:

```bash
echo '{"action": "stop_channel", "channel": "matrix"}' > /opt/continuants/instances/CGR-55/control/command.json
python3 control_exec.py --instance-dir /opt/continuants/instances/CGR-55
```

## Permissions

`<instance-dir>/control/` must be `root:10001` (the dashboard's fixed GID,
same convention as `body/dashboard`'s README), `chmod 770` — this is the
**only** directory a dashboard container is allowed to write into.
`log.jsonl` itself: `root:10001`, `chmod 660`.

`control-exec` runs as root (it edits config/cron state the instance's own
container user must not touch directly, and it shells out to `docker
compose`), same posture as `tools/audit-tap`.
