#!/usr/bin/env python3
"""
SARA Museum Search App - Mobile Application (Kivy Version)
Search and explore objects from the SARA database
Built with Kivy for cross-platform mobile deployment

Now with modular architecture:
- components/: Reusable UI components
- screens/: Screen-specific layouts and logic
- utils/: Data management and utilities
"""

import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

# Import our modular components
from screens.home_screen import HomeScreen
from screens.saved_screen import SavedScreen
from screens.results_screen import ResultsScreen
from components.bottom_nav import BottomNavigation


class MainScreen(Screen):
    """Main screen container with navigation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        self._create_layout()
    
    def _create_layout(self):
        """Create the main layout with content and navigation"""
        main_layout = BoxLayout(orientation='vertical')
        
        # Add white background
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            main_layout.bg_rect = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Content area with screen manager
        self.content_manager = ScreenManager()
        
        # Add home screen
        home_screen = Screen(name='home')
        self.home_content = HomeScreen()
        home_screen.add_widget(self.home_content)
        self.content_manager.add_widget(home_screen)
        
        # Add saved screen
        saved_screen = Screen(name='saved')
        self.saved_content = SavedScreen()
        saved_screen.add_widget(self.saved_content)
        self.content_manager.add_widget(saved_screen)
        
        # Add results screen
        results_screen = Screen(name='results')
        self.results_content = ResultsScreen()
        results_screen.add_widget(self.results_content)
        self.content_manager.add_widget(results_screen)
        
        # Start with home screen
        self.content_manager.current = 'home'
        
        # Bottom navigation
        self.bottom_nav = BottomNavigation(
            home_callback=self.go_to_home,
            saved_callback=self.go_to_saved
        )
        # Bind the button callbacks
        self.bottom_nav.bind_button_callbacks(
            home_callback=self.go_to_home,
            gemte_callback=self.go_to_saved
        )
        
        # Add to layout
        main_layout.add_widget(self.content_manager)
        main_layout.add_widget(self.bottom_nav)
        
        self.add_widget(main_layout)
    
    def _update_bg(self, instance, value):
        """Update background rectangle when layout changes"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.size = instance.size
            instance.bg_rect.pos = instance.pos
    
    def go_to_home(self, *args):
        """Navigate to home screen"""
        self.content_manager.current = 'home'
        self.bottom_nav.set_active_button('hjem')
        
        # Clear search if needed
        if hasattr(self.home_content, 'clear_search'):
            self.home_content.clear_search()
    
    def go_to_saved(self, *args):
        """Navigate to saved screen"""
        self.content_manager.current = 'saved'
        self.bottom_nav.set_active_button('gemte')
        
        # Refresh saved items
        if hasattr(self.saved_content, 'refresh_saved_items'):
            self.saved_content.refresh_saved_items()


class SaraMuseumApp(App):
    """Main application class"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "SARA Museum Søgning"
    
    def build(self):
        """Build app interface"""
        # Create screen manager
        screen_manager = ScreenManager()
        
        # Add main screen
        screen_manager.add_widget(MainScreen())
        
        return screen_manager


if __name__ == "__main__":
    SaraMuseumApp().run()