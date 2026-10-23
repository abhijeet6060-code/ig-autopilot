# IG Autopilot: Complete Automation & Architecture Guide

A fully autonomous, zero-cost Instagram carousel automation engine for **`@abhijeetkumar.founder`**. 
Finds trending AI & business stories, writes executive carousel breakdowns using Google Gemini, renders high-converting 1080×1350 slides with Pillow, and publishes directly to Instagram via Meta Graph API using GitHub Actions as a free cloud scheduler.

---

## 📑 Table of Contents
1. [Architecture & How It Works](#1-architecture--how-it-works)
2. [Prerequisites & Free Tools](#2-prerequisites--free-tools)
3. [Step-by-Step Setup Guide](#3-step-by-step-setup-guide)
   - [Step 1: Meta Developer & Instagram API Setup](#step-1-meta-developer--instagram-api-setup)
   - [Step 2: Google Gemini API Setup](#step-2-google-gemini-api-setup)
   - [Step 3: Local Environment & Verification](#step-3-local-environment--verification)
   - [Step 4: GitHub Repository & Cloud Secrets](#step-4-github-repository--cloud-secrets)
4. [Complete Terminal Commands Reference](#4-complete-terminal-commands-reference)
5. [Visual Design & Rotating Themes Engine](#5-visual-design--rotating-themes-engine)
6. [Scheduling & Daily Execution](#6-scheduling--daily-execution)
7. [Troubleshooting & Maintenance](#7-troubleshooting--maintenance)

---

## 1. Architecture & How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. GitHub Actions Cloud Runner (Ubuntu VM)                  │
│    Wakes up on cron schedule: 09:00 AM & 07:00 PM IST       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Scrapes Live Trends (trends.py)                          │
│    Hacker News (top stories) + Google News + Reddit RSS     │
│    Deduplicates and skips stories already in state.json     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Content Generation (content.py)                          │
│    Google Gemini (gemini-flash-latest with 2.5 failover)    │
│    Writes: Hook, 3-5 Slides, Executive Caption, Hashtags    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Slide Rendering (images.py)                              │
│    Pillow renders 5 slides (1080x1350, 4:5 Instagram ratio) │
│    Auto-rotates: Dark Gradients, Light Editorial, Glass     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Temporary Image Hosting (uploader.py)                    │
│    Uploads slides to public GitHub repo (tmp-media/)        │
│    Generates public raw.githubusercontent.com URLs          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Instagram Publishing (instagram.py)                      │
│    Meta Graph API creates Carousel container & publishes    │
│    Immediately deletes temporary images from GitHub repo    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. State Persistence (db.py)                                │
│    Records media_id in state.json & commits back to GitHub  │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Prerequisites & Free Tools

| Component | Provider | Tier | Why It's Needed |
|---|---|---|---|
| **Cloud Runner** | GitHub Actions | 100% Free (2,000 min/mo) | Executes code in the cloud with zero laptop upkeep |
| **Trend Discovery** | Hacker News, Google News, Reddit | Free public feeds | Real-time AI & business news discovery |
| **AI Copywriter** | Google Gemini API (`gemini-flash-latest`) | Free tier (AI Studio) | Writes hook headlines, takeaways, and captions |
| **Slide Graphics** | Pillow (PIL) + Google Inter Font | Free / Local | Renders crisp 1080×1350 carousel images |
| **Image Hosting** | Public GitHub Repo (`tmp-media/`) | Free | Temporary URL host for Instagram crawler (auto-deleted) |
| **Publishing API** | Meta Instagram Graph API | Free | Official direct posting to `@abhijeetkumar.founder` |

---

## 3. Step-by-Step Setup Guide

### Step 1: Meta Developer & Instagram API Setup

1. **Convert Instagram Account**:
   - Open Instagram on your phone → **Settings and privacy** → **Account type and tools** → Switch to **Professional (Creator or Business) Account**.
   - Connect it to your Facebook Page (e.g. *The Royals Valley* or *Abhijeet Kumar*).

2. **Create Meta App**:
   - Go to [developers.facebook.com](https://developers.facebook.com) → **My Apps** → **Create App**.
   - App Name: `Content Pilot` (Avoid using "Instagram" or "IG" to prevent trademark rejection).
   - Use cases: Select **Manage messaging & content on Instagram**.
   - Business Portfolio: Select your portfolio (or proceed without verification).
   - Click **Create App**.

3. **Add Instagram Tester**:
   - Inside the app dashboard, navigate to **API setup with Instagram login**.
   - Under **2. Generate access tokens**, click **Add account** (or **Roles** → **Add Instagram Tester**).
   - Enter your Instagram handle: `abhijeetkumar.founder`.
   - On your phone: Open Instagram → **Settings** → **Apps and websites** → **Tester invites** → Tap **Accept**.

4. **Copy Your Credentials**:
   - Under **Generate access tokens**, find your account:
     - **`IG_USER_ID`**: The 17-digit number displayed under your profile name (e.g. `17841443688126866`).
     - **`IG_ACCESS_TOKEN`**: Click **Generate token**, log in, check "I understand", and copy the long token.

---

### Step 2: Google Gemini API Setup

1. Visit [aistudio.google.com](https://aistudio.google.com) and log in with your Google account.
2. Click **Get API key** → **Create API key**.
3. Copy your key.

---

### Step 3: Local Environment & Verification

Run these commands in PowerShell in the project directory:

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Store your API Key securely in Windows User Environment (Masked input)
$sec = Read-Host "Enter Gemini API Key" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $key, 'User')
$env:GEMINI_API_KEY = $key

# 3. Store your Instagram Access Token securely
$sec = Read-Host "Enter Instagram Access Token" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
[System.Environment]::SetEnvironmentVariable('IG_ACCESS_TOKEN', $key, 'User')
$env:IG_ACCESS_TOKEN = $key

# 4. Set your IG_USER_ID in .env
# Edit .env and verify:
# IG_USER_ID=17841443688126866

# 5. Run a local dry run (Generates slides into output/ without publishing)
python main.py --once --dry-run
```

---

### Step 4: GitHub Repository & Cloud Secrets

1. **Create Public GitHub Repository**:
   - Go to [github.com/new](https://github.com/new).
   - Name: `ig-autopilot`.
   - Visibility: **Public** *(required for raw.githubusercontent.com image fetching)*.
   - Leave README, .gitignore, and License **unchecked**.

2. **Push Local Code to GitHub**:
   ```powershell
   git init
   git add .
   git commit -m "feat: initialize IG Autopilot"
   git branch -M main
   git remote add origin https://github.com/abhijeet6060-code/ig-autopilot.git
   git push -u origin main
   ```

3. **Add Secrets on GitHub**:
   Go to: `https://github.com/abhijeet6060-code/ig-autopilot/settings/secrets/actions`
   Click **New repository secret** and add:

   | Secret Name | Secret Value |
   |---|---|
   | `GEMINI_API_KEY` | Your Google Gemini API Key |
   | `IG_USER_ID` | `17841443688126866` |
   | `IG_ACCESS_TOKEN` | Your Instagram Access Token |

4. **Grant Workflow Write Permissions**:
   - Go to: `https://github.com/abhijeet6060-code/ig-autopilot/settings/actions`
   - Scroll down to **Workflow permissions**.
   - Select **Read and write permissions**.
   - Click **Save**.

---

## 4. Complete Terminal Commands Reference

### Dependency Installation
```powershell
pip install -r requirements.txt
```

### Secure Credential Storage (No plain text in history)
```powershell
# Set Gemini API Key
$sec = Read-Host "Enter Gemini API Key" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', $key, 'User')
$env:GEMINI_API_KEY = $key

# Set Instagram Token
$sec = Read-Host "Enter Instagram Access Token" -AsSecureString
$key = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec))
[System.Environment]::SetEnvironmentVariable('IG_ACCESS_TOKEN', $key, 'User')
$env:IG_ACCESS_TOKEN = $key
```

### Local Testing & Running
```powershell
# 1. Carousel Mode
# Test a Carousel draft (saves 5 slides to output/)
python main.py --once --dry-run --type carousel

# Publish a Carousel live to Instagram
python main.py --once --type carousel

# 2. Reels Mode (9:16 vertical 1080x1920 video with AI voice & kinetic captions)
# Test a Reel draft (generates .mp4 in output/)
python main.py --once --reel --dry-run

# Publish a Reel live to Instagram
python main.py --once --reel

# 3. Daemon Mode (Local scheduled background runner)
# Automatically publishes Carousel at morning (09:00) and Reel at evening (19:00)
python main.py --daemon --type auto
```

### Git & Deployment Commands
```powershell
# Check current git status
git status

# Stage updated code
git add .

# Commit changes
git commit -m "feat: your commit message"

# Push to GitHub
git push origin main

# Pull latest state (when GitHub Actions updates state.json)
git pull
```

---

## 5. Visual Design & Rotating Themes Engine

All slides are rendered in **1080 × 1350 px (Instagram 4:5 Portrait Ratio)** to maximize vertical feed real estate.

### Rotating Theme Engine (`images.py`)
Each run randomly selects from 3 distinct visual styles so your Instagram profile looks diverse and dynamic:

1. **Deep Dark Gradients** (`dark`):
   - **Royal Blue**: Slate `#0F172A` → Royal Blue `#1E40AF`
   - **Deep Violet**: Charcoal `#111827` → Rich Violet `#6D28D9`
   - **Midnight Teal**: Deep Black `#030712` → Teal `#0D9488`
   - **Warm Copper**: Zinc `#18181B` → Burnt Copper `#B44119`
   - Crisp white typography, accent divider lines, and high contrast.

2. **Luxury Light Editorial** (`light`):
   - **Slate Minimal**: Off-White `#F8FAFC` background with Deep Charcoal `#0F172A` typography.
   - **Cream Editorial**: Warm Cream `#FFFAF5` with Espresso `#1C1917` typography and Magenta accents.
   - **Ice Clean**: Pure White `#FAFAFA` with Navy Charcoal typography.
   - Outer frame borders and white container cards (Forbes / Monocle style).

3. **Cyber Glassmorphic Combo** (`glass`):
   - Deep obsidian space background with semi-transparent frosted glass cards (`rgba(15, 28, 55, 0.7)`).
   - Glowing neon cyan borders (`#38BDF8`) and glowing pill buttons.

### Slide Structure (5-Slide Carousel):
- **Slide 1 (Cover / Hook)**: Header `@abhijeetkumar.founder`, big bold title (font size 82), accent line, and `Swipe >`.
- **Slide 2 (What Happened)**: Category tag pill, headline, breakdown card, and bottom takeaway bar.
- **Slide 3 (Why It Matters)**: Strategic & operational founder impact analysis.
- **Slide 4 (Action Playbook)**: Concrete actionable takeaways.
- **Slide 5 (Outro / CTA)**: Follow `@abhijeetkumar.founder`, audience question prompt to drive comments, and source credit.

> **Note on Counter Badge**: Instagram mobile app automatically overlays its own translucent `1/5`, `2/5` pill in the upper-right corner. The slide generator leaves the top-right corner clear to ensure zero overlap.

---

## 6. Scheduling & Daily Execution

The automated schedule is defined in [`.github/workflows/post.yml`](.github/workflows/post.yml):

```yaml
on:
  schedule:
    - cron: "30 3 * * *"    # 09:00 AM IST (03:30 UTC)
    - cron: "30 13 * * *"   # 07:00 PM IST (13:30 UTC)
```

### Execution Flow:
1. **Scheduled Runs**: Automatically runs `python main.py --once` with `AUTO_POST: "true"`. Scrapes, writes, renders, publishes, and cleans up.
2. **Manual Runs**:
   - Go to **Actions** tab on GitHub → **ig-autopilot** → **Run workflow**.
   - Check *"Draft only"* for a test run (saves artifact).
   - Uncheck *"Draft only"* to trigger an immediate live post on demand.

---

## 7. Troubleshooting & Maintenance

### 1. Gemini 503 / 429 Errors (High Demand Spikes)
Google AI Studio models occasionally experience transient demand spikes. [`content.py`](content.py) includes an automatic multi-model failover chain:
```python
gemini-flash-latest ➔ gemini-2.5-flash ➔ gemini-2.5-pro
```
If one model returns 503 or 429, it automatically waits 2 seconds and switches to the next healthy model without crashing the pipeline.

### 2. Daily Post Cap (`MAX_POSTS_PER_DAY`)
Configured to `3` in [`config.py`](config.py). If you trigger a manual post to test, your scheduled morning (09:00 AM) and evening (07:00 PM) posts will still run without hitting the daily limit.

### 3. Duplicate Prevention
[`state.json`](state.json) stores the last 300 processed story URLs. Once a story is posted or drafted, it will never be selected again.

### 4. Temporary Image Cleanup
All temporary slide images uploaded to `tmp-media/` in your GitHub repo for Instagram's crawler are automatically deleted via GitHub REST API as soon as Instagram confirms the publish status.
