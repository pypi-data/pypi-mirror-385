# ASNDB

[![Python Version](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org) ![PyPI - Version](https://img.shields.io/pypi/v/asndb) [![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/blacklanternsecurity/radixtarget/blob/master/LICENSE) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff) [![Tests](https://github.com/blacklanternsecurity/asndb/actions/workflows/tests.yml/badge.svg)](https://github.com/blacklanternsecurity/asndb/actions/workflows/tests.yml)

A simple Python CLI + library for instant lookup of ASN data by IP address, AS number, or organization. Uses BBOT.IO API (`asndb.api.bbot.io`).

ASNs are automatically cached for instant lookups and minimal network traffic.

## Installation

```
pip install asndb

# or using uv
uv add asndb
```

## Usage (CLI)

Note: To avoid rate limits, export your BBOT.IO API key as an environment variable:
```bash
export BBOT_IO_API_KEY=<your_api_key>
```

### IP Lookup
```bash
asndb ip 1.1.1.1
```

Output:
```json
{
  "asn": 13335,
  "asn_name": "CLOUDFLARENET",
  "country": "US",
  "ip": "1.1.1.1",
  "org": "Cloudflare, Inc.",
  "org_id": "CLOUD14-ARIN",
  "rir": "ARIN",
  "subnets": [
    "1.0.0.0/24",
    "1.0.1.0/24"
  ]
}
```

### AS Number Lookup

```bash
asndb asn 13335
```

Output:
```json
{
  "asn": 13335,
  "asn_name": "CLOUDFLARENET",
  "country": "US",
  "ip": "1.1.1.1",
  "org": "Cloudflare, Inc.",
  "org_id": "CLOUD14-ARIN",
  "rir": "ARIN",
  "subnets": [
    "1.0.0.0/24",
    "1.0.1.0/24"
  ]
}
```

### Organization Lookup

```bash
# Look up an organization
asndb org CLOUD14-ARIN
```

Output:
```json
{
  "asns": [
    13335,
    14789,
    395747,
    394536
  ]
}
```

### CLI Help

```
$ uv run asndb --help
                                                                                              
 Usage: asndb [OPTIONS] COMMAND [ARGS]...                                                     
                                                                                              
╭─ Options ──────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                    │
│ --show-completion             Show completion for the current shell, to copy it or         │
│                               customize the installation.                                  │
│ --help                        Show this message and exit.                                  │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ─────────────────────────────────────────────────────────────────────────────────╮
│ ip    Lookup ASN by IP address                                                             │
│ asn   Lookup ASN by AS number                                                              │
│ org   Get all the ASNs for an organization, by its registered organization ID, e.g.        │
│       GOGL-ARIN                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────╯
```

## Usage (Python)

```python
from asndb import ASNDB

# Create a new ASNDB client
asndb = ASNDB()


# Look up an IP address
asn = asndb.lookup_ip_sync("1.1.1.1")
# {
#   "asn": 13335,
#   "asn_name": "CLOUDFLARENET",
#   "country": "US",
#   "ip": "1.1.1.1",
#   "org": "Cloudflare, Inc.",
#   "org_id": "CLOUD14-ARIN",
#   "rir": "ARIN",
#   "subnets": [
#     "1.0.0.0/24",
#     "1.0.1.0/24"
#   ]
# }

# Look up an AS number
asn = asndb.lookup_asn_sync(13335)
# {
#   "asn": 13335,
#   "asn_name": "CLOUDFLARENET",
#   "country": "US",
#   "ip": "1.1.1.1",
#   "org": "Cloudflare, Inc.",
#   "org_id": "CLOUD14-ARIN",
#   "rir": "ARIN",
#   "subnets": [
#     "1.0.0.0/24",
#     "1.0.1.0/24"
#   ]
# }

# Look up an organization
org = asndb.lookup_org_sync("CLOUD14-ARIN")
# {
#   "asns": [
#     13335,
#     14789,
#     395747,
#     394536
#   ]
# }
```

## Environment Variables

You can customize the behavior of the ASNDB client by exporting the following environment variables:

- `BBOT_IO_API_KEY`: Your BBOT.IO API key.
- `ASNDB_BASE_URL`: The base URL of the ASNDB API (default: https://asndb.api.bbot.io/v1).
- `ASNDB_TIMEOUT`: The timeout for the ASNDB API requests (default: 60 seconds).
- `ASNDB_CACHE_SIZE`: The size of the cache for the ASNDB API requests (default: 10000).
