# How to Contribute

We're so thankful you're considering contributing to the notion-action-extractor. If you're unsure about anything, just ask -- or submit the issue or pull request anyway. The worst that can happen is you'll be politely asked to change something. We appreciate all friendly contributions.

We encourage you to read this project's CONTRIBUTING policy (you are here), its [LICENSE](LICENSE.md), and its [README](README.md).

## Getting Started

Good first issues for newcomers:
- Enhancing logging and error messages
- Writing tests for the text extraction functions

### Building Dependencies

**System Requirements:**
- Python 3.13 or higher
- pip package manager
- Git

**Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**Required packages:**
- `notion-client` - Async Notion API client
- `python-dateutil` - Date parsing utilities
- `asyncio` - Asynchronous programming support

### Building the Project

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sachin-panayil/notion-action-extractor.git
   cd notion-action-extractor
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env  # If available
   # Edit .env with your Notion credentials
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Test the setup:**
   ```bash
   python main.py
   ```

### Workflow and Branching

We follow the [GitHub Flow Workflow](https://guides.github.com/introduction/flow/)

1. Fork the project 
2. Check out the `main` branch 
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Write code and tests for your change 
5. From your branch, make a pull request against `main`
6. Work with repo maintainers to get your change reviewed 
7. Wait for your change to be pulled into `main`
8. Delete your feature branch

### Testing Conventions

**Manual Testing:**
- Test with sample Notion databases containing various ACTION item formats
- Verify that duplicate prevention works correctly
- Check completion tracking flows from Master Action Items back to kanban notes

**Areas needing automated tests:**
- `extract_action_items()` function with various text inputs
- Time comparison logic in `process_single_page()`
- Error handling for malformed database responses
