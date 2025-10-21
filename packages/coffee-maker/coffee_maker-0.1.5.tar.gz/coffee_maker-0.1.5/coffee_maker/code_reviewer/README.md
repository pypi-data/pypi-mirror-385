# Multi-Model Code Review Agent

AI-powered code review system that analyzes code from multiple perspectives using specialized LLMs.

## 🎯 Overview

The Multi-Model Code Review Agent provides comprehensive code analysis by combining insights from four specialized perspectives:

- **Bug Hunter** (GPT-4): Identifies logic errors, edge cases, and potential bugs
- **Architect Critic** (Claude): Reviews architecture, design patterns, and code organization
- **Performance Analyst** (Gemini): Analyzes algorithmic complexity and optimization opportunities
- **Security Auditor**: Audits for security vulnerabilities and best practices

Each perspective uses pattern-based analysis (extensible to full LLM integration) to provide targeted, actionable feedback.

## 🚀 Quick Start

### Basic Usage

```python
from coffee_maker.code_reviewer import MultiModelCodeReviewer

# Initialize reviewer
reviewer = MultiModelCodeReviewer()

# Review a single file
report = reviewer.review_file("mycode.py")

# Check results
print(f"Found {report.metrics['total_issues']} issues")
print(f"Critical: {report.metrics['critical']}")
print(f"High: {report.metrics['high']}")

# Save HTML report
from coffee_maker.code_reviewer.report_generator import ReportGenerator

generator = ReportGenerator()
generator.save_html_report(report, "review_report.html")
```

### Review a Directory

```python
# Review all Python files in a directory
reports = reviewer.review_directory("src/", "*.py")

# Aggregate metrics
total_issues = sum(r.metrics['total_issues'] for r in reports)
print(f"Total issues across {len(reports)} files: {total_issues}")
```

### Install Git Hooks

```python
from coffee_maker.code_reviewer.git_integration import GitIntegration

# Initialize integration
git = GitIntegration(
    block_on_critical=True,  # Block commits with critical issues
    block_on_high=False      # Allow high severity issues
)

# Install pre-commit hook
git.install_pre_commit_hook()

# Now git commit will automatically run code review!
```

## 📋 Features

### Multi-Perspective Analysis

Each perspective focuses on specific aspects:

**Bug Hunter**
- Bare except clauses
- Resource leaks (files, connections)
- None dereference potential
- Type mismatches

**Architect Critic**
- Class size (God Object anti-pattern)
- Function complexity
- SOLID principle violations
- Coupling issues

**Performance Analyst**
- Nested loops (O(n²) complexity)
- Inefficient list operations
- String concatenation in loops
- N+1 database query problems

**Security Auditor**
- SQL injection vulnerabilities
- Command injection
- Hardcoded secrets
- Insecure random generation
- Path traversal

### Rich Reports

Generate reports in multiple formats:

**HTML Reports**
- Interactive, filterable
- Color-coded by severity
- Code snippets included
- Actionable suggestions

**Markdown Reports**
- Documentation-friendly
- Issue grouping by severity
- Export for GitHub/GitLab

**JSON Reports**
- Programmatic access
- CI/CD integration
- Custom processing

### Git Integration

Automatic code review on:
- **Pre-commit**: Review staged files before commit
- **Pre-push**: Review all changes before push
- **Manual**: Review specific files or branches

## 💻 Usage Examples

### Custom Perspective Selection

```python
# Only run security audit
reviewer = MultiModelCodeReviewer(
    enable_perspectives=["security_auditor"]
)

report = reviewer.review_file("auth.py")
```

### Filter Issues by Severity

```python
report = reviewer.review_file("app.py")

# Get only critical issues
critical = report.get_issues_by_severity("critical")

for issue in critical:
    print(f"{issue.title} at line {issue.line_number}")
    print(f"Suggestion: {issue.suggestion}")
```

### Filter Issues by Category

```python
# Get only security issues
security_issues = report.get_issues_by_category("security")

# Get only performance issues
perf_issues = report.get_issues_by_category("performance")
```

### Async Review (for large codebases)

```python
import asyncio

async def review_large_codebase():
    reviewer = MultiModelCodeReviewer()
    report = await reviewer.review_file_async("large_file.py")
    return report

report = asyncio.run(review_large_codebase())
```

## 🏗️ Architecture

```
coffee_maker/code_reviewer/
├── __init__.py              # Package interface
├── reviewer.py              # MultiModelCodeReviewer orchestrator
├── perspectives/
│   ├── base_perspective.py  # Abstract base class
│   ├── bug_hunter.py        # Bug detection (GPT-4)
│   ├── architect_critic.py  # Architecture review (Claude)
│   ├── performance_analyst.py  # Performance analysis (Gemini)
│   └── security_auditor.py  # Security audit
├── report_generator.py      # HTML/Markdown/JSON reports
└── git_integration.py       # Git hooks integration
```

## 📊 Report Format

Reports include:

