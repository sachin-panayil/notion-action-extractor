import os
import asyncio

from notion_action_extractor import NotionActionExtractor

async def main():
    NOTION_TOKEN = os.environ("NOTION_API_KEY")
    KANBAN_DB_ID = os.environ("KANBAN_DB_ID")
    ACTION_ITEMS_DB_ID = os.environ("ACTION_ITEMS_DB_ID")

    extractor = NotionActionExtractor(NOTION_TOKEN, KANBAN_DB_ID, ACTION_ITEMS_DB_ID)

    await extractor.process_kanban_updates()
    await extractor.monitor_completion_updates()

if __name__ == "__main__":
    asyncio.run(main())