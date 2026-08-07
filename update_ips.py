import urllib.request
import json

# ASNs של Disney / BAMTECH
ASNS = [
    "AS13649",  # Disney Streaming Services (BAMTECH)
    "AS396032"  # Disney Infrastructure
]

def fetch_asn_prefixes(asn):
    prefixes = set()
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            prefixes_list = data.get('data', {}).get('prefixes', [])
            for item in prefixes_list:
                prefix = item.get('prefix')
                if prefix and ':' not in prefix:  # IPv4 בלבד
                    prefixes.add(prefix)
    except Exception as e:
        print(f"Error fetching prefixes for {asn}: {e}")
    return prefixes

def main():
    all_ips = set()
    
    for asn in ASNS:
        print(f"Fetching IP ranges for {asn}...")
        prefixes = fetch_asn_prefixes(asn)
        print(f"  -> Found {len(prefixes)} IPv4 prefixes for {asn}")
        all_ips.update(prefixes)

    print(f"\nWriting total of {len(all_ips)} unique prefixes to disney_ips.txt")
    with open("disney_ips.txt", "w") as f:
        for ip in sorted(all_ips):
            f.write(f"{ip}\n")

if __name__ == "__main__":
    main()
