import random
import os

import requests


BASE_URL = "http://127.0.0.1:8000"
USERNAME = os.getenv("SIM_USERNAME", "admin")
PASSWORD = os.getenv("SIM_PASSWORD", "pratik123")

if not PASSWORD:
    raise RuntimeError("SIM_PASSWORD must be set before running simulate_requests.py")

auth_response = requests.post(
    f"{BASE_URL}/auth/token",
    json={"username": USERNAME, "password": PASSWORD},
)

if auth_response.status_code != 200:
    print(f"Auth failed: {auth_response.json()}")
    raise SystemExit(1)

token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Authenticated. Sending 200 predictions...\n")

for index in range(200):
    features = [round(random.uniform(-5, 5), 4) for _ in range(30)]
    response = requests.post(
        f"{BASE_URL}/predict",
        json={"features": features},
        headers=headers,
    )
    result = response.json()
    print(
        f"[{index + 1:03d}] "
        f"pred={result.get('prediction')} "
        f"conf={result.get('confidence')} "
        f"latency={result.get('latency_ms')}ms"
    )
