# Main To Home Import Status

Created: 2026-07-09
Status: completed

## Intended Action

Execute the quarantine-only import described in
`MAIN_TO_HOME_EVIDENCE_IMPORT_PLAN.md`.

Destination would be:

- `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/`

Final import destination:

- `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/`

## What Was Tried

Public Main route:

- `ssh root@155.212.227.115`
- Result: `Connection timed out`

TCP port check:

- `/dev/tcp/155.212.227.115/22`
- Result: closed or timeout

Ping:

- `ping 155.212.227.115`
- Result: 100% packet loss

Tailscale status on Home:

- `openclaw-vps` visible as `100.127.146.46`
- State: offline, last seen about 1 minute earlier during the check

Tailscale Main route:

- `ssh root@100.127.146.46`
- Result: `Connection timed out`

Retry:

- After a short wait, both public and Tailscale SSH routes were retried.
- Result: both still timed out.

## Current Conclusion

The initial import was blocked because Main was not reachable from Home over SSH.
After Stanislav checked Main from the source side, the route recovered:

- `openclaw-vps` became active in Tailscale.
- Tailnet port 22 opened.
- Tailscale SSH requested an additional check URL.
- Public SSH to `155.212.227.115` succeeded with the Home key.

The controlled import was then completed via public SSH.

## Import Result

- Destination: `/home/stanislav/.openclaw/workspace/transfers/main-server-evidence-20260709/`
- Data root: `root-openclaw-workspace/`
- Files copied: 808 regular files.
- Size: about 317M on disk.
- Manifest: `MANIFEST.tsv`, 808 lines.
- Checksums: `SHA256SUMS`, 808 lines.
- Verification: `sha256sum -c SHA256SUMS` passed.
- Command log: `SOURCE_COMMANDS.md`.

Excluded:

- `.git/`
- `node_modules/`
- `.env`
- `.env.*`
- `.cache/`
- `dist/.cache/`

Preserved paths include:

- `special-tech-astro/`
- `agents/main/website/spectech/`
- `knowledge/rewrite/`
- `tmp/alpha_hmi_libs_20260506/UMOSS_3/`
- `tmp_specialtechnology_calculator.html`
- `tmp_specialtechnology_calculator.js`

## Nothing Changed Outside Quarantine

- No Home working tree overwritten.
- No Main files, services, configs, or deploy targets changed.
- No live site deploy performed.

## Resume Steps

For the next work slice:

1. Compare live site vs Home `website/spectech` vs imported Main static tree.
2. Compare imported Main `special-tech-astro` against live/deploy archives.
3. Decide source-of-truth before any site edits.
