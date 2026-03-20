# GeoIP Country MMDB

A lightweight, production-ready GeoIP database optimized for quick IP lookups. This project automatically merges multiple open-source GeoIP data sources and outputs a single MMDB file containing country codes, ASN, and organization information.

**Weekly automated builds** with the latest GeoIP data.

---

## Features

- 🚀 **Lightweight**: ~18MB for global IPv4 + IPv6 coverage
- 🌐 **Country Codes**: ISO 3166-1 alpha-2 format
- 🔢 **ASN Data**: ~95% coverage for IPv4, ~90% for IPv6
- 🏢 **Organization Names**: Mappings from ASN to organization
- 📈 **Multi-source Voting**: Combines 6 authoritative sources for accuracy
- 🔄 **Automated Updates**: Weekly releases via GitHub Actions

---

## Quick Start

### Download

Get the latest `country.mmdb` from [Releases](../../releases).

### Usage

```python
import maxminddb

with maxminddb.open_database('country.mmdb') as reader:
    data = reader.get('99.109.53.30')
    print(data)
    # Output:
    # {
    #     'country': {'iso_code': 'US'},
    #     'autonomous_system_number': 7018,
    #     'autonomous_system_organization': 'ATT-INTERNET4'
    # }
```

---

## Data Sources

### Country Voting (6 sources)

Used to determine the authoritative country for each IP range:

1. **IP2Location LITE** - Commercial geolocation database
   - Coverage: Global
   - Update frequency: Monthly
   - Source: https://lite.ip2location.com

2. **Geo-WHOIS-ASN-Country** - Official RIR WHOIS data
   - Coverage: High accuracy, lower coverage
   - Update frequency: Weekly
   - Source: Regional Internet Registries (AFRINIC, APNIC, ARIN, LACNIC, RIPE NCC)

3. **DB-IP LITE** - Dedicated geolocation database
   - Coverage: Global  
   - Update frequency: Monthly
   - Source: https://db-ip.com

4. **GeoLite2** - MaxMind free geolocation database
   - Coverage: Comprehensive
   - Update frequency: Monthly
   - Source: https://www.maxmind.com

5. **IPinfo Country** - IPinfo.io geolocation data
   - Coverage: Global
   - Update frequency: Weekly
   - Source: https://ipinfo.io

6. **IPlocate** - IPlocate geolocation data
   - Coverage: Global
   - Update frequency: Monthly
   - Source: https://iplocate.io

### ASN/Organization (Primary)

**IPtoASN** - Authoritative ASN-to-organization mapping
- Format: TSV with start/end IPs, ASN, country, organization
- Coverage: ~95% IPv4, ~90% IPv6
- Update frequency: Daily
- Source: https://iptoasn.com

---

## Build Process

### Prerequisites

```bash
# Python 3.11+
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate
```

### Build Steps

```bash
# Install dependencies
make deps

# Download all data sources
make download

# Merge data with voting algorithm
make merge

# Build MMDB
make build
```

### Output

- `country.mmdb` - Final database file (~18MB)
- `merged_ipv4.tsv` - Intermediate merged data
- `merged_ipv6.tsv` - Intermediate merged data

---

## Merge Algorithm

The merge process uses a multi-stage voting algorithm:

1. **Country Voting** (6 sources)
   - Each IP range receives votes from 6 country sources
   - Highest vote count wins
   - Tie-breaking: Uses configured priority order

2. **ASN/Organization Extraction**
   - Primary source: IPtoASN.com
   - Fallback: WHOIS data (if available from voting results)
   - Normalization: Handles missing values, invalid entries

3. **Range Merging** (Lite Profile)
   - Adjacent IP ranges with identical (country, ASN, ORG) are merged
   - Reduces database size by ~73% (8.07M → 1.09M ranges)
   - No precision loss for retained fields

---

## Database Schema

### Record Format

```json
{
  "country": {
    "iso_code": "US"  // 2-letter ISO 3166-1 alpha-2
  },
  "autonomous_system_number": 7018,  // 32-bit integer
  "autonomous_system_organization": "ATT-INTERNET4"  // String
}
```

### Database Metadata

- **Type**: MaxMind MMDB v2.0
- **Database Type**: GeoIP2-Country-ASN
- **IP Version**: 6 (includes IPv4-compatible)
- **Total Ranges**: ~1.09M (IPv4 + IPv6 combined)

---

## GitHub Actions Workflow

Automated builds run on:

- **Schedule**: Weekly (Wednesday 03:00 UTC)
- **Push**: On every commit to `main` branch
- **Manual**: Available via `workflow_dispatch`

Releases are automatically created with:
- Release notes
- Database file
- Metadata (size, build time)

Older releases (> 3) are automatically cleaned up.

---

## File Comparison

| Aspect | City MMDB | Country MMDB (Lite) |
|--------|-----------|---------------------|
| Size | 106 MB | 18 MB |
| IPv4 Ranges | 8.07M | 635K |
| IPv6 Ranges | 3.94M | 454K |
| Country | ✓ | ✓ |
| Coordinates | ✓ | ✗ |
| Timezone | ✓ | ✗ |
| ASN | ✓ | ✓ |
| Organization | ✓ | ✓ |
| Use Case | Full geolocation | IP origin/routing |

---

## Licenses & Attribution

### Geolocation Data

| Source | License | Attribution |
|--------|---------|-------------|
| IP2Location LITE | CC BY 4.0 | [IP2Location](https://lite.ip2location.com) |
| GeoLite2 | CC BY 4.0 | [MaxMind](https://www.maxmind.com) |
| DB-IP Lite | CC BY 4.0 | [DB-IP](https://db-ip.com) |
| IPtoASN | CC BY 4.0 | [IPtoASN](https://iptoasn.com) |
| RIR WHOIS | Public | [RIRs](https://www.apnic.net/) |

### Code

This project is open source. All contributions welcome.

---

## Links

- 📦 [Latest Release](../../releases)
- 📋 [License](LICENSE)
- 🐛 [Issues](../../issues)
- 📝 [Changelog](../../releases)
