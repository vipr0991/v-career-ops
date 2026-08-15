import httpx
import json
import time

RAILWAY_TOKEN = "36463e49-d7d1-428e-8410-aa5e2c4ab591"
PROJECT_ID = "c7c93590-59a2-416f-9fb7-3c8d7761eb7f"
SERVICE_ID = "8a47abd9-3b08-4088-8d2a-ad1542e4313d"
ENV_ID = "4ddade5d-f9f9-4adb-ba1c-efd31ffc5a1b"

headers = {
    "Authorization": f"Bearer {RAILWAY_TOKEN}",
    "Content-Type": "application/json"
}

def trigger():
    mutation = """
    mutation ServiceInstanceRedeploy($serviceId: String!, $environmentId: String!) {
      serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
    }
    """
    r = httpx.post("https://backboard.railway.app/graphql/v2", headers=headers, json={
        "query": mutation,
        "variables": {"serviceId": SERVICE_ID, "environmentId": ENV_ID}
    })
    print("Redeploy trigger:", r.json())

def check():
    query = """
    query {
      deployments(input: { serviceId: "%s" }, first: 2) {
        edges {
          node {
            id
            status
            createdAt
            meta
          }
        }
      }
    }
    """ % SERVICE_ID
    r = httpx.post("https://backboard.railway.app/graphql/v2", headers=headers, json={"query": query})
    data = r.json()
    edges = data.get("data", {}).get("deployments", {}).get("edges", [])
    for e in edges:
        n = e.get("node", {})
        print(f"Deployment: {n.get('id')} | Status: {n.get('status')} | Commit: {n.get('meta', {}).get('commitHash')} | Message: {n.get('meta', {}).get('commitMessage')}")

if __name__ == "__main__":
    trigger()
    time.sleep(3)
    check()
