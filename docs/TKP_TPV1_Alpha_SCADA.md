# Commercial Proposal — Alpha SCADA for TPV1

**Date:** 2026-03-11
**Tariff year:** 2026
**Status:** Preliminary (TPV1 only; TPV3 to be added upon receipt of data)

---

## 1. Confirmed Input Data

| Parameter | Value |
|---|---|
| Facility | TPV1 |
| I/O Points | 300 total: DI=130, DO=50, AI=100, AO=20 |
| Protocol | Siemens S7 Communication (S7-1200 CPUs, Ethernet/TCP/IP over fiber) |
| Server configuration | Single server, no redundancy |
| Operator workstations | 1 (Full client, laptop AWS) |
| Remote/WEB access | Not required |
| Data logging (Historian) | Yes — 1 year retention, scan rate 200–500 ms |
| Reports | Daily summaries, alarm reports, trend reports; Excel export |
| License type | Perpetual (no updates required) |
| Technical support | Quotations for Basic/Standard/Extended + separate 5-year quotation |
| Timeline | 1 month |

---

## 2. Tag Calculation

**Mode:** signals_only
**Information power level:** medium

| Signal | Count | Coefficient | Tags |
|---|---|---|---|
| DI | 130 | ×2 | 260 |
| DO | 50 | ×5 | 250 |
| AI | 100 | ×10 | 1 000 |
| AO | 20 | ×1 | 20 |
| **Total** | **300** | | **1 530** |

**Selected tier:** 3 000 tags (nearest upper step)

---

## 3. Option A — Alpha.One+ (Recommended)

Best fit for this architecture: single server, single client, no redundancy, <50k tags.

| # | SKU | Description | Qty |
|---|---|---|---|
| 1 | ONE-N3k | Alpha.One+, 3 000 tags | 1 |
| 2 | DRV-PACK-INDUSTRY | Driver pack (S7, BACnet, Ethernet/IP, FINS, RP 570) | 1 |
| 3 | HIST-S2k | Alpha.Historian, 2 000 tags | 1 |
| 4 | RPT-E2k | Alpha.Reports Pro, 2 000 tags | 1 |
| 5 | RPT-CL1 | Alpha.Reports Client, 1 user | 1 |

### Total licenses (excl. VAT): 2 275 900 ₽

### Technical Support Options (Option A)

**Default support period = 1 year. BASE level is included in perpetual license at no additional cost.**

#### Per year (excl. VAT):

| Level | Description | Annual cost |
|---|---|---|
| BASE (Basic) | Perpetual license, included | 0 ₽ |
| STD (Standard) | Updates + remote support, business hours | 227 590 ₽ |
| OPT (Extended) | Updates + priority support, guaranteed response time | 341 385 ₽ |
| PRM (Premium) | Updates + premium priority support | 568 975 ₽ |

#### 5-year support (excl. VAT):

| Level | 5-year total | VAT 22% | 5-year total incl. VAT |
|---|---|---|---|
| BASE | 0 ₽ | 0 ₽ | 0 ₽ |
| STD | 1 137 950 ₽ | 250 349 ₽ | 1 388 299 ₽ |
| OPT | 1 706 925 ₽ | 375 524 ₽ | 2 082 449 ₽ |
| PRM | 2 844 875 ₽ | 625 872 ₽ | 3 470 747 ₽ |

### Total Payable — Option A

| Component | BASE | STD (1 yr) | OPT (1 yr) | PRM (1 yr) |
|---|---|---|---|---|
| Licenses (excl. VAT) | 2 275 900 | 2 275 900 | 2 275 900 | 2 275 900 |
| SLA (excl. VAT) | 0 | 227 590 | 341 385 | 568 975 |
| VAT 22% on SLA | 0 | 50 070 | 75 105 | 125 175 |
| SLA (incl. VAT) | 0 | 277 660 | 416 490 | 694 150 |
| **Total payable** | **2 275 900** | **2 553 560** | **2 692 390** | **2 970 050** |
| incl. VAT 22% | 0 | 50 070 | 75 105 | 125 175 |

---

## 4. Option B — Alpha.SCADA (Scalable)

