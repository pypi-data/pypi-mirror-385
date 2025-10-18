# CodeMind 🧠

> Give GitHub Copilot memory across all your projects

[![Tests](https://img.shields.io/badge/tests-110%2B%20passing-brightgreen)]() [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]() [![License](https://img.shields.io/badge/license-MIT-blue)]()

**CodeMind** is an MCP server that gives GitHub Copilot 20 specialized tools for understanding your codebase.

<!-- mcp-name: io.github.mrunreal/codemind -->

---

## Why CodeMind?

**Without it:**
- ❌ Copilot creates duplicate files
- ❌ Forgets decisions you just made
- ❌ Doesn't understand your project structure

**With it:**
- ✅ Finds existing code before creating new files
- ✅ Remembers architectural decisions
- ✅ Understands dependencies and relationships
- ✅ Warns about breaking changes

---

## Quick Start

### Option 1: Install from PyPI (Recommended)

**1. Install the package**
```bash
pip install mcp-codemind
```

**2. Configure VS Code**

Add to `.vscode/settings.json`:
```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["-m", "codemind"]
    }
  }
}
```

**3. Reload**

Press `Ctrl+Shift+P` → "Developer: Reload Window"

Done! 🎉

---

### Option 2: Install from Source

**1. Clone and install**
```bash
git clone https://github.com/MrUnreal/codemind.git
cd codemind
pip install -r requirements.txt
```

**2. Configure VS Code**

Add to `.vscode/settings.json`:
```json
{
  "mcp.servers": {
    "codemind": {
      "command": "python",
      "args": ["D:/path/to/codemind/codemind.py"]
    }
  }
}
```

**3. Reload**

Press `Ctrl+Shift+P` → "Developer: Reload Window"

---

## What You Get

**20 AI Tools in 6 Categories:**

| Category | What It Does |
|----------|-------------|
| 🔍 Search | Find existing code, check if features exist |
| 📝 Context | Understand files, track changes, remember decisions |
| 🔗 Dependencies | See what imports what, visualize structure |
| 📊 Analysis | Code quality metrics, config auditing |
| ⚠️ Safety | Check breaking changes before refactoring |
| 🗂️ Management | Index files, find TODOs, git history |

---

## How It Works

**You ask naturally:**
```
"Add authentication"
```

**Copilot automatically:**
1. Searches existing code
2. Finds `src/auth/jwt.py`
3. Suggests modifying it instead of creating new files

**No explicit tool calls needed!**

---

## Example Usage

```
💬 "Does this project have authentication?"
✅ Found in src/auth/jwt.py

💬 "What will break if I rename UserModel?"
⚠️ 7 files will be affected

💬 "What depends on database.py?"
📋 Used by: models/, auth/, tests/

💬 "Show me TODOs"
📝 Found 12 TODOs across 5 files
```

---

## Multi-Workspace Support

Work with multiple projects simultaneously:
- Each project gets its own database
- No cross-contamination
- Isolated configurations

---

## Documentation

| Document | Purpose |
|----------|---------|
| [Usage Guide](USAGE_GUIDE.md) | How to use with Copilot |
| [Changelog](CHANGELOG.md) | Version history |
| [Tools Reference](docs/TOOLS.md) | All 20 tools explained |
| [Architecture](docs/ARCHITECTURE.md) | Technical details |
| [Examples](docs/EXAMPLES.md) | Real-world scenarios |
| [FAQ](docs/FAQ.md) | Common questions |

---

## Requirements

- Python 3.10+
- VS Code with GitHub Copilot
- ~80MB for embedding model
- ~5MB per project for database

---

## Status

- ✅ 20/20 tools operational
- ✅ 110+ tests passing (99%+ rate)
- ✅ Production ready
- ✅ Actively maintained

---

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

---

## License

MIT - See [LICENSE](LICENSE)

---

**Built with**: Python, FastMCP, sentence-transformers, SQLite

*Making Copilot smarter, one project at a time* 🚀
