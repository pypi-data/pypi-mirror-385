"""Notion API parser for dynamic task cards"""

import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..core.config import Config

class NotionParser:
    """Parser for Notion tasks via API"""
    
    def __init__(self, config: Config):
        self.config = config
        if not config.has_notion_config:
            raise ValueError("Notion configuration incomplete")
    
    def get_todays_tasks(self) -> List[Dict[str, Any]]:
        """Fetch today's tasks from Notion database"""
        if not self.config.has_notion_config:
            raise ValueError("Notion API key or database ID not configured")
        
        # Query Notion database for today's tasks
        url = f"https://api.notion.com/v1/databases/{self.config.tasks_database_id}/query"
        
        # Use the same query structure as the original working implementation
        query_data = {
            "filter": {
                "or": [
                    {
                        "property": "Status",
                        "status": {
                            "equals": "Today"
                        }
                    },
                    {
                        "property": "Status",
                        "status": {
                            "equals": "In Progress"
                        }
                    }
                ]
            },
            "sorts": [
                {
                    "property": "Due Date",
                    "direction": "ascending"
                }
            ]
        }
        
        try:
            response = requests.post(url, headers=self.config.notion_headers, json=query_data, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            tasks = []
            
            for result in data.get('results', []):
                task = self.format_notion_task_data(result)
                if task:
                    tasks.append(task)
            
            return tasks
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch Notion tasks: {e}")
    
    def format_notion_task_data(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format Notion task data into card format"""
        try:
            properties = task.get('properties', {})
            
            # Extract task name
            task_name = ""
            if 'Name' in properties and properties['Name']['title']:
                task_name = properties['Name']['title'][0]['text']['content']
            elif 'Task' in properties and properties['Task']['title']:
                task_name = properties['Task']['title'][0]['text']['content']
            
            if not task_name:
                return None
            
            # Extract priority
            priority = ""
            if 'Priority' in properties and properties['Priority']['select']:
                priority = properties['Priority']['select']['name']
            
            # Extract status
            status = ""
            if 'Status' in properties and properties['Status']['status']:
                status = properties['Status']['status']['name']
            
            # Extract due date
            due_date = ""
            if 'Due Date' in properties and properties['Due Date']['date']:
                due_date = properties['Due Date']['date']['start']
            
            # Extract description/notes
            content = ""
            if 'Description' in properties and properties['Description']['rich_text']:
                content = properties['Description']['rich_text'][0]['text']['content']
            
            # Generate QR code URL (link to Notion page)
            qr_data = task.get('url', '')
            
            return {
                'title': task_name,
                'priority': priority,
                'status': status,
                'due_date': due_date,
                'content': content,
                'qr_data': qr_data,
                'tasks': [{'text': task_name, 'priority': priority.lower() in ['high', 'urgent']}]
            }
            
        except Exception as e:
            # Silently handle error - could add logging here if needed
            return None
    
    def test_connection(self) -> bool:
        """Test Notion API connection"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.config.tasks_database_id}"
            response = requests.get(url, headers=self.config.notion_headers, timeout=10)
            response.raise_for_status()
            return True
        except:
            return False 