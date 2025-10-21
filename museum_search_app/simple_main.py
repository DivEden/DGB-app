#!/usr/bin/env python3
"""
SARA Museum Søge App - Simpel Version
Søg efter objekter i SARA databasen
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.metrics import dp

from sara_api import SaraAPI


class SaraApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "SARA Museum Søger"
        self.api = SaraAPI()

    def build(self):
        # Hovedlayout
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Titel
        title = Label(
            text='SARA Museum Søger',
            size_hint_y=None,
            height=dp(50),
            font_size='20sp'
        )
        main_layout.add_widget(title)
        
        # Søgefelt
        self.search_input = TextInput(
            hint_text='Indtast objektnummer (f.eks. 0054x0007)',
            size_hint_y=None,
            height=dp(40),
            multiline=False
        )
        self.search_input.bind(on_text_validate=self.search_objects)
        main_layout.add_widget(self.search_input)
        
        # Søgeknap
        search_btn = Button(
            text='Søg',
            size_hint_y=None,
            height=dp(40)
        )
        search_btn.bind(on_release=self.search_objects)
        main_layout.add_widget(search_btn)
        
        # Resultater
        self.scroll = ScrollView()
        self.results_layout = BoxLayout(
            orientation='vertical',
            spacing=10,
            size_hint_y=None
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        self.scroll.add_widget(self.results_layout)
        main_layout.add_widget(self.scroll)
        
        # Velkomstbesked
        welcome = Label(
            text='Velkommen til SARA Museum Søger\n\nSøg med objektnummer:\n• 0054x0007\n• 12345;15\n• AAB 1234\n• 1234',
            size_hint_y=None,
            height=dp(150),
            halign='center'
        )
        welcome.bind(size=welcome.setter('text_size'))
        self.results_layout.add_widget(welcome)
        
        return main_layout
    
    def search_objects(self, *args):
        """Søg efter objekter"""
        query = self.search_input.text.strip()
        if not query:
            return
        
        # Ryd resultater
        self.results_layout.clear_widgets()
        
        # Vis loading
        loading = Label(
            text=f'Søger efter "{query}"...',
            size_hint_y=None,
            height=dp(40)
        )
        self.results_layout.add_widget(loading)
        
        # Planlæg søgning
        Clock.schedule_once(lambda dt: self.perform_search(query), 0.1)
    
    def perform_search(self, query):
        """Udfør søgning"""
        try:
            results = self.api.search_objects(query, limit=10)
            
            # Ryd loading
            self.results_layout.clear_widgets()
            
            if not results:
                no_results = Label(
                    text='Ingen objekter fundet.\nTjek objektnummer format.',
                    size_hint_y=None,
                    height=dp(60),
                    halign='center'
                )
                no_results.bind(size=no_results.setter('text_size'))
                self.results_layout.add_widget(no_results)
                return
            
            # Vis resultater
            for obj in results:
                self.add_result_card(obj)
                
        except Exception as e:
            self.results_layout.clear_widgets()
            error = Label(
                text=f'Fejl: {str(e)}',
                size_hint_y=None,
                height=dp(60),
                halign='center'
            )
            error.bind(size=error.setter('text_size'))
            self.results_layout.add_widget(error)
    
    def add_result_card(self, obj):
        """Tilføj resultatkort"""
        # Layout for objektet - dynamisk højde for fuld beskrivelse og billede
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        has_image = obj.get('hasImage', False) or obj.get('primaryImage', '')
        
        estimated_lines = max(2, len(description) // 30 + 1)
        base_height = dp(120)  # Base højde for andre elementer
        desc_height = min(dp(150), dp(15 * estimated_lines))
        image_height = dp(80) if has_image else dp(20)  # Plads til billede
        total_height = base_height + desc_height + image_height
        
        card_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=total_height,
            spacing=5
        )
        
        # Titel
        title = Label(
            text=obj.get('title', 'Uden titel'),
            size_hint_y=None,
            height=dp(30),
            font_size='16sp',
            halign='left',
            bold=True
        )
        title.bind(size=title.setter('text_size'))
        
        # Objekttype
        object_name = Label(
            text=f"Type: {obj.get('objectName', 'Ukendt')}",
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            halign='left'
        )
        object_name.bind(size=object_name.setter('text_size'))
        
        # Objektnummer
        object_number = Label(
            text=f"Nr: {obj.get('objectNumber', 'Ukendt')}",
            size_hint_y=None,
            height=dp(25),
            font_size='14sp',
            halign='left'
        )
        object_number.bind(size=object_number.setter('text_size'))
        
        # Beskrivelse (ny) - FULD længde
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        
        # Dynamisk højde baseret på tekstlængde
        estimated_lines = max(2, len(description) // 30 + 1)
        desc_height = min(dp(150), dp(15 * estimated_lines))
        
        desc_label = Label(
            text=f"Beskrivelse: {description}",
            size_hint_y=None,
            height=desc_height,
            font_size='13sp',
            halign='left',
            valign='top'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        
        # Billede sektion (simpel version)
        has_image = obj.get('hasImage', False) or obj.get('primaryImage', '')
        primary_image_url = obj.get('primaryImage', '')
        additional_images = obj.get('additionalImages', [])
        
        if has_image and primary_image_url:
            # Vis kun primært billede i simple version
            image_container = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height=dp(80),
                spacing=dp(10)
            )
            
            try:
                # Primært billede
                primary_image = AsyncImage(
                    source=primary_image_url,
                    size_hint_x=None,
                    width=dp(70),
                    allow_stretch=True,
                    keep_ratio=True
                )
                image_container.add_widget(primary_image)
                
                # Billede info
                total_images = 1 + len(additional_images)
                image_info_label = Label(
                    text=f"Billeder: {total_images}",
                    font_size='12sp',
                    halign='left',
                    valign='middle'
                )
                image_info_label.bind(size=image_info_label.setter('text_size'))
                image_container.add_widget(image_info_label)
                
            except:
                # Fallback hvis billede ikke loader
                image_container = Label(
                    text="Billede: Tilgængeligt men kunne ikke indlæses",
                    size_hint_y=None,
                    height=dp(20),
                    font_size='12sp',
                    halign='left'
                )
                image_container.bind(size=image_container.setter('text_size'))
        else:
            # Ingen billeder
            image_container = Label(
                text="Billede: Nej",
                size_hint_y=None,
                height=dp(20),
                font_size='12sp',
                halign='left'
            )
            image_container.bind(size=image_container.setter('text_size'))
        
        # SARA ID
        sara_id = Label(
            text=f"SARA ID: {obj.get('priref', 'Ukendt')}",
            size_hint_y=None,
            height=dp(20),
            font_size='12sp',
            halign='left'
        )
        sara_id.bind(size=sara_id.setter('text_size'))
        
        # Seperator
        separator = Label(
            text='─' * 40,
            size_hint_y=None,
            height=dp(10),
            font_size='10sp'
        )
        
        card_layout.add_widget(title)
        card_layout.add_widget(object_name)
        card_layout.add_widget(object_number)
        card_layout.add_widget(desc_label)    # Ny beskrivelse
        card_layout.add_widget(image_container)   # Billede sektion
        card_layout.add_widget(sara_id)
        card_layout.add_widget(separator)
        
        self.results_layout.add_widget(card_layout)


if __name__ == '__main__':
    SaraApp().run()