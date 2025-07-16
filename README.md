# notion-action-extractor

Automatically extract ACTION items from Notion kanban cards and manage them in a centralized Master Action Items database with completion tracking.

## About the Project

This project solves the common problem of ACTION items getting lost or forgotten in project notes. When working with Notion kanban boards, team members often write ACTION items inline with their project updates, making it difficult to track and manage all pending tasks across multiple projects.

The Notion ACTION Items Extractor automatically finds ACTION items in your kanban card notes, creates individual trackable entries in a Master Action Items database, and syncs completion status back to the original notes with visual indicators.

**📖 For the complete story behind this project, detailed problem analysis, and comprehensive Notion setup guidance, see [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)**

### Project Mission
Streamline action item management in Notion workspaces by automating the extraction, tracking, and completion workflow for ACTION items embedded in project notes.

## How It Works

1. **Monitors** your Notion kanban database for cards containing "ACTION:" items in their Notes field
2. **Extracts** individual ACTION items using intelligent text parsing
3. **Creates** separate, trackable entries in your Master Action Items database
4. **Prevents duplicates** by comparing last edited vs. last processed timestamps
5. **Syncs completion** by adding ✅ indicators to original kanban notes when items are marked complete
6. **Runs automatically** via GitHub Actions 3 times daily (9am, 1pm, 5pm EST)

## Core Team

A list of core team members responsible for the code and documentation in this repository can be found in [COMMUNITY.md](COMMUNITY.md).

## Repository Structure

```
├── main.py                      # Entry point script
├── notion_action_extractor.py   # Core extraction and processing logic
├── requirements.txt             # Python dependencies
├── .github/workflows/           # GitHub Actions automation
```

## Local Development

### Prerequisites
- Python 3.13+
- Notion API integration token
- Two Notion databases: Kanban board and Master Action Items

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables:
   ```bash
   export NOTION_API_KEY="your_notion_token"
   export KANBAN_DB_ID="your_kanban_database_id"
   export ACTION_ITEMS_DB_ID="your_action_items_database_id"
   ```
4. Run: `python main.py`

### Required Notion Database Properties

**Kanban Database:**
- `Notes` (Rich Text) - where ACTION items are written
- `Task Name` (Title) - card titles
- `Last Processed` (Date) - tracks processing timestamps
- `Last Edited Time` (Last Edited Time) - automatic edit tracking

**Master Action Items Database:**
- `Action Item` (Title) - the action item text
- `Status` (Checkbox) - completion status
- `Source Card` (Relation) - links back to kanban card
- `Date Added` (Created Time) - creation timestamp

## Contributing
Thank you for considering contributing to this open source project! For more information about our contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Feedback
If you have ideas for improvements or encounter issues, please file an **issue on our GitHub repository**.

## Policies

This project follows standard open source practices and government guidelines for code sharing and collaboration.