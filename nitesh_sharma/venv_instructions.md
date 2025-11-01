# Virtual Environment Instructions

## Important Note
Always use Command Prompt (cmd) instead of PowerShell to avoid execution policy restrictions.

## How to Activate the Virtual Environment

1. Open Command Prompt (cmd)
2. Navigate to your project directory:
   ```cmd
   cd "C:\Users\NSHAR\OneDrive - paramanands limited\nnr bkp\Documents\GitHub\Submissions_C2\nitesh_sharma"
   ```
3. Activate the virtual environment:
   ```cmd
   env_v1\Scripts\activate
   ```
   When activated successfully, you'll see `(env_v1)` at the beginning of your command prompt.

## How to Deactivate the Virtual Environment

1. Simply type:
   ```cmd
   deactivate
   ```
   The `(env_v1)` prefix will disappear from your command prompt.

## Installing Requirements

After activating the virtual environment, install the required packages:
```cmd
pip install -r env_v1_requirement.txt
```

This will install all the required packages including:
- openai
- streamlit
- pandas
- numpy
- python-dotenv
- and other dependencies
# Run the Streamlit app

After activating the virtual environment, you can run the Streamlit app included in this repo.

From the project root:
```cmd
cd src
streamlit run assignment1_v3.py
```

Or, from the project root in a single line (Windows cmd):
```cmd
cd src && streamlit run assignment1_v3.py
```

This will launch the Streamlit app in your browser. Use Ctrl+C in the terminal to stop it.

# Tips
- Always make sure you're using Command Prompt (cmd) and not PowerShell
- The virtual environment must be activated each time you open a new command prompt
- You can verify if the virtual environment is active by checking for the `(env_v1)` prefix in your command prompt
- Install packages only when the virtual environment is activated