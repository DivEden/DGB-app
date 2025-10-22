#!/usr/bin/env python3
"""
SARA Museum Søge App - Mobil Applikation (Kivy Version)
Søg og udforsk objekter fra SARA databasen 
Bygget med Kivy til cross-platform mobil deployment
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle, PushMatrix, PopMatrix
from kivy.graphics.instructions import InstructionGroup
import json
import os
from threading import Thread
import traceback

from sara_api import SaraAPI


class SearchScreen(Screen):
    """Skærm til at søge efter museums objekter"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "search"
        self.api = SaraAPI()
        self.recent_searches = []
        self.recent_searches_file = "recent_searches.json"
        self.saved_searches = []
        self.saved_searches_file = "saved_searches.json"
        self.load_recent_searches()
        self.load_saved_searches()
        self.build_screen()
    
    def load_recent_searches(self):
        """Indlæs seneste søgninger fra fil"""
        try:
            if os.path.exists(self.recent_searches_file):
                with open(self.recent_searches_file, 'r', encoding='utf-8') as f:
                    self.recent_searches = json.load(f)
        except Exception as e:
            print(f"Fejl ved indlæsning af seneste søgninger: {e}")
            self.recent_searches = []
    
    def save_recent_searches(self):
        """Gem seneste søgninger til fil"""
        try:
            with open(self.recent_searches_file, 'w', encoding='utf-8') as f:
                json.dump(self.recent_searches, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fejl ved gemning af seneste søgninger: {e}")
    
    def load_saved_searches(self):
        """Indlæs gemte søgninger fra fil"""
        try:
            if os.path.exists(self.saved_searches_file):
                with open(self.saved_searches_file, 'r', encoding='utf-8') as f:
                    self.saved_searches = json.load(f)
        except Exception as e:
            print(f"Fejl ved indlæsning af gemte søgninger: {e}")
            self.saved_searches = []
    
    def save_saved_searches(self):
        """Gem gemte søgninger til fil"""
        try:
            with open(self.saved_searches_file, 'w', encoding='utf-8') as f:
                json.dump(self.saved_searches, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Fejl ved gemning af gemte søgninger: {e}")
    
    def add_to_saved_searches(self, obj):
        """Tilføj objekt til gemte søgninger"""
        obj_number = obj.get('objectNumber', obj.get('NB', ''))
        
        # Tjek om det allerede er gemt
        for item in self.saved_searches:
            if item.get('objectNumber', item.get('NB', '')) == obj_number:
                return False  # Allerede gemt
        
        # Tilføj til gemte
        search_item = {
            'title': obj.get('title', obj.get('TI', 'Ingen titel')),
            'objectNumber': obj_number,
            'primaryImage': obj.get('primaryImage', ''),
            'hasImage': obj.get('hasImage', False),
            'timestamp': Clock.get_time()
        }
        
        self.saved_searches.insert(0, search_item)
        self.save_saved_searches()
        return True  # Successfuldt gemt
    
    def remove_from_saved_searches(self, obj_number):
        """Fjern objekt fra gemte søgninger"""
        self.saved_searches = [item for item in self.saved_searches 
                              if item.get('objectNumber', item.get('NB', '')) != obj_number]
        self.save_saved_searches()
        
        # Opdater gemte skærm hvis den er åben
        if self.manager and self.manager.has_screen('saved'):
            saved_screen = self.manager.get_screen('saved')
            saved_screen.update_saved_carousel()
    
    def is_saved(self, obj_number):
        """Tjek om objekt er gemt"""
        for item in self.saved_searches:
            if item.get('objectNumber', item.get('NB', '')) == obj_number:
                return True
        return False
    
    def add_to_recent_searches(self, obj):
        """Add object to recent searches"""
        # Remove duplicates based on object number
        obj_number = obj.get('objectNumber', obj.get('NB', ''))
        self.recent_searches = [item for item in self.recent_searches 
                              if item.get('objectNumber', item.get('NB', '')) != obj_number]
        
        # Debug: Print the object data to see what image fields are available
        print(f"DEBUG: Adding to recent - Object data keys: {list(obj.keys())}")
        print(f"DEBUG: hasImage: {obj.get('hasImage')}, primaryImage: {obj.get('primaryImage')}")
        
        # Add to top with proper image mapping
        search_item = {
            'title': obj.get('title', obj.get('TI', 'Ingen titel')),
            'objectNumber': obj_number,
            'primaryImage': obj.get('primaryImage', ''),  # This should be the image URL
            'hasImage': obj.get('hasImage', False),  # This should be True/False
            'timestamp': Clock.get_time()
        }
        
        print(f"DEBUG: Created search_item - hasImage: {search_item['hasImage']}, primaryImage: {search_item['primaryImage']}")
        
        self.recent_searches.insert(0, search_item)
        
        # Keep only the latest 10
        self.recent_searches = self.recent_searches[:10]
        
        # Save to file
        self.save_recent_searches()
        
        # Update carousel
        self.update_recent_carousel()
    
    def clear_recent_searches(self):
        """Ryd seneste søgninger"""
        self.recent_searches = []
        self.save_recent_searches()
        self.update_recent_carousel()
    
    def build_screen(self):
        """Byg søge interfacet med bottom navigation"""
        # Hovedlayout
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(0),
            padding=[0, 0, 0, 0]
        )
        
        # Clean white background
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # Clean white background
            main_layout.bg = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Content area (takes most space)
        content_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=[dp(20), dp(20), dp(20), dp(10)]
        )
        
        # Modern search section with clear styling
        search_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),  # Reduced height for phone screens
            spacing=dp(5),
            padding=[dp(20), dp(10), dp(20), dp(10)]  # Horizontal padding for phone screens
        )
        
        search_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),  # Reduced height for mobile
            spacing=dp(10)  # Reduced spacing
        )
        
        # Clear search input with rounded corners
        self.search_input = TextInput(
            hint_text='Indtast objektnummer...',
            font_size='16sp',  # Slightly smaller for mobile
            multiline=False,
            size_hint_x=0.75,
            background_color=(1, 1, 1, 0.9),  # Semi-transparent white background
            foreground_color=(0.2, 0.2, 0.2, 1),  # Dark gray text
            cursor_color=(0.4, 0.4, 0.4, 1),  # Gray cursor
            padding=[dp(15), dp(12)]  # Adjusted padding
        )
        
        self.search_input.bind(on_text_validate=self.search_objects)
        
        # Compact navy blue search button
        search_btn = Button(
            text='SØG',
            size_hint_x=0.25,
            font_size='14sp',  # Smaller font for mobile
            bold=True,
            color=(1, 1, 1, 1),  # White text
            background_color=(0.15, 0.25, 0.4, 1)  # Navy blue background
        )
        
        search_btn.bind(on_release=self.search_objects)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        search_container.add_widget(search_layout)
        content_layout.add_widget(search_container)
        
        # Recent searches carousel with Volt-style design
        self.recent_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(240),  # Increased height for larger cards
            padding=[0, dp(10), 0, dp(10)],
            spacing=dp(15)
        )
        
        # Titel for seneste søgninger
        recent_title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )
        
        recent_title = Label(
            text='Seneste søgninger',
            size_hint_x=1.0,  # Take full width since no clear button
            font_size='16sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        recent_title.bind(size=recent_title.setter('text_size'))
        
        recent_title_layout.add_widget(recent_title)
        
        # Carousel scroll view with generous spacing
        self.carousel_scroll = ScrollView(
            size_hint_y=None,
            height=dp(190),  # Increased height for larger cards
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)  # Hide scrollbars
        )
        
        # Carousel layout - Volt-style with generous spacing
        self.carousel_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(20),  # Generous spacing between cards as specified
            padding=[dp(15), 0, dp(15), 0]
        )
        self.carousel_layout.bind(minimum_width=self.carousel_layout.setter('width'))
        
        self.carousel_scroll.add_widget(self.carousel_layout)
        
        self.recent_container.add_widget(recent_title_layout)
        self.recent_container.add_widget(self.carousel_scroll)
        
        content_layout.add_widget(self.recent_container)
        
        # Resultater sektion med elegant styling
        self.results_scroll = ScrollView()
        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=[0, dp(15), 0, dp(15)]
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        self.results_scroll.add_widget(self.results_layout)
        content_layout.add_widget(self.results_scroll)
        
        # Add content to main layout
        main_layout.add_widget(content_layout)
        
        # Modern search section with clear styling
        search_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),  # Reduced height for phone screens
            spacing=dp(5),
            padding=[dp(20), dp(10), dp(20), dp(10)]  # Horizontal padding for phone screens
        )
        
        search_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(45),  # Reduced height for mobile
            spacing=dp(10)  # Reduced spacing
        )
        
        # Clear search input with rounded corners
        self.search_input = TextInput(
            hint_text='Indtast objektnummer...',
            font_size='16sp',  # Slightly smaller for mobile
            multiline=False,
            size_hint_x=0.75,
            background_color=(1, 1, 1, 0.9),  # Semi-transparent white background
            foreground_color=(0.2, 0.2, 0.2, 1),  # Dark gray text
            cursor_color=(0.4, 0.4, 0.4, 1),  # Gray cursor
            padding=[dp(15), dp(12)]  # Adjusted padding
        )
        
        self.search_input.bind(on_text_validate=self.search_objects)
        
        # Compact navy blue search button
        search_btn = Button(
            text='SØG',
            size_hint_x=0.25,
            font_size='14sp',  # Smaller font for mobile
            bold=True,
            color=(1, 1, 1, 1),  # White text
            background_color=(0.15, 0.25, 0.4, 1)  # Navy blue background
        )
        
        search_btn.bind(on_release=self.search_objects)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        search_container.add_widget(search_layout)
        main_layout.add_widget(search_container)
        
        # Recent searches carousel with Volt-style design
        self.recent_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(240),  # Increased height for larger cards
            padding=[0, dp(10), 0, dp(10)],
            spacing=dp(15)
        )
        
        # Titel for seneste søgninger
        recent_title_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(10)
        )
        
        recent_title = Label(
            text='Seneste søgninger',
            size_hint_x=1.0,  # Take full width since no clear button
            font_size='16sp',
            bold=True,
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='middle'
        )
        recent_title.bind(size=recent_title.setter('text_size'))
        
        recent_title_layout.add_widget(recent_title)
        
        # Carousel scroll view with generous spacing
        self.carousel_scroll = ScrollView(
            size_hint_y=None,
            height=dp(190),  # Increased height for larger cards
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)  # Hide scrollbars
        )
        
        # Carousel layout - Volt-style with generous spacing
        self.carousel_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(20),  # Generous spacing between cards as specified
            padding=[dp(15), 0, dp(15), 0]
        )
        self.carousel_layout.bind(minimum_width=self.carousel_layout.setter('width'))
        
        self.carousel_scroll.add_widget(self.carousel_layout)
        
        self.recent_container.add_widget(recent_title_layout)
        self.recent_container.add_widget(self.carousel_scroll)
        
        main_layout.add_widget(self.recent_container)
        
        # Resultater sektion med elegant styling
        self.results_scroll = ScrollView()
        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None,
            padding=[0, dp(15), 0, dp(15)]
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        self.results_scroll.add_widget(self.results_layout)
        content_layout.add_widget(self.results_scroll)
        
        # Add content to main layout
        main_layout.add_widget(content_layout)
        
        # Bottom navigation bar
        bottom_nav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(20),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Bottom nav background
        with bottom_nav.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            bottom_nav.bg_rect = Rectangle(
                pos=bottom_nav.pos,
                size=bottom_nav.size
            )
        bottom_nav.bind(pos=self._update_bottom_nav_bg, size=self._update_bottom_nav_bg)
        
        # Home button
        home_btn = Button(
            text='🏠 Hjem',
            size_hint_x=0.5,
            font_size='14sp',
            background_color=(0, 0, 0, 0)  # Transparent
        )
        
        # Style home button
        with home_btn.canvas.before:
            Color(0.15, 0.25, 0.4, 1)  # Navy blue
            home_btn.bg_rect = RoundedRectangle(
                pos=home_btn.pos,
                size=home_btn.size,
                radius=[8, 8, 8, 8]
            )
        home_btn.bind(pos=self._update_nav_button_bg, size=self._update_nav_button_bg)
        home_btn.bind(on_press=self.go_to_home)
        home_btn.color = [1, 1, 1, 1]  # White text
        
        # Saved searches button
        saved_btn = Button(
            text='⭐ Gemte',
            size_hint_x=0.5,
            font_size='14sp',
            background_color=(0, 0, 0, 0)  # Transparent
        )
        
        # Style saved button
        with saved_btn.canvas.before:
            Color(0.15, 0.25, 0.4, 1)  # Navy blue
            saved_btn.bg_rect = RoundedRectangle(
                pos=saved_btn.pos,
                size=saved_btn.size,
                radius=[8, 8, 8, 8]
            )
        saved_btn.bind(pos=self._update_nav_button_bg, size=self._update_nav_button_bg)
        saved_btn.bind(on_press=self.go_to_saved)
        saved_btn.color = [1, 1, 1, 1]  # White text
        
        bottom_nav.add_widget(home_btn)
        bottom_nav.add_widget(saved_btn)
        
        main_layout.add_widget(bottom_nav)
        
        # Velkomstbesked
        self.update_recent_carousel()
        
        self.add_widget(main_layout)
    
    def _update_bg(self, instance, value):
        """Opdater baggrundsfarve"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def _update_instruction_bg(self, instance, value):
        """Opdater instruktions baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = [instance.pos[0] + dp(10), instance.pos[1] + dp(5)]
            instance.bg_rect.size = [instance.size[0] - dp(20), instance.size[1] - dp(10)]
    
    def _update_button_bg(self, instance, value):
        """Opdater knap baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_bottom_nav_bg(self, instance, value):
        """Opdater bottom navigation baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_nav_button_bg(self, instance, value):
        """Opdater navigation knap baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def go_to_home(self, *args):
        """Gå til hjemmeside (ryd søgeresultater og vis velkomst)"""
        self.clear_results()
        self.search_input.text = ""
    
    def go_to_saved(self, *args):
        """Gå til gemte søgninger"""
        if self.manager:
            if not self.manager.has_screen('saved'):
                # Opret saved screen hvis den ikke eksisterer
                saved_screen = SavedSearchesScreen()
                saved_screen.search_screen = self  # Reference til at kunne gemme
                self.manager.add_widget(saved_screen)
            self.manager.current = 'saved'
    
    def update_recent_carousel(self):
        """Opdater carousel med seneste søgninger"""
        # Ryd eksisterende elementer
        self.carousel_layout.clear_widgets()
        
        if not self.recent_searches:
            # Vis "ingen seneste søgninger" besked
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
        
        # Tilføj seneste søgninger til carousel
        for search_item in self.recent_searches:
            card = self.create_carousel_card(search_item)
            self.carousel_layout.add_widget(card)
    
    def create_carousel_card(self, search_item):
        """Create modern Volt-style card for carousel - 3 cards on phone screen"""
        # Card container with generous spacing between cards - use FloatLayout for overlays
        from kivy.uix.floatlayout import FloatLayout
        
        card_container = FloatLayout(
            size_hint_x=None,
            width=dp(130)
        )
        
        # Main content area
        content_area = BoxLayout(
            orientation='vertical',
            spacing=0,
            padding=[0, 0, 0, 0],
            size_hint=(1, 1)
        )
        
        # Image section - takes up top two-thirds of card with rounded top corners
        image_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(110)  # Increased for 2/3 proportion
        )
        
        if search_item.get('hasImage') and search_item.get('primaryImage'):
            # Debug: Print image info
            print(f"DEBUG: Item has image - hasImage: {search_item.get('hasImage')}, primaryImage: {search_item.get('primaryImage')}")
            # Create simple image that will be masked by the overall card shape
            image = AsyncImage(
                source=search_item['primaryImage'],
                fit_mode="cover",
                size_hint=(1, 1)
            )
            image_section.add_widget(image)
        else:
            # Debug: Print why no image
            print(f"DEBUG: No image - hasImage: {search_item.get('hasImage')}, primaryImage: {search_item.get('primaryImage')}")
            # Modern placeholder with soft pastel background and rounded top corners
            placeholder_container = BoxLayout(
                orientation='vertical'
            )
            
            # Soft pastel background for placeholder with rounded top corners only
            with placeholder_container.canvas.before:
                Color(0.96, 0.97, 0.98, 1)  # Very soft blue-gray
                placeholder_container.placeholder_bg = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[16, 16, 0, 0]  # Only round top corners
                )
            
            placeholder_container.bind(pos=self._update_placeholder_bg, size=self._update_placeholder_bg)
            
            placeholder_label = Label(
                text='Intet billede',
                font_size='14sp',
                color=(0.7, 0.7, 0.7, 1),
                halign='center',
                valign='middle'
            )
            placeholder_container.add_widget(placeholder_label)
            image_section.add_widget(placeholder_container)
        
        # Text area - bottom third of card (no separate background needed)
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(55),  # Bottom third of card
            padding=[dp(12), dp(8), dp(12), dp(8)],  # Generous padding
            spacing=dp(4)
        )
        
        # Bold title (clean sans-serif, medium weight)
        title_text = search_item.get('title', 'Ingen titel')
        if len(title_text) > 20:
            title_text = title_text[:17] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='12sp',
            bold=True,  # Bold heading as specified
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(106), None),  # Constrain width for wrapping
            max_lines=1
        )
        
        # Lighter subtitle (objektnummer if available)
        objektnummer = search_item.get('objectNumber', '')
        if objektnummer:
            subtitle_label = Label(
                text=objektnummer,
                font_size='10sp',
                color=(0.6, 0.6, 0.6, 1),  # Lighter color as specified
                halign='center',
                valign='top',
                text_size=(dp(106), None)
            )
            text_section.add_widget(title_label)
            text_section.add_widget(subtitle_label)
        else:
            text_section.add_widget(title_label)
        
        # Add unified card background that creates the complete rounded rectangle effect
        with content_area.canvas.before:
            # Soft shadow effect
            Color(0, 0, 0, 0.08)  # Very subtle shadow
            content_area.shadow_rect = RoundedRectangle(
                pos=[content_area.pos[0] + dp(2), content_area.pos[1] - dp(2)],
                size=content_area.size,
                radius=[16, 16, 16, 16]  # Fully rounded shadow
            )
            # Main card background - this creates the unified rounded rectangle
            Color(1, 1, 1, 1)  # White background
            content_area.card_bg = RoundedRectangle(
                pos=content_area.pos,
                size=content_area.size,
                radius=[16, 16, 16, 16]  # Complete rounded rectangle
            )
        
        content_area.bind(pos=self._update_carousel_card_bg, size=self._update_carousel_card_bg)
        
        # Gem knap i øverste højre hjørne
        save_btn = Button(
            text='⭐',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'right': 1, 'top': 1},
            background_color=(0, 0, 0, 0),  # Transparent
            font_size='16sp'
        )
        
        # Style save button
        with save_btn.canvas.before:
            Color(1, 1, 1, 0.9)  # Semi-transparent white
            save_btn.bg_circle = RoundedRectangle(
                pos=save_btn.pos,
                size=save_btn.size,
                radius=[15, 15, 15, 15]
            )
        save_btn.bind(pos=self._update_save_btn_bg, size=self._update_save_btn_bg)
        
        # Tjek om allerede gemt
        obj_number = search_item.get('objectNumber', '')
        if self.is_saved(obj_number):
            save_btn.color = [1, 0.8, 0, 1]  # Gylden farve hvis gemt
        else:
            save_btn.color = [0.7, 0.7, 0.7, 1]  # Grå hvis ikke gemt
        
        def on_save_click(instance):
            if self.is_saved(obj_number):
                # Fjern fra gemte
                self.remove_from_saved_searches(obj_number)
                instance.color = [0.7, 0.7, 0.7, 1]  # Grå
            else:
                # Tilføj til gemte - skal have fulde objekt data
                try:
                    results = self.api.search_objects(obj_number, limit=1)
                    if results:
                        success = self.add_to_saved_searches(results[0])
                        if success:
                            instance.color = [1, 0.8, 0, 1]  # Gylden
                except Exception as e:
                    print(f"Fejl ved gemning: {e}")
        
        save_btn.bind(on_press=on_save_click)
        
        # Tilføj gem knap til card container som overlay
        card_container.add_widget(content_area)
        card_container.add_widget(save_btn)
        
        # Assemble content sections to content_area
        content_area.add_widget(image_section)
        content_area.add_widget(text_section)
        
        # Make card clickable
        def on_card_click(touch):
            if card_container.collide_point(*touch.pos):
                self.search_recent_item(search_item)
                return True
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
    
    def _update_save_btn_bg(self, instance, value):
        """Update save button background"""
        if hasattr(instance, 'bg_circle'):
            instance.bg_circle.pos = instance.pos
            instance.bg_circle.size = instance.size
    
    def search_recent_item(self, search_item):
        """Søg på et element fra seneste søgninger"""
        obj_number = search_item.get('objectNumber', '')
        if obj_number:
            # Perform search to get full object details
            try:
                results = self.api.search_objects(obj_number, limit=1)
                if results:
                    # Navigate directly to detail view
                    if self.manager:
                        detail_screen = self.manager.get_screen('detail')
                        detail_screen.show_object(results[0])
                        self.manager.current = 'detail'
            except Exception as e:
                print(f"Error searching recent item: {e}")
                # Fallback to regular search
                self.search_input.text = obj_number
                self.search_objects()
    
        self.clear_results()
        
        # Velkomst container med elegant baggrund

        # Velkomst besked med moderne styling

    def _update_welcome_bg(self, instance, value):
        """Opdater velkomst baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = [instance.pos[0] + dp(10), instance.pos[1] + dp(5)]
            instance.bg_rect.size = [instance.size[0] - dp(20), instance.size[1] - dp(10)]
    
    def clear_results(self):
        """Clear search results"""
        self.results_layout.clear_widgets()
    
    def search_objects(self, *args):
        query = self.search_input.text.strip()
        if not query:
            return
        
        # Ryd tidligere resultater
        self.results_layout.clear_widgets()
        
        # Vis loading besked
        loading = Label(
            text=f'Søger efter "{query}"...',
            size_hint_y=None,
            height=dp(60),
            font_size='16sp',
            halign='center',
            color=(0.4, 0.4, 0.4, 1)
        )
        loading.bind(size=loading.setter('text_size'))
        self.results_layout.add_widget(loading)
        
        # Planlæg API kald for at undgå UI blokering
        Clock.schedule_once(lambda dt: self.perform_search(query), 0.1)
    
    def perform_search(self, query):
        """Udfør den faktiske søgning og vis resultater"""
        try:
            results = self.api.search_objects(query, limit=20)
            
            # Ryd loading besked
            self.results_layout.clear_widgets()
            
            if not results:
                no_results = Label(
                    text='Ingen objekter fundet.\n\n' +
                         'Tjek objektnummer format:\n' +
                         '• 0054x0007\n• 12345;15\n• AAB 1234\n• 1234',
                    size_hint_y=None,
                    height=dp(150),
                    font_size='16sp',
                    halign='center',
                    color=(0.6, 0.4, 0.4, 1)
                )
                no_results.bind(size=no_results.setter('text_size'))
                self.results_layout.add_widget(no_results)
                return
            
            # If we found results, show the first one in detail view
            first_object = results[0]
            
            # Add to recent searches
            self.add_to_recent_searches(first_object)
            
            # Navigate to detail screen
            if self.manager:
                detail_screen = self.manager.get_screen('detail')
                detail_screen.show_object(first_object)
                self.manager.current = 'detail'
                
        except Exception as e:
            self.results_layout.clear_widgets()
            error_label = Label(
                text=f'Søgefejl:\n{str(e)}\n\nTjek din internetforbindelse og prøv igen.',
                size_hint_y=None,
                height=dp(120),
                font_size='16sp',
                halign='center',
                color=(0.8, 0.4, 0.4, 1)
            )
            error_label.bind(size=error_label.setter('text_size'))
            self.results_layout.add_widget(error_label)
    

    
    def _update_card_bg(self, instance, value):
        """Opdater kort baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = [instance.pos[0] + dp(5), instance.pos[1] + dp(5)]
            instance.bg_rect.size = [instance.size[0] - dp(10), instance.size[1] - dp(10)]


class DetailScreen(Screen):
    """Full-screen detailed view of an object"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "detail"
        self.current_object = None
        self.current_image_index = 0  # Track which image is currently displayed
        self.all_images = []  # Store all available images
        self.main_image_widget = None  # Reference to the main image widget
        self.image_counter_widget = None  # Reference to the image counter
        
    def show_object(self, obj):
        """Display full details for an object"""
        self.current_object = obj
        self.clear_widgets()
        self.build_detail_screen()
        self.update_save_button_state()
        
    def build_detail_screen(self):
        """Build the detailed object view"""
        if not self.current_object:
            return
            
        # Main container
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(0),
            padding=[0, 0, 0, 0]
        )
        
        # Clean white background
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            main_layout.bg = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Header with back button
        header_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Back arrow button
        back_button = Button(
            text='< Tilbage',
            size_hint=(None, 1),
            width=dp(100),
            font_size='16sp',
            background_color=(0, 0, 0, 0)  # Transparent background
        )
        
        # Style back button
        with back_button.canvas.before:
            Color(0.15, 0.25, 0.4, 1)  # Navy blue background
            back_button.bg_rect = RoundedRectangle(
                pos=back_button.pos,
                size=back_button.size,
                radius=[8, 8, 8, 8]
            )
        
        back_button.bind(pos=self._update_button_bg, size=self._update_button_bg)
        back_button.bind(on_press=self.go_back)
        back_button.color = [1, 1, 1, 1]  # White text
        
        header_layout.add_widget(back_button)
        
        # Add spacer to push buttons to sides
        header_spacer = Widget()
        header_layout.add_widget(header_spacer)
        
        # Save button
        self.save_button = Button(
            text='⭐',
            size_hint=(None, 1),
            width=dp(50),
            font_size='20sp',
            background_color=(0, 0, 0, 0)  # Transparent background
        )
        
        # Style save button
        with self.save_button.canvas.before:
            Color(0.15, 0.25, 0.4, 1)  # Navy blue background
            self.save_button.bg_rect = RoundedRectangle(
                pos=self.save_button.pos,
                size=self.save_button.size,
                radius=[8, 8, 8, 8]
            )
        
        self.save_button.bind(pos=self._update_button_bg, size=self._update_button_bg)
        self.save_button.bind(on_press=self.toggle_save)
        self.save_button.color = [1, 1, 1, 1]  # White text
        
        header_layout.add_widget(self.save_button)
        
        main_layout.add_widget(header_layout)
        
        # Scrollable content area
        scroll = ScrollView()
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint_y=None,
            padding=[dp(20), dp(20), dp(20), dp(20)]
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Object title - large and prominent
        title = Label(
            text=self.current_object.get('title', 'Ingen titel'),
            size_hint_y=None,
            height=dp(60),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='middle',
            text_size=(None, None)
        )
        title.bind(size=title.setter('text_size'))
        content_layout.add_widget(title)
        
        # Object number - prominent display
        obj_num = self.current_object.get('objectNumber', 'Ukendt')
        number_label = Label(
            text=f"Objektnummer: {obj_num}",
            size_hint_y=None,
            height=dp(40),
            font_size='18sp',
            bold=True,
            color=(0.15, 0.25, 0.4, 1),  # Navy blue accent
            halign='left',
            valign='middle'
        )
        number_label.bind(size=number_label.setter('text_size'))
        content_layout.add_widget(number_label)
        
        # Images section - full width display
        self.add_images_section(content_layout)
        
        # Object details in clean cards
        self.add_detail_cards(content_layout)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
    def add_images_section(self, parent_layout):
        """Add images section with large primary image and clickable thumbnails"""
        obj = self.current_object
        primary_image_url = obj.get('primaryImage', '')
        additional_images = obj.get('additionalImages', [])
        has_image = obj.get('hasImage', False)
        
        if has_image and primary_image_url:
            # Build complete images list (primary + additional)
            self.all_images = [primary_image_url] + additional_images
            self.current_image_index = 0
            
            # Primary image container - large display
            image_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(300),  # Large image display
                spacing=dp(10)
            )
            
            # Main image - now stored as instance variable for updating
            self.main_image_widget = AsyncImage(
                source=self.all_images[self.current_image_index],
                size_hint_y=None,
                height=dp(280),
                fit_mode="contain"
            )
            image_container.add_widget(self.main_image_widget)
            
            # Image counter if multiple images - also stored for updating
            total_images = len(self.all_images)
            if total_images > 1:
                self.image_counter_widget = Label(
                    text=f"Billede {self.current_image_index + 1} af {total_images}",
                    size_hint_y=None,
                    height=dp(20),
                    font_size='12sp',
                    color=(0.5, 0.5, 0.5, 1),
                    halign='center'
                )
                image_container.add_widget(self.image_counter_widget)
            
            parent_layout.add_widget(image_container)
            
            # Add thumbnails for all images if there are multiple images
            if total_images > 1:
                self.add_thumbnail_section(parent_layout, self.all_images)
        else:
            # No image placeholder
            no_image_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(150)
            )
            
            # Placeholder background
            with no_image_container.canvas.before:
                Color(0.95, 0.95, 0.95, 1)  # Light gray
                no_image_container.bg_rect = RoundedRectangle(
                    pos=no_image_container.pos,
                    size=no_image_container.size,
                    radius=[10, 10, 10, 10]
                )
            no_image_container.bind(pos=self._update_placeholder_bg, size=self._update_placeholder_bg)
            
            no_image_label = Label(
                text="Intet billede tilgængeligt",
                font_size='16sp',
                color=(0.6, 0.6, 0.6, 1),
                halign='center',
                valign='middle'
            )
            no_image_container.add_widget(no_image_label)
            parent_layout.add_widget(no_image_container)
    
    def add_thumbnail_section(self, parent_layout, all_images):
        """Add thumbnails for all images"""
        # Scrollable container for thumbnails
        thumb_scroll = ScrollView(
            size_hint_y=None,
            height=dp(80),
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)  # Hide scrollbars
        )
        
        thumb_container = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(10),
            padding=[dp(5), 0, dp(5), 0]
        )
        thumb_container.bind(minimum_width=thumb_container.setter('width'))
        
        # Add thumbnails for ALL images - now clickable and scrollable
        for i, img_url in enumerate(all_images):
            try:
                thumbnail = AsyncImage(
                    source=img_url,
                    size_hint_x=None,
                    width=dp(70),
                    fit_mode="cover"
                )
                
                # Store the correct image index (0-based, matching self.all_images)
                thumbnail.image_index = i
                
                # Make thumbnail clickable with proper closure
                def make_click_handler(index):
                    def thumbnail_touch_handler(instance, touch):
                        if instance.collide_point(*touch.pos):
                            self.switch_to_image(index)
                            return True
                        return False
                    return thumbnail_touch_handler
                
                thumbnail.bind(on_touch_down=make_click_handler(i))
                thumb_container.add_widget(thumbnail)
            except Exception as e:
                print(f"Failed to load thumbnail {i}: {e}")
                pass  # Skip failed thumbnails
        
        thumb_scroll.add_widget(thumb_container)
        parent_layout.add_widget(thumb_scroll)
    

    
    def switch_to_image(self, new_index):
        """Switch the main image to a different one"""
        if 0 <= new_index < len(self.all_images):
            old_index = self.current_image_index
            self.current_image_index = new_index
            
            # Update main image
            if self.main_image_widget:
                self.main_image_widget.source = self.all_images[new_index]
            
            # Update counter
            if self.image_counter_widget:
                total_images = len(self.all_images)
                self.image_counter_widget.text = f"Billede {new_index + 1} af {total_images}"
            
            # Update thumbnail borders (if we have access to them)
            # We'll need to rebuild the thumbnails to update borders properly
            # For now, this provides the core functionality
            print(f"Switched from image {old_index + 1} to image {new_index + 1}")
    
    def _update_thumb_border(self, instance, value):
        """Update thumbnail border positioning"""
        if hasattr(instance, 'border'):
            instance.border.pos = instance.pos
            instance.border.size = instance.size
    
    def add_detail_cards(self, parent_layout):
        """Add detailed information in clean card format"""
        obj = self.current_object
        
        # Description card
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        if description and description != 'Ingen beskrivelse tilgængelig':
            desc_card = self.create_info_card("Beskrivelse", description)
            parent_layout.add_widget(desc_card)
        
        # Object details card
        details_info = []
        
        object_type = obj.get('objectName', '')
        if object_type:
            details_info.append(f"Type: {object_type}")
            
        department = obj.get('department', '')
        if department:
            details_info.append(f"Afdeling: {department}")
            
        date_info = obj.get('objectDate', '')
        if date_info:
            details_info.append(f"Dato: {date_info}")
            
        medium = obj.get('medium', '')
        if medium:
            details_info.append(f"Materiale: {medium}")
            
        technique = obj.get('technique', '')
        if technique:
            details_info.append(f"Teknik: {technique}")
            
        dimensions = obj.get('dimensions', '')
        if dimensions:
            details_info.append(f"Dimensioner: {dimensions}")
            
        if details_info:
            details_text = "\n".join(details_info)
            details_card = self.create_info_card("Objekt detaljer", details_text)
            parent_layout.add_widget(details_card)
        
        # Artist information if available
        artist = obj.get('artistDisplayName', '')
        if artist and artist != 'Ukendt kunstner':
            artist_info = []
            artist_info.append(f"Kunstner: {artist}")
            
            nationality = obj.get('artistNationality', '')
            if nationality:
                artist_info.append(f"Nationalitet: {nationality}")
                
            if artist_info:
                artist_text = "\n".join(artist_info)
                artist_card = self.create_info_card("Kunstner information", artist_text)
                parent_layout.add_widget(artist_card)
        
        # Collection information
        collection_info = []
        
        sara_id = obj.get('priref', '')
        if sara_id:
            collection_info.append(f"SARA ID: {sara_id}")
            
        repository = obj.get('repository', '')
        if repository:
            collection_info.append(f"Opbevaringssted: {repository}")
            
        acquisition_year = obj.get('acquisitionYear', '')
        if acquisition_year:
            collection_info.append(f"Erhvervelsesår: {acquisition_year}")
            
        if collection_info:
            collection_text = "\n".join(collection_info)
            collection_card = self.create_info_card("Samlings information", collection_text)
            parent_layout.add_widget(collection_card)
    
    def create_info_card(self, title, content):
        """Create a clean information card"""
        # Calculate dynamic height based on content length
        estimated_lines = max(2, len(content) // 50 + 1)
        content_height = min(dp(200), dp(20 * estimated_lines))
        total_height = dp(50) + content_height + dp(20)  # Title + content + padding
        
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=total_height,
            spacing=dp(10),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        
        # Card background
        with card_container.canvas.before:
            Color(0.98, 0.98, 0.99, 1)  # Very light blue-gray
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[12, 12, 12, 12]
            )
        card_container.bind(pos=self._update_card_bg, size=self._update_card_bg)
        
        # Title
        title_label = Label(
            text=title,
            size_hint_y=None,
            height=dp(30),
            font_size='16sp',
            bold=True,
            color=(0.15, 0.25, 0.4, 1),  # Navy blue
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        # Content
        content_label = Label(
            text=content,
            size_hint_y=None,
            height=content_height,
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        content_label.bind(size=content_label.setter('text_size'))
        
        card_container.add_widget(title_label)
        card_container.add_widget(content_label)
        
        return card_container
    
    def go_back(self, *args):
        """Navigate back to search screen"""
        if self.manager:
            self.manager.current = 'search'
    
    def toggle_save(self, *args):
        """Toggle save state for current object"""
        if not self.current_object:
            return
            
        obj_number = self.current_object.get('objectNumber', '')
        if not obj_number:
            return
        
        # Get search screen reference
        search_screen = None
        if self.manager and self.manager.has_screen('search'):
            search_screen = self.manager.get_screen('search')
        
        if search_screen:
            if search_screen.is_saved(obj_number):
                # Fjern fra gemte
                search_screen.remove_from_saved_searches(obj_number)
                self.save_button.color = [1, 1, 1, 1]  # Hvid
            else:
                # Tilføj til gemte
                success = search_screen.add_to_saved_searches(self.current_object)
                if success:
                    self.save_button.color = [1, 0.8, 0, 1]  # Gylden
    
    def update_save_button_state(self):
        """Opdater save button baseret på om objektet er gemt"""
        if not self.current_object or not hasattr(self, 'save_button'):
            return
            
        obj_number = self.current_object.get('objectNumber', '')
        if not obj_number:
            return
        
        # Get search screen reference
        search_screen = None
        if self.manager and self.manager.has_screen('search'):
            search_screen = self.manager.get_screen('search')
        
        if search_screen and search_screen.is_saved(obj_number):
            self.save_button.color = [1, 0.8, 0, 1]  # Gylden hvis gemt
        else:
            self.save_button.color = [1, 1, 1, 1]  # Hvid hvis ikke gemt
    
    def _update_bg(self, instance, value):
        """Update background"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def _update_button_bg(self, instance, value):
        """Update button background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_card_bg(self, instance, value):
        """Update card background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size


class SavedSearchesScreen(Screen):
    """Skærm til gemte søgninger"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "saved"
        self.search_screen = None  # Reference til SearchScreen
        self.build_screen()
    
    def build_screen(self):
        """Byg gemte søgninger interface"""
        # Hovedlayout
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(0),
            padding=[0, 0, 0, 0]
        )
        
        # Clean white background
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            main_layout.bg = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Content area
        content_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=[dp(20), dp(20), dp(20), dp(10)]
        )
        
        # Header titel
        header_label = Label(
            text='Gemte søgninger',
            size_hint_y=None,
            height=dp(50),
            font_size='24sp',
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='middle'
        )
        header_label.bind(size=header_label.setter('text_size'))
        content_layout.add_widget(header_label)
        
        # Carousel for gemte søgninger
        self.saved_scroll = ScrollView(
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)
        )
        
        self.saved_layout = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(20),
            padding=[dp(15), 0, dp(15), 0]
        )
        self.saved_layout.bind(minimum_width=self.saved_layout.setter('width'))
        
        self.saved_scroll.add_widget(self.saved_layout)
        content_layout.add_widget(self.saved_scroll)
        
        main_layout.add_widget(content_layout)
        
        # Bottom navigation bar (samme som SearchScreen)
        bottom_nav = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(20),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Bottom nav background
        with bottom_nav.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Light gray background
            bottom_nav.bg_rect = Rectangle(
                pos=bottom_nav.pos,
                size=bottom_nav.size
            )
        bottom_nav.bind(pos=self._update_bottom_nav_bg, size=self._update_bottom_nav_bg)
        
        # Home button
        home_btn = Button(
            text='🏠 Hjem',
            size_hint_x=0.5,
            font_size='14sp',
            background_color=(0, 0, 0, 0)
        )
        
        with home_btn.canvas.before:
            Color(0.15, 0.25, 0.4, 1)
            home_btn.bg_rect = RoundedRectangle(
                pos=home_btn.pos,
                size=home_btn.size,
                radius=[8, 8, 8, 8]
            )
        home_btn.bind(pos=self._update_nav_button_bg, size=self._update_nav_button_bg)
        home_btn.bind(on_press=self.go_to_home)
        home_btn.color = [1, 1, 1, 1]
        
        # Saved searches button (highlighted da vi er her)
        saved_btn = Button(
            text='⭐ Gemte',
            size_hint_x=0.5,
            font_size='14sp',
            background_color=(0, 0, 0, 0)
        )
        
        with saved_btn.canvas.before:
            Color(0.2, 0.4, 0.6, 1)  # Lighter blue to show active
            saved_btn.bg_rect = RoundedRectangle(
                pos=saved_btn.pos,
                size=saved_btn.size,
                radius=[8, 8, 8, 8]
            )
        saved_btn.bind(pos=self._update_nav_button_bg, size=self._update_nav_button_bg)
        saved_btn.color = [1, 1, 1, 1]
        
        bottom_nav.add_widget(home_btn)
        bottom_nav.add_widget(saved_btn)
        
        main_layout.add_widget(bottom_nav)
        
        self.add_widget(main_layout)
        
        # Load saved searches når skærmen bygges
        self.update_saved_carousel()
    
    def update_saved_carousel(self):
        """Opdater carousel med gemte søgninger"""
        self.saved_layout.clear_widgets()
        
        if not self.search_screen or not self.search_screen.saved_searches:
            # Vis "ingen gemte søgninger" besked
            no_saved_label = Label(
                text='Ingen gemte søgninger endnu\nTryk ⭐ på objekter for at gemme dem',
                size_hint_x=None,
                width=dp(320),
                font_size='16sp',
                color=(0.6, 0.6, 0.6, 1),
                halign='center',
                valign='middle'
            )
            no_saved_label.bind(size=no_saved_label.setter('text_size'))
            self.saved_layout.add_widget(no_saved_label)
            return
        
        # Tilføj gemte søgninger til carousel
        for search_item in self.search_screen.saved_searches:
            card = self.create_saved_card(search_item)
            self.saved_layout.add_widget(card)
    
    def create_saved_card(self, search_item):
        """Create card for saved item med fjern knap"""
        # Genbruger samme design som recent search cards
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(130),
            spacing=0,
            padding=[0, 0, 0, 0]
        )
        
        # Image section
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
                text='Intet billede',
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
            height=dp(55),
            padding=[dp(12), dp(8), dp(12), dp(8)],
            spacing=dp(4)
        )
        
        title_text = search_item.get('title', 'Ingen titel')
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
        
        # Card background
        with card_container.canvas.before:
            Color(0, 0, 0, 0.08)
            card_container.shadow_rect = RoundedRectangle(
                pos=[card_container.pos[0] + dp(2), card_container.pos[1] - dp(2)],
                size=card_container.size,
                radius=[16, 16, 16, 16]
            )
            Color(1, 1, 1, 1)
            card_container.card_bg = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[16, 16, 16, 16]
            )
        
        card_container.bind(pos=self._update_carousel_card_bg, size=self._update_carousel_card_bg)
        
        # Fjern knap i øverste højre hjørne
        remove_btn = Button(
            text='✕',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'right': 1, 'top': 1},
            background_color=(0, 0, 0, 0),
            font_size='16sp'
        )
        
        with remove_btn.canvas.before:
            Color(1, 0.3, 0.3, 0.9)  # Rød baggrund
            remove_btn.bg_circle = RoundedRectangle(
                pos=remove_btn.pos,
                size=remove_btn.size,
                radius=[15, 15, 15, 15]
            )
        remove_btn.bind(pos=self._update_save_btn_bg, size=self._update_save_btn_bg)
        remove_btn.color = [1, 1, 1, 1]  # Hvid tekst
        
        def on_remove_click(instance):
            obj_number = search_item.get('objectNumber', '')
            if self.search_screen:
                self.search_screen.remove_from_saved_searches(obj_number)
        
        remove_btn.bind(on_press=on_remove_click)
        
        # Tilføj fjern knap som overlay
        card_container.add_widget(remove_btn)
        
        card_container.add_widget(image_section)
        card_container.add_widget(text_section)
        
        # Make card clickable
        def on_card_click(touch):
            if card_container.collide_point(*touch.pos):
                self.view_saved_item(search_item)
                return True
            return False
        
        card_container.on_touch_down = on_card_click
        
        return card_container
    
    def view_saved_item(self, search_item):
        """Vis gemt objekt i detail view"""
        obj_number = search_item.get('objectNumber', '')
        if obj_number and self.search_screen:
            try:
                results = self.search_screen.api.search_objects(obj_number, limit=1)
                if results:
                    if self.manager:
                        detail_screen = self.manager.get_screen('detail')
                        detail_screen.show_object(results[0])
                        self.manager.current = 'detail'
            except Exception as e:
                print(f"Error viewing saved item: {e}")
    
    def go_to_home(self, *args):
        """Gå til søgeskærm"""
        if self.manager:
            self.manager.current = 'search'
    
    def _update_bg(self, instance, value):
        """Update background"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def _update_bottom_nav_bg(self, instance, value):
        """Update bottom nav background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_nav_button_bg(self, instance, value):
        """Update nav button background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_bg'):
            instance.placeholder_bg.pos = instance.pos
            instance.placeholder_bg.size = instance.size
    
    def _update_carousel_card_bg(self, instance, value):
        """Update card background"""
        if hasattr(instance, 'shadow_rect'):
            instance.shadow_rect.pos = [instance.pos[0] + dp(2), instance.pos[1] - dp(2)]
            instance.shadow_rect.size = instance.size
        if hasattr(instance, 'card_bg'):
            instance.card_bg.pos = instance.pos
            instance.card_bg.size = instance.size
    
    def _update_save_btn_bg(self, instance, value):
        """Update save button background"""
        if hasattr(instance, 'bg_circle'):
            instance.bg_circle.pos = instance.pos
            instance.bg_circle.size = instance.size


class SaraMuseumApp(App):
    """Hoved applikations klasse"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "SARA Museums App"
    
    def build(self):
        """Byg app interfacet"""
        # Skærm manager with multiple screens
        screen_manager = ScreenManager()
        
        # Tilføj søge skærm
        screen_manager.add_widget(SearchScreen())
        
        # Tilføj detail skærm
        screen_manager.add_widget(DetailScreen())
        
        return screen_manager


if __name__ == "__main__":
    SaraMuseumApp().run()