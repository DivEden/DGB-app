#!/usr/bin/env python3
"""
SARA Museum Søge App - Mobil Applikation (Kivy Version)
Søg og udforsk objekter fra SARA databasen (Danmarks Geologiske og Biologiske Samling)
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
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

from sara_api import SaraAPI


class SearchScreen(Screen):
    """Skærm til at søge efter museums objekter"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "search"
        self.api = SaraAPI()
        self.build_screen()
    
    def build_screen(self):
        """Byg søge interfacet"""
        # Hovedlayout med baggrundsfarve
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            padding=[dp(10), dp(10), dp(10), dp(10)]
        )
        
        # Bind til canvas for baggrundsfarve
        with main_layout.canvas.before:
            Color(0.95, 0.95, 0.95, 1)  # Lys grå baggrund
            main_layout.bg = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Titel
        title = Label(
            text='🔬 SARA Museum Søger',
            size_hint_y=None,
            height=dp(50),
            font_size='20sp',
            color=[0.2, 0.2, 0.8, 1]
        )
        main_layout.add_widget(title)
        
        # Instruktioner
        instructions = Label(
            text='Søg efter objektnummer i Danmarks Geologiske og Biologiske Samling\n(f.eks. 0054x0007, 12345;15, AAB 1234)',
            size_hint_y=None,
            height=dp(60),
            font_size='14sp',
            halign='center',
            color=[0.4, 0.4, 0.4, 1]
        )
        instructions.bind(size=instructions.setter('text_size'))
        main_layout.add_widget(instructions)
        
        # Søge sektion
        search_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10)
        )
        
        # Søge input
        self.search_input = TextInput(
            hint_text='Indtast objektnummer...',
            font_size='16sp',
            multiline=False,
            size_hint_x=0.8
        )
        self.search_input.bind(on_text_validate=self.search_objects)
        
        # Søge knap
        search_btn = Button(
            text='Søg',
            size_hint_x=0.2,
            font_size='16sp'
        )
        search_btn.bind(on_release=self.search_objects)
        
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        main_layout.add_widget(search_layout)
        
        # Resultater sektion
        self.results_scroll = ScrollView()
        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(10),
            size_hint_y=None,
            padding=[0, dp(10), 0, 0]
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        self.results_scroll.add_widget(self.results_layout)
        main_layout.add_widget(self.results_scroll)
        
        # Velkomstbesked
        self.show_welcome_message()
        
        self.add_widget(main_layout)
    
    def _update_bg(self, instance, value):
        """Opdater baggrundsfarve"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def show_welcome_message(self):
        """Vis velkomstbesked"""
        welcome = Label(
            text='📚 Velkommen til SARA Museum Søger!\n\n' +
                 'Søg gennem Danmarks Geologiske og Biologiske Samling (SARA) med objektnummer:\n\n' +
                 '• Traditionelt format: 0054x0007, 1234X4321\n' +
                 '• Genstands format: 00073;15, 12345;2015\n' +
                 '• AAB format: AAB 1234\n' +
                 '• Enkelt nummer: 1234\n\n' +
                 'Indtast et objektnummer ovenfor og tryk Søg',
            size_hint_y=None,
            height=dp(300),
            font_size='16sp',
            halign='center',
            valign='middle',
            color=[0.3, 0.3, 0.3, 1]
        )
        welcome.bind(size=welcome.setter('text_size'))
        self.results_layout.add_widget(welcome)
    
    def search_objects(self, *args):
        """Søg efter objekter ved hjælp af API"""
        query = self.search_input.text.strip()
        if not query:
            return
        
        # Ryd tidligere resultater
        self.results_layout.clear_widgets()
        
        # Vis loading besked
        loading = Label(
            text=f'🔍 Søger efter "{query}"...',
            size_hint_y=None,
            height=dp(60),
            font_size='16sp',
            halign='center',
            color=[0.2, 0.6, 0.2, 1]
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
                    text='❌ Ingen objekter fundet.\n\n' +
                         'Tjek objektnummer formatet:\n' +
                         '• 0054x0007\n• 12345;15\n• AAB 1234\n• 1234',
                    size_hint_y=None,
                    height=dp(150),
                    font_size='16sp',
                    halign='center',
                    color=[0.8, 0.4, 0.4, 1]
                )
                no_results.bind(size=no_results.setter('text_size'))
                self.results_layout.add_widget(no_results)
                return
            
            # Vis antal resultater
            count_label = Label(
                text=f'✅ Fandt {len(results)} objekt(er):',
                size_hint_y=None,
                height=dp(40),
                font_size='16sp',
                halign='center',
                color=[0.2, 0.6, 0.2, 1]
            )
            count_label.bind(size=count_label.setter('text_size'))
            self.results_layout.add_widget(count_label)
            
            # Vis resultater
            for i, obj in enumerate(results, 1):
                self.add_object_card(obj, i)
                
        except Exception as e:
            self.results_layout.clear_widgets()
            error_label = Label(
                text=f'❌ Fejl ved søgning:\n{str(e)}\n\nTjek din internetforbindelse og prøv igen.',
                size_hint_y=None,
                height=dp(120),
                font_size='16sp',
                halign='center',
                color=[0.8, 0.2, 0.2, 1]
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
        
        # Baggrund for kortet
        with card_container.canvas.before:
            Color(1, 1, 1, 1)  # Hvid baggrund
            card_container.bg = Rectangle(size=card_container.size, pos=card_container.pos)
        card_container.bind(size=self._update_card_bg, pos=self._update_card_bg)
        
        # Titel med nummer
        title_text = f"{index}. {obj.get('title', 'Uden titel')}"
        title = Label(
            text=title_text,
            size_hint_y=None,
            height=dp(30),
            font_size='16sp',
            halign='left',
            bold=True,
            color=[0.1, 0.1, 0.1, 1]
        )
        title.bind(size=title.setter('text_size'))
        
        # Objekttype
        object_type = obj.get('objectName', 'Ukendt objekttype')
        type_label = Label(
            text=f"📋 Type: {object_type}",
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            halign='left',
            color=[0.3, 0.3, 0.3, 1]
        )
        type_label.bind(size=type_label.setter('text_size'))
        
        # Objektnummer
        obj_num = obj.get('objectNumber', 'Ukendt')
        number_label = Label(
            text=f"🔢 Objektnummer: {obj_num}",
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            halign='left',
            color=[0.3, 0.3, 0.3, 1]
        )
        number_label.bind(size=number_label.setter('text_size'))
        
        # Beskrivelse (ny) - FULD længde uden begrænsning
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        
        # Beregn højde baseret på tekstlængde (circa 40 tegn per linje)
        estimated_lines = max(3, len(description) // 40 + 1)
        desc_height = min(dp(200), dp(20 * estimated_lines))  # Max 200dp højde
        
        desc_label = Label(
            text=f"📝 Beskrivelse: {description}",
            size_hint_y=None,
            height=desc_height,
            font_size='13sp',
            halign='left',
            valign='top',
            color=[0.2, 0.2, 0.6, 1],
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
                    allow_stretch=True,
                    keep_ratio=True
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
                        allow_stretch=True,
                        keep_ratio=True
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
            # Ingen billeder tilgængelige
            image_container = Label(
                text="📷 Ingen billeder tilgængelige",
                size_hint_y=None,
                height=dp(40),
                font_size='12sp',
                halign='left',
                color=[0.6, 0.6, 0.6, 1]
            )
            image_container.bind(size=image_container.setter('text_size'))
            
            image_info = None
        
        # Afdeling
        dept = obj.get('department', '')
        if dept:
            dept_label = Label(
                text=f"🏛️ Afdeling: {dept}",
                size_hint_y=None,
                height=dp(25),
                font_size='14sp',
                halign='left',
                color=[0.3, 0.3, 0.3, 1]
            )
            dept_label.bind(size=dept_label.setter('text_size'))
            card_container.add_widget(dept_label)
        
        # SARA ID
        sara_id = obj.get('priref', 'Ukendt')
        id_label = Label(
            text=f"🆔 SARA ID: {sara_id}",
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            halign='left',
            color=[0.5, 0.5, 0.5, 1]
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
        
        # Separator
        separator = Label(
            text='─' * 50,
            size_hint_y=None,
            height=dp(20),
            font_size='10sp',
            color=[0.8, 0.8, 0.8, 1]
        )
        
        self.results_layout.add_widget(card_container)
        self.results_layout.add_widget(separator)
    
    def _update_card_bg(self, instance, value):
        """Opdater kort baggrund"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size


class SaraMuseumApp(App):
    """Hoved applikations klasse"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "SARA Museum Søger"
    
    def build(self):
        """Byg app interfacet"""
        # Skærm manager (kan udvides senere til flere skærme)
        screen_manager = ScreenManager()
        
        # Tilføj søge skærm
        screen_manager.add_widget(SearchScreen())
        
        return screen_manager


if __name__ == "__main__":
    SaraMuseumApp().run()