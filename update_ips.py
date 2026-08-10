import sys
import json
import ipaddress
import urllib.request

# ASNs של Disney / BAMTECH
ASNS = [
    "AS13649",   # Disney Streaming Services (BAMTECH)
    "AS396032"   # Disney Infrastructure
]

OUTPUT_FILE = "disney_ips.txt"
MINIMUM_EXPECTED_PREFIXES = 5  # סף מינימלי להגנה מפני קובץ ריק/חסר

def fetch_asn_prefixes(asn):
    valid_prefixes = set()
    url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        # Timeout מוגדר של 15 שניות
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode())
            prefixes_list = data.get('data', {}).get('prefixes', [])
            
            for item in prefixes_list:
                prefix = item.get('prefix')
                if not prefix or ':' in prefix:  # סינון IPv6
                    continue
                
                try:
                    # 1. אימות תקינות ונרמול מבנה ה-CIDR עבור Palo Alto
                    net_obj = ipaddress.ip_network(prefix, strict=False)
                    
                    # 2. סינון כתובות פרטיות/לא תקינות (RFC 1918)
                    if not (net_obj.is_private or net_obj.is_loopback or net_obj.is_unspecified):
                        valid_prefixes.add(str(net_obj))
                    else:
                        print(f"[WARN] Ignored private network for {asn}: {prefix}", file=sys.stderr)
                except ValueError:
                    print(f"[WARN] Ignored malformed prefix for {asn}: {prefix}", file=sys.stderr)
                    continue

    except Exception as e:
        print(f"[ERROR] Error fetching prefixes for {asn}: {e}", file=sys.stderr)
        
    return valid_prefixes

def main():
    print("[INFO] Starting Disney IP prefix retrieval via RIPE Stat...")
    all_ips = set()
    
    for asn in ASNS:
        print(f"[INFO] Fetching IP ranges for {asn}...")
        prefixes = fetch_asn_prefixes(asn)
        print(f"  -> Found {len(prefixes)} valid IPv4 prefixes for {asn}")
        all_ips.update(prefixes)

    # 3. מנגנון Fail-Safe: הגנה מפני קובץ ריק או תוצאה חלקית בגלל כשל תקשורת
    if len(all_ips) < MINIMUM_EXPECTED_PREFIXES:
        print(f"[CRITICAL] Only {len(all_ips)} prefixes retrieved. Expected at least {MINIMUM_EXPECTED_PREFIXES}.", file=sys.stderr)
        print("[CRITICAL] Aborting file write to protect existing Palo Alto EDL.", file=sys.stderr)
        sys.exit(1)  # הכשלת ה-Action ב-GitHub למניעת Commit של קובץ פגום

    # 4. כתיבה ממוינת ונקייה לקובץ
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for ip in sorted(all_ips):
            f.write(f"{ip}\n")
            
    print(f"[SUCCESS] Successfully updated {OUTPUT_FILE} with {len(all_ips)} unique prefixes.")

if __name__ == "__main__":
    main()
