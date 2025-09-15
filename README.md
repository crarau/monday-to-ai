# Pivot Monday.com Exporter

A clean, simple tool to export Monday.com tasks with all their content for AI context sharing.

## 🎯 Purpose

Export Monday.com tasks as markdown documents with all comments, replies, and referenced images - perfect for sharing complete context with AI assistants.

## 📁 Structure

```
pivot-monday/
├── monday_exporter.py   # The exporter tool
├── .env.example         # Template for API token
├── .gitignore          # Excludes downloaded tasks from git
└── [Task Folders]/     # Downloaded tasks (git-ignored)
    ├── README.md       # Task content
    └── images/         # Referenced images
```

## 🚀 Quick Start

### 1. Set up API Token (Optional)

```bash
cp .env.example .env
# Edit .env and add your Monday.com API token
```

Get your token from: https://monday.com/developers/v2#authentication

### 2. Export a Task

```bash
# Using URL
python3 monday_exporter.py https://example.monday.com/boards/123/pulses/456

# Using item ID
python3 monday_exporter.py 456
```

## 📂 Output

Each export creates a folder named after the task:

```
[Task Name]/
├── README.md    # Complete task content (always this name)
└── images/      # All images referenced in the markdown
```

### What's Included

- ✅ Task metadata (board, assignees, dates, status)
- ✅ All custom fields
- ✅ Complete comment history with timestamps
- ✅ **All reply comments** with proper threading
- ✅ Downloaded images with markdown references
- ✅ Clean, readable formatting

## 💡 AI Context Workflow

1. **Export the Monday task:**
   ```bash
   python3 monday_exporter.py [url-or-id]
   ```

2. **Share the folder with AI** - the README.md contains everything

3. **If images are needed**, tell the AI:
   - "Check the screenshot in images/comment_0_0.png"
   - Images are only loaded when visual details matter

## 🔧 Requirements

- Python 3.6+
- `requests` library

```bash
pip install requests
```

## 📝 Example Export

The markdown includes everything in a clean format:

```markdown
# Task: Bug in messaging system

## 📌 Task Information
- Board: Development Sprint
- Assigned to: John Doe

## 💬 Comments & Updates

### 💭 Alice - 2024-01-15 10:30
Found the issue - here's a screenshot:
![Image](images/comment_0_0.png)

#### Replies:
**↳ Bob** - 2024-01-15 11:00
I can reproduce this bug...
```

## 🚫 Git Ignore

Downloaded tasks are automatically excluded from git via `.gitignore`. This keeps your repository clean while allowing local task exports.

---

*Simple. Clean. Effective.*