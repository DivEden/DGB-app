#!/usr/bin/env python3
"""
Result Card Component for SARA Museum App
Displays individual search results in grid format (simple thumbnail + title)
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock

from utils.data_manager import DataManager


class ResultCard(BoxLayout):
    """Card component for displaying individual search results in grid format"""
    
    def __init__(self, obj_data=None, index=1, save_callback=None, click_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.size_hint_x = None
        self.width = dp(100)  # Reduced to fit 3 per row on phone
        self.height = dp(140)  # 90 image + 50 text
        self.spacing = dp(0)
        self.padding = [dp(2), dp(2), dp(2), 0]
        
        self.obj_data = obj_data or {}
        self.index = index
        self.save_callback = save_callback
        self.click_callback = click_callback
        
        # Initialize data manager for save functionality
        self.data_manager = DataManager()
        
        # Create card container with white background
        self.card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            spacing=dp(0)
        )
        
        # Add white background
        with self.card_container.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = RoundedRectangle(
                pos=self.card_container.pos,
                size=self.card_container.size,
                radius=[dp(0), dp(0), dp(0), dp(0)]  # Square corners
            )
        
        self.card_container.bind(pos=self._update_bg, size=self._update_bg)
        
        self._create_card()
        self.add_widget(self.card_container)
        
    def _update_bg(self, *args):
        """Update background rectangle"""
        self.bg_rect.pos = self.card_container.pos
        self.bg_rect.size = self.card_container.size
    
    def on_touch_down(self, touch):
        """Handle click to view details"""
        if self.card_container.collide_point(*touch.pos):
            if self.click_callback:
                self.click_callback(self.obj_data)
                return True
        return super().on_touch_down(touch)
        
    def _create_card(self):
        """Create simple grid card - image + title"""
        # Image section (top 2/3)
        self._create_image_section()
        
        # Text section (bottom 1/3)
        self._create_text_section()
    
    def _create_image_section(self):
        """Create image section - 100x90dp"""
        image_container = FloatLayout(
            size_hint_y=None,
            height=dp(90)
        )
        
        image_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        
        primary_image_url = self.obj_data.get('primaryImage', '')
        has_image = self.obj_data.get('hasImage', False)
        
        if has_image and primary_image_url:
            # Real image with cover mode
            image = AsyncImage(
                source=primary_image_url,
                fit_mode="cover",
                size_hint=(1, 1),
                mipmap=True
            )
            image_section.add_widget(image)
            
            # Add rounded corner overlay
            with image_section.canvas.after:
                Color(1, 1, 1, 1)
                image_section.corner_border = Line(
                    rounded_rectangle=(
                        image_section.x, 
                        image_section.y, 
                        image_section.width, 
                        image_section.height, 
                        dp(8)
                    ),
                    width=dp(3)
                )
            
            image_section.bind(pos=self._update_image_overlay, size=self._update_image_overlay)
        else:
            # No image placeholder
            placeholder_container = BoxLayout(orientation='vertical')
            
            with placeholder_container.canvas.before:
                Color(0.96, 0.97, 0.98, 1)
                placeholder_container.placeholder_rect = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[dp(8), dp(8), dp(8), dp(8)]
                )
            placeholder_container.bind(pos=self._update_placeholder_bg, size=self._update_placeholder_bg)
            
            # Show object number and title in placeholder
            placeholder_layout = BoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(5)
            )
            
            obj_num = self.obj_data.get('objectNumber', 'Ukendt')
            obj_label = Label(
                text=f'[b]{obj_num}[/b]',
                markup=True,
                font_size='16sp',
                color=(0.3, 0.3, 0.3, 1),
                halign='center',
                valign='middle'
            )
            obj_label.bind(size=obj_label.setter('text_size'))
            
            title_text = self.obj_data.get('title', 'No title')
            if len(title_text) > 25:
                title_text = title_text[:22] + '...'
            title_label = Label(
                text=title_text,
                font_size='12sp',
                color=(0.5, 0.5, 0.5, 1),
                halign='center',
                valign='middle'
            )
            title_label.bind(size=title_label.setter('text_size'))
            
            placeholder_layout.add_widget(obj_label)
            placeholder_layout.add_widget(title_label)
            placeholder_container.add_widget(placeholder_layout)
            image_section.add_widget(placeholder_container)
        
        image_container.add_widget(image_section)
        self.card_container.add_widget(image_container)
    
    def _create_text_section(self):
        """Create text section - title and object number"""
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(50),  # Reduced height
            padding=[dp(5), dp(5), dp(5), dp(5)],
            spacing=dp(2)
        )
        
        # Title - smaller font
        title_text = self.obj_data.get('title', 'No title')
        if len(title_text) > 20:
            title_text = title_text[:17] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='12sp',  # Smaller font
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(90), None),
            shorten=True,
            shorten_from='right',
            max_lines=1
        )
        
        # Object number - smaller font
        objektnummer = self.obj_data.get('objectNumber', '')
        if objektnummer:
            subtitle_label = Label(
                text=objektnummer,
                font_size='10sp',  # Smaller font
                color=(0.46, 0.46, 0.46, 1),
                halign='center',
                valign='top',
                text_size=(dp(90), None)
            )
            text_section.add_widget(title_label)
            text_section.add_widget(subtitle_label)
        else:
            text_section.add_widget(title_label)
        
        self.card_container.add_widget(text_section)
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_rect'):
            instance.placeholder_rect.pos = instance.pos
            instance.placeholder_rect.size = instance.size
    
    def _update_image_overlay(self, instance, value):
        """Update image overlay border"""
        if hasattr(instance, 'corner_border'):
            instance.corner_border.rounded_rectangle = (
                instance.x,
                instance.y, 
                instance.width,
                instance.height,
                dp(8)
            )
