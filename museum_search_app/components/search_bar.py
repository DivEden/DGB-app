#!/usr/bin/env python3
"""
Search Bar Component for SARA Museum App
Clean, minimalist search bar with icon
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp, cm


class SearchBar(BoxLayout):
    """Minimalist search bar with magnifying glass icon"""
    
    def __init__(self, search_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        # Height proportional to screen - approximately 0.55cm on a typical phone
        self.height = dp(35)
        # Width takes up about 88% of screen width (6.3/7.1 ≈ 0.887)
        self.size_hint_x = 0.887
        self.spacing = 0
        self.padding = [0, 0, 0, 0]
        
        self.search_callback = search_callback
        
        self._create_search_layout()
    
    def _create_search_layout(self):
        """Create the clean search bar with icon"""
        # Container with light grey background
        search_container = BoxLayout(
            orientation='horizontal',
            spacing=0,
            padding=[dp(10), dp(5), dp(10), dp(5)]
        )
        
        # Add light grey background - no rounded corners
        with search_container.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light grey
            search_container.bg_rect = RoundedRectangle(
                pos=search_container.pos,
                size=search_container.size,
                radius=[0, 0, 0, 0]  # No rounded corners
            )
        
        search_container.bind(pos=self._update_bg, size=self._update_bg)
        
        # Container for icon to center it vertically
        icon_container = BoxLayout(
            orientation='vertical',
            size_hint=(None, 1),
            width=dp(20)
        )
        
        # Magnifying glass icon - centered vertically
        icon = Image(
            source='utils/Images/search.png',
            size_hint=(1, None),
            height=dp(20),
            pos_hint={'center_y': 0.5},
            allow_stretch=True,
            keep_ratio=True,
            mipmap=True  # Better quality scaling
        )
        
        icon_container.add_widget(BoxLayout())  # Top spacer
        icon_container.add_widget(icon)
        icon_container.add_widget(BoxLayout())  # Bottom spacer
        
        # Create search input - no visible border, transparent background
        self.search_input = TextInput(
            hint_text='Søg...',
            hint_text_color=(0.6, 0.6, 0.6, 1),
            font_size='14sp',
            multiline=False,
            size_hint_x=1,
            padding=[dp(10), dp(5), dp(10), dp(5)],
            background_color=(0, 0, 0, 0),  # Transparent
            foreground_color=(0.2, 0.2, 0.2, 1),  # Dark grey text
            cursor_color=(0.2, 0.2, 0.2, 1),
            border=(0, 0, 0, 0)  # No border
        )
        
        self.search_input.bind(on_text_validate=self._on_search)
        print("SearchBar: Created minimalist search bar")
        
        search_container.add_widget(icon_container)
        search_container.add_widget(self.search_input)
        self.add_widget(search_container)
    
    def _update_bg(self, instance, value):
        """Update background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
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