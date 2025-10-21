# Coffee Maker Agent - Autonomous Development System

An autonomous development system that reads `ROADMAP.md` and automatically implements features using Claude AI.

## 🤖 What It Does

The Coffee Maker Agent is a **self-implementing AI system** that:
- Reads your roadmap and implements priorities autonomously
- Creates feature branches, commits, and pull requests automatically
- Uses Claude AI to write code following your specifications
- Runs continuously until all planned features are complete

**Current Status**: PRIORITY 2 (80%) & PRIORITY 3 (90%) - Core autonomous daemon operational!

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
poetry install

# 2. Run the autonomous daemon
python run_daemon.py

# 3. Monitor progress (in another terminal)
project-manager notifications
```

**⚠️ Important**: Run the daemon from a separate terminal, not from within Claude Code sessions.

---

## 📋 Project Roadmap - Single Source of Truth

**THE ONE AND ONLY ROADMAP**: [`docs/roadmap/ROADMAP.md`](docs/roadmap/ROADMAP.md)

This file is the **SINGLE SOURCE OF TRUTH** for:
- All project priorities and features
- Implementation plans and timelines
- Current status and progress
- Future vision (roadmap-driven development library)

**Used by**:
- 🤖 Autonomous Daemon (reads and implements features)
- 🎯 Project Manager CLI (reads and updates status)
- 👨‍💻 Human Developers (plan and review)

**Documentation Structure**: See [`docs/README_DOCS.md`](docs/README_DOCS.md) for complete documentation organization.

⚠️ **IMPORTANT**: Never create alternative roadmap files. Always edit `docs/roadmap/ROADMAP.md` directly.

---

## 🎯 Core Components

### 1. Autonomous Development Daemon (`run_daemon.py`)
Continuously reads ROADMAP.md and implements features autonomously using Claude AI.

**Usage**:
```bash
python run_daemon.py              # Interactive mode (asks for approval)
python run_daemon.py --auto-approve   # Autonomous mode (full automation)
python run_daemon.py --help        # Show all options
```

### 2. Project Manager CLI (`project-manager`)
Manage roadmap and communicate with the daemon.

**Usage**:
```bash
project-manager view               # View roadmap
project-manager notifications      # List pending notifications
project-manager respond <id> approve   # Approve daemon's work
```

### 3. Notification System
SQLite-based communication system between daemon and user with WAL mode for concurrent access.

### 4. ACE Streamlit App (`ace-ui`) ⭐ NEW
Visual interface for ACE (Agentic Context Engineering) framework management.

**Launch**:
```bash
poetry run ace-ui
```

**Features**:
- 📊 **Real-time Monitoring**: Live trace feed with agent performance metrics
- 📚 **Playbook Management**: Interactive bullet curation with search, filters, and bulk actions
- 📈 **Analytics Dashboard**: Comprehensive performance insights, cost tracking, and recommendations
- ⚙️ **Configuration**: Agent-level ACE settings *(Phase 1 - Coming Soon)*

**Documentation**:
- **User Guide**: [`docs/ACE_STREAMLIT_USER_GUIDE.md`](docs/ACE_STREAMLIT_USER_GUIDE.md) - Complete usage instructions
- **Technical Spec**: [`docs/STREAMLIT_ACE_APP_SPEC.md`](docs/STREAMLIT_ACE_APP_SPEC.md) - Architecture and implementation details

**Quick Start**:
```bash
# Start the app
poetry run ace-ui

# Open browser at http://localhost:8501

