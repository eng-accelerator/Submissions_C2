# Contributing to Text Summarization MVP

Thank you for your interest in contributing! This is a bootcamp project, but I welcome improvements and learning opportunities.

## 🤝 How to Contribute

### Types of Contributions Welcome

1. **Bug Fixes** 🐛
   - Fix errors in code
   - Improve error handling
   - Resolve compatibility issues

2. **Documentation** 📝
   - Fix typos
   - Improve clarity
   - Add examples
   - Translate to other languages

3. **Features** ✨
   - New export formats
   - Additional models
   - UI improvements
   - Performance optimizations

4. **Tests** 🧪
   - Unit tests
   - Integration tests
   - Edge case coverage

## 📋 Before You Start

1. **Open an Issue First**
   - Describe what you want to change
   - Wait for feedback/approval
   - Avoid duplicate work

2. **Check Existing Issues**
   - Someone might already be working on it
   - Can you help with existing issues?

## 🚀 Getting Started

### 1. Fork the Repository

Click "Fork" button on GitHub

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/day2-text-summarization-mvp.git
cd day2-text-summarization-mvp
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch Naming Convention**:
- `feature/add-spanish-support`
- `fix/cache-key-collision`
- `docs/improve-readme`
- `test/add-unit-tests`

### 4. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest black flake8
```

## 💻 Making Changes

### Code Style

**Follow PEP 8**:
```bash
# Format code
black *.py

# Check style
flake8 *.py
```

**Key Guidelines**:
- Class names: `PascalCase`
- Function names: `snake_case`
- Constants: `UPPER_CASE`
- Docstrings for all public methods
- Type hints where possible

**Example**:
```python
class ModelManager:
    """Manages loading and caching of AI models."""

    def load_model(self, model_id: str) -> Tuple[Tokenizer, Model]:
        """
        Load model and tokenizer from HuggingFace.

        Args:
            model_id: HuggingFace model identifier

        Returns:
            Tuple of (tokenizer, model)
        """
        # Implementation...
```

### Testing

**Run Tests** (when implemented):
```bash
pytest tests/
```

**Manual Testing**:
1. Run application locally
2. Test your changes thoroughly
3. Test on different platforms if possible
4. Check all export formats work

### Documentation

- Update README.md if adding features
- Add docstrings to new functions
- Update ARCHITECTURE.md for architectural changes
- Add examples for new features

## 📤 Submitting Changes

### 1. Commit Your Changes

```bash
git add .
git commit -m "feat: add Spanish language support for exports"
```

**Commit Message Format**:
```
type: brief description

[optional detailed description]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat: add PDF export functionality
fix: resolve cache key collision issue
docs: improve SETUP.md installation steps
refactor: extract export logic to separate class
```

### 2. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Other (specify)

## Testing
How did you test your changes?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Tested locally
- [ ] Documentation updated
- [ ] No breaking changes
```

## 🔍 Code Review Process

1. **Initial Review** (1-2 days)
   - Maintainer reviews code
   - May request changes

2. **Discussion**
   - Address feedback
   - Make requested changes
   - Push updates to same branch

3. **Approval**
   - Once approved, PR will be merged
   - Your contribution will be credited!

## 🎯 Good First Issues

Look for issues labeled:
- `good first issue`
- `beginner-friendly`
- `documentation`
- `help wanted`

**Suggested Contributions**:
1. Add few-shot prompting examples
2. Create unit tests for TextProcessor
3. Add more language support (audio)
4. Improve error messages
5. Add model comparison feature

## ❌ What NOT to Contribute

- Breaking changes without discussion
- Reformatting entire codebase
- Adding heavy dependencies
- Removing existing features
- Changing license

## 📞 Getting Help

**Questions?**
- Open a Discussion on GitHub
- Comment on relevant issue
- Email maintainer (see README)

**Stuck?**
- Review existing PRs for examples
- Check ARCHITECTURE.md for code structure
- Ask in bootcamp community

## 🏆 Recognition

Contributors will be acknowledged in:
- README.md (Contributors section)
- Release notes
- Special thanks in presentations

## 📜 Code of Conduct

### Our Standards

**Positive Behavior**:
- ✅ Be respectful and inclusive
- ✅ Welcome newcomers
- ✅ Focus on constructive feedback
- ✅ Assume good intentions

**Unacceptable Behavior**:
- ❌ Harassment or discrimination
- ❌ Trolling or insulting comments
- ❌ Personal attacks
- ❌ Spam or advertising

### Enforcement

Violations will result in:
1. Warning
2. Temporary ban
3. Permanent ban (severe cases)

Report issues to [maintainer email]

## 🎓 Learning Resources

**Python Best Practices**:
- [PEP 8 Style Guide](https://pep8.org/)
- [Real Python](https://realpython.com/)

**Git & GitHub**:
- [GitHub Guides](https://guides.github.com/)
- [Oh My Git!](https://ohmygit.org/) (interactive)

**Transformers**:
- [HuggingFace Course](https://huggingface.co/course)
- [Transformers Docs](https://huggingface.co/docs/transformers)

**Gradio**:
- [Gradio Quickstart](https://gradio.app/quickstart/)
- [Gradio Examples](https://gradio.app/demos/)

## 🙏 Thank You!

Your contributions make this project better. Whether it's a bug fix, feature, or documentation improvement - every contribution matters!

**Happy Contributing!** 🎉

---

**Questions?** Open an issue or discussion on GitHub.
