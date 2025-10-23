#!/usr/bin/env python3
"""
Saved Item Grid Component for SARA Museum App
Displays saved items in a grid format with image thumbnails
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class SavedItemGrid(GridLayout):
    """Grid layout for saved items with thumbnails"""
    
    def __init__(self, saved_items=None, remove_callback=None, view_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3  # Three columns like recent searches
        self.spacing = dp(15)
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        self.saved_items = saved_items or []
        self.remove_callback = remove_callback
        self.view_callback = view_callback
        
        self._populate_grid()
    
    def _populate_grid(self):
        """Populate the grid with saved items"""
        self.clear_widgets()
        
        for item in self.saved_items:
            grid_item = SavedGridItem(
                obj_data=item,
                remove_callback=self.remove_callback,
                view_callback=self.view_callback
            )
            self.add_widget(grid_item)


class SavedGridItem(BoxLayout):
    """Individual grid item for saved objects - styled like recent searches"""
    
    def __init__(self, obj_data=None, remove_callback=None, view_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(165)  # Similar to recent searches cards
        self.spacing = dp(0)
        self.padding = [0, 0, 0, 0]
        
        self.obj_data = obj_data or {}
        self.remove_callback = remove_callback
        self.view_callback = view_callback
        
        # Create card container with background
        self.card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(165),
            spacing=dp(0)
        )
        
        # Add background similar to recent searches
        with self.card_container.canvas.before:
            Color(0.98, 0.98, 0.98, 1)
            self.bg_rect = RoundedRectangle(
                pos=self.card_container.pos,
                size=self.card_container.size,
                radius=[12, 12, 12, 12]
            )
        
        self.card_container.bind(pos=self._update_bg, size=self._update_bg)
        
        self._create_item()
        self.add_widget(self.card_container)
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg_rect.pos = self.card_container.pos
        self.bg_rect.size = self.card_container.size
    
    def _create_item(self):
        """Create the grid item content - styled like recent searches"""
        # Image section (top 2/3, similar to recent searches)
        self._create_image_section()
        
        # Text section (bottom 1/3, similar to recent searches)
        self._create_text_section()
    
    def _create_image_section(self):
        """Create image section similar to recent searches"""
        image_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110),  # Similar to recent searches
            spacing=dp(0)
        )
        
        primary_image_url = self.obj_data.get('primaryImage', '')
        has_image = self.obj_data.get('hasImage', False)
        
        if has_image and primary_image_url:
            # Real image
            image = AsyncImage(
                source=primary_image_url,
                allow_stretch=True,
                keep_ratio=True
            )
            image_section.add_widget(image)
        else:
            # No image placeholder
            placeholder_container = BoxLayout(
                orientation='vertical',
                size_hint_y=1.0
            )
            
            with placeholder_container.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                placeholder_container.placeholder_rect = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[12, 12, 0, 0]  # Rounded top corners only
                )
            placeholder_container.bind(pos=self._update_placeholder_bg, size=self._update_placeholder_bg)
            
            placeholder_label = Label(
                text='Intet billede',
                font_size='11sp',
                color=(0.7, 0.7, 0.7, 1),
                halign='center',
                valign='middle'
            )
            placeholder_container.add_widget(placeholder_label)
            image_section.add_widget(placeholder_container)
        
        # Add small red X button overlay at bottom-right of image section
        button_overlay = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(30),
            padding=[0, 0, dp(8), dp(8)]
        )
        
        # Push to bottom
        button_overlay.add_widget(BoxLayout())
        
        # Button container aligned to right
        button_row = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(22)
        )
        
        # Spacer to push button to right
        button_row.add_widget(BoxLayout())
        
        # Small red X button
        remove_btn = Button(
            text='×',
            size_hint=(None, None),
            size=(dp(22), dp(22)),
            font_size='16sp',
            background_color=(0.9, 0.2, 0.2, 0.95),
            color=(1, 1, 1, 1),
            bold=True
        )
        remove_btn.bind(on_press=lambda x: self._handle_remove())
        button_row.add_widget(remove_btn)
        
        button_overlay.add_widget(button_row)
        
        self.card_container.add_widget(image_section)
        self.card_container.add_widget(button_overlay)
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_rect'):
            instance.placeholder_rect.pos = instance.pos
            instance.placeholder_rect.size = instance.size
    
    def _create_text_section(self):
        """Create text section similar to recent searches"""
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(35),  # Smaller since we have the button overlay
            padding=[dp(12), dp(4), dp(12), dp(4)],
            spacing=dp(2)
        )
        
        # Title (truncated like recent searches)
        title_text = self.obj_data.get('title', 'Ingen titel')
        if len(title_text) > 20:
            title_text = title_text[:17] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='12sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(106), None),  # Same width as recent searches
            max_lines=1
        )
        
        # Subtitle (object number)
        obj_number = self.obj_data.get('objectNumber', '')
        if obj_number:
            subtitle_label = Label(
                text=obj_number,
                font_size='10sp',
                color=(0.6, 0.6, 0.6, 1),
                halign='center',
                valign='top',
                text_size=(dp(106), None)
            )
            text_section.add_widget(title_label)
            text_section.add_widget(subtitle_label)
        else:
            text_section.add_widget(title_label)
        
        self.card_container.add_widget(text_section)
    
    def _handle_remove(self):
        """Handle remove button press"""
        if self.remove_callback:
            self.remove_callback(self.obj_data)