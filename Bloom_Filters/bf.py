import os
import redis
from dotenv import load_dotenv

load_dotenv()

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=redis_host, port=redis_port, db=1)

key = "mobile:brand"
r.delete(key)

# Reserve a Bloom filter with a realistic false-positive rate and enough capacity.
# This makes it much more likely to show at least one false positive during the demo.
res1 = r.bf().reserve(key, 0.01, 10, noScale=True)
print(f"Filter Reserved: {res1}")

real_items = [f"brand:{i}" for i in range(200)]
test_items = [f"test_brand:{i}" for i in range(1000)]

try:
    r.bf().madd(key, *real_items)
    results = r.bf().mexists(key, *test_items)
except redis.exceptions.ResponseError as e:
    print(f"Redis Error during processing: {e}")
    raise

false_positives = [item for item, is_member in zip(test_items, results) if is_member]

print(f"\nInserted {len(real_items)} items and tested {len(test_items)} unseen items.")
print(f"False positives found: {len(false_positives)}")

for item in false_positives[:10]:
    print(f"🚨 {item} is a False Positive! (Never added, but Bloom filter says 1)")
