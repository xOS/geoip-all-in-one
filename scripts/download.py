"""
Download GeoIP sources defined in sources.yaml
"""

import gzip
import os
import sys
from datetime import datetime

import requests
import yaml


def log(msg):
    """Print timestamped log message."""
    print(f"[{datetime.now().isoformat()}] {msg}", file=sys.stderr)


def download_file(url, dest_path, decompress_gzip=False):
    """Download file from URL with optional gzip decompression."""
    if not url:
        log(f"⊘ Skipping (no URL): {dest_path}")
        return -1

    log(f"⬇ Downloading: {url}")
    try:
        resp = requests.get(url, stream=True, timeout=300)

        if resp.status_code != 200:
            log(f"✗ Failed ({resp.status_code}): {url}")
            return resp.status_code

        if decompress_gzip:
            compressed = bytearray()
            for chunk in resp.iter_content(chunk_size=8192):
                compressed.extend(chunk)
            data = gzip.decompress(bytes(compressed))
            with open(dest_path, 'wb') as f:
                f.write(data)
        else:
            with open(dest_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)

        log(f"✓ Saved: {dest_path}")
        return 200
    except Exception as e:
        log(f"✗ Error: {e}")
        return -1


def main():
    if len(sys.argv) != 4:
        print("Usage: download.py <sources.yaml> <ipv4|ipv6> <output_dir>", file=sys.stderr)
        sys.exit(1)

    sources_file = sys.argv[1]
    ip_version = sys.argv[2]
    output_dir = sys.argv[3]

    if ip_version not in ('ipv4', 'ipv6'):
        log(f"Error: Invalid IP version '{ip_version}'")
        sys.exit(1)

    with open(sources_file) as f:
        sources = yaml.safe_load(f)

    os.makedirs(output_dir, exist_ok=True)
    failed = []

    for section in ('latlong', 'country', 'asn'):
        log(f"Downloading {ip_version} {section} sources...")
        for name, info in sources.get(section, {}).items():
            url = info.get(ip_version, '')
            ext = 'csv' if info.get('format') == 'decimal_csv' else 'tsv'
            dest = os.path.join(output_dir, f"{name}.{ext}")
            decompress_gzip = url.endswith('.gz')
            status = download_file(url, dest, decompress_gzip=decompress_gzip)
            if status != 200:
                failed.append((name, status))

    if failed:
        log(f"Failed downloads: {len(failed)}")
        for name, status in failed:
            log(f"  {name}: HTTP {status}")
        sys.exit(1)

    log("Download complete!")


if __name__ == '__main__':
    main()
