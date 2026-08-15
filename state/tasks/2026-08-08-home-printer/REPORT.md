# Home printer setup report

Date: 2026-08-08

## Result

- Printer: Pantum CP1100 connected by USB to Synology S218.
- Synology queue: `ipp://192.168.68.103:631/printers/usbprinter1`.
- Home queue: `Pantum_CP1100`.
- Default media: A4.
- Home queue is the system default, accepting jobs, enabled, idle, color-capable,
  and shared to the local network through CUPS on TCP 631.
- Remote-printer discovery is disabled on Home to prevent duplicate temporary
  queues; local publishing remains enabled through DNS-SD.
- `cups-browsed` is disabled because it created duplicate queues for the same
  Synology printer.

## Driver

- Official Pantum package: `pantum 1.1.100-1`.
- Download SHA-256:
  `569272558aa9602678288f1217a6f8e4b802493d7a8c34ac8d8f4deb562710fc`.
- The CP1100 PPD uses the vendor `ptps` PDF filter. Its runtime libraries resolve
  successfully on Ubuntu 24.04.
- The package's unnecessary local USB/IPP hook was removed because the printer is
  attached to Synology, not Home.

## Verification

- CUPS scheduler active and enabled.
- Only the persistent `Pantum_CP1100` queue remains.
- IPP endpoint on Home responds at
  `ipp://192.168.68.125:631/printers/Pantum_CP1100`.
- Test job `Pantum_CP1100-2` completed in both Home and Synology queues.
- Physical page appearance still requires user confirmation.

## Rollback

- CUPS backup: `cups-backup-20260808-114216.tar.gz`.
- Pre-change queue status: `lpstat-before.txt`.
- Pre-change `printers.conf`: `printers.conf.before`.
- Remove the vendor package with `sudo apt remove pantum` only if rollback is
  explicitly requested; restore the CUPS archive after stopping CUPS.
