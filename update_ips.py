import urllib.request
import json
import re

# ASNs של Disney+ / BAMGRID / Disney Direct-to-Consumer
ASNS = [
    "AS3223",   # Disney Direct-to-Consumer & International
]

def fetch_asn_prefixes(asn):
    prefixes = set()
    # שימוש ב-API של BGPView לשליפת טווחי ה-IP של ה-ASN
    url = f"https://api.bgpview.io/asn/{asn}/prefixes"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            ipv4_prefixes = data.get('data', {}).get('ipv4_prefixes', [])
            for item in ipv4_prefixes:
                prefix = item.get('prefix')
                if prefix:
                    prefixes.add(prefix)
    except Exception as e:
        print(f"Error fetching prefixes for {asn}: {e}")
    return prefixes

def main():
    all_ips = set()
    
    for asn in ASNS:
        print(f"Fetching IP ranges for {asn}...")
        prefixes = fetch_asn_prefixes(asn)
        all_ips.update(prefixes)

    # שמירת הרשימה לקובץ
    with open("disney_ips.txt", "w") as f:
        for ip in sorted(all_ips):
            f.write(f"{ip}\n")
            
    print(f"Total prefixes fetched: {len(all_ips)}")

if __name__ == "__main__":
    main()
