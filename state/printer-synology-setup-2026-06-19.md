# Synology Printer Sharing Setup - 2026-06-19

Goal: make the printer connected to Synology available from devices in the home network across common OSes.

## Checklist

- [x] Identify printer as seen by Synology
- [x] Identify existing print services and ports
- [x] Choose sharing method for Windows/macOS/Linux/iOS/Android
- [x] Configure only the minimum required services
- [x] Verify discovery and direct connection URLs from the LAN
- [ ] Report final connection details

## Notes

- Synology host: `S218` / `192.168.68.103`
- Access path: SSH `openclaw-admin@192.168.68.103 -p 2222`
- Root-level Synology changes are allowed for this task by Stanislav's Telegram request on 2026-06-19 18:18 MSK.
- Printer configured: Pantum CP1100 series, CUPS queue `usbprinter1`
- Primary IPP URL: `ipp://192.168.68.103:631/printers/usbprinter1`
- LPR queue: host `192.168.68.103`, queue `usbprinter1`
- Bonjour/AirPrint-style name: `Pantum CP1100 @ S218`
- Synology services active after setup: `cupsd`, `cups-lpd.socket`, `avahi`
- Persistence: enabled `openclaw-printer-share.service` on Synology; script at `/usr/local/sbin/openclaw-printer-share.sh`
- Backup made on Synology: `/root/openclaw-printer-backup-20260619-182240`
- Local `openclaw-home` CUPS queue `homeprinter` now points to the same Synology IPP URL instead of stale `socket://192.168.68.103:9100`

## Verification

- `192.168.68.103:631` open, returns `HTTP/1.1 200 OK` for `/printers/usbprinter1`
- `192.168.68.103:515` open for LPR
- `192.168.68.103:9100` closed; not used
- `avahi-browse` sees `Pantum CP1100 @ S218` as `_ipp._tcp` and `_printer._tcp`
- `lpstat` on Synology: `printer usbprinter1 is idle` and enabled

## Caveat

The CUPS queue is restored and network-visible, but no physical test page was printed yet. If a real print job fails, first check that the USB cable/power path between Pantum and Synology is live; earlier low-level USB enumeration did not show a currently attached non-hub USB device even though the saved DSM printer profile exists.
