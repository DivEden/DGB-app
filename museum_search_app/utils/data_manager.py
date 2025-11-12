#!/usr/bin/env python3
"""
Data Manager for SARA Museum App
Handles data persistence, recent searches, and saved items
"""

import json
import os
from kivy.clock import Clock
from typing import List, Dict, Any


class DataManager:
    """Manages data persistence for the SARA Museum App (Singleton)"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if DataManager._initialized:
            return
            
        DataManager._initialized = True
        
        self.recent_searches = []
        self.saved_items = []
        self.recent_searches_file = 'recent_searches.json'
        self.saved_items_file = 'saved_items.json'
        
        # Load existing data
        self.load_recent_searches()
        self.load_saved_items()
    
    # Recent Searches Management
    def load_recent_searches(self):
        """Load recent searches from file"""
        try:
            if os.path.exists(self.recent_searches_file):
                with open(self.recent_searches_file, 'r', encoding='utf-8') as f:
                    self.recent_searches = json.load(f)
        except Exception as e:
            print(f"Error loading recent searches: {e}")
            self.recent_searches = []
    
    def save_recent_searches(self):
        """Save recent searches to file"""
        try:
            with open(self.recent_searches_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_searches, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving recent searches: {e}")
    
    def add_to_recent_searches(self, obj: Dict[str, Any]):
        """Add object to recent searches"""
        # Remove duplicates based on object number
        obj_number = obj.get('objectNumber', obj.get('NB', ''))
        self.recent_searches = [item for item in self.recent_searches 
                              if item.get('objectNumber', item.get('NB', '')) != obj_number]
        
        # Add to top with proper image mapping
        search_item = {
            'title': obj.get('title', obj.get('TI', 'No title')),
            'objectNumber': obj_number,
            'primaryImage': obj.get('primaryImage', ''),
            'hasImage': obj.get('hasImage', False),
            'timestamp': Clock.get_time()
        }
        
        self.recent_searches.insert(0, search_item)
        
        # Keep only the latest 10
        self.recent_searches = self.recent_searches[:10]
        
        # Save to file
        self.save_recent_searches()
    
    def get_recent_searches(self) -> List[Dict[str, Any]]:
        """Get list of recent searches"""
        return self.recent_searches
    
    def clear_recent_searches(self):
        """Clear all recent searches"""
        self.recent_searches = []
        self.save_recent_searches()
    
    # Saved Items Management
    def load_saved_items(self):
        """Load saved items from file"""
        try:
            if os.path.exists(self.saved_items_file):
                with open(self.saved_items_file, 'r', encoding='utf-8') as f:
                    self.saved_items = json.load(f)
            else:
                self.saved_items = []
        except Exception as e:
            print(f"Error loading saved items: {e}")
            self.saved_items = []
    
    def save_saved_items(self):
        """Save saved items to file"""
        try:
            with open(self.saved_items_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving saved items: {e}")
    
    def add_to_saved_items(self, obj: Dict[str, Any]):
        """Add object to saved items"""
        # Remove duplicates based on priref (unique ID) instead of object number
        obj_priref = obj.get('priref', '')
        if obj_priref:
            self.saved_items = [item for item in self.saved_items 
                               if item.get('priref', '') != obj_priref]
        
        # Add complete object data to saved items
        saved_item = dict(obj)  # Copy all data from the original object
        saved_item['timestamp'] = Clock.get_time()
        
        self.saved_items.insert(0, saved_item)
        
        # Save to file
        self.save_saved_items()
    
    def remove_from_saved_items(self, obj: Dict[str, Any]):
        """Remove object from saved items"""
        # Remove based on priref (unique ID) instead of object number
        obj_priref = obj.get('priref', '')
        if obj_priref:
            self.saved_items = [item for item in self.saved_items 
                               if item.get('priref', '') != obj_priref]
        self.save_saved_items()
    
    def get_saved_items(self) -> List[Dict[str, Any]]:
        """Get list of saved items"""
        return self.saved_items
    
    def is_item_saved(self, obj_number: str) -> bool:
        """Check if an item is saved by object number (may return True for multiple items with same number)"""
        return any(item.get('objectNumber', '') == obj_number 
                  for item in self.saved_items)
    
    def is_item_saved_by_priref(self, priref: str) -> bool:
        """Check if a specific item is saved by priref (unique check)"""
        return any(item.get('priref', '') == priref 
                  for item in self.saved_items)
    
    def clear_saved_items(self):
        """Clear all saved items"""
        self.saved_items = []
        self.save_saved_items()