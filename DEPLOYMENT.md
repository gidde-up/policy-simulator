# Deployment Guide: Policy Simulator on Render.com

## What This Does

Deploys the Economic Policy Simulator to a public URL, protected by a shared username/password (HTTP Basic Auth). When colleagues visit the URL, the browser prompts for credentials before showing the app.

---

## Prerequisites

- A **GitHub account** (https://github.com)
- A **Render.com account** (https://render.com — sign up with GitHub)
- (`ANTHROPIC_API_KEY` is only relevant to the dormant chat endpoints;
  the app needs no API keys)

---

## Step 1: Configure Git (One-Time)

Open a terminal and run (replace with your actual name and email):

```
git config --global user.email "your.email@example.com"
git config --global user.name "Your Name"
```

---

## Step 2: Create a GitHub Repository

1. Go to https://github.com/new
2. Repository name: `policy-simulator`
3. Set to **Private** (recommended — the code won't be public)
4. Do NOT initialize with README (we already have files)
5. Click **Create repository**
6. Copy the repository URL (e.g., `https://github.com/YOUR_USERNAME/policy-simulator.git`)

---

## Step 3: Push Code to GitHub

Open a terminal in `C:\Users\bernd\vibecode\policy-simulator` and run:

```
git add -A
git commit -m "Initial commit: Economic Policy Simulator"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/policy-simulator.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

GitHub will prompt for authentication — use your GitHub password or a Personal Access Token (Settings > Developer Settings > Personal Access Tokens).

---

## Step 4: Deploy on Render.com

1. Go to https://render.com and sign in with GitHub
2. Click **New** > **Web Service**
3. Connect your `policy-simulator` repository
4. Render should auto-detect the Dockerfile. Confirm these settings:
   - **Name**: `policy-simulator` (or any name you like)
   - **Region**: Frankfurt (closest to Turin) or any EU region
   - **Instance Type**: Free
   - **Build Command**: *(leave empty — Dockerfile handles this)*
   - **Start Command**: *(leave empty — Dockerfile handles this)*
5. Click **Advanced** and add these **Environment Variables**:

   | Key | Value | Notes |
   |-----|-------|-------|
   | `AUTH_USERNAME` | Choose a username (e.g., `epap`) | Shared with colleagues |
   | `AUTH_PASSWORD` | Choose a strong password | Shared with colleagues |
   | `ANTHROPIC_API_KEY` | `sk-ant-...` | Your API key (optional) |

6. Click **Create Web Service**

Render will build and deploy. This takes 3-5 minutes the first time.

---

## Step 5: Access Your App

Once deployed, Render provides a URL like:

```
https://policy-simulator-XXXX.onrender.com
```

Visit it. The browser will show a login popup — enter the username and password you set in Step 4.

---

## Sharing with Colleagues

Send colleagues:
1. The **URL** (e.g., `https://policy-simulator-XXXX.onrender.com`)
2. The **username** and **password**

They simply open the link, enter the credentials once, and use the app. No account creation needed.

---

## Important Notes

### Free Tier Behaviour and Classroom Delivery
- The service **spins down after 15 minutes of inactivity**
- The first visit after inactivity is a **cold start: typically 30-60
  seconds** (container boot + the engine loading all five country files;
  after boot, simulations are matrix-vector products and effectively
  instant)
- **For classroom or workshop delivery, do one of the following:**
  1. **Recommended**: upgrade the service to a paid instance
     ($7/month) for the training period - no spin-down, no cold starts;
  2. or set up an **external keep-alive ping** hitting
     `https://YOUR-APP.onrender.com/health` every 10 minutes (e.g. a
     free uptime monitor such as UptimeRobot). `/health` is exempt from
     the Basic Auth, so monitors work without credentials;
  3. at minimum, open the app 5 minutes before the session starts.

### Continuous Integration
GitHub Actions (`.github/workflows/tests.yml`) runs the full test suite
(data validation, engine tests including the tariff acceptance
constraint, API contract smoke, frontend build) on every push. House
rule: push to `main` only after the suite passes locally; the Action is
the public record.

### Changing the Password
1. Go to your Render dashboard > policy-simulator > Environment
2. Update `AUTH_PASSWORD` (and/or `AUTH_USERNAME`)
3. Render automatically redeploys with the new credentials

### Updating the App
After making local changes:
```
git add -A
git commit -m "Description of changes"
git push
```
Render automatically redeploys on every push to `main`.

### Local Development
The app still works locally as before — `start.bat` runs it without password protection (auth is only active when `AUTH_USERNAME` and `AUTH_PASSWORD` environment variables are set).
