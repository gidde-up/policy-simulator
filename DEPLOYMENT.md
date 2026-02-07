# Deployment Guide: Policy Simulator on Render.com

## What This Does

Deploys the Economic Policy Simulator to a public URL, protected by a shared username/password (HTTP Basic Auth). When colleagues visit the URL, the browser prompts for credentials before showing the app.

---

## Prerequisites

- A **GitHub account** (https://github.com)
- A **Render.com account** (https://render.com — sign up with GitHub)
- Your **Anthropic API key** (for the AI chatbot; optional)

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

### Free Tier Behaviour
- The service **spins down after 15 minutes of inactivity**
- First visit after inactivity has a **~30 second loading time**
- After that, it responds normally
- Upgrade to paid ($7/month) to keep it always on

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
