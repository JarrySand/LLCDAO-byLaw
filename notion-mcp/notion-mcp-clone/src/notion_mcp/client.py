"""Notion API client implementation."""

import os
from typing import Any, Dict, List, Optional, Union
import httpx
import logging
import sys
import rich
from rich.logging import RichHandler

from .models.notion import Database, Page, SearchResults, PropertyValue, Comment, CommentList, User

class NotionClient:
    """Client for interacting with the Notion API."""
    
    def __init__(self, api_key: str):
        """Initialize the Notion client.
        
        Args:
            api_key: Notion API key
        """
        self.api_key = api_key
        self.base_url = "https://api.notion.com/v1"
        # Updated to the latest stable Notion API version
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-02-22"
        }
        
        # Set up logging to stderr to avoid breaking MCP
        self.logger = logging.getLogger("notion_client")
        self.logger.setLevel(logging.INFO)
        
        # Make sure handler outputs to stderr
        if not self.logger.handlers:
            handler = RichHandler(rich_tracebacks=True, console=rich.console.Console(file=sys.stderr))
            self.logger.addHandler(handler)
    
    async def list_databases(self) -> List[Database]:
        """List all databases the integration has access to."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json={
                        "filter": {
                            "property": "object",
                            "value": "database"
                        },
                        "page_size": 100,
                        "sort": {
                            "direction": "descending",
                            "timestamp": "last_edited_time"
                        }
                    }
                )
                response.raise_for_status()
                data = response.json()
                if not data.get("results"):
                    return []
                return [Database.model_validate(db) for db in data["results"]]
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error listing databases: {str(e)}")
            raise
    
    async def query_database(
        self,
        database_id: str,
        filter: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Query a database."""
        try:
            body = {
                "page_size": page_size
            }
            if filter:
                body["filter"] = filter
            if sorts:
                body["sorts"] = sorts
            if start_cursor:
                body["start_cursor"] = start_cursor
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/databases/{database_id}/query",
                    headers=self.headers,
                    json=body
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error querying database {database_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error querying database {database_id}: {str(e)}")
            raise
    
    async def create_page(
        self,
        parent_id: str,
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Page:
        """Create a new page."""
        try:
            body = {
                "parent": {"database_id": parent_id},
                "properties": properties
            }
            if children:
                body["children"] = children
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/pages",
                    headers=self.headers,
                    json=body
                )
                response.raise_for_status()
                return Page.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error creating page: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error creating page: {str(e)}")
            raise
    
    async def update_page(
        self,
        page_id: str,
        properties: Dict[str, Any],
        archived: Optional[bool] = None
    ) -> Page:
        """Update a page."""
        try:
            body = {"properties": properties}
            if archived is not None:
                body["archived"] = archived
                
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/pages/{page_id}",
                    headers=self.headers,
                    json=body
                )
                response.raise_for_status()
                return Page.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error updating page {page_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error updating page {page_id}: {str(e)}")
            raise
    
    async def append_block_children(
        self,
        block_id: str,
        children: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Append block children to a page or block."""
        try:
            body = {"children": children}
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/blocks/{block_id}/children",
                    headers=self.headers,
                    json=body
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error appending blocks to {block_id}: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error appending blocks to {block_id}: {str(e)}")
            raise
    
    async def search(
        self,
        query: str = "",
        filter: Optional[Dict[str, Any]] = None,
        sort: Optional[Dict[str, Any]] = None,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> SearchResults:
        """Search Notion."""
        try:
            body = {
                "query": query,
                "page_size": page_size
            }
            if filter:
                body["filter"] = filter
            if sort:
                body["sort"] = sort
            if start_cursor:
                body["start_cursor"] = start_cursor
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/search",
                    headers=self.headers,
                    json=body
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert results based on their object type
                results = []
                for item in data.get("results", []):
                    try:
                        if item["object"] == "database":
                            results.append(Database.model_validate(item))
                        elif item["object"] == "page":
                            results.append(Page.model_validate(item))
                    except Exception as e:
                        self.logger.warning(f"Error processing search result: {str(e)}")
                        continue
                
                return SearchResults(
                    object="list",
                    results=results,
                    next_cursor=data.get("next_cursor"),
                    has_more=data.get("has_more", False)
                )
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error during search: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error during search: {str(e)}")
            raise
            
    async def get_block_children(
        self,
        block_id: str,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> Dict[str, Any]:
        """Get children blocks of a block."""
        try:
            params = {"page_size": page_size}
            if start_cursor:
                params["start_cursor"] = start_cursor
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/blocks/{block_id}/children",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error getting block children: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting block children: {str(e)}")
            raise
            
    async def get_database(
        self,
        database_id: str
    ) -> Database:
        """Get database metadata."""
        try:                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/databases/{database_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                return Database.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error getting database: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting database: {str(e)}")
            raise
            
    async def get_comments(
        self,
        block_id: str,
        start_cursor: Optional[str] = None,
        page_size: int = 100
    ) -> CommentList:
        """Get comments for a specific page or block."""
        try:
            params = {
                "block_id": block_id,
                "page_size": page_size
            }
            if start_cursor:
                params["start_cursor"] = start_cursor
                
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/comments",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Convert comment objects
                comments = []
                for comment_data in data.get("results", []):
                    try:
                        comments.append(Comment.model_validate(comment_data))
                    except Exception as e:
                        self.logger.warning(f"Error processing comment: {str(e)}")
                        continue
                
                return CommentList(
                    object="list",
                    results=comments,
                    next_cursor=data.get("next_cursor"),
                    has_more=data.get("has_more", False)
                )
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error getting comments: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Error getting comments: {str(e)}")
            raise
            
    async def create_comment(
        self,
        parent_id: str,
        rich_text: List[Dict[str, Any]]
    ) -> Comment:
        """Create a comment on a page or discussion."""
        try:
            body = {
                "parent": {
                    "page_id": parent_id
                },
                "rich_text": rich_text
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/comments",
                    headers=self.headers,
                    json=body
                )
                response.raise_for_status()
                return Comment.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error creating comment: {e.response.status_code} - {e.response.text}")
            raise  
        except Exception as e:
            self.logger.error(f"Error creating comment: {str(e)}")
            raise
            
    async def get_comment_context(
        self,
        comment: Comment
    ) -> Dict[str, Any]:
        """Get detailed context information for a comment."""
        try:
            context = {
                "comment_id": comment.id,
                "discussion_id": comment.discussion_id,
                "created_time": comment.created_time,
                "author": {
                    "id": comment.created_by.id if hasattr(comment.created_by, 'id') else None,
                    "type": comment.created_by.type if hasattr(comment.created_by, 'type') else None
                },
                "content": "".join([rt.plain_text if hasattr(rt, 'plain_text') else rt.get('plain_text', '') for rt in comment.rich_text]),
                "parent": comment.parent,
                "target_content": None
            }
            
            # Get the content of the target block/page
            parent_id = comment.parent.get('block_id') or comment.parent.get('page_id')
            if parent_id:
                try:
                    # Try to get block children to understand what was commented on
                    block_info = await self.get_block_children(parent_id)
                    if block_info.get('results'):
                        context["target_content"] = {
                            "type": "block_with_children",
                            "block_count": len(block_info['results']),
                            "first_blocks": [
                                {
                                    "id": block.get('id'),
                                    "type": block.get('type'),
                                    "content": self._extract_block_text(block)
                                }
                                for block in block_info['results'][:3]  # First 3 blocks for context
                            ]
                        }
                    else:
                        # This might be a specific block, try to get its parent
                        context["target_content"] = {
                            "type": "specific_block",
                            "block_id": parent_id
                        }
                except Exception as e:
                    self.logger.warning(f"Could not get target content: {str(e)}")
                    context["target_content"] = {"type": "unknown", "error": str(e)}
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting comment context: {str(e)}")
            raise
            
    def _extract_block_text(self, block: Dict[str, Any]) -> str:
        """Extract text content from a block."""
        block_type = block.get('type', '')
        if not block_type:
            return ""
            
        type_data = block.get(block_type, {})
        rich_text = type_data.get('rich_text', [])
        
        if rich_text:
            return "".join([rt.get('plain_text', '') for rt in rich_text])[:100]  # First 100 chars
        
        return f"[{block_type} block]" 