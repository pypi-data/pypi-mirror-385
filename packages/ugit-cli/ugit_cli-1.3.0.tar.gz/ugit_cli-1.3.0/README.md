# ugit 🚀

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A minimal Git implementation in Python that demonstrates the core concepts of version control systems. Perfect for learning how Git works under the hood!

## ✨ Features

### Core Git Functionality
- **Repository initialization** - Create new ugit repositories
- **File staging** - Add files to the staging area  
- **Committing** - Create commits from staged changes
- **History viewing** - Browse commit history with detailed logs
- **Checkout** - Restore files from specific commits
- **Status checking** - See which files are modified, staged, or untracked
- **Branching** - Create, switch, and manage branches
- **Merging** - Merge branches with conflict resolution
- **Remotes** - Work with remote repositories (clone, fetch, pull, push)
- **Stashing** - Temporarily save changes for later (save, list, pop, apply, drop)
- **Diffing** - Compare changes between commits, files, or working directory

### 🌐 Web Interface
- **Beautiful Dark Mode Interface** - Modern, professional repository browser
- **File Explorer** - Navigate repository files and directories with ease
- **Code Viewer** - Syntax-highlighted file viewing with line numbers
- **Commit History** - Visual commit timeline with detailed information  
- **Real-time Updates** - Dynamic loading of repository data
- **Responsive Design** - Works perfectly on desktop and mobile devices

## � Documentation

- **[Installation Guide](docs/installation.md)** - How to install and set up ugit
- **[User Guide](docs/user-guide.md)** - Complete guide to using ugit commands
- **[Examples](docs/examples.md)** - Practical examples and use cases
- **[API Reference](docs/api-reference.md)** - Technical documentation
- **[Developer Guide](docs/developer-guide.md)** - Guide for contributors
- **[Architecture](docs/architecture.md)** - System design overview
- **[FAQ](docs/faq.md)** - Frequently asked questions
- **[Troubleshooting](docs/troubleshooting.md)** - Common issues and solutions

## �🚀 Quick Start

### Installation Options

#### Option 1: Basic Installation (CLI Only)
```bash
pip install ugit-cli
```
This installs the core ugit functionality for command-line usage.

#### Option 2: Full Installation (CLI + Web Interface)
```bash
pip install ugit-cli[web]
```
This includes the beautiful web interface for browsing repositories.

#### Option 3: Development Installation
```bash
# Clone the repository
git clone https://github.com/night-slayer18/ugit.git
cd ugit

# Install in development mode (CLI only)
pip install -e .

# Or install with web interface support
pip install -e .[web]
```

pip install -e .[web]
```

### Basic Usage

#### Command Line Interface
```bash
# Initialize a new repository
ugit init

# Add files to staging area
ugit add file.txt
ugit add .

# Create a commit
ugit commit -m "Initial commit"
ugit commit -m "Commit message" --author "Name <email@example.com>"

# Check repository status
ugit status

# View commit history
ugit log                    # Full history
ugit log --oneline         # Compact view
ugit log --graph           # ASCII graph
ugit log -n 5              # Limit to 5 commits
ugit log --since "2025-01-01"  # Since date

# Checkout commits and branches
ugit checkout <commit-sha>  # Checkout specific commit
ugit checkout <branch>      # Switch to branch
ugit checkout -b <branch>   # Create and switch to branch

# Branch management
ugit branch                 # List branches
ugit branch <name>          # Create branch
ugit branch -d <name>       # Delete branch

# Merge branches
ugit merge <branch>         # Merge branch
ugit merge <branch> --no-ff # Force merge commit

# Show differences
ugit diff                   # Working directory changes
ugit diff --staged          # Staged changes
ugit diff <commit1> <commit2>  # Between commits

# Reset operations
ugit reset                  # Unstage all files
ugit reset <commit>         # Reset to commit (soft)
ugit reset --hard <commit>  # Reset to commit (hard)
ugit reset --soft <commit>  # Reset to commit (keep staged)

# Stash operations
ugit stash                  # Stash current changes
ugit stash save "message"   # Stash with message
ugit stash list             # List all stashes
ugit stash pop              # Apply and remove latest stash
ugit stash pop 1            # Apply specific stash by index
ugit stash apply            # Apply stash without removing
ugit stash drop             # Remove stash without applying
ugit stash -u               # Include untracked files

# Remote repository operations
ugit clone <url> [directory]     # Clone repository
ugit remote                      # List remotes
ugit remote -v                   # List remotes with URLs
ugit remote add origin <url>     # Add remote
ugit remote remove <name>        # Remove remote
ugit remote show <name>          # Show remote details

# Fetch, pull, and push
ugit fetch                       # Fetch from origin
ugit fetch <remote>              # Fetch from specific remote
ugit pull                        # Pull from origin/current branch
ugit pull <remote> <branch>      # Pull specific branch
ugit push                        # Push to origin/current branch
ugit push <remote> <branch>      # Push specific branch
ugit push -f                     # Force push

# Configuration
ugit config user.name "Your Name"
ugit config user.email "you@example.com"
ugit config --list           # List all configuration
```

#### 🌐 Web Interface
```bash
# Start the web interface (requires ugit[web] installation)
ugit serve

