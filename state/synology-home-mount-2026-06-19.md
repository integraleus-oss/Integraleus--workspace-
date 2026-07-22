# Synology Mount On Home - 2026-06-19

## Goal

Connect Synology storage to the Home server for stable local access.

## Checklist

- [x] Inspect current Home hostname, mounts, `/etc/fstab`, and NFS tools.
- [x] Inspect Synology reachability and exported NFS shares without changing Synology.
- [x] Choose mount point(s) and protocol.
- [x] Mount now.
- [x] Add persistent automount entry if needed.
- [x] Verify read/list access without exposing file contents.
- [x] Record final connection details.

## Notes

- Synology data must not leave the home network.
- Avoid Synology root-level changes unless Stanislav explicitly asks for them.

## Result

- Home server: `openclaw-home` (`192.168.68.125`).
- Synology: `S218` (`192.168.68.103`).
- Protocol: NFS v3 over LAN.
- Synology changes: none.
- `/etc/fstab` backup before changes: `/etc/fstab.openclaw-synology-20260619-1849.bak`.
- Persistent mount target: `/mnt/synology`.

Mounted shares:

- `/mnt/synology/Documents` -> `192.168.68.103:/volume1/Documents`
- `/mnt/synology/video` -> `192.168.68.103:/volume1/video`
- `/mnt/synology/music` -> `192.168.68.103:/volume1/music`
- `/mnt/synology/homes` -> `192.168.68.103:/volume1/homes`
- `/mnt/synology/surveillance` -> `192.168.68.103:/volume1/surveillance`
- `/mnt/synology/PlexMediaServer` -> `192.168.68.103:/volume1/PlexMediaServer`
- `/mnt/synology/Lost` -> `192.168.68.103:/volume1/Lost`

Verification:

- `ping 192.168.68.103` OK.
- TCP ports `2049` and `111` reachable.
- `showmount -e 192.168.68.103` lists the seven shares above for `192.168.68.125`.
- `sudo mount -av -t nfs,nfs4` reports all Synology entries as `already mounted`.
- `findmnt -t nfs,nfs4` shows all seven Synology mounts.
- `remote-fs.target` is `active` and `enabled`.
- `sudo findmnt --verify --verbose` reports 0 parse errors and 0 errors; the remaining warning is the pre-existing swap `/swap.img` line, not Synology.

## Exchange Folder

Stanislav clarified that Synology will be used as the local file-transfer layer between Home and his PC.

Created:

- `/mnt/synology/Documents/OpenClawExchange`
- `/mnt/synology/Documents/OpenClawExchange/README.md`

Use this folder for local files that should move between the PC and Home while staying inside the home network.
