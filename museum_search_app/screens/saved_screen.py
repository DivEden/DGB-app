#!/usr/bin/env python3
"""
Saved Items Screen for SARA Museum App
Displays saved museum objects and items in a grid format
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

from components.saved_item_grid import SavedItemGrid
from components.result_card import ResultCard
from utils.data_manager import DataManager


class SavedScreen(BoxLayout):
    """Screen for displaying saved museum items in a grid format"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Add white background
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[0, 0, 0, 0]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Initialize data manager
        self.data_manager = DataManager()
        
        # Track current view mode
        self.view_mode = 'grid'  # 'grid' or 'detail'
        self.current_detail_item = None
        
        self._create_layout()
        self.refresh_saved_items()
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _create_layout(self):
        """Create the main layout"""
        # Header section
        self.header_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(120),
            padding=[dp(20), dp(20), dp(20), dp(10)],
            spacing=dp(10)
        )
        
        # Title and navigation container
        title_nav_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Back button (initially hidden)
        self.back_btn = Button(
            text='← Tilbage',
            size_hint_x=None,
            width=dp(100),
            font_size='14sp',
            background_color=(0.5, 0.5, 0.5, 1),
            color=(1, 1, 1, 1),
            on_press=self.show_grid_view
        )
        self.back_btn.opacity = 0  # Hidden initially
        
        # Title
        self.title = Label(
            text='Gemte objekter',
            font_size='24sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center'
        )
        
        title_nav_container.add_widget(self.back_btn)
        title_nav_container.add_widget(self.title)
        
        # Clear all button
        self.clear_all_btn = Button(
            text='Ryd alle gemte objekter',
            size_hint_y=None,
            height=dp(40),
            font_size='14sp',
            background_color=(0.8, 0.3, 0.3, 1),
            color=(1, 1, 1, 1),
            on_press=self.clear_all_saved_items
        )
        
        self.header_layout.add_widget(title_nav_container)
        self.header_layout.add_widget(self.clear_all_btn)
        
        # Content container for switching between grid and detail view
        self.content_container = BoxLayout(orientation='vertical')
        
        # Saved items scroll container
        self.saved_scroll = ScrollView()
        
        self.saved_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=[0, dp(15), 0, dp(15)]
        )
        self.saved_layout.bind(minimum_height=self.saved_layout.setter('height'))
        
        self.saved_scroll.add_widget(self.saved_layout)
        self.content_container.add_widget(self.saved_scroll)
        
        self.add_widget(self.header_layout)
        self.add_widget(self.content_container)
    
    def refresh_saved_items(self):
        """Refresh the display of saved items"""
        # Clear current display
        self.saved_layout.clear_widgets()
        
        # Get saved items
        saved_items = self.data_manager.get_saved_items()
        
        if not saved_items:
            # Show empty state
            self._show_empty_state()
            self.clear_all_btn.disabled = True
            return
        
        self.clear_all_btn.disabled = False
        
        if self.view_mode == 'grid':
            # Show items count
            count_label = Label(
                text=f'{len(saved_items)} gemte objekt(er):',
                size_hint_y=None,
                height=dp(40),
                font_size='16sp',
                halign='center',
                color=(0.2, 0.6, 0.2, 1)
            )
            count_label.bind(size=count_label.setter('text_size'))
            self.saved_layout.add_widget(count_label)
            
            # Create grid container with centered layout
            grid_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                padding=[dp(10), dp(10), dp(10), dp(10)]
            )
            grid_container.bind(minimum_height=grid_container.setter('height'))
            
            # Left spacer for centering
            grid_container.add_widget(BoxLayout(size_hint_x=0.1))
            
            # Center container for grid
            center_container = BoxLayout(
                orientation='vertical',
                size_hint_x=0.8,
                size_hint_y=None
            )
            center_container.bind(minimum_height=center_container.setter('height'))
            
            # Create and add grid
            saved_grid = SavedItemGrid(
                saved_items=saved_items,
                remove_callback=self.remove_saved_item,
                view_callback=self.show_item_detail
            )
            
            center_container.add_widget(saved_grid)
            grid_container.add_widget(center_container)
            
            # Right spacer for centering
            grid_container.add_widget(BoxLayout(size_hint_x=0.1))
            
            self.saved_layout.add_widget(grid_container)
        
        elif self.view_mode == 'detail' and self.current_detail_item:
            # Show single item in detail view
            detail_card = ResultCard(
                obj_data=self.current_detail_item,
                save_callback=None  # No save button in detail view since it's already saved
            )
            self.saved_layout.add_widget(detail_card)
    
    def _show_empty_state(self):
        """Show message when no saved items"""
        empty_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            padding=[dp(40), dp(40), dp(40), dp(40)],
            spacing=dp(20)
        )
        
        with empty_container.canvas.before:
            Color(0.95, 0.95, 0.95, 1)
            empty_container.bg_rect = RoundedRectangle(
                pos=empty_container.pos,
                size=empty_container.size,
                radius=[15, 15, 15, 15]
            )
        
        empty_container.bind(pos=self._update_empty_bg, size=self._update_empty_bg)
        
        empty_icon = Label(
            text='',
            size_hint_y=None,
            height=dp(20),
            font_size='48sp',
            halign='center'
        )
        
        empty_message = Label(
            text='Ingen gemte objekter endnu\\n\\nGem objekter fra søgeresultaterne\\nfor at se dem her',
            size_hint_y=None,
            height=dp(80),
            font_size='16sp',
            halign='center',
            color=(0.5, 0.5, 0.5, 1)
        )
        empty_message.bind(size=empty_message.setter('text_size'))
        
        empty_container.add_widget(empty_icon)
        empty_container.add_widget(empty_message)
        
        self.saved_layout.add_widget(empty_container)
    
    def _update_empty_bg(self, instance, value):
        """Update empty state background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def remove_saved_item(self, obj_data):
        """Remove an item from saved items"""
        self.data_manager.remove_from_saved_items(obj_data)
        self.refresh_saved_items()
        print(f"Removed saved item: {obj_data.get('title', 'Unknown')}")
    
    def show_item_detail(self, obj_data):
        """Show detailed view of a saved item"""
        self.view_mode = 'detail'
        self.current_detail_item = obj_data
        self.title.text = obj_data.get('title', 'Objekt detaljer')
        self.back_btn.opacity = 1  # Show back button
        self.clear_all_btn.opacity = 0  # Hide clear all button in detail view
        self.refresh_saved_items()
    
    def show_grid_view(self, instance=None):
        """Return to grid view"""
        self.view_mode = 'grid'
        self.current_detail_item = None
        self.title.text = 'Gemte objekter'
        self.back_btn.opacity = 0  # Hide back button
        self.clear_all_btn.opacity = 1  # Show clear all button
        self.refresh_saved_items()
    
    def clear_all_saved_items(self, instance):
        """Clear all saved items"""
        self.data_manager.clear_saved_items()
        self.show_grid_view()  # Return to grid view after clearing
        print("Cleared all saved items")