```python
ReviewReport(
    file_path="app.py",
    timestamp=datetime.now(),
    issues=[
        ReviewIssue(
            severity="critical",          # critical, high, medium, low, info
            category="security",          # bug, architecture, performance, security
            title="SQL Injection vulnerability",
            description="Direct string interpolation in SQL query",
            line_number=42,
            code_snippet='query = f"SELECT * FROM users WHERE id = {user_id}"',
            suggestion="Use parameterized queries: execute(query, (user_id,))",
            perspective="Security Auditor"
        )
    ],
    summary="Found 1 critical issue requiring immediate attention",
    metrics={
        'total_issues': 5,
        'critical': 1,
        'high': 2,
        'medium': 1,
        'low': 1,
        'bugs': 2,
        'security': 1,
        'performance': 1,
        'architecture': 1
    }
)
```

## 🔧 Git Hooks Configuration

### Pre-Commit Hook

Automatically reviews staged files before commit:

```bash
# Install hook
python -c "from coffee_maker.code_reviewer.git_integration import GitIntegration; GitIntegration().install_pre_commit_hook()"

# Now commits are checked automatically
git add myfile.py
git commit -m "Update feature"
# 🔍 Running code review on staged files...
# ✅ Review passed (2 medium issues found)
```

### Pre-Push Hook

Reviews all changes before push:

```bash
# Install hook
python -c "from coffee_maker.code_reviewer.git_integration import GitIntegration; GitIntegration().install_pre_push_hook()"

# Now pushes are checked
git push
# 🔍 Running code review on changed files...
# ❌ PUSH BLOCKED: 1 critical issue found!
```

### Hook Configuration

```python
# Configure hooks
git = GitIntegration(
    repo_path="/path/to/repo",
    block_on_critical=True,   # Block if critical issues found
    block_on_high=False        # Allow high severity issues
)

git.install_pre_commit_hook(force=True)  # Overwrite existing hook
```

### Bypass Hooks

```bash
# Skip hooks when needed
git commit --no-verify -m "Emergency fix"
```

### Uninstall Hooks

```python
git = GitIntegration()
git.uninstall_hooks()
```

## 🧪 Testing

Run tests:

```bash
# All tests
pytest tests/code_reviewer/

# Specific test file
pytest tests/code_reviewer/test_reviewer.py

# With coverage
pytest tests/code_reviewer/ --cov=coffee_maker.code_reviewer
```

## 🎨 Customization

### Create Custom Perspective

```python
from coffee_maker.code_reviewer.perspectives.base_perspective import BasePerspective
from coffee_maker.code_reviewer.reviewer import ReviewIssue

class CustomPerspective(BasePerspective):
    def __init__(self):
        super().__init__(
            model_name="custom-model",
            perspective_name="Custom Analyzer"
        )

    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        issues = []

        # Your custom analysis logic
        if "TODO" in code_content:
            issues.append(
                self._create_issue(
                    severity="low",
                    category="maintenance",
                    title="TODO comment found",
                    description="TODO comment should be addressed",
                    suggestion="Create a ticket or fix the TODO"
                )
            )

        return issues

    async def analyze_async(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        return self.analyze(code_content, file_path)
```

### Integrate with LLM APIs

```python
# Example: Integrate Bug Hunter with actual GPT-4 API
class BugHunterWithGPT4(BugHunter):
    def analyze(self, code_content: str, file_path: str) -> List[ReviewIssue]:
        # Call GPT-4 API
        from openai import OpenAI

        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{
                "role": "system",
                "content": "You are a code reviewer focused on finding bugs..."
            }, {
                "role": "user",
                "content": f"Review this code:\n\n{code_content}"
            }]
        )

        # Parse response and create ReviewIssue objects
        # ...

        return issues
```

## 📈 Business Impact

Based on ROADMAP specifications:

- **⚡ Code review time reduction**: 30-50%
- **🐛 Early bug detection**: -40% bugs in production
- **📈 Code quality improvement**: Measurable via metrics
- **💰 Direct measurable ROI**: Reduced debugging time

## 🔮 Future Enhancements

- [ ] Full LLM API integration (GPT-4, Claude, Gemini)
- [ ] Machine learning for custom pattern detection
- [ ] IDE integration (VS Code, PyCharm)
- [ ] CI/CD pipeline integration (GitHub Actions, GitLab CI)
- [ ] Custom rule configuration (YAML/JSON)
- [ ] Historical trend analysis
- [ ] Team collaboration features
- [ ] Automated fix suggestions with code generation

## 📚 Examples

See `examples/` directory:

- `examples/code_reviewer/basic_review.py` - Basic usage
- `examples/code_reviewer/git_hooks.py` - Git integration
- `examples/code_reviewer/custom_perspective.py` - Custom perspectives
- `examples/code_reviewer/batch_review.py` - Reviewing multiple files

## 🤝 Contributing

To extend the code reviewer:

1. Create custom perspective by inheriting from `BasePerspective`
2. Add pattern detection methods
3. Write tests in `tests/code_reviewer/`
4. Update documentation

## 📄 License

See project LICENSE file.

---

**Built with ☕ by the Coffee Maker Agent team**

**Part of PRIORITY 6: Innovative Projects**