# Custom host and port
ugit serve --host 0.0.0.0 --port 8080

# Don't open browser automatically
ugit serve --no-browser
```

The web interface provides:
- **Beautiful file browser** with syntax highlighting
- **Interactive commit history** with timeline view
- **Responsive design** that works on all devices
- **Real-time repository exploration** without command line

## 📁 Project Structure

```
ugit/
├── ugit/                   # Main package
│   ├── __init__.py        # Package initialization
│   ├── cli.py             # Command-line interface
│   ├── core/              # Core functionality
│   │   ├── objects.py     # Object storage and hashing
│   │   └── repository.py  # Repository and index management
│   ├── commands/          # Command implementations
│   │   ├── init.py        # Repository initialization
│   │   ├── add.py         # File staging
│   │   ├── commit.py      # Commit creation
│   │   ├── log.py         # History viewing
│   │   ├── checkout.py    # File restoration
│   │   ├── status.py      # Status checking
│   │   ├── serve.py       # Web interface server
│   │   ├── branch.py      # Branch management
│   │   ├── merge.py       # Branch merging
│   │   ├── remote.py      # Remote repositories
│   │   ├── clone.py       # Repository cloning
│   │   ├── fetch.py       # Fetch from remotes
│   │   ├── pull.py        # Pull changes
│   │   ├── push.py        # Push changes
│   │   ├── stash.py       # Stash management
│   │   ├── reset.py       # Reset operations
│   │   ├── diff.py        # Show differences
│   │   └── config.py      # Configuration management
│   ├── web/               # Web interface components
│   │   ├── server.py      # FastAPI web server
│   │   ├── templates/     # HTML templates
│   │   │   └── index.html # Main interface template
│   │   └── static/        # Static assets
│   │       ├── css/       # Stylesheets
│   │       │   └── style.css  # Main dark theme styles
│   │       └── js/        # JavaScript files
│   │           └── app.js     # Frontend application logic
│   └── utils/             # Utility functions
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── pyproject.toml        # Project configuration
├── requirements.txt      # Basic dependencies
├── web-requirements.txt  # Web interface dependencies
└── README.md            # This file
```

## 🔧 How It Works

ugit implements the core Git concepts:

### Object Storage
- **Blobs**: Store file contents
- **Trees**: Store directory structures  
- **Commits**: Store snapshots with metadata
- Objects are stored by SHA-1 hash in `.ugit/objects/`

### Repository Structure
```
.ugit/
├── objects/           # Object storage (blobs, trees, commits)
├── refs/heads/        # Branch references
├── HEAD              # Current branch pointer
└── index             # Staging area
```

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `init` | Initialize repository | `ugit init` |
| `add` | Stage files | `ugit add file.txt` |
| `commit` | Create commit | `ugit commit -m "message"` |
| `status` | Show status | `ugit status` |
| `config` | Configuration | `ugit config user.name "John"` |
| `log` | Show history | `ugit log --oneline --graph` |
| `checkout` | Restore files/switch branches | `ugit checkout -b feature` |
| `branch` | Manage branches | `ugit branch -d old-feature` |
| `merge` | Merge branches | `ugit merge feature --no-ff` |
| `diff` | Show changes | `ugit diff --staged` |
| `reset` | Reset changes | `ugit reset --hard HEAD~1` |
| **`stash`** | **Temporarily save changes** | **`ugit stash save "WIP"`** |
| **`stash list`** | **List all stashes** | **`ugit stash list`** |
| **`stash pop`** | **Apply and remove stash** | **`ugit stash pop 1`** |
| **`stash apply`** | **Apply stash (keep it)** | **`ugit stash apply`** |
| **`stash drop`** | **Remove stash** | **`ugit stash drop 0`** |
| `clone` | Clone repository | `ugit clone <url>` |
| `remote` | Manage remotes | `ugit remote add origin <url>` |
| `fetch` | Fetch from remote | `ugit fetch origin` |
| `pull` | Pull changes | `ugit pull origin main` |
| `push` | Push changes | `ugit push -f origin main` |
| **`serve`** | **Start web interface** | **`ugit serve --port 8080`** |

## 🧪 Development

### Setup Development Environment

```bash
# Clone and install in development mode
git clone https://github.com/night-slayer18/ugit.git
cd ugit
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ugit

# Run specific test file
pytest tests/test_commands.py
```

### Code Quality

```bash
# Format code
black ugit/ tests/

# Sort imports  
isort ugit/ tests/

# Type checking
mypy ugit/

# Linting
flake8 ugit/ tests/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick Contribution Guide

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest`)
6. Format your code (`black .` and `isort .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to your branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 📚 Learning Resources

- [Git Internals](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
- [Building Git by James Coglan](https://shop.jcoglan.com/building-git/)
- [Git from the Bottom Up](https://jwiegley.github.io/git-from-the-bottom-up/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the excellent Git internals documentation
- Built for educational purposes to understand version control systems
- Thanks to all contributors who help improve this project

## 📞 Support

- 📫 Create an [issue](https://github.com/night-slayer18/ugit/issues) for bug reports or feature requests
- 💬 Start a [discussion](https://github.com/night-slayer18/ugit/discussions) for questions
- ⭐ Star this repository if you find it helpful!

---