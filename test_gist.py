import requests
import json

# Test GitHub API access
GIST_ID = "e5f2784739d9e2784a3f067217b25e01"  # From your secrets
GITHUB_TOKEN = "11ARPSUVA0oMhjJ78bZpD8_KrLMMGyi97DZzjAU7K7rUZC76qEX34WACqYNoBsVfKVSQ3LNXVZIcIvhQTD"

def test_gist_access():
    url = f"https://api.github.com/gists/{GIST_ID}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    print(f"Testing access to gist: {GIST_ID}")
    print(f"URL: {url}")
    
    try:
        r = requests.get(url, headers=headers)
        print(f"Status code: {r.status_code}")
        
        if r.status_code == 200:
            print("✅ Success! Gist is accessible.")
            gist_data = r.json()
            print(f"Gist description: {gist_data.get('description', 'No description')}")
            print(f"Files in gist: {list(gist_data.get('files', {}).keys())}")
        else:
            print("❌ Failed to access gist")
            print(f"Response: {r.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_gist_access()