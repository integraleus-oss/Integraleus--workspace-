# AppArmor change: local Codex bubblewrap

## Target

- Installed profile: `/etc/apparmor.d/bwrap`
- Executable: `/usr/bin/bwrap`
- Global user-namespace restriction remains enabled.

## Reason

Local Codex workspace-write runs fail before tool execution because Ubuntu's
generic `unprivileged_userns` profile denies `setpcap` and `net_admin` needed
by bubblewrap to construct its sandbox namespace.

## Apply

1. Validate staged profile with `apparmor_parser`.
2. Install staged profile as `/etc/apparmor.d/bwrap` with root ownership and
   mode `0644`.
3. Load/replace the profile with `apparmor_parser -r`.
4. Verify `aa-status`, a direct bubblewrap probe, and local Codex read/write
   probes.

## Rollback

1. Unload the profile:
   `sudo apparmor_parser -R /etc/apparmor.d/bwrap`
2. Move `/etc/apparmor.d/bwrap` out of `/etc/apparmor.d/` to the task evidence
   folder or delete it only with explicit intent.
3. Confirm `/usr/bin/bwrap` again transitions to the generic restricted
   profile and that `kernel.apparmor_restrict_unprivileged_userns` remains `1`.

## Safety boundary

This does not disable AppArmor, change the global userns sysctl, alter Gateway,
or grant Codex `--danger`. Bubblewrap continues to enforce Codex's namespace,
filesystem, and process sandbox; AppArmor only permits bubblewrap to create the
namespace.
