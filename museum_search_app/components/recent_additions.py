#!/usr/bin/env python3
"""
Recent Additions Component for SARA Museum App
Displays recently registered/added objects from the SARA database
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from datetime import datetime


class RecentAdditionsCarousel(BoxLayout):
    """Carousel displaying recently added objects from SARA"""
    
    def __init__(self, item_click_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(220)  # Same as recent searches
        self.padding = [0, dp(15), 0, dp(10)]
        self.spacing = dp(5)
        
        self.item_click_callback = item_click_callback
        
        self._create_carousel_layout()
    
    def _create_carousel_layout(self):
        """Create the carousel layout"""
        # Divider line
        divider = BoxLayout(
            size_hint_y=None,
            height=dp(1),
            padding=[dp(20), 0, dp(20), 0]
        )
        
        with divider.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light grey
            divider.line_rect = RoundedRectangle(
                pos=divider.pos,
                size=divider.size,
                radius=[0, 0, 0, 0]
            )
        
        divider.bind(pos=self._update_divider_bg, size=self._update_divider_bg)
        
        # Title section
        title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10),
            padding=[dp(20), dp(10), dp(20), 0]
        )
        
        recent_title = Label(
            text='Seneste tilføjelser',
            size_hint_x=1.0,
            font_size='16sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        recent_title.bind(size=recent_title.setter('text_size'))
        title_layout.add_widget(recent_title)
        
        # Carousel scroll view
        self.carousel_scroll = ScrollView(
            size_hint_y=None,
            height=dp(175),
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)
        )
        
        # Carousel layout
        self.carousel_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(15),
            padding=[dp(20), dp(5), dp(20), dp(5)]
        )
        self.carousel_layout.bind(minimum_width=self.carousel_layout.setter('width'))
        
        self.carousel_scroll.add_widget(self.carousel_layout)
        
        self.add_widget(divider)
        self.add_widget(title_layout)
        self.add_widget(self.carousel_scroll)
    
    def update_carousel(self, recent_objects):
        """Update carousel with recent objects data"""
        # Clear existing elements
        self.carousel_layout.clear_widgets()
        
        if not recent_objects:
            # Show "no recent objects" message
            no_recent_label = Label(
                text='Ingen nye tilføjelser endnu',
                size_hint_x=None,
                width=dp(320),
                font_size='16sp',
                color=(0.6, 0.6, 0.6, 1),
                halign='center',
                valign='middle'
            )
            no_recent_label.bind(size=no_recent_label.setter('text_size'))
            self.carousel_layout.add_widget(no_recent_label)
            return
        
        # Sort by creation date (newest first)
        sorted_objects = self._sort_by_date(recent_objects)
        
        # Add recent objects to carousel (max 20)
        for obj in sorted_objects[:20]:
            card = self._create_carousel_card(obj)
            self.carousel_layout.add_widget(card)
    
    def _sort_by_date(self, objects):
        """Sort objects by creation date (newest first)"""
        def get_creation_date(obj):
            # Try @created field first
            created = obj.get('@created', '')
            if created:
                try:
                    return datetime.fromisoformat(created.replace('Z', '+00:00'))
                except:
                    pass
            
            # Try input.date as fallback
            input_date = obj.get('input', {}).get('date', '')
            if input_date:
                try:
                    return datetime.strptime(input_date, '%Y-%m-%d')
                except:
                    pass
            
            # Return very old date if no date found
            return datetime(1900, 1, 1)
        
        return sorted(objects, key=get_creation_date, reverse=True)
    
    def _create_carousel_card(self, obj):
        """Create card for carousel - same design as recent searches"""
        # Card container - same size as recent searches
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(145),
            spacing=0,
            padding=[dp(2), dp(2), dp(2), 0]
        )
        
        # Add card background (white, square corners)
        with card_container.canvas.before:
            Color(1, 1, 1, 1)
            card_container.card_bg = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(0), dp(0), dp(0), dp(0)]
            )
        
        card_container.bind(pos=self._update_card_container_bg, size=self._update_card_container_bg)
        
        # Image section
        image_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(109)
        )
        
        # Get image URL
        image_url = self._get_image_url(obj)
        
        if image_url:
            image = AsyncImage(
                source=image_url,
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
                    width=dp(2)
                )
            
            image_section.bind(pos=self._update_image_overlay, size=self._update_image_overlay)
        else:
            # Placeholder
            placeholder_container = BoxLayout(orientation='vertical')
            
            with placeholder_container.canvas.before:
                Color(0.96, 0.97, 0.98, 1)
                placeholder_container.placeholder_bg = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[dp(8), dp(8), dp(8), dp(8)]
                )
            
            placeholder_container.bind(pos=self._update_placeholder_bg, size=self._update_placeholder_bg)
            
            placeholder_label = Label(
                text='No Image',
                font_size='14sp',
                color=(0.7, 0.7, 0.7, 1),
                halign='center',
                valign='middle'
            )
            placeholder_container.add_widget(placeholder_label)
            image_section.add_widget(placeholder_container)
        
        # Text section
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=1,
            height=dp(60),
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(3)
        )
        
        # Get title
        title_text = self._get_title(obj)
        if len(title_text) > 22:
            title_text = title_text[:19] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='13sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(130), None),
            shorten=True,
            shorten_from='right',
            max_lines=1
        )
        
        # Get object number
        obj_number = self._get_object_number(obj)
        if obj_number:
            subtitle_label = Label(
                text=obj_number,
                font_size='11sp',
                color=(0.46, 0.46, 0.46, 1),
                halign='center',
                valign='top',
                text_size=(dp(130), None)
            )
            text_section.add_widget(title_label)
            text_section.add_widget(subtitle_label)
        else:
            text_section.add_widget(title_label)
        
        # Assemble card
        card_container.add_widget(image_section)
        card_container.add_widget(text_section)
        
        # Make card clickable
        def on_card_click(touch):
            if card_container.collide_point(*touch.pos):
                if self.item_click_callback:
                    self.item_click_callback(obj)
                return True
            return False
        
        card_container.on_touch_down = on_card_click
        
        return card_container
    
    def _get_image_url(self, obj):
        """Extract image URL from object data"""
        # Try to get image from Reproduction field
        reproduction = obj.get('Reproduction', [])
        if reproduction and len(reproduction) > 0:
            ref = reproduction[0].get('reproduction.reference', {}).get('spans', [])
            if ref and len(ref) > 0:
                return ref[0].get('text', '')
        
        # Fallback to primaryImage if available
        return obj.get('primaryImage', '')
    
    def _get_title(self, obj):
        """Extract title from object data"""
        # Try Title field first
        title_field = obj.get('Title', [])
        if title_field and len(title_field) > 0:
            title_value = title_field[0].get('title.value', {}).get('spans', [])
            if title_value and len(title_value) > 0:
                return title_value[0].get('text', 'No title')
        
        # Fallback to title if available
        return obj.get('title', 'No title')
    
    def _get_object_number(self, obj):
        """Extract object number from object data"""
        # Try object_number field
        obj_num = obj.get('object_number', {}).get('spans', [])
        if obj_num and len(obj_num) > 0:
            return obj_num[0].get('text', '')
        
        # Fallback to objectNumber
        return obj.get('objectNumber', '')
    
    def _update_divider_bg(self, instance, value):
        """Update divider line"""
        if hasattr(instance, 'line_rect'):
            instance.line_rect.pos = instance.pos
            instance.line_rect.size = instance.size
    
    def _update_card_container_bg(self, instance, value):
        """Update card container background"""
        if hasattr(instance, 'card_bg'):
            instance.card_bg.pos = instance.pos
            instance.card_bg.size = instance.size
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_bg'):
            instance.placeholder_bg.pos = instance.pos
            instance.placeholder_bg.size = instance.size
    
    def _update_image_overlay(self, instance, value):
        """Update image overlay border with rounded corners"""
        if hasattr(instance, 'corner_border'):
            instance.corner_border.rounded_rectangle = (
                instance.x,
                instance.y, 
                instance.width,
                instance.height,
                dp(8)
            )
    
    def set_item_click_callback(self, callback):
        """Set the callback for when carousel items are clicked"""
        self.item_click_callback = callback
