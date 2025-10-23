#!/usr/bin/env python3
"""
Recent Searches Carousel Component for SARA Museum App
Volt-style card carousel for displaying recent searches
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class RecentSearchesCarousel(BoxLayout):
    """Volt-style carousel for displaying recent searches"""
    
    def __init__(self, item_click_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(240)
        self.padding = [0, dp(10), 0, dp(10)]
        self.spacing = dp(15)
        
        self.item_click_callback = item_click_callback
        
        self._create_carousel_layout()
    
    def _create_carousel_layout(self):
        """Create the carousel layout"""
        # Title section
        title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
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
        
        # Carousel scroll view
        self.carousel_scroll = ScrollView(
            size_hint_y=None,
            height=dp(190),
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)
        )
        
        # Carousel layout
        self.carousel_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(20)
        )
        self.carousel_layout.bind(minimum_width=self.carousel_layout.setter('width'))
        
        self.carousel_scroll.add_widget(self.carousel_layout)
        
        self.add_widget(title_layout)
        self.add_widget(self.carousel_scroll)
    
    def update_carousel(self, recent_searches):
        """Update carousel with recent searches data"""
        # Clear existing elements
        self.carousel_layout.clear_widgets()
        
        if not recent_searches:
            # Show "no recent searches" message
            no_recent_label = Label(
                text='Ingen seneste søgninger endnu\\nSøg efter objekter for at se dem her',
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
        """Create modern Volt-style card for carousel"""
        # Card container
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(130),
            spacing=0,
            padding=[0, 0, 0, 0]
        )
        
        # Add unified card background
        with card_container.canvas.before:
            # Soft shadow effect
            Color(0, 0, 0, 0.08)
            card_container.shadow_rect = RoundedRectangle(
                pos=[card_container.pos[0] + dp(2), card_container.pos[1] - dp(2)],
                size=card_container.size,
                radius=[16, 16, 16, 16]
            )
            # Main card background
            Color(1, 1, 1, 1)
            card_container.card_bg = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[16, 16, 16, 16]
            )
        
        card_container.bind(pos=self._update_carousel_card_bg, size=self._update_carousel_card_bg)
        
        # Image section (top two-thirds)
        image_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110)
        )
        
        if search_item.get('hasImage') and search_item.get('primaryImage'):
            image = AsyncImage(
                source=search_item['primaryImage'],
                fit_mode="cover",
                size_hint=(1, 1)
            )
            image_section.add_widget(image)
        else:
            # Placeholder
            placeholder_container = BoxLayout(orientation='vertical')
            
            with placeholder_container.canvas.before:
                Color(0.96, 0.97, 0.98, 1)
                placeholder_container.placeholder_bg = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[16, 16, 0, 0]
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
        
        # Text section (bottom third)
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(55),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(4)
        )
        
        # Title
        title_text = search_item.get('title', 'No title')
        if len(title_text) > 20:
            title_text = title_text[:17] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='12sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(106), None),
            max_lines=1
        )
        
        # Subtitle (object number if available)
        objektnummer = search_item.get('objectNumber', '')
        if objektnummer:
            subtitle_label = Label(
                text=objektnummer,
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
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_bg'):
            instance.placeholder_bg.pos = instance.pos
            instance.placeholder_bg.size = instance.size
    
    def _update_carousel_card_bg(self, instance, value):
        """Update carousel card background and shadow"""
        if hasattr(instance, 'shadow_rect'):
            instance.shadow_rect.pos = [instance.pos[0] + dp(2), instance.pos[1] - dp(2)]
            instance.shadow_rect.size = instance.size
        if hasattr(instance, 'card_bg'):
            instance.card_bg.pos = instance.pos
            instance.card_bg.size = instance.size
    
    def set_item_click_callback(self, callback):
        """Set the callback for when carousel items are clicked"""
        self.item_click_callback = callback