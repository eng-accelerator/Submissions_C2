# 🔐 Setting Up .env File for API Keys

This guide shows you how to securely store your API keys using a `.env` file.

---

## 📋 Steps to Set Up

### Step 1: Install python-dotenv

```bash
pip install python-dotenv
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 2: Create .env File

Create a file named `.env` in the `Day_6/session_2/` folder with the following content:

**Windows (File Explorer):**
1. Navigate to `C:\Users\gengi\OneDrive\Desktop\ai-accelerator-C2\Day_6\session_2\`
2. Right-click → New → Text Document
3. Name it `.env` (with the dot at the start)
4. If Windows hides extensions, you may need to:
   - Enable "Show file extensions" in File Explorer settings
   - Or use a text editor to create the file

**Windows (Command Prompt):**
```cmd
cd C:\Users\gengi\OneDrive\Desktop\ai-accelerator-C2\Day_6\session_2
echo OPENROUTER_API_KEY=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 > .env
```

**Windows (PowerShell):**
```powershell
cd "C:\Users\gengi\OneDrive\Desktop\ai-accelerator-C2\Day_6\session_2"
"OPENROUTER_API_KEY=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" | Out-File -FilePath .env -Encoding utf8
```

**Using a Text Editor:**
1. Open Notepad, VS Code, or any text editor
2. Paste this content:
   ```
   OPENROUTER_API_KEY=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
   ```
3. Save the file as `.env` (with the dot at the start) in the `session_2` folder
4. Make sure it's saved as a plain text file (not `.env.txt`)

### Step 3: Verify .env File

Your `.env` file should:
- Be located at: `Day_6/session_2/.env`
- Contain exactly:
  ```
  OPENROUTER_API_KEY=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
  ```
- Have no extra spaces or quotes around the key

### Step 4: Verify .gitignore

I've already created a `.gitignore` file that includes `.env`, so your API key won't be committed to Git. The `.gitignore` file includes:
```
# Environment variables - DO NOT COMMIT API KEYS!
.env
```

---

## ✅ Verification

After creating the `.env` file:

1. **Re-run Cell 1** in your notebook (to load dotenv)
2. **Re-run Cell 2** (to load settings)

You should now see:
```
✅ OPENROUTER_API_KEY found - full advanced RAG functionality available
✅ Advanced RAG settings configured
```

---

## 🔒 Security Best Practices

✅ **DO:**
- Keep `.env` file local (never commit to Git)
- Add `.env` to `.gitignore` (already done)
- Use different API keys for different projects
- Rotate API keys regularly

❌ **DON'T:**
- Commit `.env` files to version control
- Share API keys in code or documentation
- Hardcode API keys in notebooks (use `.env` instead)
- Post API keys publicly

---

## 🐛 Troubleshooting

### Issue: "python-dotenv not installed"
**Solution**: Run `pip install python-dotenv`

### Issue: "OPENROUTER_API_KEY not found" after creating .env
**Solutions**:
1. Make sure `.env` file is in the correct location: `Day_6/session_2/.env`
2. Check the file is named exactly `.env` (not `.env.txt` or `env`)
3. Verify the content format: `OPENROUTER_API_KEY=your_key_here` (no spaces around `=`)
4. Restart the Jupyter kernel and re-run the cells

### Issue: File Explorer doesn't show .env file
**Solution**: 
- Enable "Show hidden files" in File Explorer settings
- Or use command line to verify the file exists

### Issue: Windows shows "File name cannot contain: ."
**Solution**: 
- Use command line (cmd or PowerShell) to create the file
- Or create it as `env` and rename it to `.env` after saving

---

## 📝 File Structure

After setup, your folder should look like:
```
Day_6/session_2/
├── .env                    ← Your API key (NOT in Git)
├── .gitignore              ← Protects .env from being committed
├── requirements.txt
├── assignments/
├── data/
└── ...
```

---

## 🎯 Alternative: Environment Variables

If you prefer to set environment variables directly (without .env file):

**Windows (Command Prompt):**
```cmd
set OPENROUTER_API_KEY=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
```

**Windows (PowerShell):**
```powershell
$env:OPENROUTER_API_KEY="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"
```

**Note**: These only last for the current session. `.env` file is more convenient.

---

**That's it! Your API key is now securely stored and won't be committed to Git.** 🔐

