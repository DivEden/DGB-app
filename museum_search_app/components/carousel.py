#!/usr/bin/env python3
"""
Recent Searches Carousel Component for SARA Museum App
Volt-style card carousel for displaying recent searches
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock


class RecentSearchesCarousel(BoxLayout):
    """Volt-style carousel for displaying recent searches"""
    
    def __init__(self, item_click_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(220)  # Reduced from 290dp for smaller cards (109 + 60 + padding)
        self.padding = [0, dp(15), 0, dp(10)]
        self.spacing = dp(5)  # Reduced spacing between title and carousel
        
        self.item_click_callback = item_click_callback
        
        self._create_carousel_layout()
        
    def safe_set_image_source(self, image_widget, local_path):
        """Sæt billede source sikkert på UI-tråden (Android-compatible)"""
        def _apply_source(dt):
            if image_widget and local_path:
                image_widget.source = str(local_path)
                image_widget.reload()
        Clock.schedule_once(_apply_source, 0)
    
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
            padding=[dp(20), dp(10), dp(20), 0]  # Add horizontal padding
        )
        
        recent_title = Label(
            text='Seneste søgninger',
            size_hint_x=1.0,
            font_size='16sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        recent_title.bind(size=recent_title.setter('text_size'))
        title_layout.add_widget(recent_title)
        
        # Carousel scroll view - height to accommodate smaller cards
        self.carousel_scroll = ScrollView(
            size_hint_y=None,
            height=dp(175),  # Reduced from 240dp (109 image + 60 text + padding)
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)
        )
        
        # Carousel layout with padding to prevent clipping
        self.carousel_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(15),  # Reduced from 20dp for tighter layout
            padding=[dp(20), dp(5), dp(20), dp(5)]  # Add padding especially on top
        )
        self.carousel_layout.bind(minimum_width=self.carousel_layout.setter('width'))
        
        self.carousel_scroll.add_widget(self.carousel_layout)
        
        self.add_widget(divider)
        self.add_widget(title_layout)
        self.add_widget(self.carousel_scroll)
    
    def update_carousel(self, recent_searches):
        """Update carousel with recent searches data"""
        # Clear existing elements
        self.carousel_layout.clear_widgets()
        
        if not recent_searches:
            # Show "no recent searches" message
            no_recent_label = Label(
                text='Ingen seneste søgninger endnu\nSøg efter objekter for at se dem her',
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
        
        # Add recent searches to carousel
        for search_item in recent_searches:
            card = self._create_carousel_card(search_item)
            self.carousel_layout.add_widget(card)
    
    def _create_carousel_card(self, search_item):
        """Create modern card for carousel with subtle shadow and border"""
        # Card container - fixed width 145dp for 2 cards + peek on phone
        # Add small padding to prevent clipping by rounded corners
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(145),  # Reduced from 200dp to fit 2 cards + peek
            spacing=0,
            padding=[dp(2), dp(2), dp(2), 0]  # Small padding on top and sides
        )
        
        # Add card background (no shadow)
        with card_container.canvas.before:
            # Main card background (white)
            Color(1, 1, 1, 1)
            card_container.card_bg = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[dp(0), dp(0), dp(0), dp(0)]  # Square corners
            )
        
        card_container.bind(pos=self._update_card_container_bg, size=self._update_card_container_bg)
        
        # Image section - fixed size 145x109dp (4:3 aspect ratio)
        image_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(109)  # 145 * 3/4 for 4:3 aspect
        )
        
        if search_item.get('hasImage') and search_item.get('primaryImage'):
            image = AsyncImage(
                source=search_item['primaryImage'],
                fit_mode="cover",  # Cover to fill entire space and maintain consistent size
                size_hint=(1, 1),
                mipmap=True
            )
            image_section.add_widget(image)
            
            # Add rounded corner overlay - draw only in corners to avoid visible lines
            with image_section.canvas.after:
                Color(1, 1, 1, 1)  # White to match card background
                # Create rounded border effect with minimal visibility
                image_section.corner_border = Line(
                    rounded_rectangle=(
                        image_section.x, 
                        image_section.y, 
                        image_section.width, 
                        image_section.height, 
                        dp(8)  # radius
                    ),
                    width=dp(3)  # Moderate width for corner coverage
                )
            
            image_section.bind(pos=self._update_image_overlay, size=self._update_image_overlay)
        else:
            # Placeholder with rounded corners
            placeholder_container = BoxLayout(orientation='vertical')
            
            with placeholder_container.canvas.before:
                Color(0.96, 0.97, 0.98, 1)
                placeholder_container.placeholder_bg = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[dp(8), dp(8), dp(8), dp(8)]  # Rounded corners on all sides
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
        
        # Text section - padding 8-12px, no separate background (uses card background)
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=1,
            height=dp(60),  # Reduced from 70dp for smaller cards
            padding=[dp(8), dp(8), dp(8), dp(8)],
            spacing=dp(3)
        )
        
        # Title - 14-16px semibold, max 1 line with ellipsis
        title_text = search_item.get('title', 'No title')
        if len(title_text) > 22:
            title_text = title_text[:19] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='13sp',  # Slightly smaller for smaller cards
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(130), None),  # Reduced from 180dp
            shorten=True,
            shorten_from='right',
            max_lines=1
        )
        
        # Subtitle (object number if available) - 12-13px, color #757575
        objektnummer = search_item.get('objectNumber', '')
        if objektnummer:
            subtitle_label = Label(
                text=objektnummer,
                font_size='11sp',  # Slightly smaller
                color=(0.46, 0.46, 0.46, 1),  # #757575
                halign='center',
                valign='top',
                text_size=(dp(130), None)  # Reduced from 180dp
            )
            text_section.add_widget(title_label)
            text_section.add_widget(subtitle_label)
        else:
            text_section.add_widget(title_label)
        
        # Assemble card
        card_container.add_widget(image_section)
        card_container.add_widget(text_section)
        
        # Make card clickable - using the old working approach
        def on_card_click(touch):
            print(f"Carousel card clicked! Touch: {touch.pos}")
            if card_container.collide_point(*touch.pos):
                print(f"Carousel: Touch collision detected for item: {search_item.get('title', 'Unknown')}")
                if self.item_click_callback:
                    print("Carousel: Calling item_click_callback")
                    self.item_click_callback(search_item)
                else:
                    print("Carousel: No item_click_callback set!")
                return True
            else:
                print("Carousel: Touch outside card bounds")
            return False
        
        card_container.on_touch_down = on_card_click
        
        return card_container
    
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