import requests

# Make sure access_token is defined
# access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYVUh3VWZKaHVDVWo0X3k4ZF8xM0hxWXBYMFdwdDd2anhob2FPLUxzREZFIn0.eyJleHAiOjE3NzAwMTY0NjgsImlhdCI6MTc3MDAxNDY2OCwianRpIjoiYjllODRiZjgtYWU5ZC00MmIwLTkzYTctMzQ4ZTVhOWNhYjEyIiwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5kYXRhc3BhY2UuY29wZXJuaWN1cy5ldS9hdXRoL3JlYWxtcy9DRFNFIiwiYXVkIjpbIkNMT1VERkVSUk9fUFVCTElDIiwiYWNjb3VudCJdLCJzdWIiOiI1NjkzMzVmMi0xM2M0LTQ1ZmUtOTZlOC03ZTUwMjY2M2EwYWQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJjZHNlLXB1YmxpYyIsInNlc3Npb25fc3RhdGUiOiJmYTIzYTBmNy1kNDcxLTQzZWQtYjJjMy0yYmJhNjI4ZTVmNjMiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9sb2NhbGhvc3Q6NDIwMCIsIioiLCJodHRwczovL3dvcmtzcGFjZS5zdGFnaW5nLWNkc2UtZGF0YS1leHBsb3Jlci5hcHBzLnN0YWdpbmcuaW50cmEuY2xvdWRmZXJyby5jb20iXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImNvcGVybmljdXMtZ2VuZXJhbC1xdW90YSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJkZWZhdWx0LXJvbGVzLWNkYXMiLCJjb3Blcm5pY3VzLWdlbmVyYWwiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6IkFVRElFTkNFX1BVQkxJQyBvcGVuaWQgZW1haWwgcHJvZmlsZSBvbmRlbWFuZF9wcm9jZXNzaW5nIHVzZXItY29udGV4dCIsInNpZCI6ImZhMjNhMGY3LWQ0NzEtNDNlZC1iMmMzLTJiYmE2MjhlNWY2MyIsImdyb3VwX21lbWJlcnNoaXAiOlsiL2FjY2Vzc19ncm91cHMvdXNlcl90eXBvbG9neS9jb3Blcm5pY3VzX2dlbmVyYWwiLCIvb3JnYW5pemF0aW9ucy9kZWZhdWx0LTU2OTMzNWYyLTEzYzQtNDVmZS05NmU4LTdlNTAyNjYzYTBhZC9yZWd1bGFyX3VzZXIiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJNb2hhbW1lZCBBYmR1bGxhaCIsIm9yZ2FuaXphdGlvbnMiOlsiZGVmYXVsdC01NjkzMzVmMi0xM2M0LTQ1ZmUtOTZlOC03ZTUwMjY2M2EwYWQiXSwidXNlcl9jb250ZXh0X2lkIjoiZTgwYTFmZmItYThhNi00MjcxLWIxYmQtYjkxOWMwMzFhZGU2IiwiY29udGV4dF9yb2xlcyI6e30sImNvbnRleHRfZ3JvdXBzIjpbIi9hY2Nlc3NfZ3JvdXBzL3VzZXJfdHlwb2xvZ3kvY29wZXJuaWN1c19nZW5lcmFsLyIsIi9vcmdhbml6YXRpb25zL2RlZmF1bHQtNTY5MzM1ZjItMTNjNC00NWZlLTk2ZTgtN2U1MDI2NjNhMGFkL3JlZ3VsYXJfdXNlci8iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoibW9oYW1tZWQuYUBiaWdiYW5nYm9vbS5jb20iLCJnaXZlbl9uYW1lIjoiTW9oYW1tZWQiLCJmYW1pbHlfbmFtZSI6IkFiZHVsbGFoIiwidXNlcl9jb250ZXh0IjoiZGVmYXVsdC01NjkzMzVmMi0xM2M0LTQ1ZmUtOTZlOC03ZTUwMjY2M2EwYWQiLCJlbWFpbCI6Im1vaGFtbWVkLmFAYmlnYmFuZ2Jvb20uY29tIn0.MGZ1uuEQVuFB4gzBQBWgCaN5T9SCqRN0HiWEcTrHDSgH36OszjLcxqCsyNs80UvnTEy_UcoMqUrZOxEL49cCGfqmxBpj3_5JG8kdpx0GIyv-Rl3JdYtKEZE4_GBh14Kr0y3qDAeXnCHzvOwt5aFZvRI_mBuvUh2wjiBfL8HDN1lFh03syuG-0bbCTbUlaGC4eRVmReIneb24TMJaExKLh2m4N7gTJ7yHxJL6ZnXa19bdymtC6otCFo-wRW6Is5-gFVpYykhZTZHMvk_i0pzAMBWcaaZSsuNe5KeoNE9oM6NfeFSNY_eWQFKyuVWHV2K8J_swVdH58VWMpmFDEglwgw"  # Replace with your actual access token
access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJYVUh3VWZKaHVDVWo0X3k4ZF8xM0hxWXBYMFdwdDd2anhob2FPLUxzREZFIn0.eyJleHAiOjE3NzAwMjA2MTYsImlhdCI6MTc3MDAxODgxNiwianRpIjoiOGNlMjc4MDctOWI0Yy00NThiLThiMjgtMmVlZWNjMTViZjRmIiwiaXNzIjoiaHR0cHM6Ly9pZGVudGl0eS5kYXRhc3BhY2UuY29wZXJuaWN1cy5ldS9hdXRoL3JlYWxtcy9DRFNFIiwiYXVkIjpbIkNMT1VERkVSUk9fUFVCTElDIiwiYWNjb3VudCJdLCJzdWIiOiI1NjkzMzVmMi0xM2M0LTQ1ZmUtOTZlOC03ZTUwMjY2M2EwYWQiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJjZHNlLXB1YmxpYyIsInNlc3Npb25fc3RhdGUiOiJlOTc4N2ZmMS1iMWE4LTQ3YTctYTIzNC0wY2YxNjhjM2NhOGQiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cHM6Ly9sb2NhbGhvc3Q6NDIwMCIsIioiLCJodHRwczovL3dvcmtzcGFjZS5zdGFnaW5nLWNkc2UtZGF0YS1leHBsb3Jlci5hcHBzLnN0YWdpbmcuaW50cmEuY2xvdWRmZXJyby5jb20iXSwicmVhbG1fYWNjZXNzIjp7InJvbGVzIjpbImNvcGVybmljdXMtZ2VuZXJhbC1xdW90YSIsIm9mZmxpbmVfYWNjZXNzIiwidW1hX2F1dGhvcml6YXRpb24iLCJkZWZhdWx0LXJvbGVzLWNkYXMiLCJjb3Blcm5pY3VzLWdlbmVyYWwiXX0sInJlc291cmNlX2FjY2VzcyI6eyJhY2NvdW50Ijp7InJvbGVzIjpbIm1hbmFnZS1hY2NvdW50IiwibWFuYWdlLWFjY291bnQtbGlua3MiLCJ2aWV3LXByb2ZpbGUiXX19LCJzY29wZSI6IkFVRElFTkNFX1BVQkxJQyBvcGVuaWQgZW1haWwgcHJvZmlsZSBvbmRlbWFuZF9wcm9jZXNzaW5nIHVzZXItY29udGV4dCIsInNpZCI6ImU5Nzg3ZmYxLWIxYTgtNDdhNy1hMjM0LTBjZjE2OGMzY2E4ZCIsImdyb3VwX21lbWJlcnNoaXAiOlsiL2FjY2Vzc19ncm91cHMvdXNlcl90eXBvbG9neS9jb3Blcm5pY3VzX2dlbmVyYWwiLCIvb3JnYW5pemF0aW9ucy9kZWZhdWx0LTU2OTMzNWYyLTEzYzQtNDVmZS05NmU4LTdlNTAyNjYzYTBhZC9yZWd1bGFyX3VzZXIiXSwiZW1haWxfdmVyaWZpZWQiOnRydWUsIm5hbWUiOiJNb2hhbW1lZCBBYmR1bGxhaCIsIm9yZ2FuaXphdGlvbnMiOlsiZGVmYXVsdC01NjkzMzVmMi0xM2M0LTQ1ZmUtOTZlOC03ZTUwMjY2M2EwYWQiXSwidXNlcl9jb250ZXh0X2lkIjoiZTgwYTFmZmItYThhNi00MjcxLWIxYmQtYjkxOWMwMzFhZGU2IiwiY29udGV4dF9yb2xlcyI6e30sImNvbnRleHRfZ3JvdXBzIjpbIi9hY2Nlc3NfZ3JvdXBzL3VzZXJfdHlwb2xvZ3kvY29wZXJuaWN1c19nZW5lcmFsLyIsIi9vcmdhbml6YXRpb25zL2RlZmF1bHQtNTY5MzM1ZjItMTNjNC00NWZlLTk2ZTgtN2U1MDI2NjNhMGFkL3JlZ3VsYXJfdXNlci8iXSwicHJlZmVycmVkX3VzZXJuYW1lIjoibW9oYW1tZWQuYUBiaWdiYW5nYm9vbS5jb20iLCJnaXZlbl9uYW1lIjoiTW9oYW1tZWQiLCJmYW1pbHlfbmFtZSI6IkFiZHVsbGFoIiwidXNlcl9jb250ZXh0IjoiZGVmYXVsdC01NjkzMzVmMi0xM2M0LTQ1ZmUtOTZlOC03ZTUwMjY2M2EwYWQiLCJlbWFpbCI6Im1vaGFtbWVkLmFAYmlnYmFuZ2Jvb20uY29tIn0.D5DGeeO5_fDsPn-tKl-1T4uKiNMFO8kUlyN_OC9sS6djKal0pugE9XiPWWmcmMNnF-OTDaung7CB35bXZArk1tMo2KXqbiIrKGOIj7_HW2GQR_zVCKqYnCaI2iRq1SangrhiK9IjobTjqS3t0332-GW1jtkM1nZi7SbE4vcfWRbrGM3S1e2vZqbHmq6sJ63vMgFxDMohrfmaKp3XiF2gsq66Jh_9_HbD9KsuWrWK0qPSVeFHY4k8UqeEd_NUOKljNjmH4wLbZTBKMlOaQgBD4rS7DwRQeNmrCZzMUoezqIkoovKXTaC2l4X_voNnayPE7Azk755Zh-EvKL77vRXt5A"  # Replace with your actual access token

