# How to Deploy Your Play Formatter Web App

## What You'll Get

A live website (like playformatter.streamlit.app) where anyone can:
- Upload a play file (.docx)
- Click a button
- Download the professionally formatted version

**No installation needed for your colleagues!**

---

## Step-by-Step Deployment (15 minutes)

### Step 1: Create a GitHub Account (if you don't have one)

1. Go to: https://github.com
2. Click "Sign up"
3. Create a free account
4. Verify your email

### Step 2: Create a New Repository

1. Once logged in, click the "+" in the top right
2. Click "New repository"
3. Name it: `play-formatter` (or anything you want)
4. Description: "Professional play formatting tool"
5. Make it **Public**
6. Check "Add a README file"
7. Click "Create repository"

### Step 3: Upload Your Files

You need to upload these 4 files to your repository:

1. Click "Add file" → "Upload files"
2. Drag and drop these files:
   - `streamlit_app.py`
   - `requirements.txt`
   - `packages.txt`
   - `setup.sh`
3. Click "Commit changes"

### Step 4: Deploy to Streamlit Cloud

1. Go to: https://streamlit.io/cloud
2. Click "Sign in" (or "Sign up") with GitHub
3. It will ask to connect to your GitHub account - click "Authorize"
4. Click "New app"
5. Fill in:
   - **Repository**: Select your `play-formatter` repository
   - **Branch**: main
   - **Main file path**: `streamlit_app.py`
6. Click "Advanced settings" (optional but recommended)
   - Under "Secrets" you can add any API keys if needed later
   - Under "Python version" select 3.11
7. Click "Deploy!"

### Step 5: Wait for Deployment

- The app will build (takes 3-5 minutes the first time)
- You'll see logs scrolling
- When it says "Your app is live!" you're done!

### Step 6: Get Your URL

- Your app will be live at: `https://[your-username]-play-formatter.streamlit.app`
- Or something like: `https://play-formatter.streamlit.app`
- Share this URL with your colleagues!

---

## Using Your Web App

**For you and your colleagues:**

1. Go to your Streamlit app URL
2. Click "Browse files" or drag and drop a .docx file
3. Wait a few seconds for formatting
4. Click "Download Formatted Play"
5. Done!

**No installation, no command line, just drag and drop!**

---

## Free Limits

Streamlit Cloud free tier includes:
- ✅ 1GB of storage
- ✅ Unlimited apps
- ✅ Reasonable usage (enough for dozens of plays per day)

If you need more, there are paid plans, but the free tier should be plenty for your needs.

---

## Updating Your App

If you want to make changes later:

1. Go to your GitHub repository
2. Click on the file you want to edit (like `streamlit_app.py`)
3. Click the pencil icon (Edit)
4. Make your changes
5. Click "Commit changes"
6. Your Streamlit app will automatically redeploy with the updates!

---

## Troubleshooting

### App won't deploy
- Make sure all 4 files are uploaded
- Check that filenames are exactly right
- Look at the deployment logs for error messages

### App crashes when uploading file
- Make sure the file is .docx format
- Check that character names are in ALL CAPS
- Try a simpler test file first

### Need to restart the app
- Go to Streamlit Cloud dashboard
- Click the menu (three dots) next to your app
- Click "Reboot app"

---

## Alternative: Run Locally First (Testing)

Before deploying, you can test locally:

1. Install Streamlit: `pip install streamlit`
2. Run: `streamlit run streamlit_app.py`
3. Opens in browser at localhost:8501
4. Test with a sample file
5. If it works, deploy to Streamlit Cloud!

---

## What Your Colleagues Will See

A clean web interface with:
- 🎭 Title and description
- 📁 File upload button
- ✅ Success message when done
- 📥 Download button for formatted play
- 📖 Instructions and troubleshooting

**Simple, professional, and works on any device!**

---

## Summary

1. ✅ Create GitHub account
2. ✅ Create repository
3. ✅ Upload 4 files
4. ✅ Deploy to Streamlit Cloud
5. ✅ Share URL with colleagues
6. ✅ Done!

Total time: 10-15 minutes
Total cost: $0 (free!)

Your colleagues will love how easy this is! 🎭
