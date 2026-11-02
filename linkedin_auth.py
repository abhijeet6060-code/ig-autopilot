"""One-click LinkedIn OAuth helper:
Exchanges OAuth authorization code for a 2-month Access Token and retrieves personal Author URN.
"""
import http.server
import os
import urllib.parse
import webbrowser
import dotenv
import requests

REDIRECT_URI = "http://localhost:8080/callback"
PORT = 8080


def get_auth_url(client_id):
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid profile w_member_social",
    }
    return f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"


def exchange_code(client_id, client_secret, code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    r = requests.post(url, data=data, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Failed to get LinkedIn access token: {r.status_code} {r.text}")
    return r.json().get("access_token")


def get_author_urn(access_token):
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers, timeout=30)
    if not r.ok:
        raise RuntimeError(f"Failed to get userinfo: {r.status_code} {r.text}")
    sub = r.json().get("sub")
    name = r.json().get("name", "LinkedIn User")
    return f"urn:li:person:{sub}", name


def main():
    dotenv.load_dotenv(override=True)
    client_id = os.getenv("LINKEDIN_CLIENT_ID", "77drlsp3j6xu35")
    client_secret = os.getenv("LINKEDIN_CLIENT_SECRET")

    if not client_secret:
        print("[linkedin_auth] Please enter your Primary Client Secret (from the LinkedIn Auth tab):")
        client_secret = input("Client Secret: ").strip()

    auth_url = get_auth_url(client_id)
    print("\n" + "=" * 60)
    print("Opening LinkedIn in your browser to authorize:")
    print(auth_url)
    print("=" * 60 + "\n")

    auth_code = None

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            if "code" in query:
                auth_code = query["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Success! You can close this tab and return to your terminal.</h1>")
            else:
                self.send_response(400)
                self.end_headers()

        def log_message(self, format, *args):
            return

    server = http.server.HTTPServer(("localhost", PORT), CallbackHandler)
    webbrowser.open(auth_url)
    print("[linkedin_auth] Waiting for authorization in browser...")
    while auth_code is None:
        server.handle_request()
    server.server_close()

    print("[linkedin_auth] Exchanging authorization code for 2-month access token...")
    token = exchange_code(client_id, client_secret, auth_code)
    urn, name = get_author_urn(token)

    print(f"\n[linkedin_auth] Success! Connected as: {name}")
    print(f"[linkedin_auth] Author URN: {urn}")

    # Append or update .env
    env_path = ".env"
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    updated = []
    has_token, has_urn = False, False
    for line in lines:
        if line.startswith("LINKEDIN_ACCESS_TOKEN="):
            updated.append(f"LINKEDIN_ACCESS_TOKEN={token}\n")
            has_token = True
        elif line.startswith("LINKEDIN_AUTHOR_URN="):
            updated.append(f"LINKEDIN_AUTHOR_URN={urn}\n")
            has_urn = True
        elif line.startswith("LINKEDIN_CLIENT_SECRET="):
            updated.append(f"LINKEDIN_CLIENT_SECRET={client_secret}\n")
        else:
            updated.append(line)

    if not has_token:
        updated.append(f"\nLINKEDIN_CLIENT_ID={client_id}\n")
        updated.append(f"LINKEDIN_CLIENT_SECRET={client_secret}\n")
        updated.append(f"LINKEDIN_ACCESS_TOKEN={token}\n")
        updated.append(f"LINKEDIN_AUTHOR_URN={urn}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(updated)

    print("[linkedin_auth] Saved LINKEDIN_ACCESS_TOKEN and LINKEDIN_AUTHOR_URN to .env!")


if __name__ == "__main__":
    main()

