# Monday.com to AI Export Tool 🚀

> Transform your [Monday.com](https://monday.com) tasks into AI-ready markdown with full context, images, and discussions

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Monday.com API](https://img.shields.io/badge/Monday.com-API-red.svg)](https://developer.monday.com/api-reference/docs)

## 🎯 Why This Tool?

Working with AI assistants like **ChatGPT**, **Claude**, or **Gemini** on your [Monday.com](https://monday.com) projects? This tool bridges the gap by exporting your Monday.com tasks with **complete context** - including all comments, replies, images, and attachments - into clean markdown that AI assistants can understand perfectly.

### ✨ Key Features

- 📋 **Complete Context Export** - Every comment, reply, and discussion thread
- 🖼️ **Image Preservation** - Downloads and embeds all referenced images
- 📎 **File Attachments** - Captures all attached documents
- 🤖 **AI-Optimized Format** - Clean markdown structure that AI models parse perfectly
- 💬 **Thread Preservation** - Maintains conversation hierarchy and context
- 🎨 **Clean Output** - Beautiful, readable markdown files

## 🖼️ What You Get

Transform your Monday.com tasks from this:

![Monday.com Task View](https://monday.com/blog/wp-content/uploads/2022/09/monday-UI.png)

Into beautiful markdown like this:

<details>
<summary><b>📄 Click to see example output</b></summary>

```markdown
# Web: Implement Dark Mode Feature

*Exported from Monday.com on 2024-03-15 14:30*

## 📌 Task Information

- **Board:** Product Development Sprint
- **Status:** Development 🚀
- **Assigned to:** Alex Rodriguez, Emma Watson
- **Due Date:** 2024-03-20
- **Priority:** High

## 💬 Comments & Discussion

### 💭 Sarah Chen - 2024-03-12 10:30

@Alex @Emma Let's implement dark mode! Here's the design mockup:

![Dark Mode Design](images/comment_0_0.png)

Key requirements:
- Toggle in settings menu
- Respect system preferences
- Smooth CSS transitions

#### Replies:

**↳ Alex Rodriguez** - 2024-03-12 11:15
  Great! I'll start with the theme context provider...

**↳ Emma Watson** - 2024-03-12 14:20
  I'll handle the UI components...

### 💭 Alex Rodriguez - 2024-03-13 16:45

Progress update: Core implementation done! ✅

![Dark Mode Working](images/comment_1_0.png)

[... continues with full context ...]
```

</details>

See [full example output](example_output.md) →

## 🚀 Quick Start

### 1. Install

```bash
git clone https://github.com/crarau/monday-to-ai.git
cd monday-to-ai
pip install -r requirements.txt
```

### 2. Get Your Monday.com API Token

1. Log into [Monday.com](https://monday.com)
2. Click your **avatar** → **Developers**
3. Click **Developer** → **My Access Tokens**
4. Create a personal API token
5. Copy and save it to `.env`:

```bash
echo 'MONDAY_API_TOKEN=your-token-here' > .env
```

### 3. Export Your First Task

```bash
# Using a Monday.com URL
python monday_exporter.py https://yourworkspace.monday.com/boards/123/pulses/456

# Or just the item ID
python monday_exporter.py 456
```

## 📂 Output Structure

Each export creates a clean folder structure:

```
Task_Name/
├── README.md           # Complete task in markdown
└── images/            # All images from comments
    ├── comment_0_0.png
    ├── reply_1_0.png
    └── attachment_2.pdf
```

## 🤝 Perfect for AI Workflows

### Use Case 1: Code Review with AI
Export your code review task from Monday.com and share with ChatGPT or Claude for detailed analysis.

### Use Case 2: Bug Investigation
Export bug reports with all screenshots and discussions for AI-assisted debugging.

### Use Case 3: Feature Planning
Share feature requests with AI to generate implementation plans and technical specs.

### Use Case 4: Documentation
Convert Monday.com tasks into technical documentation with AI assistance.

## 📊 What Gets Exported?

| Content Type | Exported | Details |
|-------------|----------|---------|
| Task metadata | ✅ | Title, status, dates, assignees |
| Custom fields | ✅ | All column values |
| Comments | ✅ | Full comment history |
| Replies | ✅ | Threaded conversations |
| Images | ✅ | Downloaded locally |
| File attachments | ✅ | Referenced with links |
| @mentions | ✅ | Preserved in text |
| Emojis | ✅ | Rendered correctly |
| Code blocks | ✅ | With syntax highlighting |
| Updates | ✅ | Status changes, edits |

## 💡 Pro Tips

### Batch Export
```bash
# Export multiple tasks
for id in 123 456 789; do
    python monday_exporter.py $id
done
```

### Generate PDFs
```bash
# Add --pdf flag for PDF output
python monday_exporter.py 456 --pdf
```

### CI/CD Integration
```yaml
# GitHub Action example
- name: Export Monday Task
  run: |
    python monday_exporter.py ${{ github.event.inputs.monday_id }}
```

## 🔧 Configuration

### Environment Variables
- `MONDAY_API_TOKEN` - Your Monday.com API token (required)

### Optional Settings
- Customize output directory
- Filter specific fields
- Choose export format

## 🛡️ Security

- ✅ API tokens stored in `.env` (never committed)
- ✅ Read-only access to Monday.com
- ✅ Local storage of exports
- ✅ No data sent to third parties

## 📈 Monday.com API Limits

- **Rate Limit:** 5,000 requests/minute
- **Complexity:** 10M points/minute
- This tool uses ~100 points per task

## 🤔 FAQ

**Q: Does this work with Monday.com Enterprise?**
A: Yes! Works with all Monday.com plans that have API access.

**Q: Can I export entire boards?**
A: Currently exports individual items. Board export coming soon!

**Q: Are subitems included?**
A: Yes, subitems are exported as part of the main task.

**Q: What about private boards?**
A: You can export any board/item your API token has access to.

## 🚦 Roadmap

- [ ] Bulk export multiple items
- [ ] Export entire boards
- [ ] Custom field mapping
- [ ] Notion export format
- [ ] Obsidian export format
- [ ] Interactive CLI with progress bars
- [ ] Web interface
- [ ] Monday.com app integration

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- Built for the [Monday.com](https://monday.com) community
- Inspired by the need to leverage AI for project management
- Special thanks to all contributors

## 🔗 Links

- **Monday.com:** [https://monday.com](https://monday.com)
- **API Documentation:** [https://developer.monday.com](https://developer.monday.com)
- **Report Issues:** [GitHub Issues](https://github.com/crarau/monday-to-ai/issues)

---

<p align="center">
  Made with ❤️ for better Monday.com → AI workflows
  <br>
  <a href="https://monday.com">Monday.com</a> •
  <a href="https://github.com/crarau/monday-to-ai">GitHub</a> •
  <a href="https://developer.monday.com">API Docs</a>
</p>