# Navigate between pages using the sidebar:
# - 📊 Monitor: Real-time execution traces
# - 📚 Playbooks: Manage playbook bullets
# - 📈 Analytics: Performance insights
```

---

## 📊 Project Statistics

- **Code**: ~5,000 lines of Python (excluding tests)
- **Tests**: 159 tests passing (0 regressions)
- **Documentation**: 3,321 lines across multiple documents
- **Architecture**: Hybrid Shared SQLite with WAL mode
- **Dependencies**: Poetry-managed, minimal external dependencies

---

## 🏗️ Architecture

```
coffee_maker/
├── autonomous/           # Autonomous daemon system
│   ├── daemon.py        # Core daemon loop
│   ├── roadmap_parser.py    # ROADMAP.md parser
│   ├── claude_cli_interface.py  # Claude CLI wrapper
│   └── git_manager.py   # Git operations
├── cli/                 # CLI tools
│   ├── roadmap_cli.py   # project-manager command
│   └── notifications.py # Notification system
└── langchain_observe/   # Analytics & observability
    └── analytics/       # Native sqlite3 analytics
```

---

## 📚 Documentation

- **[ROADMAP.md](docs/roadmap/ROADMAP.md)**: Complete project roadmap (single source of truth)
- **[DAEMON_USAGE.md](docs/DAEMON_USAGE.md)**: Daemon usage guide (540 lines)
- **[TUTORIALS.md](docs/TUTORIALS.md)**: Practical tutorials for all features
- **[ACE Console Demo Tutorial](docs/ACE_CONSOLE_DEMO_TUTORIAL.md)**: Master the ACE Generator system ⭐ NEW
- **[ACE Quick Reference](docs/ACE_QUICK_REFERENCE.md)**: One-page ACE reference card ⭐ NEW
- **[ADR_001](docs/ADR_001_DATABASE_SYNC_STRATEGY.md)**: Database sync architecture decision
- **[README_DOCS.md](docs/README_DOCS.md)**: Documentation organization

---

## 🔧 Development

For contributor instructions, see [`AGENTS.md`](AGENTS.md).

[**Static github pages**](https://bobain.github.io/MonolithicCoffeeMakerAgent/)

![Coffee Maker](ressources/README/coffee_maker.png)

---

# Some help

## Advice for Developing an Agent in Python

Here are some specific recommendations to keep in mind when building this Python agent:

### 1. Python Project Structure (might not be up to date)

```text
MonolithicCoffeeMakerAgent/
├── coffee_maker/ # The main source package
│ ├── init.py
│ ├── agent_core.py # Main agent logic
│ ├── module_example/ # Specific modules/capabilities
│ │ ├── init.py
│ │ └── coffee_making_module.py # Example module
│ └── utils/ # Utility functions
├── tests/ # Unit and integration tests
│ ├── init.py
│ ├── test_agent_core.py
│ └── test_coffee_making_module.py
├── docs/ # Documentation
│ └── usage.md
├── examples/ # Usage examples
│ └── ...
├── ...
├── .env.example # Example environment file : the one you use should be named .env and never ever be commited/pushed
├── ...
├── README.md # This file!
├── ...
```

### 2. Robust Logging

Good logging is crucial for understanding and debugging your agent's behavior.

*   Use Python's built-in `logging` module.
*   Configure different log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).
*   Allow configuration of log formats and their destinations (console, file).

#### Basic logging setup example
import logging

#### Configure basic logging
logging.basicConfig(
    level=logging.INFO, # Set the default logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # Define log message format
    datefmt='%Y-%m-%d %H:%M:%S' # Define date format
)

#### Create a logger instance for the current module
logger = logging.getLogger(__name__)

#### Example log messages
logger.info("Agent has started successfully.")
logger.debug("This is a detailed debug message for troubleshooting.")
logger.warning("A potential issue was detected.")

### 3. Thorough Testing

useless as long as it does nothing

Testing is essential to ensure the agent's reliability and robustness.
*   Unit Tests: Test small units of code (functions, methods) in isolation. The pytest framework is highly recommended for its simplicity and power.
*   Integration Tests: Test how different modules of the agent interact with each other and with external systems (if any).
*   Using fixtures if needed
*   Mocking: Use mocks (e.g., Python's unittest.mock library) to simulate external dependencies (APIs, file systems, databases) during tests. This allows for isolated and predictable testing.


### 4. Documenting Agent Capabilities

useless as long as it does nothing



## git_init.py failure : Support for password authentication was removed on August 13, 2021 : GitHub Authentication for Pushing

When using git_init.py to push to a GitHub repository via HTTPS (e.g., `https://github.com/user/repo.git`), you will need to authenticate. GitHub no longer supports password authentication for Git operations over HTTPS since August 13, 2021.

