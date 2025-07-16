import re
import asyncio
import logging
from notion_client import AsyncClient
from datetime import datetime, timezone
import dateutil.parser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Property names used in Notion databases
NOTES_PROPERTY = "Notes"
TASK_NAME_PROPERTY = "Task Name"
STATUS_PROPERTY = "Status"
SOURCE_CARD_PROPERTY = "Source Card"
DATE_ADDED_PROPERTY = "Date Added"
LAST_PROCESSED_PROPERTY = "Last Processed"
LAST_EDITED_TIME_PROPERTY = "Last Edited Time"
ACTION_ITEM_PROPERTY = "Action Item"

# Regex patterns for finding and processing ACTION items
ACTION_PATTERN = r'ACTION:\s*([^-]+?)(?=\s*-?\s*ACTION:|$)'
COMPLETED_ACTION_PATTERN = r'✅\s*ACTION:\s*{}'
ACTION_REPLACEMENT_PATTERN = r'ACTION:\s*{}'

# Keywords and markers
ACTION_KEYWORD = "ACTION:"
COMPLETED_MARKER = "✅"

# Notion property types
RICH_TEXT_TYPE = "rich_text"
TEXT_TYPE = "text"
TITLE_TYPE = "title"
CHECKBOX_TYPE = "checkbox"
RELATION_TYPE = "relation"
DATE_TYPE = "date"

