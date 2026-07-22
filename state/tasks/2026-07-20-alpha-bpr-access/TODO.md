# Alpha BPR Access Switch - 2026-07-20

## Goal

Move public Alpha BPR demo access away from retired Main VPS `155.212.227.115`.

## Checklist

- [x] Confirm old Main URL times out.
- [x] Confirm Home Alpha BPR local services are healthy.
- [x] Find a working public route that does not depend on Main.
- [x] Stop/disable stale Main reverse tunnel.
- [x] Verify new public HTTP URL.
- [x] Verify new public HTTPS URL.
- [x] Report the replacement URL to Stanislav.

## Current Candidate

- `http://alpha-bpr.31.10.95.23.sslip.io/alpha-bpr-hmi/`
- `https://alpha-bpr.31.10.95.23.sslip.io/alpha-bpr-hmi/`

Notes: HTTPS currently uses the Home nginx certificate; HTTP avoids browser
certificate warnings. The old Main route is
`https://alpha-bpr.155.212.227.115.sslip.io/alpha-bpr-hmi/`.

## Verification

- 14:48 MSK: `alpha-bpr-vps-reverse-tunnel.service` is `inactive (dead)` and
  `disabled`.
- 14:48 MSK: HTTP UI returned `200`, `186356` bytes, remote `31.10.95.23`.
- 14:48 MSK: HTTP `/readyz` returned `200`.
- 14:48 MSK: HTTP `/api/demo/recipe-workbench` returned `200`.
- 14:48 MSK: HTTPS UI, `/readyz`, and `/api/demo/recipe-workbench` returned
  `200` with `curl -k`.
