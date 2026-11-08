import os
import urllib.parse

def generate_subscriptions():
    if not os.path.exists('iplist.txt'):
        return

    with open('iplist.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    current_region = None
    region_ips = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # 判斷標頭
        if '.' not in line and ':' not in line:
            current_region = line
            if current_region not in region_ips:
                region_ips[current_region] = []
        elif current_region:
            region_ips[current_region].append(line)

    for region, ips in region_ips.items():
        filename = f"{region}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for ip in ips:
                f.write(f"{ip}#{region}\n")

if __name__ == '__main__':
    generate_subscriptions()
