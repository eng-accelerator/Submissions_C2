# agents/llm/IChatbot.py

import os
from typing import List, Tuple, Dict, Optional, Any

try:
    from agents.llm.llm_client import llm_chat
except ImportError:
    try:
        from llm.llm_client import llm_chat
    except ImportError:
        def llm_chat(system_prompt: str, user_prompt: str, max_tokens: int = 1500) -> str:
            return "LLM client not configured. Please set up OpenRouter API key."


class Chatbot:
    """
    AI chatbot assistant for browser automation guidance.
    Maintains conversation context and provides helpful responses.
    Enhanced with domain knowledge and test execution context.
    """
    
    def __init__(self):
        self.conversation_history: List[Tuple[str, str]] = []
        self.last_test_result: Optional[Dict[str, Any]] = None
        self.system_prompt = """You are a friendly and helpful AI assistant for the AI Browser Automation Lab system. 
You can chat about general topics, but your expertise is in browser automation and testing.

**YOUR CONVERSATIONAL STYLE:**
- Be warm, approachable, and helpful for ANY question
- Answer general questions briefly and naturally
- When appropriate, connect general topics to browser automation concepts
- Gently guide users back to the lab's capabilities when relevant
- Use a conversational tone, not overly technical unless asked
- It's okay to chat about non-testing topics, but look for opportunities to be helpful with automation

**EXAMPLE RESPONSES:**
User: "What's the weather like?"
You: "I don't have access to real-time weather data, but if you're building a weather app, I can help you write automated tests for it! Want to learn how to test web forms or API responses?"

User: "I'm feeling stuck"
You: "I understand that feeling! Sometimes taking a break helps. If you're stuck on a test that's failing, I can help analyze what went wrong. Want to try one of our example scenarios to get back in flow?"

**SYSTEM CAPABILITIES:**
- Automated test script generation using Playwright (Python sync API)
- Self-healing tests that automatically repair broken selectors
- Visual regression testing with baseline comparison and diff highlighting
- Support for 10+ pre-built test scenarios across multiple test sites

**AVAILABLE TEST SCENARIOS:**
1. **Login Validation** (the-internet.herokuapp.com) - Basic auth flow testing
2. **Add to Cart** (saucedemo.com) - E-commerce cart functionality
3. **Visual Regression Demo** (saucedemo.com) - Alternates between views to demonstrate visual changes
4. **Contact Form** (automationexercise.com) - Form submission testing
5. **Checkout with Self-Heal** (demoblaze.com) - Intentionally broken script that auto-repairs
6. **Dynamic Content** (herokuapp) - Handles dynamically loaded elements
7. **Drag and Drop** (herokuapp) - Tests drag-drop interactions
8. **File Upload** (herokuapp) - Upload functionality testing
9. **Dropdown Selection** (herokuapp) - Dropdown interaction testing
10. **Multiple Windows** (herokuapp) - Multi-window/tab handling

**KEY FEATURES:**

*Self-Healing:*
- Automatically fixes broken selectors and timing issues
- Uses deterministic patterns for known sites (e.g., Demoblaze)
- LLM-based repair for unknown failures
- Applies minimal changes to preserve test intent

*Visual Regression:*
- First run creates a baseline screenshot
- Subsequent runs compare against baseline
- Configurable pixel difference threshold (default 0.1%)
- Generates red-highlighted diff images
- Detects layout shifts and visual changes

*Error Diagnosis:*
- Analyzes failure logs for common patterns
- Identifies selector, timing, navigation, and auth issues
- Provides actionable feedback for manual fixes

**YOUR ROLE:**
- Chat naturally about any topic, but be most helpful with browser automation
- Help users understand system capabilities
- Guide them through test scenarios
- Explain failures and suggest fixes
- Provide Playwright code examples when relevant
- Be conversational and encouraging
- Connect their interests to testing opportunities when possible

When users share errors, analyze them and suggest using self-heal or visual regression features.
Format responses clearly with bullet points for lists, code blocks for examples.

Remember: You're a helpful companion, not just a documentation bot. Be friendly!"""
    
    def set_test_context(self, test_result: Dict[str, Any]):
        """
        Inject context from recent test execution.
        
        Args:
            test_result: Dict with keys like:
                - 'success': bool
                - 'log': str (execution output/errors)
                - 'screenshot_path': str or None
                - 'visual_check': dict or None
                - 'self_heal_applied': bool or str (note about healing)
                - 'scenario': str (optional - which example was run)
                - 'error_diagnosis': str (optional)
        """
        self.last_test_result = test_result
    
    def clear_test_context(self):
        """Clear the stored test context."""
        self.last_test_result = None
    
    def reply(self, user_message: str) -> str:
        """
        Generate a response to the user's message.
        Enhanced with quick answers and test context.
        
        Args:
            user_message: The user's input message
            
        Returns:
            The assistant's response
        """
        # Check for quick answers first (avoids LLM call)
        quick_answer = self._check_quick_answers(user_message)
        if quick_answer:
            self.conversation_history.append(("user", user_message))
            self.conversation_history.append(("assistant", quick_answer))
            return quick_answer
        
        # Build enhanced context with test results
        context = self._build_enhanced_context()
        
        # Create full user prompt with context
        full_prompt = f"{context}\n\nUser: {user_message}\n\nAssistant:"
        
        # Get response from LLM
        try:
            response = llm_chat(
                system_prompt=self.system_prompt,
                user_prompt=full_prompt,
                max_tokens=800
            )
            
            if not response:
                response = self._get_fallback_response(user_message)
            
        except Exception as e:
            response = self._get_error_response(str(e))
        
        # Store conversation
        self.conversation_history.append(("user", user_message))
        self.conversation_history.append(("assistant", response))
        
        # Keep only last 10 messages (5 exchanges) to manage context
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
        
        return response
    
    def _check_quick_answers(self, user_message: str) -> Optional[str]:
        """
        Return quick answers for common questions without LLM call.
        This improves response time and reduces API costs.
        """
        msg_lower = user_message.lower()
        
        # Define quick answer patterns
        quick_answers = {
            ("how does self-heal", "self heal work", "self-healing work"): (
                "**Self-Healing System:**\n\n"
                "The system repairs broken tests automatically in two ways:\n\n"
                "1. **Deterministic Fixes** (for known sites):\n"
                "   - Detects failures on recognized sites (e.g., Demoblaze)\n"
                "   - Replaces with pre-tested, hardened scripts\n"
                "   - Uses stable selectors and proper waits\n\n"
                "2. **LLM-Based Repair** (for other sites):\n"
                "   - Sends error log and script to AI\n"
                "   - Gets minimal selector/timing fixes\n"
                "   - Preserves test intent and structure\n\n"
                "**Try it:** Run Example 5 (Demoblaze) - it's intentionally broken and auto-repairs!"
            ),
            
            ("visual regression", "screenshot comparison", "baseline comparison"): (
                "**Visual Regression Testing:**\n\n"
                "Compares screenshots to detect UI changes:\n\n"
                "1. **First Run**: Creates baseline image (`_baseline_v2.png`)\n"
                "2. **Subsequent Runs**: Compares against baseline\n"
                "3. **Threshold Check**: Default 0.1% pixel difference allowed\n"
                "4. **Diff Image**: Red highlights show changed areas (`_diff_v2.png`)\n\n"
                "**Modes:**\n"
                "- Self-baseline: Compares against own previous run\n"
                "- Explicit comparison: Compare against specific baseline ID\n"
                "- Force baseline: Re-create baseline\n\n"
                "**Try it:** Run Example 3 (Saucedemo) twice - it alternates cart/inventory views to show visual differences!"
            ),
            
            ("which example", "what example", "which scenario", "where to start", "getting started"): (
                "**Recommended Examples by Goal:**\n\n"
                "🟢 **Beginners:**\n"
                "   - Example 1: Login test (simple, stable)\n"
                "   - Example 2: Add to cart (e-commerce basics)\n\n"
                "🔧 **Self-Healing Demo:**\n"
                "   - Example 5: Demoblaze checkout (auto-repairs broken selectors)\n\n"
                "👁️ **Visual Regression:**\n"
                "   - Example 3: Saucedemo (run twice to see baseline → comparison)\n\n"
                "⚡ **Advanced Interactions:**\n"
                "   - Example 7: Drag and drop\n"
                "   - Example 8: File upload\n"
                "   - Example 10: Multiple windows\n\n"
                "💡 **Tip:** Check the 'Enable Self-Heal' and 'Enable Visual Regression' options!"
            ),
            
            ("examples list", "all examples", "list examples", "available scenarios"): (
                "**All 10 Test Scenarios:**\n\n"
                "1. Login Validation (herokuapp)\n"
                "2. Add to Cart (saucedemo)\n"
                "3. Visual Regression Demo (saucedemo) ⭐\n"
                "4. Contact Form (automationexercise)\n"
                "5. Checkout with Self-Heal (demoblaze) ⭐\n"
                "6. Dynamic Content (herokuapp)\n"
                "7. Drag and Drop (herokuapp)\n"
                "8. File Upload (herokuapp)\n"
                "9. Dropdown Selection (herokuapp)\n"
                "10. Multiple Windows (herokuapp)\n\n"
                "⭐ = Recommended for feature demos\n\n"
                "💡 **You can also test ANY website!** Just enter your own URL and describe what you want to test."
            ),
            
            ("custom url", "own website", "test my site", "any website", "different site"): (
                "**Testing Custom URLs:**\n\n"
                "Yes! You can test ANY website, not just the examples:\n\n"
                "1. **Enter your URL** in the 'Target URL' field\n"
                "2. **Describe your goal** - Be specific about what to test\n"
                "3. **Click Generate & Run** - AI will create a custom script\n\n"
                "**Examples of custom goals:**\n"
                "- 'Fill out the contact form and submit'\n"
                "- 'Search for \"laptop\" and verify results appear'\n"
                "- 'Click the login button and check for error message'\n"
                "- 'Add product to cart and verify cart count increases'\n\n"
                "**Tips for best results:**\n"
                "✅ Be specific about actions (click, fill, verify)\n"
                "✅ Mention element text or labels if you know them\n"
                "✅ Describe expected outcomes\n\n"
                "The AI will generate Playwright code tailored to your site!"
            ),
            
            ("playwright", "playwright syntax", "how to write"): (
                "**Playwright Basics (Python Sync API):**\n\n"
                "```python\n"
                "# Navigate\n"
                "page.goto('https://example.com', wait_until='load')\n\n"
                "# Fill inputs\n"
                "page.fill('#username', 'myuser')\n\n"
                "# Click elements\n"
                "page.click('button:has-text(\"Login\")')\n\n"
                "# Wait for elements\n"
                "page.wait_for_selector('.success-message', timeout=5000)\n\n"
                "# Screenshots\n"
                "page.screenshot(path='result.png', full_page=True)\n"
                "```\n\n"
                "**Selector Tips:**\n"
                "- ID: `#username`\n"
                "- Class: `.btn-primary`\n"
                "- Text: `button:has-text(\"Submit\")`\n"
                "- Attribute: `[data-testid=\"login-btn\"]`"
            ),
            
            ("timeout", "element not found", "selector issue"): (
                "**Common Selector/Timing Issues:**\n\n"
                "1. **Element not loaded yet**\n"
                "   → Add: `page.wait_for_selector('.element', timeout=5000)`\n\n"
                "2. **Wrong selector**\n"
                "   → Use browser DevTools to verify\n"
                "   → Try text-based: `:has-text(\"Button Text\")`\n\n"
                "3. **Element in iframe**\n"
                "   → Use: `frame = page.frame_locator('iframe')`\n\n"
                "4. **Dynamic content**\n"
                "   → Add delay: `page.wait_for_timeout(1000)`\n\n"
                "💡 **Quick fix:** Enable Self-Heal to auto-repair timing issues!"
            ),
            
            ("failed", "error", "not working", "help debug"): (
                "**Debugging Failed Tests:**\n\n"
                "1. **Check error log** - Look for specific error messages\n"
                "2. **View screenshot** - See what state the page was in\n"
                "3. **Try self-heal** - Enable 'Self-Heal' option\n"
                "4. **Check selectors** - Verify elements exist on page\n"
                "5. **Add waits** - Elements might need time to load\n\n"
                "Share your error message and I can provide specific guidance!"
            ),
        }
        
        # Check each pattern group
        for patterns, answer in quick_answers.items():
            if any(pattern in msg_lower for pattern in patterns):
                return answer
        
        return None
    
    def _build_enhanced_context(self) -> str:
        """Build context including conversation history and test results."""
        parts = []
        
        # Add conversation history
        if self.conversation_history:
            for role, message in self.conversation_history[-6:]:  # Last 3 exchanges
                prefix = "User" if role == "user" else "Assistant"
                parts.append(f"{prefix}: {message}")
        
        # Add recent test execution context
        if self.last_test_result:
            parts.append("\n--- RECENT TEST EXECUTION ---")
            result = self.last_test_result
            
            # Test status
            status = "✅ PASSED" if result.get('success') else "❌ FAILED"
            parts.append(f"Status: {status}")
            
            # Scenario info
            if result.get('scenario'):
                parts.append(f"Scenario: {result['scenario']}")
            
            # Self-heal info
            if result.get('self_heal_applied'):
                heal_note = result['self_heal_applied']
                if isinstance(heal_note, str):
                    parts.append(f"Self-Heal: ✓ {heal_note}")
                else:
                    parts.append("Self-Heal: ✓ Applied")
            
            # Visual regression info
            if result.get('visual_check'):
                vc = result['visual_check']
                vc_status = vc.get('status', 'unknown').upper()
                parts.append(f"Visual Check: {vc_status}")
                
                if vc.get('message'):
                    parts.append(f"  → {vc['message']}")
            
            # Error diagnosis
            if result.get('error_diagnosis'):
                parts.append(f"Diagnosis: {result['error_diagnosis']}")
            
            # Error log snippet (if failed)
            if not result.get('success') and result.get('log'):
                error_log = result['log']
                # Extract key error lines
                error_lines = [line for line in error_log.split('\n') 
                              if any(kw in line.lower() for kw in 
                                    ['error', 'timeout', 'failed', 'exception', 'traceback'])]
                if error_lines:
                    snippet = '\n'.join(error_lines[:3])  # First 3 error lines
                    parts.append(f"Error Details:\n{snippet}")
        
        return "\n".join(parts) if parts else ""
    
    def _get_fallback_response(self, user_message: str) -> str:
        """Provide a helpful fallback when LLM is unavailable."""
        msg_lower = user_message.lower()
        
        # Context-aware fallbacks
        if any(word in msg_lower for word in ['error', 'failed', 'not working']):
            return (
                "I'm having connection issues, but here's quick help:\n\n"
                "1. Enable **Self-Heal** to auto-fix broken selectors\n"
                "2. Check the error screenshot to see page state\n"
                "3. Try adding waits: `page.wait_for_selector('.element')`\n\n"
                "Share your error message when I'm back online for detailed help!"
            )
        
        if any(word in msg_lower for word in ['example', 'start', 'try']):
            return (
                "Connection issue - Quick suggestions:\n\n"
                "• **Beginners:** Try Example 1 (Login) or Example 2 (Cart)\n"
                "• **Self-Heal Demo:** Run Example 5 (Demoblaze)\n"
                "• **Visual Regression:** Run Example 3 twice (Saucedemo)\n\n"
                "Ask me again in a moment for detailed guidance!"
            )
        
        return (
            "I'm having trouble connecting to my AI backend right now. "
            "Try the pre-built examples or check out the Playwright documentation. "
            "I'll be back shortly!"
        )
    
    def _get_error_response(self, error: str) -> str:
        """Provide helpful response when an error occurs."""
        return (
            "I encountered an error connecting to my AI service. "
            "Meanwhile, here are some quick tips:\n\n"
            "• Use **Self-Heal** for automatic script repair\n"
            "• Enable **Visual Regression** to compare screenshots\n"
            "• Check error logs and screenshots for debugging\n\n"
            f"Technical error: {error[:100]}"
        )
    
    def suggest_next_steps(self, scenario: str = None) -> str:
        """
        Provide contextual suggestions based on user's current work.
        
        Args:
            scenario: Current scenario context (e.g., 'failed_test', 'visual_regression')
        """
        suggestions = {
            "failed_test": (
                "**Next Steps for Failed Test:**\n"
                "1. Enable 'Self-Heal' and re-run\n"
                "2. Check the error screenshot\n"
                "3. Review error log for specific issues\n"
                "4. Try adding explicit waits for dynamic content"
            ),
            "visual_regression": (
                "**Visual Regression Workflow:**\n"
                "1. First run: Creates baseline\n"
                "2. Second run: Compares against baseline\n"
                "3. Check diff image if failed\n"
                "4. Update baseline if changes are intentional (re-run with 'Force Baseline')"
            ),
            "new_user": (
                "**Getting Started:**\n"
                "1. Try Example 1 (Login) for a simple test\n"
                "2. Run Example 3 twice for visual regression demo\n"
                "3. Try Example 5 to see self-healing in action\n"
                "4. Experiment with custom URLs and goals"
            ),
            "demoblaze": (
                "**Demoblaze Self-Heal Demo:**\n"
                "This scenario is intentionally broken to demonstrate self-healing:\n"
                "1. First run will fail with selector error\n"
                "2. Self-heal detects Demoblaze and applies hardened script\n"
                "3. Re-run succeeds with stable selectors\n\n"
                "Watch the logs to see the repair process!"
            ),
            "saucedemo_visual": (
                "**Saucedemo Visual Regression:**\n"
                "This example alternates between cart and inventory views:\n"
                "• Run 1: Shows cart (creates baseline)\n"
                "• Run 2: Shows inventory (triggers visual diff)\n"
                "• Run 3: Shows cart again (may pass if same as baseline)\n\n"
                "Check the diff image to see red highlighting on changes!"
            ),
        }
        
        return suggestions.get(scenario, suggestions["new_user"])
    
    def get_example_info(self, example_number: int) -> str:
        """
        Get detailed information about a specific example.
        
        Args:
            example_number: Example number (1-10)
        """
        examples = {
            1: {
                "name": "Login Validation",
                "site": "the-internet.herokuapp.com",
                "description": "Tests basic authentication flow with username/password",
                "features": ["Form filling", "Button clicks", "Success verification"],
                "tip": "Great for learning basic Playwright selectors"
            },
            2: {
                "name": "Add to Cart",
                "site": "saucedemo.com",
                "description": "E-commerce flow: login → add product → verify cart",
                "features": ["Multi-step flow", "Product selection", "Cart verification"],
                "tip": "Shows how to chain actions in a realistic scenario"
            },
            3: {
                "name": "Visual Regression Demo",
                "site": "saucedemo.com",
                "description": "Alternates between cart and inventory views to demonstrate visual changes",
                "features": ["Visual regression", "Baseline creation", "Diff highlighting"],
                "tip": "Run twice to see baseline creation → comparison workflow"
            },
            4: {
                "name": "Contact Form",
                "site": "automationexercise.com",
                "description": "Tests form submission with multiple fields",
                "features": ["Form filling", "Submission", "Success message verification"],
                "tip": "Good example of handling contact/feedback forms"
            },
            5: {
                "name": "Checkout with Self-Heal",
                "site": "demoblaze.com",
                "description": "Intentionally broken script that demonstrates automatic repair",
                "features": ["Self-healing", "Selector repair", "Multi-step checkout"],
                "tip": "Enable Self-Heal to see automatic script repair in action!"
            },
            6: {
                "name": "Dynamic Content",
                "site": "the-internet.herokuapp.com",
                "description": "Handles dynamically loaded content",
                "features": ["Dynamic waits", "Content verification", "Timing handling"],
                "tip": "Shows how to wait for elements that load asynchronously"
            },
            7: {
                "name": "Drag and Drop",
                "site": "the-internet.herokuapp.com",
                "description": "Tests drag-and-drop interactions",
                "features": ["Mouse actions", "Element manipulation", "Position verification"],
                "tip": "Demonstrates advanced mouse interaction patterns"
            },
            8: {
                "name": "File Upload",
                "site": "the-internet.herokuapp.com",
                "description": "Tests file upload functionality",
                "features": ["File input", "Temporary file creation", "Upload verification"],
                "tip": "Shows how to handle file inputs and uploads"
            },
            9: {
                "name": "Dropdown Selection",
                "site": "the-internet.herokuapp.com",
                "description": "Tests dropdown/select element interaction",
                "features": ["Dropdown handling", "Option selection", "Value verification"],
                "tip": "Simple example of working with select elements"
            },
            10: {
                "name": "Multiple Windows",
                "site": "the-internet.herokuapp.com",
                "description": "Tests handling multiple browser windows/tabs",
                "features": ["Window management", "Context switching", "Multi-window verification"],
                "tip": "Shows how to work with multiple browser contexts"
            },
        }
        
        if example_number not in examples:
            return f"Example {example_number} not found. Available examples: 1-10"
        
        ex = examples[example_number]
        return (
            f"**Example {example_number}: {ex['name']}**\n\n"
            f"**Site:** {ex['site']}\n"
            f"**Description:** {ex['description']}\n\n"
            f"**Features:**\n" + "\n".join(f"  • {f}" for f in ex['features']) + "\n\n"
            f"💡 **Tip:** {ex['tip']}"
        )
    
    def clear_history(self):
        """Clear conversation history and test context."""
        self.conversation_history = []
        self.last_test_result = None


__all__ = ["Chatbot"]