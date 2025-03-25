import os
import imagehash
import json
import subprocess
from tqdm import tqdm

# Config
THRESHOLD = 25
HASH_FILE = 'logo_hashes.json'
GROUP_METADATA_FILE = 'logo_groups.json'

def load_hashes(hash_file):
    with open(hash_file, 'r') as f:
        data = json.load(f)
    return {k: imagehash.hex_to_hash(v) for k, v in data.items()}

def group_by_similarity(hashes, threshold=23):
    groups, used = [], set()
    for host1, hash1 in hashes.items():
        if host1 in used:
            continue
        group = [host1]
        used.add(host1)
        for host2, hash2 in hashes.items():
            if host2 in used or host1 == host2:
                continue
            if hash1 - hash2 <= threshold:
                group.append(host2)
                used.add(host2)
        groups.append(group)
    return groups

def save_grouped_domains(groups, output_file='logo_groups.json'):
    data = []
    for i, group in enumerate(groups):
        domains = [host.replace('_', '.') for host in group]
        data.append({
            'group_id': i + 1,
            'domains': sorted(list(set(domains)))
        })
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"📄 Saved grouped domains to {output_file}")


def run():
    print("\n" + "=" * 50)
    print("🛠️  STEP 1: Fetching Logos with fetch_logos.py")
    print("=" * 50)
    subprocess.run(["python", "fetch_logos.py"], check=True)

    print("\n" + "=" * 50)
    print("🧠 STEP 2: Grouping Similar Logos by Hash")
    print("=" * 50)

    hashes = load_hashes(HASH_FILE)
    groups = group_by_similarity(hashes, THRESHOLD)

    save_grouped_domains(groups, GROUP_METADATA_FILE)
    print("✅ All logos grouped and metadata saved!")

if __name__ == "__main__":
    run()
