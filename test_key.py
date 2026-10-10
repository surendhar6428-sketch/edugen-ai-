from pathlib import Path
import requests

env_file = Path(__file__).resolve().parent / ".env"
print(".env file irukka:", env_file.exists(), "->", env_file)

key = None
for line in env_file.read_text(encoding="utf-8-sig").splitlines():
    if line.strip().startswith("GEMINI_API_KEY"):
        key = line.split("=", 1)[1]
        break

print("Raw key:", repr(key))
key = key.strip().strip('"').strip("'").strip()
print("Clean key length:", len(key), "(53 varanum)")

r = requests.post(
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent",
    headers={"Content-Type": "application/json", "X-goog-api-key": key},
    json={"contents": [{"parts": [{"text": "Say hello"}]}]},
    timeout=60,
)
print("Status:", r.status_code)
print(r.text[:300])
