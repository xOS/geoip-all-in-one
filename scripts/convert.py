"""
Convert merged TSV to lightweight MMDB (country + ASN/ORG only).
Optimal for quick lookups with minimal database size.
"""

import sys

import netaddr
from mmdb_writer import MMDBWriter


def int_to_ip(num, ipv6=False):
    """Convert integer to IP address object."""
    if ipv6:
        return netaddr.IPAddress(num, version=6)
    return netaddr.IPAddress(num, version=4)


def lite_key(parts):
    """Extract deduplication key for lite profile (country + ASN + ORG)."""
    country_code = parts[2]
    asn = parts[5].strip() if len(parts) > 5 else ''
    org = parts[6].strip() if len(parts) > 6 else ''
    return (country_code, asn, org)


def build_record(parts):
    """Build MMDB record with country, ASN, and ORG fields."""
    country_code = parts[2]
    data = {'country': {'iso_code': country_code}}

    if len(parts) > 5 and parts[5].strip():
        try:
            data['autonomous_system_number'] = int(parts[5].strip())
        except ValueError:
            pass

    if len(parts) > 6 and parts[6].strip():
        data['autonomous_system_organization'] = parts[6].strip()

    return data


def process_file(input_file, writer, ipv6=False):
    """Process TSV file with range merging for lite profile."""
    count = 0
    pending_start = None
    pending_end = None
    pending_key = None
    pending_parts = None

    def flush_pending():
        nonlocal count, pending_start, pending_end, pending_key, pending_parts
        if pending_parts is None:
            return

        start_ip = int_to_ip(pending_start, ipv6)
        end_ip = int_to_ip(pending_end, ipv6)
        ip_range = netaddr.IPRange(start_ip, end_ip)
        ip_set = netaddr.IPSet(ip_range)
        data = build_record(pending_parts)
        writer.insert_network(ip_set, data)
        count += 1

        pending_start = None
        pending_end = None
        pending_key = None
        pending_parts = None

    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split('\t')
            if len(parts) < 3:
                continue

            try:
                start_hex = parts[0]
                end_hex = parts[1]
                start_num = int(start_hex, 16)
                end_num = int(end_hex, 16)
                key = lite_key(parts)

                if pending_parts is None:
                    pending_start = start_num
                    pending_end = end_num
                    pending_key = key
                    pending_parts = parts
                elif key == pending_key and start_num == pending_end + 1:
                    # Adjacent range with same key - merge
                    pending_end = end_num
                else:
                    # Key changed or gap detected - flush previous and start new
                    flush_pending()
                    pending_start = start_num
                    pending_end = end_num
                    pending_key = key
                    pending_parts = parts

            except Exception as e:
                print(f"Error on line {line_num}: {e}", file=sys.stderr)
                continue

            if line_num % 100000 == 0:
                print(f"  Processed {line_num} lines...", file=sys.stderr)

    flush_pending()
    return count


def main():
    if len(sys.argv) != 4:
        print("Usage: convert.py <ipv4.tsv> <ipv6.tsv> <output.mmdb>", file=sys.stderr)
        sys.exit(1)

    ipv4_file = sys.argv[1]
    ipv6_file = sys.argv[2]
    output_file = sys.argv[3]

    writer = MMDBWriter(ip_version=6, ipv4_compatible=True, database_type='GeoIP2-Country-ASN')

    print(f"Processing {ipv4_file} (IPv4)...", file=sys.stderr)
    count4 = process_file(ipv4_file, writer, ipv6=False)

    print(f"Processing {ipv6_file} (IPv6)...", file=sys.stderr)
    count6 = process_file(ipv6_file, writer, ipv6=True)

    total = count4 + count6
    print(
        f"Writing {total} entries ({count4} IPv4, {count6} IPv6) to {output_file}...",
        file=sys.stderr,
    )
    writer.to_db_file(output_file)
    print(f"Done! Created {output_file}", file=sys.stderr)


if __name__ == '__main__':
    main()
