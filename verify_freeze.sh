#!/bin/bash
# Freeze Verification Script

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        🧊 CODE FREEZE VERIFICATION - v1.0.0 JARVIS 🧊          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check version file
if [ -f "VERSION" ]; then
    VERSION=$(cat VERSION)
    echo "✅ Version file: $VERSION"
else
    echo "❌ VERSION file missing!"
    exit 1
fi

# Check core files
echo ""
echo "📄 Core Files:"
for file in app.py orchestrator.py config.py requirements.txt; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file MISSING!"
    fi
done

# Check agents
echo ""
echo "🤖 Agents:"
AGENT_COUNT=$(find agents -name "*.py" -type f | wc -l | tr -d ' ')
if [ "$AGENT_COUNT" -ge 7 ]; then
    echo "  ✅ $AGENT_COUNT agent files found"
else
    echo "  ❌ Expected 7+ agents, found $AGENT_COUNT"
fi

# Check documentation
echo ""
echo "📚 Documentation:"
DOC_COUNT=$(find . -maxdepth 1 -name "*.md" -type f | wc -l | tr -d ' ')
if [ "$DOC_COUNT" -ge 9 ]; then
    echo "  ✅ $DOC_COUNT documentation files found"
else
    echo "  ⚠️  Expected 9+ docs, found $DOC_COUNT"
fi

# Check sample logs
echo ""
echo "🧪 Sample Logs:"
SAMPLE_COUNT=$(find . -maxdepth 1 -name "sample_logs*.txt" -type f | wc -l | tr -d ' ')
if [ "$SAMPLE_COUNT" -ge 6 ]; then
    echo "  ✅ $SAMPLE_COUNT sample log files found"
else
    echo "  ⚠️  Expected 6 samples, found $SAMPLE_COUNT"
fi

# Check for unwanted files
echo ""
echo "🧹 Cleanliness Check:"
if [ -d "__pycache__" ] || [ -n "$(find . -name "__pycache__" -type d)" ]; then
    echo "  ⚠️  __pycache__ directories found (should be removed)"
else
    echo "  ✅ No cache directories"
fi

if [ -f "STATUS.txt" ] || [ -f "JUDGE_REVIEW.md" ] || [ -f "PROJECT_SUMMARY.md" ]; then
    echo "  ⚠️  Unwanted files found"
else
    echo "  ✅ No unwanted files"
fi

# Check .gitignore
echo ""
echo "📋 Configuration:"
if [ -f ".gitignore" ]; then
    echo "  ✅ .gitignore present"
else
    echo "  ❌ .gitignore missing!"
fi

if [ -f "env.example" ]; then
    echo "  ✅ env.example present"
else
    echo "  ❌ env.example missing!"
fi

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Summary:"
echo "  Version: $VERSION"
echo "  Agents: $AGENT_COUNT files"
echo "  Documentation: $DOC_COUNT files"
echo "  Sample Logs: $SAMPLE_COUNT files"
echo ""
echo "✅ Code freeze verification complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
