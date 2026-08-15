import httpx
import json

RAILWAY_TOKEN = "36463e49-d7d1-428e-8410-aa5e2c4ab591"
DEPLOYMENT_ID = "0ee41222-6647-4c65-8133-8634a6f17948"

headers = {
    "Authorization": f"Bearer {RAILWAY_TOKEN}",
    "Content-Type": "application/json"
}

def get_logs():
    query = """
    query {
      deploymentLogs(deploymentId: "%s", limit: 50) {
        message
        severity
        timestamp
      }
    }
    """ % DEPLOYMENT_ID
    r = httpx.post("https://backboard.railway.app/graphql/v2", headers=headers, json={"query": query})
    data = r.json()
    logs = data.get("data", {}).get("deploymentLogs", [])
    for log in logs:
        print(f"[{log.get('timestamp')}] {log.get('message')}")

if __name__ == "__main__":
    get_logs()