# url = f"https://download.dataspace.copernicus.eu/odata/v1/Products(427be276-cf42-419e-9dd3-c6544a2f4d46)/$value"

import os
from pathlib import Path

BASE = "https://catalogue.dataspace.copernicus.eu/odata/v1"
DOWNLOAD = "https://download.dataspace.copernicus.eu/odata/v1"
OUT_DIR = Path(r"C:\Users\BBBS-AI-01\d\anomaly\dataset\piraeus\sar")


def query_products(token, top=50):
    """
    Query Sentinel-1 IW GRDH products between
    2017-05-01 and 2019-12-31 (inclusive).
    """
    filt = (
        "Collection/Name eq 'SENTINEL-1' and "
        "contains(Name,'IW_GRDH') and "
        "ContentDate/Start ge 2017-05-01T00:00:00Z and "
        "ContentDate/Start le 2019-12-31T23:59:59Z"
    )

    url = (
        f"{BASE}/Products?"
        f"$filter={filt}"
        f"&$select=Id,Name,Online"
        f"&$top={top}"
    )

    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        raise RuntimeError(f"Catalogue error {r.status_code}: {r.text[:200]}")

    return r.json()["value"]



def download_product(token, pid, name):
    """
    Download one product by OData Product Id.
    """
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{name}.zip"

    url = f"{DOWNLOAD}/Products({pid})/$value"
    headers = {"Authorization": f"Bearer {token}"}

    with requests.get(url, headers=headers, stream=True) as r:
        r.raise_for_status()
        with open(out, "wb") as f:
            for c in r.iter_content(8192):
                if c:
                    f.write(c)


def main(access_token):
    """
    End-to-end query + download loop.
    """
    products = query_products(access_token)

    for p in products:
        if p["Online"]:
            download_product(access_token, p["Id"], p["Name"])


if __name__ == "__main__":
    main(access_token=access_token)
