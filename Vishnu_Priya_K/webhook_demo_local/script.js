// Sample post templates for different types
const postTemplates = {
  professional: {
    short: ["Recently, I've been reflecting on {theme}.\n\nHere's what I've learned:\n→ Key insight 1\n→ Key insight 2\n→ Key insight 3\n\nWhat's your experience with this? Let's discuss in the comments.", "Quick thought on {theme}:\n\nThe landscape is changing faster than ever. Those who adapt will thrive.\n\n3 things to consider:\n1. First consideration\n2. Second consideration\n3. Third consideration\n\nWhat do you think?"],
    medium: ["I've been working in this industry for years, and {theme} continues to fascinate me.\n\nHere's what I've observed:\n\n✓ Observation 1: The market is shifting\n✓ Observation 2: New approaches are emerging\n✓ Observation 3: Traditional methods are evolving\n\nThe key takeaway? Staying curious and adaptable is more important than ever.\n\nIf you're navigating similar challenges, I'd love to hear your perspective.\n\nWhat strategies have worked for you?", "Let's talk about {theme}.\n\nI recently had a conversation that completely changed my perspective on this topic.\n\nHere's what I learned:\n\n→ The importance of continuous learning\n→ The value of diverse perspectives\n→ The power of asking the right questions\n\nThe most successful professionals I know share one trait: they never stop questioning and improving.\n\nWhat's one thing you've learned recently that changed your approach?"],
    long: ["A deep dive into {theme}:\n\nAfter years of experience and countless conversations with industry leaders, I've identified some patterns worth sharing.\n\n🔍 The Current Landscape:\nWe're at an inflection point. The old playbook doesn't work anymore, and the new one is still being written.\n\n💡 Key Insights:\n\n1. Adaptability is the new currency\n   Organizations that can pivot quickly will outperform those that can't.\n\n2. Data-driven decision making is essential\n   Gut feelings are valuable, but they need to be validated with data.\n\n3. Human connection still matters\n   Technology is amazing, but authentic relationships drive real results.\n\n🎯 What This Means for You:\n\n→ Invest in continuous learning\n→ Build diverse networks\n→ Stay curious and open-minded\n\nThe future belongs to those who can blend technical expertise with emotional intelligence.\n\nWhat's your take on this? I'd love to hear your thoughts."],
  },
  story: {
    short: ["5 years ago, I made a decision that changed everything.\n\nI decided to focus on {theme}.\n\nPeople thought I was crazy. Maybe I was.\n\nBut here's what happened:\n→ Outcome 1\n→ Outcome 2\n→ Outcome 3\n\nSometimes the best decisions are the ones that don't make sense to everyone else.", "A quick story about {theme}:\n\nLast week, something unexpected happened that reminded me why I love what I do.\n\nThe lesson? Always stay open to surprises.\n\nHave you had a similar experience?"],
    medium: [
      "I failed. Publicly. Spectacularly.\n\nIt was related to {theme}, and honestly, I wanted to hide.\n\nBut here's what that failure taught me:\n\n→ Lesson 1: Failure is feedback, not final\n→ Lesson 2: Vulnerability builds trust\n→ Lesson 3: Recovery matters more than perfection\n\nToday, I'm grateful for that failure. It shaped who I am and how I work.\n\nIf you're facing a setback right now, remember: this isn't your ending. It's just a chapter.\n\nWhat failure taught you the most?",
      "The truth about {theme} that nobody talks about:\n\nI started from zero. No connections, no shortcuts, just determination.\n\nHere's my journey:\n\n📍 Where I started: Ground zero\n📍 The challenge: Everything seemed impossible\n📍 The breakthrough: One small win at a time\n📍 Where I am now: Still learning, but much further\n\nThe lesson? Progress isn't linear. Some days you'll feel like you're moving backwards.\n\nKeep going anyway.\n\nWhat's one challenge you're working through right now?",
    ],
    long: [
      "Let me tell you a story about {theme} that changed my entire career.\n\nThree years ago, I was stuck. I had the skills, the drive, but something wasn't clicking.\n\nThen I had a conversation with a mentor who asked me a simple question:\n\n\"What are you optimizing for?\"\n\nI didn't have an answer. And that was the problem.\n\n🔄 What Changed:\n\nI started being intentional about every decision:\n\n→ Who I spent time with\n→ What projects I took on\n→ How I measured success\n\nThe results were remarkable:\n\n✓ Increased clarity in my goals\n✓ Better alignment with my values\n✓ More meaningful work and relationships\n\n💭 The Lesson:\n\nSuccess isn't about doing more. It's about doing the right things for the right reasons.\n\nWhen you're clear on what you're optimizing for, decisions become easier. Focus becomes natural. Results follow.\n\n📌 My Question to You:\n\nWhat are YOU optimizing for?\n\nTake a moment to think about it. Your answer might surprise you.\n\nShare in the comments - I'd love to hear your perspective.",
    ],
  },
  tips: {
    short: ["3 quick tips for {theme}:\n\n1. Tip number one\n2. Tip number two\n3. Tip number three\n\nTry these and let me know how it goes!\n\nWhich one will you implement first?", "Want to improve at {theme}?\n\nHere's what works:\n\n→ Do this\n→ Avoid that\n→ Remember this\n\nSimple but effective.\n\nWhat would you add to this list?"],
    medium: [
      "5 game-changing tips for {theme}:\n\n1️⃣ Start with clarity\nKnow exactly what you want to achieve before you begin.\n\n2️⃣ Focus on fundamentals\nMaster the basics before chasing advanced techniques.\n\n3️⃣ Measure what matters\nTrack progress, but don't get obsessed with metrics.\n\n4️⃣ Learn from others\nFind mentors and study what works.\n\n5️⃣ Stay consistent\nSmall daily actions beat occasional massive efforts.\n\nBonus tip: Don't try to implement everything at once. Pick one and master it.\n\nWhich tip resonates most with you?",
      "Here's what I wish someone told me about {theme} when I started:\n\n💡 Tip #1: Start before you're ready\nWaiting for perfect conditions means never starting.\n\n💡 Tip #2: Embrace the awkward phase\nEveryone starts as a beginner. Push through.\n\n💡 Tip #3: Find your community\nSurround yourself with people who get it.\n\n💡 Tip #4: Document your journey\nYour struggles today will help someone tomorrow.\n\nThe biggest mistake? Thinking you need to have it all figured out.\n\nYou don't. Just start.\n\nWhat's holding you back from starting?",
    ],
    long: [
      "The Ultimate Guide to {theme} (from my experience):\n\nI've spent years figuring this out. Here's everything I wish I knew from day one.\n\n🎯 Foundational Principles:\n\n1. Principle One: Clarity beats complexity\n   → Start with simple, clear goals\n   → Avoid overcomplicating the process\n   → Focus on what truly matters\n\n2. Principle Two: Consistency compounds\n   → Small daily actions create big results\n   → Show up even when you don't feel like it\n   → Trust the process\n\n3. Principle Three: Learn from everyone\n   → Mentors accelerate your growth\n   → Peers provide perspective\n   → Beginners ask questions you forgot to ask\n\n📋 Practical Action Steps:\n\n→ Step 1: Define your target outcome clearly\n→ Step 2: Break it down into manageable pieces\n→ Step 3: Create a system, not just goals\n→ Step 4: Track progress consistently\n→ Step 5: Adjust based on feedback\n\n⚠️ Common Mistakes to Avoid:\n\n✗ Trying to do everything at once\n✗ Comparing your beginning to someone else's middle\n✗ Giving up right before the breakthrough\n\n✅ What Actually Works:\n\n→ Start small, think big\n→ Celebrate small wins\n→ Build in public\n→ Help others along the way\n\nThe truth? There's no secret formula. Just consistent effort, continuous learning, and genuine commitment.\n\nWhat's your #1 question about {theme}? Drop it below.",
    ],
  },
  question: {
    short: ["Quick question about {theme}:\n\nHow do you approach this in your work?\n\nI'm curious to hear different perspectives.\n\nDrop your thoughts below!", "Honest question:\n\nWhen it comes to {theme}, what's your biggest challenge right now?\n\nLet's help each other out in the comments."],
    medium: ["I've been thinking a lot about {theme} lately.\n\nHere's what I'm wrestling with:\n\nOn one hand, the traditional approach has merit. It's proven and reliable.\n\nOn the other hand, new methods are emerging that show real promise.\n\nSo here's my question:\n\nHow do you balance innovation with proven strategies?\n\nI'd genuinely love to hear your perspective. What's worked for you?\n\nComment below - let's learn from each other.", "A question for the community:\n\nWhen it comes to {theme}, I see two schools of thought:\n\n1. One approach that prioritizes X\n2. Another that focuses on Y\n\nBoth have valid arguments. Both show results.\n\nBut here's what I want to know:\n\nWhich approach do YOU use and why?\n\nMore importantly - have you found a way to blend both?\n\nShare your experience in the comments. I'm here to learn from you."],
    long: [
      "Let's have an honest conversation about {theme}.\n\nI've been in this industry long enough to see trends come and go. But this topic keeps coming up, and I think it deserves a deeper discussion.\n\n🤔 Here's what I'm observing:\n\nThere's a growing divide between two approaches:\n\nApproach A: Traditional, proven, but potentially limiting\nApproach B: Innovative, exciting, but not fully tested\n\n💭 What I'm wondering:\n\n→ Are we creating a false dichotomy?\n→ Is there a middle path we're missing?\n→ What does the data actually say?\n→ How do we balance risk with innovation?\n\n📊 From my experience:\n\nI've seen both approaches work. I've also seen both fail. The difference isn't usually the approach itself - it's how it's implemented.\n\n🎯 So here are my questions for you:\n\n1. What's been your experience with this?\n2. Have you found a hybrid approach that works?\n3. What factors do you consider when choosing?\n4. What results have you actually seen?\n\nI'm not looking for textbook answers. I want to hear real experiences from real people.\n\nLet's make this comment section a knowledge hub.\n\nWho's going first?",
    ],
  },
  achievement: {
    short: ["A small win worth sharing:\n\nToday we achieved something related to {theme} that I'm proud of.\n\nIt took effort, teamwork, and persistence.\n\nGrateful for everyone who contributed.\n\nOnward!", "Milestone unlocked! 🎯\n\nExcited to share that we've reached a significant milestone in {theme}.\n\nThank you to everyone who believed in this vision.\n\nJust getting started!"],
    medium: [
      "I'm proud to share some news:\n\nAfter months of work on {theme}, we've achieved something I'm genuinely excited about.\n\nThe journey:\n→ Started with a simple idea\n→ Faced numerous challenges\n→ Learned and adapted\n→ Stayed committed to the vision\n\nThe result:\nSomething that genuinely makes a difference.\n\nBut here's what I'm most proud of - the process taught us invaluable lessons that go beyond this single achievement.\n\nGrateful for the team, the supporters, and everyone who believed in this.\n\nWhat's a recent win you're proud of? Share below!",
      "Big news to share about {theme}:\n\nWe just hit a milestone that seemed impossible six months ago.\n\nThe numbers:\n→ Metric 1: Impressive result\n→ Metric 2: Significant growth\n→ Metric 3: Meaningful impact\n\nBut numbers don't tell the whole story.\n\nThe real achievement? Building something that genuinely helps people.\n\nHuge thanks to:\n→ The team who made it happen\n→ The early believers who supported us\n→ The community who gave feedback\n\nThis is just the beginning. Excited for what's next!",
    ],
    long: [
      "Today marks a significant milestone in my journey with {theme}.\n\nLet me take you back to where this started:\n\n📍 The Beginning:\n\nA year ago, I had an idea. It seemed ambitious, maybe even unrealistic. But something told me to pursue it.\n\n⚡ The Journey:\n\nThe path wasn't linear:\n\n→ Month 1-2: Excitement and rapid progress\n→ Month 3-4: Hit major roadblocks, questioned everything\n→ Month 5-6: Breakthrough moments, gained momentum\n→ Month 7-8: Refined and improved\n→ Month 9-12: Scaled and grew\n\n🎯 The Achievement:\n\nToday, I'm proud to announce:\n\n→ We've accomplished [specific achievement]\n→ Impact: [meaningful results]\n→ Growth: [impressive metrics]\n\nBut here's what matters most:\n\n💡 Lessons Learned:\n\n1. Consistency beats intensity\n2. Community accelerates everything\n3. Setbacks are setups for comebacks\n4. Small wins compound into big victories\n\n🙏 Gratitude:\n\nThis wouldn't be possible without:\n\n→ My team who believed and executed\n→ Mentors who guided and challenged me\n→ The community who supported and gave feedback\n→ Everyone who said \"yes\" when they could have said \"no\"\n\n🚀 What's Next:\n\nThis is just chapter one. We're already working on what's next, and I can't wait to share it with you.\n\nTo anyone pursuing their own ambitious goal: keep going. Your breakthrough might be closer than you think.\n\nWhat goal are you working towards? I'd love to cheer you on.",
    ],
  },
  industry: {
    short: ["Interesting development in {theme}:\n\nThe industry is shifting in a new direction.\n\nWhat this means:\n→ Impact 1\n→ Impact 2\n→ Impact 3\n\nWorth keeping an eye on this.", "Just saw some news about {theme}.\n\nMy take: This could change everything.\n\nWhat do you think? Am I overreacting or is this as big as it seems?"],
    medium: [
      "Major shift happening in {theme}:\n\nIf you haven't been paying attention, here's what you need to know:\n\n📰 What happened:\nRecent developments are changing the landscape.\n\n🔍 Why it matters:\n→ Impacts everyone in the industry\n→ Creates new opportunities\n→ Requires strategic adaptation\n\n💭 My perspective:\nThis is bigger than most people realize. Those who adapt early will have a significant advantage.\n\n🎯 What to do:\n→ Stay informed\n→ Evaluate your current strategy\n→ Be ready to pivot\n\nWhat's your take on this? Let's discuss.",
      "Let's talk about the latest in {theme}:\n\nThe industry landscape just shifted, and I think we need to have an honest conversation about what this means.\n\n📊 The Facts:\n→ What changed and when\n→ Who's affected\n→ Initial market response\n\n🤔 The Implications:\n\nShort-term: Immediate adjustments needed\nLong-term: Fundamental shifts in how we operate\n\n💡 My Analysis:\n\nThis isn't just another trend. This is a structural change that will separate leaders from followers.\n\nThe winners will be those who:\n→ Adapt quickly\n→ Think strategically\n→ Execute decisively\n\nHow are you preparing for this shift?",
    ],
    long: [
      "Deep dive into the latest developments in {theme}:\n\nThe industry is at an inflection point. Let me break down what's happening and what it means for all of us.\n\n📈 The Current Situation:\n\nWe're seeing unprecedented changes:\n\n→ Development 1: Market dynamics shifting\n→ Development 2: New technologies emerging\n→ Development 3: Consumer behavior evolving\n→ Development 4: Regulatory landscape changing\n\n🔍 What's Driving This:\n\nSeveral factors converging:\n\n1. Technological advancement\n   → Faster innovation cycles\n   → Lower barriers to entry\n   → Increased accessibility\n\n2. Market maturation\n   → Informed consumers\n   → Higher expectations\n   → Demand for value\n\n3. Global forces\n   → Economic shifts\n   → Political changes\n   → Cultural evolution\n\n💭 My Analysis:\n\nThis is more than a trend - it's a transformation.\n\nWhere we were:\n→ Traditional approaches worked\n→ Predictable patterns\n→ Stable competitive landscape\n\nWhere we're going:\n→ Innovation required\n→ Constant adaptation\n→ Dynamic competition\n\n🎯 What This Means for You:\n\nOpportunities:\n→ New markets opening\n→ Innovation rewarded\n→ First-mover advantage available\n\nChallenges:\n→ Increased complexity\n→ Faster change required\n→ Higher stakes decisions\n\n📋 Recommended Actions:\n\n1. Assess your current position\n2. Identify gaps and opportunities\n3. Develop adaptive strategies\n4. Build flexible systems\n5. Stay informed and connected\n\n🚀 Looking Ahead:\n\nThe next 12-18 months will be critical. Those who prepare now will thrive. Those who wait will struggle to catch up.\n\nMy prediction: We'll see a clear separation between organizations that embrace this change and those that resist it.\n\n💬 Your Turn:\n\nHow is your organization preparing?\nWhat challenges are you facing?\nWhat opportunities are you seeing?\n\nLet's share insights and learn from each other. The best way to navigate change is together.",
    ],
  },
};

