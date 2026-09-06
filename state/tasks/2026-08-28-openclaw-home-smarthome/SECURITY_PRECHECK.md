# SECURITY PRECHECK

- [x] Target and user intent are explicit.
- [x] Existing services are protected by a no-touch boundary.
- [x] Network/firewall/router changes are forbidden.
- [x] Secret will be generated and stored only on Home with mode 600.
- [x] Report/evidence must exclude secret values and private NAS contents.
- [x] NAS write scope is limited to `/mnt/synology/Documents/backups/smarthome/`.
- [x] External VPS work is out of scope.
- [x] Rollback is limited to the new compose project, new timer, and `/opt/smarthome` artifacts.
