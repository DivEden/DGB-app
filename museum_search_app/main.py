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
        self.load_recent_searches()
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
            'title': obj.get('title', obj.get('TI', 'No title')),
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
        """Byg søge interfacet med flot navy blå design"""
        # Hovedlayout med gradient baggrund
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(15),
            padding=[dp(20), dp(20), dp(20), dp(20)]
        )
        
        # Navy blue gradient baggrund
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # Clean white background
            main_layout.bg = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Header med home button
        header_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15)
        )
        
        # Home button
        self.home_button = Button(
            text='Home',
            size_hint=(None, 1),
            width=dp(80),
            font_size='16sp',
            background_color=(0, 0, 0, 0)  # Transparent baggrund
        )
        
        # Stil home button med clean baggrund
        with self.home_button.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.home_button.bg_rect = RoundedRectangle(
                pos=self.home_button.pos,
                size=self.home_button.size,
                radius=[8, 8, 8, 8]
            )
        
        self.home_button.bind(pos=self._update_button_bg, size=self._update_button_bg)
        self.home_button.bind(on_press=self.go_to_home)
        
        header_layout.add_widget(self.home_button)
        main_layout.add_widget(header_layout)
        
        # Instruktioner med elegant styling
        instructions_container = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            spacing=dp(5)
        )
        
        main_layout.add_widget(instructions_container)
        
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
            hint_text='Enter object number...',
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
            text='SEARCH',
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
            text='Recent searches',
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
        main_layout.add_widget(self.results_scroll)
        
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
    
    def go_to_home(self, *args):
        """Gå til hjemmeside (ryd søgeresultater og vis velkomst)"""
        self.clear_results()
        self.search_input.text = ""
    
    def update_recent_carousel(self):
        """Opdater carousel med seneste søgninger"""
        # Ryd eksisterende elementer
        self.carousel_layout.clear_widgets()
        
        if not self.recent_searches:
            # Vis "ingen seneste søgninger" besked
            no_recent_label = Label(
                text='No recent searches yet\nSearch for objects to see them here',
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
        # Card container with generous spacing between cards
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_x=None,
            width=dp(130),  # Increased width for better proportions
            spacing=0,  # No internal spacing - all spacing controlled by layout
            padding=[0, 0, 0, 0]  # No padding on container
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
                text='No Image',
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
        title_text = search_item.get('title', 'No title')
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
        with card_container.canvas.before:
            # Soft shadow effect
            Color(0, 0, 0, 0.08)  # Very subtle shadow
            card_container.shadow_rect = RoundedRectangle(
                pos=[card_container.pos[0] + dp(2), card_container.pos[1] - dp(2)],
                size=card_container.size,
                radius=[16, 16, 16, 16]  # Fully rounded shadow
            )
            # Main card background - this creates the unified rounded rectangle
            Color(1, 1, 1, 1)  # White background
            card_container.card_bg = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[16, 16, 16, 16]  # Complete rounded rectangle
            )
        
        card_container.bind(pos=self._update_carousel_card_bg, size=self._update_carousel_card_bg)
        
        # Assemble card sections
        card_container.add_widget(image_section)
        card_container.add_widget(text_section)
        
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
    
    def search_recent_item(self, search_item):
        """Søg på et element fra seneste søgninger"""
        obj_number = search_item.get('objectNumber', '')
        if obj_number:
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
            text=f'Searching for "{query}"...',
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
                    text='No objects found.\n\n' +
                         'Check object number format:\n' +
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
            
            # Vis antal resultater
            count_label = Label(
                text=f'Found {len(results)} object(s):',
                size_hint_y=None,
                height=dp(40),
                font_size='16sp',
                halign='center',
                color=(0.2, 0.6, 0.2, 1)
            )
            count_label.bind(size=count_label.setter('text_size'))
            self.results_layout.add_widget(count_label)
            
            # Vis resultater
            for i, obj in enumerate(results, 1):
                self.add_object_card(obj, i)
                
                # Tilføj første resultat til seneste søgninger
                if i == 1:
                    self.add_to_recent_searches(obj)
                
        except Exception as e:
            self.results_layout.clear_widgets()
            error_label = Label(
                text=f'Search error:\n{str(e)}\n\nCheck your internet connection and try again.',
                size_hint_y=None,
                height=dp(120),
                font_size='16sp',
                halign='center',
                color=(0.8, 0.4, 0.4, 1)
            )
            error_label.bind(size=error_label.setter('text_size'))
            self.results_layout.add_widget(error_label)
    
    def add_object_card(self, obj, index):
        """Tilføj et objekt kort til resultatlisten"""
        # Container med baggrund - dynamisk højde for fuld beskrivelse og billeder
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        has_image = obj.get('hasImage', False) or obj.get('primaryImage', '')
        
        estimated_lines = max(3, len(description) // 40 + 1)
        base_height = dp(160)  # Base højde for andre elementer
        desc_height = min(dp(200), dp(20 * estimated_lines))
        image_height = dp(140) if has_image else dp(40)  # Plads til billeder
        total_height = base_height + desc_height + image_height
        
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=total_height,
            spacing=dp(5),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # Baggrund for kortet med light styling
        with card_container.canvas.before:
            Color(1, 1, 1, 0.95)  # White background with slight transparency
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[15, 15, 15, 15]
            )
        card_container.bind(size=self._update_card_bg, pos=self._update_card_bg)
        
        # Titel med nummer - elegant dark text
        title_text = f"{index}. {obj.get('title', 'Uden titel')}"
        title = Label(
            text=title_text,
            size_hint_y=None,
            height=dp(35),
            font_size='18sp',
            halign='left',
            bold=True,
            color=(0.2, 0.2, 0.2, 1)  # Dark gray text
        )
        title.bind(size=title.setter('text_size'))
        
        # Objekttype med clean styling
        object_type = obj.get('objectName', 'Unknown type')
        type_label = Label(
            text=f"Type: {object_type}",
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            halign='left',
            color=(0.4, 0.4, 0.4, 1)  # Medium gray text
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        # Objektnummer
        obj_num = obj.get('objectNumber', 'Unknown')
        number_label = Label(
            text=f"Object number: {obj_num}",
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            halign='left',
            color=(0.3, 0.3, 0.3, 1)  # Dark gray text
        )
        number_label.bind(size=number_label.setter('text_size'))
        
        # Beskrivelse (ny) - FULD længde uden begrænsning
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        
        # Beregn højde baseret på tekstlængde (circa 40 tegn per linje)
        estimated_lines = max(3, len(description) // 40 + 1)
        desc_height = min(dp(200), dp(20 * estimated_lines))  # Max 200dp højde
        
        # Beskrivelse med forbedret læsbarhed - FULD længde uden begrænsning
        desc_label = Label(
            text=f"Description: {description}",
            size_hint_y=None,
            height=desc_height,
            font_size='13sp',
            halign='left',
            valign='top',
            color=(0.2, 0.2, 0.2, 1),  # Dark gray text
            text_size=(None, None)
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        # Billede sektion (ny) - Vis faktiske billeder
        has_image = obj.get('hasImage', False) or obj.get('primaryImage', '')
        primary_image_url = obj.get('primaryImage', '')
        additional_images = obj.get('additionalImages', [])
        
        if has_image and primary_image_url:
            # Billede container
            image_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(120),
                spacing=dp(10)
            )
            
            # Primært billede
            try:
                primary_image = AsyncImage(
                    source=primary_image_url,
                    size_hint_x=None,
                    width=dp(100),
                    fit_mode="contain"
                )
                image_container.add_widget(primary_image)
            except:
                # Fallback hvis billede ikke loader
                image_placeholder = Label(
                    text="�️",
                    size_hint_x=None,
                    width=dp(100),
                    font_size='40sp',
                    halign='center',
                    valign='middle'
                )
                image_container.add_widget(image_placeholder)
            
            # Yderligere billeder (maksimalt 2 ekstra)
            for i, img_url in enumerate(additional_images[:2]):
                try:
                    extra_image = AsyncImage(
                        source=img_url,
                        size_hint_x=None,
                        width=dp(80),
                        fit_mode="contain"
                    )
                    image_container.add_widget(extra_image)
                except:
                    pass  # Skip hvis billede ikke loader
            
            # Billede info label
            total_images = 1 + len(additional_images)
            image_info = Label(
                text=f"🖼️ {total_images} billede{'r' if total_images > 1 else ''}",
                size_hint_y=None,
                height=dp(20),
                font_size='12sp',
                halign='left',
                color=[0.2, 0.6, 0.2, 1]
            )
            image_info.bind(size=image_info.setter('text_size'))
            
        else:
            # Ingen billeder tilgængelige med clean styling
            image_container = Label(
                text="No images available",
                size_hint_y=None,
                height=dp(40),
                font_size='12sp',
                halign='left',
                color=(0.6, 0.6, 0.6, 1)  # Light gray for no images
            )
            image_container.bind(size=image_container.setter('text_size'))
            
            image_info = None
        
        # Afdeling med clean styling
        dept = obj.get('department', '')
        if dept:
            dept_label = Label(
                text=f"Department: {dept}",
                size_hint_y=None,
                height=dp(25),
                font_size='14sp',
                halign='left',
                color=(0.4, 0.4, 0.4, 1)  # Medium gray text
            )
            dept_label.bind(size=dept_label.setter('text_size'))
            card_container.add_widget(dept_label)
        
        # SARA ID med subtil styling
        sara_id = obj.get('priref', 'Unknown')
        id_label = Label(
            text=f"SARA ID: {sara_id}",
            size_hint_y=None,
            height=dp(25),
            font_size='12sp',
            halign='left',
            color=(0.5, 0.5, 0.5, 1)  # Light gray for ID
        )
        id_label.bind(size=id_label.setter('text_size'))
        
        # Tilføj komponenter til kort
        card_container.add_widget(title)
        card_container.add_widget(type_label)
        card_container.add_widget(number_label)
        card_container.add_widget(desc_label)  # Ny beskrivelse
        card_container.add_widget(image_container)  # Billede sektion
        if image_info:
            card_container.add_widget(image_info)  # Billede info
        card_container.add_widget(id_label)
        
        
        self.results_layout.add_widget(card_container)
    
    def _update_card_bg(self, instance, value):
        """Opdater kort baggrund"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = [instance.pos[0] + dp(5), instance.pos[1] + dp(5)]
            instance.bg_rect.size = [instance.size[0] - dp(10), instance.size[1] - dp(10)]


class SaraMuseumApp(App):
    """Hoved applikations klasse"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "DGB Assistent"
    
    def build(self):
        """Byg app interfacet"""
        # Skærm manager (kan udvides senere til flere skærme)
        screen_manager = ScreenManager()
        
        # Tilføj søge skærm
        screen_manager.add_widget(SearchScreen())
        
        return screen_manager


if __name__ == "__main__":
    SaraMuseumApp().run()