// Get references to DOM elements
const generateBtn = document.getElementById("generateBtn");
const themeInput = document.getElementById("theme");
const postTypeSelect = document.getElementById("postType");
const lengthSelect = document.getElementById("length");
const toneSelect = document.getElementById("tone");
const resultContent = document.getElementById("resultContent");
const actions = document.getElementById("actions");
const copyBtn = document.getElementById("copyBtn");
const linkedinBtn = document.getElementById("linkedinBtn");

let generatedPost = "";

// Generate post function
async function generatePost() {
  const theme = themeInput.value.trim();
  const postType = postTypeSelect.value;
  const length = lengthSelect.value;
  const tone = toneSelect.value;

  // Validation
  if (!theme) {
    showMessage("Please enter a theme or idea", "error");
    return;
  }

  if (!postType) {
    showMessage("Please select a post type", "error");
    return;
  }

  if (!length) {
    showMessage("Please select post length", "error");
    return;
  }

  if (!tone) {
    showMessage("Please select a tone", "error");
    return;
  }

  // Show loading state
  generateBtn.disabled = true;
  generateBtn.innerHTML = '<div class="spinner"></div> Generating...';
  resultContent.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
  actions.style.display = "none";

  // Prepare webhook data
  const webhookData = {
    theme: theme,
    post_type: postType,
    length: length,
    tone: tone,
  };

  try {
    // Send data to webhook       https://vishnu-n8n.app.n8n.cloud/webhook-test/ee3e9945-97dc-470e-9ee5-053d528e15eb
    const response = await fetch("https://vishnu-n8n.app.n8n.cloud/webhook-test/ee3e9945-97dc-470e-9ee5-053d528e15eb", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(webhookData),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();

    // Check if webhook returned generated content
    if (data && data.generated_output) {
      generatedPost = data.generated_output;
    } else {
      // Fallback to local template if webhook doesn't return content
      const templates = postTemplates[postType][length];
      const randomTemplate = templates[Math.floor(Math.random() * templates.length)];
      generatedPost = randomTemplate.replace(/{theme}/g, theme);
    }

    // Display result
    resultContent.innerHTML = `<div class="generated-text">${generatedPost}</div>`;
    actions.style.display = "flex";
    showMessage("Post generated successfully!", "success");
  } catch (error) {
    console.error("Error generating post:", error);
    showMessage("Error connecting to server. Using local template.", "error");

    // Fallback to local template on error
    const templates = postTemplates[postType][length];
    const randomTemplate = templates[Math.floor(Math.random() * templates.length)];
    generatedPost = randomTemplate.replace(/{theme}/g, theme);

    // Display result
    resultContent.innerHTML = `<div class="generated-text">${generatedPost}</div>`;
    actions.style.display = "flex";
  } finally {
    // Reset button
    generateBtn.disabled = false;
    generateBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 4L14 8M10 4L6 8M10 4V16M4 16H16" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Generate Post
        `;
  }
}

// Copy to clipboard function
function copyToClipboard() {
  navigator.clipboard
    .writeText(generatedPost)
    .then(() => {
      showMessage("Copied to clipboard!", "success");
    })
    .catch((err) => {
      showMessage("Failed to copy", "error");
    });
}

// Share on LinkedIn function
function shareOnLinkedIn() {
  const linkedInUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(window.location.href)}`;
  window.open(linkedInUrl, "_blank", "width=600,height=600");
  showMessage("Opening LinkedIn...", "success");
}

// Show message function
function showMessage(message, type) {
  const messageEl = document.createElement("div");
  messageEl.className = "success-message";
  messageEl.style.backgroundColor = type === "error" ? "#ef4444" : "#10b981";
  messageEl.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M16.666 5L7.49935 14.1667L3.33268 10" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>${message}</span>
    `;
  document.body.appendChild(messageEl);

  setTimeout(() => {
    messageEl.remove();
  }, 3000);
}

// Event listeners
generateBtn.addEventListener("click", generatePost);
copyBtn.addEventListener("click", copyToClipboard);
linkedinBtn.addEventListener("click", shareOnLinkedIn);

// Enter key to generate
themeInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    generatePost();
  }
});