class NotionActionExtractor:
    """
    Extracts ACTION items from Notion kanban cards and manages them in a separate database.
    
    This class handles the complete lifecycle of action items:
    1. Finds ACTION items in kanban card notes
    2. Creates corresponding entries in the action items database
    3. Tracks completion status and updates original notes
    """
    
    def __init__(self, notion_token, kanban_db_id, action_items_db_id):
        """Initialize the extractor with Notion API credentials and database IDs."""
        self._validate_inputs(notion_token, kanban_db_id, action_items_db_id)
        
        self.notion = AsyncClient(auth=notion_token)
        self.kanban_db_id = kanban_db_id
        self.action_items_db_id = action_items_db_id
    
    # Validation 
    def _validate_inputs(self, notion_token, kanban_db_id, action_items_db_id):
        """Validate that all required inputs are provided and properly formatted."""
        if not notion_token or not notion_token.strip():
            raise ValueError("Notion token cannot be empty or None")
        
        if not kanban_db_id or not kanban_db_id.strip():
            raise ValueError("Kanban database ID cannot be empty or None")
        
        if not action_items_db_id or not action_items_db_id.strip():
            raise ValueError("Action items database ID cannot be empty or None")
        
        if not self._is_valid_database_id(kanban_db_id):
            raise ValueError(f"Invalid kanban database ID format: {kanban_db_id}")
        
        if not self._is_valid_database_id(action_items_db_id):
            raise ValueError(f"Invalid action items database ID format: {action_items_db_id}")
    
    def _is_valid_database_id(self, db_id):
        """Check if a database ID has a valid format (32 alphanumeric characters)."""
        cleaned_id = db_id.replace('-', '')
        return len(cleaned_id) == 32 and cleaned_id.isalnum()
    
    # Text Processing Methods
    def extract_action_items(self, text):
        """Extract ACTION items from text using regex pattern matching."""
        matches = re.findall(ACTION_PATTERN, text, re.IGNORECASE | re.MULTILINE)
        
        cleaned_items = []
        for item in matches:
            cleaned = item.strip().rstrip('-').strip()
            if cleaned: 
                cleaned_items.append(cleaned)
        
        logger.debug(f"Extracted {len(cleaned_items)} action items from text")
        return cleaned_items
    
    # Notion API Methods 
    async def get_notes_content(self, page_id):
        """Retrieve the Notes property content from a Notion page."""
        try:
            page = await self.notion.pages.retrieve(page_id)
            
            notes_property = page.get('properties', {}).get(NOTES_PROPERTY, {})
            
            if notes_property.get('type') == RICH_TEXT_TYPE:
                rich_text_items = notes_property.get(RICH_TEXT_TYPE, [])
                
                full_text = ""
                for item in rich_text_items:
                    if item.get('type') == TEXT_TYPE:
                        full_text += item.get(TEXT_TYPE, {}).get('content', '')
                
                logger.debug(f"Retrieved notes content for page {page_id}")
                return full_text
            
        except Exception as e:
            logger.error(f"Error getting notes content for page {page_id}: {e}")
        
        return ""
    
    async def create_action_item(self, action_text, source_page_id):
        """Create a new action item in the Master Action Items database."""
        try:
            new_page = await self.notion.pages.create(
                parent={"database_id": self.action_items_db_id},
                properties={
                    ACTION_ITEM_PROPERTY: {
                        TITLE_TYPE: [
                            {
                                "type": TEXT_TYPE,
                                TEXT_TYPE: {"content": action_text}
                            }
                        ]
                    },
                    STATUS_PROPERTY: {
                        CHECKBOX_TYPE: False
                    },
                    SOURCE_CARD_PROPERTY: {
                        RELATION_TYPE: [{"id": source_page_id}]
                    },
                    DATE_ADDED_PROPERTY: {
                        DATE_TYPE: {"start": datetime.now().isoformat()}
                    }
                }
            )
            logger.info(f"Created action item: {action_text}")
            return new_page
            
        except Exception as e:
            logger.error(f"Error creating action item '{action_text}': {e}")
            return None
    
    async def get_existing_action_items(self, source_page_id):
        """Get existing action items for a source page to prevent duplicates."""
        try:
            results = await self.notion.databases.query(
                database_id=self.action_items_db_id,
                filter={
                    "property": SOURCE_CARD_PROPERTY,
                    RELATION_TYPE: {"contains": source_page_id}
                }
            )
            
            existing_items = []
            for item in results['results']:
                title_prop = item['properties'].get(ACTION_ITEM_PROPERTY, {})
                if title_prop.get(TITLE_TYPE):
                    title = title_prop[TITLE_TYPE][0][TEXT_TYPE]['content']
                    existing_items.append(title)
            
            logger.debug(f"Found {len(existing_items)} existing action items for page {source_page_id}")
            return existing_items
            
        except Exception as e:
            logger.error(f"Error getting existing action items for page {source_page_id}: {e}")
            return []
    
    # Status Management Methods
    async def mark_as_processed(self, page_id):
        """Mark a kanban card as having its ACTION items extracted."""
        try:
            utc_now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z')

            await self.notion.pages.update(
                page_id=page_id,
                properties={
                    LAST_PROCESSED_PROPERTY: {DATE_TYPE: {"start": utc_now}}
                }
            )

            logger.debug(f"Updated last processed time to {utc_now} for page {page_id}")
        except Exception as e:
            logger.error(f"Error marking page {page_id} as processed: {e}")
    
    async def mark_action_completed(self, page_id, action_text):
        """Add ✅ indicator to completed ACTION items in kanban notes."""
        try:
            notes_content = await self.get_notes_content(page_id)

            already_completed_pattern = COMPLETED_ACTION_PATTERN.format(re.escape(action_text))
            if re.search(already_completed_pattern, notes_content, re.IGNORECASE):
                logger.debug(f"Action item already marked as completed: {action_text}")
                return  
            
            if notes_content and action_text in notes_content:
                pattern = ACTION_REPLACEMENT_PATTERN.format(re.escape(action_text))
                replacement = f"{COMPLETED_MARKER} {ACTION_KEYWORD} {action_text}"
                updated_content = re.sub(pattern, replacement, notes_content, count=1)
                
                await self.notion.pages.update(
                    page_id=page_id,
                    properties={
                        NOTES_PROPERTY: {
                            RICH_TEXT_TYPE: [
                                {
                                    "type": TEXT_TYPE,
                                    TEXT_TYPE: {"content": updated_content}
                                }
                            ]
                        }
                    }
                )
                logger.info(f"Marked action completed: {action_text}")
                
        except Exception as e:
            logger.error(f"Error marking action as completed '{action_text}': {e}")
    
    # Main Processing Methods
    async def process_single_page(self, page):
        """Process a single kanban page for ACTION items."""
        page_id = page['id']
        page_title = page['properties'][TASK_NAME_PROPERTY][TITLE_TYPE][0][TEXT_TYPE]['content']
        
        last_edited_prop = page['properties'].get(LAST_EDITED_TIME_PROPERTY, {})
        last_processed_prop = page['properties'].get(LAST_PROCESSED_PROPERTY, {})

        if last_edited_prop.get('last_edited_time'):
            last_edited = dateutil.parser.parse(last_edited_prop['last_edited_time'])
        else:
            last_edited = None

        if last_processed_prop.get(DATE_TYPE) and last_processed_prop[DATE_TYPE].get('start'):
            last_processed = dateutil.parser.parse(last_processed_prop[DATE_TYPE]['start'])
        else:
            last_processed = None

        # Only process if never processed before or if edited since last processing
        should_process = (
            last_processed is None or 
            (last_edited is not None and last_edited > last_processed)
        )
        
        if should_process:
            logger.info(f"Processing page: {page_title}")
            logger.debug(f"Last Edited: {last_edited}, Last Processed: {last_processed}")
            
            notes_content = await self.get_notes_content(page_id)
            
            if notes_content:
                action_items = self.extract_action_items(notes_content)
                
                if action_items:
                    logger.info(f"Found {len(action_items)} ACTION items in {page_title}")
                    
                    existing_items = await self.get_existing_action_items(page_id)
                    
                    create_tasks = []
                    for action_text in action_items:
                        if action_text not in existing_items:
                            create_tasks.append(self.create_action_item(action_text, page_id))
                        else:
                            logger.debug(f"Skipping duplicate: {action_text}")
                    
                    if create_tasks:
                        await asyncio.gather(*create_tasks)
                else:
                    logger.debug(f"No ACTION items found in notes for {page_title}")

                await self.mark_as_processed(page_id)
        else:
            logger.debug(f"Skipping page {page_title} since no updates since last processing)")
    
    async def process_kanban_updates(self):
        """Check for kanban items that need ACTION item extraction."""
        try:
            results = await self.notion.databases.query(
                database_id=self.kanban_db_id,
                filter={
                    "property": NOTES_PROPERTY,
                    RICH_TEXT_TYPE: {"contains": ACTION_KEYWORD}
                }
            )
            
            logger.info(f"Found {len(results['results'])} pages with ACTION items to process")
            
            tasks = [self.process_single_page(page) for page in results['results']]
            await asyncio.gather(*tasks)
                    
        except Exception as e:
            logger.error(f"Error processing kanban updates: {e}")
    
    async def monitor_completion_updates(self):
        """Check for completed action items and update original kanban notes."""
        try:
            results = await self.notion.databases.query(
                database_id=self.action_items_db_id,
                filter={
                    "property": STATUS_PROPERTY,
                    CHECKBOX_TYPE: {"equals": True}
                }
            )
            
            logger.info(f"Found {len(results['results'])} completed action items to process")
            
            tasks = []
            for action_item in results['results']:
                source_relation = action_item['properties'].get(SOURCE_CARD_PROPERTY, {}).get(RELATION_TYPE, [])
                if source_relation:
                    source_page_id = source_relation[0]['id']
                    action_text = action_item['properties'][ACTION_ITEM_PROPERTY][TITLE_TYPE][0][TEXT_TYPE]['content']
                    
                    tasks.append(self.mark_action_completed(source_page_id, action_text))
            
            if tasks:
                await asyncio.gather(*tasks)
                    
        except Exception as e:
            logger.error(f"Error processing completion updates: {e}")