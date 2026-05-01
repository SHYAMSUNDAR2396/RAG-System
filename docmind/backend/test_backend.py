import subprocess
import time
import urllib.request
import json
import sys

print("Starting server...")
process = subprocess.Popen(["/Users/shyamsundar/Documents/RAG/venv/bin/uvicorn", "main:app", "--port", "8000"])
time.sleep(5) # Wait for server to start

try:
    print("Testing health endpoint...")
    req = urllib.request.Request("http://127.0.0.1:8000/api/health")
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        data = json.loads(response.read().decode())
        print(f"Response: {data}")
except Exception as e:
    print(f"Error: {e}")
finally:
    print("Killing server...")
    process.terminate()
    process.wait()
