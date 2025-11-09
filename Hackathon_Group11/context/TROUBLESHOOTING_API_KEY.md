# Troubleshooting OpenRouter API Key Issues

## Error: 401 Unauthorized - "User not found"

This error means your OpenRouter API key is invalid, expired, or not set correctly.

## Quick Fix Steps

### Step 1: Verify Your .env File

1. **Check if `.env` file exists** in the project root
2. **Open `.env` file** and verify it contains:
   ```env
   OPEN_ROUTER_KEY=sk-or-your-actual-key-here
   ```

### Step 2: Check API Key Format

OpenRouter API keys should:
- Start with `sk-or-`
- Not have quotes around them
- Not have extra spaces

**Correct:**
```env
OPEN_ROUTER_KEY=sk-or-abc123def456...
```

**Incorrect:**
```env
OPEN_ROUTER_KEY="sk-or-abc123def456..."  # ❌ No quotes
OPEN_ROUTER_KEY= sk-or-abc123def456...   # ❌ No leading space
OPEN_ROUTER_KEY=sk-or-abc123def456...    # ❌ Trailing space
```

### Step 3: Get a Valid API Key

1. Visit https://openrouter.ai/keys
2. Sign up or log in
3. Create a new API key
4. Copy the key (it should start with `sk-or-`)
5. Paste it in your `.env` file

### Step 4: Test Your API Key

Run the test script:

```bash
python utils/test_api_key.py
```

This will:
- Check if the key is set
- Validate the format
- Test the API connection
- Provide detailed error messages

### Step 5: Verify Key is Active

1. Go to https://openrouter.ai/keys
2. Check that your key is:
   - ✅ Active (not revoked)
   - ✅ Has credits/balance
   - ✅ Not expired

## Common Issues

### Issue 1: Key Not Found

**Error:** `OPEN_ROUTER_KEY not found`

**Solution:**
- Create `.env` file in project root
- Add: `OPEN_ROUTER_KEY=your_key_here`
- Restart your application

### Issue 2: Key Still Has Placeholder Value

**Error:** Key is `your_openrouter_key_here`

**Solution:**
- Update `.env` file with your actual API key
- Remove the placeholder value

### Issue 3: Key Format Invalid

**Error:** Key doesn't start with `sk-or-`

**Solution:**
- Verify you're using an OpenRouter key (not OpenAI key)
- Get a new key from https://openrouter.ai/keys
- Ensure no quotes or spaces

### Issue 4: Key Has No Credits

**Error:** `401 Unauthorized` or `Insufficient credits`

**Solution:**
- Check your balance at https://openrouter.ai/keys
- Add credits to your account
- Verify the key has sufficient balance

### Issue 5: Key Revoked/Expired

**Error:** `User not found` or `401 Unauthorized`

**Solution:**
- Check key status at https://openrouter.ai/keys
- Create a new API key
- Update `.env` file with new key

## Testing Your Setup

### Quick Test

```bash
python utils/test_api_key.py
```

### Full System Test

```bash
python test_system.py
```

### Manual Test

1. Check environment variable:
   ```bash
   # Windows
   echo %OPEN_ROUTER_KEY%
   
   # macOS/Linux
   echo $OPEN_ROUTER_KEY
   ```

2. Verify .env file is loaded:
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   print(os.getenv("OPEN_ROUTER_KEY"))
   ```

## Still Having Issues?

1. **Double-check your .env file:**
   - File is named exactly `.env` (not `.env.txt`)
   - File is in the project root directory
   - No typos in variable name: `OPEN_ROUTER_KEY`

2. **Restart your application:**
   - Environment variables are loaded at startup
   - Changes require restart

3. **Check for multiple .env files:**
   - Only one `.env` file should exist
   - Check project root and subdirectories

4. **Verify virtual environment:**
   - Make sure venv is activated
   - `.env` file should be in project root, not venv

5. **Test with a simple script:**
   ```python
   from dotenv import load_dotenv
   import os
   load_dotenv()
   key = os.getenv("OPEN_ROUTER_KEY")
   print(f"Key found: {key is not None}")
   print(f"Key starts with sk-or-: {key and key.startswith('sk-or-')}")
   ```

## Need Help?

- OpenRouter Docs: https://openrouter.ai/docs
- Get API Key: https://openrouter.ai/keys
- Check Status: https://openrouter.ai/status

---

**After fixing, test again with:** `python utils/test_api_key.py`

