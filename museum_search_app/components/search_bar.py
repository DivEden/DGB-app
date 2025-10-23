#!/usr/bin/env python3
"""
Search Bar Component for SARA Museum App
Clean, mobile-optimized search input and button
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class SearchBar(BoxLayout):
    """Mobile-optimized search bar with input and button"""
    
    def __init__(self, search_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(60)
        self.spacing = dp(5)
        self.padding = [dp(20), dp(10), dp(20), dp(10)]
        
        self.search_callback = search_callback
        
        self._create_search_layout()
    
    def _create_search_layout(self):
        """Create the search input and button layout"""
        search_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),
            spacing=dp(10)
        )
        
        # Create search input - simplified without custom border
        self.search_input = TextInput(
            hint_text='Indtast objektnummer...',
            font_size='16sp',
            multiline=False,
            size_hint_x=0.75,
            padding=[dp(15), dp(12)]
        )
        
        self.search_input.bind(
            on_text_validate=self._on_search
        )
        print("SearchBar: Created TextInput and bound on_text_validate to _on_search")
        
        # Create search button
        self.search_btn = Button(
            text='SOG',
            size_hint_x=0.25,
            font_size='14sp',
            bold=True,
            color=(1, 1, 1, 1),
            background_color=(0.15, 0.25, 0.4, 1)
        )
        
        self.search_btn.bind(on_release=self._on_search)
        print("SearchBar: Bound search button on_release to _on_search")
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(self.search_btn)
        self.add_widget(search_layout)
    
    def _on_search(self, *args):
        """Handle search button press or enter key"""
        query = self.search_input.text.strip()
        print(f"SearchBar._on_search called with query: '{query}'")
        print(f"SearchBar callback exists: {self.search_callback is not None}")
        if query and self.search_callback:
            print(f"SearchBar calling callback with: '{query}'")
            self.search_callback(query)
        else:
            print("SearchBar: Either no query or no callback")
    
    def clear_search(self):
        """Clear the search input"""
        self.search_input.text = ""
    
    def get_search_text(self):
        """Get current search text"""
        return self.search_input.text.strip()
    
    def set_search_callback(self, callback):
        """Set the search callback function"""
        self.search_callback = callback