Better scalability: supports additional clients, WEB access, and server redundancy if needed in the future.

| # | SKU | Description | Qty |
|---|---|---|---|
| 1 | SCADA-SRV3k | Alpha.SCADA, 3 000 tags | 1 |
| 2 | CL-F | Full client | 1 |
| 3 | DRV-PACK-INDUSTRY | Driver pack (S7, BACnet, Ethernet/IP, FINS, RP 570) | 1 |
| 4 | HIST-S2k | Alpha.Historian, 2 000 tags | 1 |
| 5 | RPT-E2k | Alpha.Reports Pro, 2 000 tags | 1 |
| 6 | RPT-CL1 | Alpha.Reports Client, 1 user | 1 |

### Total licenses (excl. VAT): 2 635 700 ₽

### Technical Support Options (Option B)

#### Per year (excl. VAT):

| Level | Description | Annual cost |
|---|---|---|
| BASE (Basic) | Perpetual license, included | 0 ₽ |
| STD (Standard) | Updates + remote support, business hours | 263 570 ₽ |
| OPT (Extended) | Updates + priority support, guaranteed response time | 395 355 ₽ |
| PRM (Premium) | Updates + premium priority support | 658 925 ₽ |

#### 5-year support (excl. VAT):

| Level | 5-year total | VAT 22% | 5-year total incl. VAT |
|---|---|---|---|
| BASE | 0 ₽ | 0 ₽ | 0 ₽ |
| STD | 1 317 850 ₽ | 289 927 ₽ | 1 607 777 ₽ |
| OPT | 1 976 775 ₽ | 434 891 ₽ | 2 411 666 ₽ |
| PRM | 3 294 625 ₽ | 724 817 ₽ | 4 019 442 ₽ |

### Total Payable — Option B

| Component | BASE | STD (1 yr) | OPT (1 yr) | PRM (1 yr) |
|---|---|---|---|---|
| Licenses (excl. VAT) | 2 635 700 | 2 635 700 | 2 635 700 | 2 635 700 |
| SLA (excl. VAT) | 0 | 263 570 | 395 355 | 658 925 |
| VAT 22% on SLA | 0 | 57 985 | 86 978 | 144 964 |
| SLA (incl. VAT) | 0 | 321 555 | 482 333 | 803 889 |
| **Total payable** | **2 635 700** | **2 957 255** | **3 118 033** | **3 439 589** |
| incl. VAT 22% | 0 | 57 985 | 86 978 | 144 964 |

---

## 5. What's Included

- Perpetual software licenses (no expiration)
- Siemens S7 Communication driver (native support for S7-1200 CPUs)
- Built-in trending and alarm management
- Data historian with configurable scan rate (200–500 ms supported)
- Report generation with Excel export
- BASE technical support (lifetime, included in license cost)

## 6. What's NOT Included

- Hardware (server, workstation, network equipment)
- Project development / configuration / commissioning services
- On-site engineering
- Training (available separately, see training catalog)
- TPV3 licensing (to be quoted separately upon receipt of I/O data)

---

## 7. TPV3 Compatibility Estimate

Without confirmed I/O data, a rough estimate for TPV3:
- If similar scale (~300 I/O, same architecture) → additional server upgrade license (SCADA-SRV-UP or ONE-N-UP) + Historian upgrade
- Approximate additional cost: **30–50% of the server license component**
- Driver pack (DRV-PACK-INDUSTRY) and Reports licenses are reusable across the system
- Detailed quotation will be provided within 3–5 days upon receipt of TPV3 data

---

## 8. Assumptions & Open Items

1. Information power level = **medium** (standard for industrial SCADA with S7-1200 PLCs and significant analog I/O)
2. Historian sized to cover **all tags** (1 530 → tier 2 000)
3. Reports sized to cover **all tags** (1 530 → tier 2 000) — can be reduced if reporting is needed for a subset only
4. SLA mapping: Basic → BASE (free), Standard → STD (10%), Extended → OPT (15%); PRM (25%) shown as additional option
5. VAT 22% applied to SLA only (licenses are shown excl. VAT)
6. Single-server configuration confirmed — no redundancy costs

---

**Pricing calculated per 2026 tariff.**
