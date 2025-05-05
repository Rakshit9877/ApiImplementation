import requests
import logging
from django.conf import settings

# Configure logging
logger = logging.getLogger(__name__)

# Flask API base URL
FLASK_API_BASE_URL = getattr(settings, 'FLASK_API_BASE_URL', 'http://localhost:5000/api')

class FlaskAPIClient:
    """Client for consuming Flask REST APIs"""
    
    @classmethod
    def get_items(cls):
        """Get all items from Flask API"""
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/items")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching items from Flask API: {e}")
            return []
    
    @classmethod
    def get_item(cls, item_id):
        """Get a specific item from Flask API"""
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/items/{item_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching item {item_id} from Flask API: {e}")
            return None
    
    @classmethod
    def create_item(cls, item_data):
        """Create a new item via Flask API"""
        try:
            response = requests.post(
                f"{FLASK_API_BASE_URL}/items", 
                json=item_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating item in Flask API: {e}")
            return {"error": str(e)}
    
    @classmethod
    def update_item(cls, item_id, item_data):
        """Update an existing item via Flask API"""
        try:
            response = requests.put(
                f"{FLASK_API_BASE_URL}/items/{item_id}", 
                json=item_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating item {item_id} in Flask API: {e}")
            return {"error": str(e)}
    
    @classmethod
    def delete_item(cls, item_id):
        """Delete an item via Flask API"""
        try:
            response = requests.delete(f"{FLASK_API_BASE_URL}/items/{item_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting item {item_id} in Flask API: {e}")
            return {"error": str(e)}
    
    @classmethod
    def get_groups(cls):
        """Get all groups from Flask API"""
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/groups")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching groups from Flask API: {e}")
            return []
    
    @classmethod
    def get_group(cls, group_id):
        """Get a specific group from Flask API"""
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/groups/{group_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching group {group_id} from Flask API: {e}")
            return None
    
    @classmethod
    def create_group(cls, group_data):
        """Create a new group via Flask API"""
        try:
            response = requests.post(
                f"{FLASK_API_BASE_URL}/groups", 
                json=group_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating group in Flask API: {e}")
            return {"error": str(e)}
    
    @classmethod
    def update_group(cls, group_id, group_data):
        """Update an existing group via Flask API"""
        try:
            response = requests.put(
                f"{FLASK_API_BASE_URL}/groups/{group_id}", 
                json=group_data
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating group {group_id} in Flask API: {e}")
            return {"error": str(e)}
    
    @classmethod
    def delete_group(cls, group_id):
        """Delete a group via Flask API"""
        try:
            response = requests.delete(f"{FLASK_API_BASE_URL}/groups/{group_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error deleting group {group_id} in Flask API: {e}")
            return {"error": str(e)}
    
    @classmethod
    def get_dashboard_data(cls):
        """Get dashboard data from Flask API"""
        try:
            response = requests.get(f"{FLASK_API_BASE_URL}/dashboard")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching dashboard data from Flask API: {e}")
            return {} 