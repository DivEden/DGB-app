#!/usr/bin/env python3
"""
Results Screen for SARA Museum App
Displays search results with back navigation to home
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

from components.result_card import ResultCard
from utils.data_manager import DataManager


class ResultsScreen(Screen):
    """Screen for displaying search results"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "results"
        self.data_manager = DataManager()
        self.results_data = []
        self.search_query = ""
        
        self._create_layout()
    
    def _create_layout(self):
        """Create the results screen layout"""
        main_layout = BoxLayout(orientation='vertical')
        
        # Header with back button
        header_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(70),
            padding=[dp(15), dp(15), dp(15), dp(10)],
            spacing=dp(10)
        )
        
        # Back button
        self.back_button = Button(
            text='←',
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            font_size='24sp',
            background_color=(0, 0, 0, 0)  # Transparent background
        )
        
        # Style back button
        with self.back_button.canvas.before:
            Color(0.9, 0.9, 0.9, 1)  # Light gray background
            self.back_button.bg_rect = RoundedRectangle(
                pos=self.back_button.pos,
                size=self.back_button.size,
                radius=[25, 25, 25, 25]
            )
        
        self.back_button.bind(pos=self._update_back_btn_bg, size=self._update_back_btn_bg)
        self.back_button.bind(on_press=self.go_back)
        
        # Title
        self.title_label = Label(
            text='Søgeresultater',
            font_size='20sp',
            bold=True,
            halign='center',
            color=(0.2, 0.2, 0.2, 1)
        )
        self.title_label.bind(size=self.title_label.setter('text_size'))
        
        # Spacer
        spacer = BoxLayout(size_hint=(None, None), size=(dp(50), dp(50)))
        
        header_layout.add_widget(self.back_button)
        header_layout.add_widget(self.title_label)
        header_layout.add_widget(spacer)
        
        # Results scroll area
        self.results_scroll = ScrollView()
        
        self.results_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(15),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        self.results_layout.bind(minimum_height=self.results_layout.setter('height'))
        
        self.results_scroll.add_widget(self.results_layout)
        
        main_layout.add_widget(header_layout)
        main_layout.add_widget(self.results_scroll)
        
        self.add_widget(main_layout)
    
    def _update_back_btn_bg(self, instance, value):
        """Update back button background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def show_results(self, results, query):
        """Display search results on this screen"""
        self.results_data = results
        self.search_query = query
        
        # Update title
        self.title_label.text = f'Resultater for "{query}"'
        
        # Clear previous results
        self.results_layout.clear_widgets()
        
        if not results:
            # Show no results message
            no_results = Label(
                text='No objects found.\\n\\n' +
                     'Check object number format:\\n' +
                     '• 0054x0007\\n• 12345;15\\n• AAB 1234\\n• 1234',
                size_hint_y=None,
                height=dp(150),
                font_size='16sp',
                halign='center',
                color=(0.6, 0.4, 0.4, 1)
            )
            no_results.bind(size=no_results.setter('text_size'))
            self.results_layout.add_widget(no_results)
            return
        
        # Show results count
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
        
        # Display results
        for i, obj in enumerate(results, 1):
            result_card = ResultCard(
                obj_data=obj,
                index=i
            )
            self.results_layout.add_widget(result_card)
    
    def go_back(self, *args):
        """Go back to the home screen"""
        print("ResultsScreen: go_back called")
        
        # Navigate through the nested screen structure
        # We need to go: ResultsScreen -> Screen('results') -> ScreenManager -> MainScreen
        parent = self.parent
        while parent and not hasattr(parent, 'current'):
            print(f"ResultsScreen: Checking parent: {type(parent)}")
            parent = parent.parent
        
        if parent and hasattr(parent, 'current'):
            print("ResultsScreen: Found screen manager, navigating to home")
            parent.current = 'home'
        else:
            print("ResultsScreen: Could not find screen manager")