**The recommended method is to use a Personal Access Token (PAT).**

### Using a Personal Access Token (PAT) - Recommended for HTTPS

A PAT is a more secure way to authenticate with GitHub for command-line operations or scripts.

**1. Generate a Personal Access Token on GitHub:**

   a. Go to your GitHub **Settings**. (Click your profile picture in the top-right corner, then "Settings").

   b. In the left sidebar, scroll down and click on **Developer settings**.

   c. In the left sidebar, click on **Personal access tokens**, then **Tokens (classic)**.
      *(While "Fine-grained tokens" exist, "Tokens (classic)" are often simpler for this direct script usage).*

   d. Click the **Generate new token** button (or **Generate new token (classic)**).

   e. Give your token a descriptive **Note** (e.g., "Git Initializer Script Token" or "My Laptop Git Access").

   f. Set an **Expiration** for your token. For security, avoid "No expiration" if possible. 30 or 90 days is a good start.

   g. Under **Select scopes**, you **must** check the **`repo`** scope. This scope grants full control of private and public repositories.
      ![GitHub PAT repo scope](https://i.stack.imgur.com/9N4yN.png) *(Illustrative image, UI might vary slightly)*

   h. Click **Generate token** at the bottom of the page.

**2. Copy Your Token:**

   *   **VERY IMPORTANT:** GitHub will only show you this token **ONCE**. Copy it immediately and store it in a safe place (like a password manager). If you lose it or navigate away from the page, you'll have to generate a new one.

**3. Use the Token with the Script (or Git):**

   When the script (or any Git command) prompts you for your password for `https://github.com`, do the following:
    Username for 'https://github.com': YOUR_GITHUB_USERNAME
    Password for 'https://YOUR_GITHUB_USERNAME@github.com': <PASTE_YOUR_PERSONAL_ACCESS_TOKEN_HERE>

**Do NOT enter your regular GitHub account password. Use the PAT you just generated.**

### Making it Easier: Credential Helpers

To avoid entering your PAT every time you push or pull, you can configure Git to use a credential helper. This will securely store your PAT after the first successful authentication.

*   **macOS:** Git can use the macOS Keychain. To enable this:
 ```bash
 git config --global credential.helper osxkeychain
 ```
 The first time you authenticate with your PAT, macOS should ask if you want to save it to your Keychain.

*   **Windows:** Git for Windows usually comes with "Git Credential Manager," which should handle this automatically. If not, you can configure it:
 ```bash
 git config --global credential.helper manager-core # or just 'manager' for older versions
 ```

*   **Linux:** You can use `libsecret` (if installed) or other helpers like `cache` or `store`:
 ```bash
 # For libsecret (recommended if available, integrates with GNOME Keyring, KWallet, etc.)
 git config --global credential.helper /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret
 # Or to cache for a limited time (e.g., 1 hour)
 # git config --global credential.helper 'cache --timeout=3600'
 # Or to store in plain text (less secure, use with caution)
 # git config --global credential.helper store
 ```

### Alternative: Using SSH Keys

For a more seamless experience without needing tokens or passwords for each push/pull, consider setting up SSH keys with GitHub.

1.  [Generate a new SSH key and add it to the ssh-agent](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent).
2.  [Add your SSH public key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
3.  Once set up, you can use the SSH URL for your repository with the script or when cloning/setting remotes:
 *   If the remote `origin` already exists with an HTTPS URL, change it:
     ```bash
     git remote set-url origin git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git
     ```
 *   When using this script, provide the SSH URL:
     ```bash
     python your_script_name.py -u git@github.com:YOUR_USERNAME/YOUR_REPOSITORY.git
     ```

By following these instructions, you should be able to authenticate successfully when the script attempts to push your newly initialized repository to GitHub.
