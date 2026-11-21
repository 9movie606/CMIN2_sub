import os


def generate_subscriptions():
  if not os.path.exists('iplist.txt'):
    return

  with open('iplist.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

  current_region = None
  region_ips = {}
  ip_regions_map = {}  # 記錄每個 IP 對應的所有地區列表

  for line in lines:
    line = line.strip()
    if not line:
      continue

    # 判斷標頭（所有地區分類，包含「云南-測試」等皆會納入）
    if '.' not in line and ':' not in line:
      current_region = line
      if current_region not in region_ips:
        region_ips[current_region] = []
    elif current_region:
      # 保持原始順序並避免單一地區內重複
      if line not in region_ips[current_region]:
        region_ips[current_region].append(line)

      # 記錄該 IP 出現過的所有地區（保持出現順序且不重複）
      if line not in ip_regions_map:
        ip_regions_map[line] = []
      if current_region not in ip_regions_map[line]:
        ip_regions_map[line].append(current_region)

  # 1. 原有邏輯：生成各地區獨立訂閱檔案（保留 #地區 標記）
  for region, ips in region_ips.items():
    filename = f'{region}.txt'
    with open(filename, 'w', encoding='utf-8') as f:
      for ip in ips:
        f.write(f'{ip}#{region}\n')

  # 2. 新增邏輯：輪詢抽取指定數量不重複 IP，生成 all_list.txt（帶多地區備註）
  target_count = int(os.environ.get('TARGET_IP_COUNT', 60))
  header_note = os.environ.get('HEADER_NOTE', '').strip()

  # 複製各區列表供輪詢消耗，並依 IP 數量由少到多排序（優先保障節點少的地區覆蓋率）
  pools = {r: list(ips) for r, ips in region_ips.items()}
  sorted_regions = sorted(pools.keys(), key=lambda r: len(pools[r]))

  selected_ips = []
  seen_ips = set()

  while len(selected_ips) < target_count:
    added_in_round = False
    for r in sorted_regions:
      while pools[r]:
        ip = pools[r].pop(0)
        if ip not in seen_ips:
          seen_ips.add(ip)
          selected_ips.append(ip)
          added_in_round = True
          break
      if len(selected_ips) >= target_count:
        break
    if not added_in_round:
      break

  # 寫入 all_list.txt（格式：IP#地區1-地區2）
  with open('all_list.txt', 'w', encoding='utf-8') as f:
    if header_note:
      f.write(f'{header_note}\n')
    for ip in selected_ips:
      regions_str = '-'.join(ip_regions_map[ip])
      f.write(f'{ip}#{regions_str}\n')


if __name__ == '__main__':
  generate_subscriptions()
