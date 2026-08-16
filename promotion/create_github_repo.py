import urllib.request
import json
import base64
import sys

TOKEN = open("E:/Android/hermes-skill-or-mcp/.ghtoken").read().strip()
HDRS = {
    "Authorization": "token " + TOKEN,
    "Accept": "application/vnd.github+json",
    "User-Agent": "hermes-agent",
}

README = """# AI Video Tools — Tested & Ranked

Independent reviews and comparisons of AI video generators.
Synthesia, HeyGen, Runway, Pictory and Pika — matched to your actual
use case, not the hype.

**Live site:** https://aivideotest.com/

## Guides

| Guide | Focus |
|-------|-------|
| [Best AI Video Generators 2026](https://aivideotest.com/) | Ranked & compared |
| [Synthesia vs HeyGen vs Runway](https://aivideotest.com/synthesia-vs-heygen-vs-runway) | 3 tools, 3 different jobs |
| [Make Videos Without a Camera](https://aivideotest.com/no-camera) | Faceless channel workflow |
| [Best AI Avatars for YouTube](https://aivideotest.com/ai-avatars) | Synthesia / HeyGen / D-ID |
| [AI Video Tool Pricing](https://aivideotest.com/pricing) | The hidden cost of credits |
| [TikTok & Shorts Tools](https://aivideotest.com/short-form) | Pika / HeyGen / Pictory |
| [Clone Yourself with AI](https://aivideotest.com/clone-yourself) | HeyGen guide |

## About

We tested the leading AI video platforms hands-on and ranked them by
real use case: AI avatars, text-to-video, and article-to-video. The
full breakdown — pricing, credit systems, and step-by-step workflows —
is on the site.

## Tech

- FastAPI (Python) + static HTML templates
- Deployed on Fly.io (free tier)
- Full technical SEO: Article / FAQ / Breadcrumb / WebSite schema,
  sitemap, robots.txt, OG + Twitter cards
"""


def call(url, data=None, method=None):
    req = urllib.request.Request(url, headers=HDRS, method=method)
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        req = urllib.request.Request(url, data=body, headers=HDRS, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=20)
        return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())


# 1. Create repo
status, data = call(
    "https://api.github.com/user/repos",
    data={
        "name": "ai-video-tools",
        "description": "Independent reviews & comparisons of AI video generators — Synthesia, HeyGen, Runway, Pictory, Pika. Live at aivideotest.com",
        "homepage": "https://aivideotest.com/",
        "public": True,
        "has_issues": True,
    },
    method="POST",
)
print("create repo status:", status)
if status not in (201, 422):
    print(data)
    sys.exit(1)

# 2. Create README.md
status, data = call(
    "https://api.github.com/repos/buigialy30206-eng/ai-video-tools/contents/README.md",
    data={
        "message": "Add README with site link",
        "content": base64.b64encode(README.encode()).decode(),
    },
    method="PUT",
)
print("create README status:", status)
if status not in (200, 201):
    print(data)
    sys.exit(1)

print("README committed:", data["commit"]["sha"][:8])
print("Repo URL:", data["content"]["html_url"])
