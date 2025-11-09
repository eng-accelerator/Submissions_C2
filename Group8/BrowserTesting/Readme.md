# Browser Automation AI Agent 🧠

An intelligent browser automation system that converts natural language goals into self-healing Playwright test scripts, now enhanced with AI-powered chatbot assistance.

## Overview

This project implements an AI-powered Browser Automation Agent that:
- Takes a **URL** and a **natural language goal** (e.g., "Test login flow", "Add item to cart")
- **Discovers** the expected user journey
- **Generates** an executable Playwright script
- **Runs** it automatically
- On failure, **diagnoses** the issue and attempts a **self-healing fix**

### Why This Matters

Traditional browser tests have several challenges:
- ✅ Manual to create
- ❌ Fragile when UI changes
- ❌ Expensive to maintain

Our solution addresses these by:
- Reducing repetitive manual testing/scripting work
- Maintaining test stability via adaptive repairs
- Providing transparent, reviewable code (no black box)

## Project Structure

```
├── main.py              # Main Streamlit application
├── chatbot.py          # AI-powered chatbot with web search
├── requirements.txt     # Project dependencies
├── generated_test.py    # Generated test scripts
├── .env                # Environment configuration file
└── agents/             # Core agent modules
    ├── flow_discovery.py     # Discovers user journey steps
    ├── script_generator.py   # Generates Playwright scripts
    ├── execution.py          # Executes and monitors tests
    ├── error_diagnosis.py    # Analyzes test failures
    ├── adaptive_repair.py    # Implements self-healing
    └── regression_monitor.py # Monitors visual regressions
```

## Core Components

0. **AI Chatbot** 🤖
   - Provides intelligent assistance
   - Integrates with OpenAI models (GPT-4, GPT-3.5)
   - Features web search capabilities
   - Helps with test planning and debugging

1. **Flow Discovery Agent** 🔍
   - Interprets natural language goals
   - Maps goals to concrete user steps
   - Understands application context

2. **Script Generator Agent** 🧾
   - Converts steps into Playwright code
   - Generates maintainable test scripts
   - Implements best practices

3. **Execution Agent** ▶️
   - Runs generated scripts
   - Captures logs and screenshots
   - Reports execution status

4. **Error Diagnosis Agent** 🩺
   - Analyzes test failures
   - Identifies root causes
   - Provides human-readable explanations

5. **Adaptive Repair Agent** 🔁
   - Suggests fixes for failing tests
   - Implements self-healing strategies
   - Maintains test stability

6. **Regression Monitor Agent** 🖼️
   - Tracks visual changes over time
   - Detects UI/layout regressions
   - Ensures visual consistency

## Requirements

- Python 3.7+
- Streamlit >= 1.32.0
- Playwright >= 1.42.0
- python-dotenv
- requests

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   - Create a `.env` file in the project root
   - Add the following variables:
     ```
     OPENROUTER_API_KEY=your_openrouter_api_key
     GOOGLE_API_KEY=your_google_api_key
     GOOGLE_CSE_ID=your_google_cse_id
     ```

3. Run the Streamlit application:
   ```bash
   streamlit run main.py
   ```

4. Access the web interface and:
   - Enter your target URL
   - Describe your testing goal
   - Click "Generate & Run"
   - Use the AI chatbot for assistance

## Use Cases

- Automated testing of web applications
- UI regression testing
- User flow validation
- Continuous integration testing
- QA automation
- Self-healing test maintenance
- AI-assisted test planning and debugging
- Real-time testing guidance via chatbot
- Automated web research for test scenarios

## Future Work

- Enhanced visual regression analysis
- Support for additional automation frameworks
- Advanced self-healing strategies
- Integration with CI/CD pipelines
- Extended browser compatibility testing