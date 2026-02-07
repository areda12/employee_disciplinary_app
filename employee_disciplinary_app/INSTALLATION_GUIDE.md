# Complete GitHub Upload and ERPNext Installation Guide

## Compatibility
✅ **ERPNext v16 Compatible**
✅ Also works with ERPNext v15
✅ Requires HRMS module to be installed

## Step 1: Upload to GitHub (Do this ONCE)

### A. On GitHub Website:
1. Go to https://github.com and log in
2. Click the **"+"** button (top right corner) → Select **"New repository"**
3. Fill in:
   - **Repository name**: `employee_disciplinary_app` (exactly this)
   - **Description**: "Employee Disciplinary Action Report for ERPNext"
   - Keep it **Public** (or Private if you prefer)
   - **DO NOT** check "Add a README file" (we already have one)
   - Click **"Create repository"**

4. After creating, you'll see a page with commands. **Keep this page open!**

### B. On Your Computer (where you downloaded the files):

1. **Extract the zip file** you downloaded from this chat to a folder (e.g., Desktop)

2. **Open Terminal/Command Prompt** and navigate to the extracted folder:
   ```bash
   cd ~/Desktop/employee_disciplinary_app
   ```
   (Adjust the path based on where you extracted it)

3. **Run these commands ONE BY ONE** (copy-paste each line):

   ```bash
   git init
   ```

   ```bash
   git add .
   ```

   ```bash
   git commit -m "Initial commit"
   ```

   ```bash
   git branch -M main
   ```

   Now, run this command:
   ```bash
   git remote add origin https://github.com/areda12/employee_disciplinary_app.git
   ```

   ```bash
   git push -u origin main
   ```

4. When prompted, enter your GitHub username and password
   - **Note**: GitHub now requires a Personal Access Token instead of password
   - If you don't have one, go to: GitHub → Settings → Developer settings → Personal access tokens → Generate new token
   - Give it "repo" permissions and use this token as your password

5. **Done!** Your code is now on GitHub

---

## Step 2: Install on ERPNext (Do this on your ERPNext server)

### A. Connect to your ERPNext server via SSH

### B. Install the app:

1. Navigate to your bench directory:
   ```bash
   cd ~/frappe-bench
   ```

2. Get the app from GitHub:
   ```bash
   bench get-app https://github.com/areda12/employee_disciplinary_app
   ```

3. Install the app on your site (replace YOUR_SITE_NAME with your actual site name):
   ```bash
   bench --site YOUR_SITE_NAME install-app employee_disciplinary_app
   ```

4. Clear cache and restart:
   ```bash
   bench --site YOUR_SITE_NAME clear-cache
   bench restart
   ```

### C. Verify Installation:

1. Log in to your ERPNext
2. Go to **HR** module
3. Search for **"Employee Disciplinary History"** in the search bar
4. You should see the new report!

---

## Troubleshooting

**Problem**: "Permission denied" when pushing to GitHub
**Solution**: Make sure you're using a Personal Access Token instead of password

**Problem**: "bench: command not found"
**Solution**: Make sure you're in the correct directory and bench is installed

**Problem**: App not showing in ERPNext
**Solution**: 
- Clear cache: `bench --site YOUR_SITE_NAME clear-cache`
- Rebuild: `bench build`
- Restart: `bench restart`

**Problem**: Need to update the app later
**Solution**:
- On GitHub: Make changes and commit
- On ERPNext server: 
  ```bash
  cd ~/frappe-bench
  bench update --app employee_disciplinary_app
  bench restart
  ```

---

## Important Notes:

1. **Your GitHub username** - areda12 (already configured in the commands above)
2. **Your site name** - Usually something like `site1.local` or your domain name
3. Keep your GitHub repository public if you want easy installation, or use authentication for private repos

## Need Help?

If you encounter any issues, check:
1. GitHub repository is created and code is uploaded
2. You're using the correct GitHub username in commands
3. You're using the correct site name in ERPNext
4. You have proper permissions on the ERPNext server
