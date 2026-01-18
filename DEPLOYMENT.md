# 🚀 Deployment Guide - UMBB Exam Scheduler

This guide covers deploying your exam scheduler application with Railway MySQL database.

## 📋 Prerequisites

- Railway MySQL database (already configured ✅)
- GitHub account (for deployment)
- Your application code pushed to GitHub

## 🗄️ Database Configuration

Your Railway MySQL database credentials:
- **Host**: `tramway.proxy.rlwy.net`
- **Port**: `42679`
- **User**: `root`
- **Password**: `EngSdeIrptGoJVoAYYErdRiKFtFbFVbA`
- **Database**: `railway`

> [!WARNING]
> Never commit credentials to version control! Use `.streamlit/secrets.toml` locally (already in `.gitignore`)

---

## 🎯 Deployment Options

You have two deployment options:

### Option 1: Streamlit Community Cloud (Recommended) ⭐

**Pros**: Free, designed for Streamlit, simple setup  
**Cons**: Streamlit apps only

### Option 2: Railway (Full Stack)

**Pros**: Everything in one place, more control  
**Cons**: May not be free tier eligible depending on usage

---

## 🟢 Option 1: Deploy to Streamlit Community Cloud

### Step 1: Push to GitHub

```bash
cd /Users/test/Documents/exam_scheduler
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### Step 2: Initialize Database

Before deploying, initialize your Railway database with the schema and seed data:

```bash
# Make sure you have created .streamlit/secrets.toml first (see below)
python3 -m backend.seed
```

This will create all tables and populate with 13,000 students and demo accounts.

### Step 3: Create Local Secrets File

```bash
# Copy the example file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

The file already contains the Railway credentials. Keep this file local - it's in `.gitignore`.

### Step 4: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click **New app**
4. Select your repository: `whosfouzi/projetBDA`
5. Set **Main file path**: `app.py`
6. Click **Advanced settings** → **Secrets**
7. Paste this TOML configuration:

```toml
[mysql]
host = "tramway.proxy.rlwy.net"
port = 42679
user = "root"
password = "EngSdeIrptGoJVoAYYErdRiKFtFbFVbA"
database = "railway"
```

8. Click **Deploy**!

### Step 5: Verify Deployment

1. Wait for deployment to complete (~2-3 minutes)
2. Visit your app URL (e.g., `https://yourapp.streamlit.app`)
3. Try logging in with: `admin@univ.edu` / `admin`
4. Verify all features work

---

## 🔵 Option 2: Deploy to Railway

### Step 1: Initialize Database (Same as Option 1)

```bash
# Create local secrets file
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Initialize the database
python3 -m backend.seed
```

### Step 2: Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select `whosfouzi/projetBDA`

### Step 3: Configure Environment Variables

In Railway dashboard, add these variables:

```env
MYSQL_HOST=tramway.proxy.rlwy.net
MYSQL_PORT=42679
MYSQL_USER=root
MYSQL_PASSWORD=EngSdeIrptGoJVoAYYErdRiKFtFbFVbA
MYSQL_DATABASE=railway
```

### Step 4: Update Code for Railway

You'll need to modify `backend/db.py` to support environment variables:

```python
import mysql.connector
import streamlit as st
import os

def get_connection():
    # Try environment variables first (for Railway), then fall back to Streamlit secrets
    if os.getenv("MYSQL_HOST"):
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
    else:
        return mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
```

### Step 5: Create Procfile

Create a file named `Procfile` in the project root:

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Step 6: Deploy

```bash
git add .
git commit -m "Configure for Railway deployment"
git push origin main
```

Railway will automatically deploy your app.

---

## 🧪 Testing Your Deployment

### Demo Accounts

Test with these accounts:

| Role | Email | Password |
|------|-------|----------|
| 👤 Directeur | admin@univ.edu | admin |
| 🏛️ Vice-Doyen | doyen@univ.edu | doyen123 |
| 💻 Chef Info | chef.info@univ.edu | chef123 |
| 👨‍🏫 Professeur | amine.ziani@univ.edu | password123 |
| 🎓 Étudiant | sarah.toumi@student.edu | password123 |

### Verification Checklist

- [ ] Login works with demo accounts
- [ ] Dashboard loads correctly
- [ ] Timetable generation works
- [ ] Database queries execute successfully
- [ ] No connection errors in logs

---

## 🛠️ Troubleshooting

### "Connection refused" error

- Check that Railway MySQL is running
- Verify you're using the **public URL** (`tramway.proxy.rlwy.net`), not internal URL
- Confirm port is `42679` for public access

### "Access denied" error

- Verify credentials are correct
- Check that password doesn't have extra spaces
- Ensure user `root` has permissions

### Database tables not found

Run the seed script to initialize:
```bash
python3 -m backend.seed
```

### App crashes on startup

- Check Streamlit Cloud logs or Railway logs
- Verify all dependencies in `requirements.txt`
- Ensure secrets are configured correctly

---

## 📝 Next Steps

After successful deployment:

1. **Custom Domain** (Streamlit Cloud): Add via dashboard settings
2. **Monitoring**: Set up logging and error tracking
3. **Backups**: Configure Railway database backups
4. **Performance**: Monitor database query performance
5. **Security**: Rotate credentials periodically

---

## 🔒 Security Notes

> [!CAUTION]
> - Never commit `.streamlit/secrets.toml` to Git (already in `.gitignore`)
> - Rotate database passwords regularly
> - Use environment-specific credentials (dev vs prod)
> - Monitor database access logs

---

## 📞 Support

If you encounter issues:
- Check Railway database status
- Review application logs
- Verify network connectivity
- Test database connection separately

**Happy Deploying! 🎉**
