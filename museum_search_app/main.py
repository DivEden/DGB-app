#!/usr/bin/env python3
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.core.window import Window
from screens.home_screen import HomeScreen
from screens.results_screen import ResultsScreen  
from screens.detail_screen import DetailScreen
from screens.saved_screen import SavedScreen
from components.bottom_nav import BottomNavigation
from utils.data_manager import DataManager
from sara_api import SaraAPI

# Set window size to phone dimensions for testing
Window.size = (360, 640)

class SearchScreen(Screen):
    def __init__(self, sara_api=None, **kwargs):
        super().__init__(**kwargs)
        self.name = "search"
        self.data_manager = DataManager()
        self.sara_api = sara_api if sara_api else SaraAPI()
        self.home_screen = HomeScreen()
        self.home_screen.sara_api = self.sara_api  # Share the API instance
        self.home_screen.search_bar.set_search_callback(self.perform_search)
        if hasattr(self.home_screen, 'carousel'):
            def search_recent_wrapper(search_item):
                obj_number = search_item.get('objectNumber', '')
                if obj_number:
                    self.perform_search(obj_number)
            self.home_screen.carousel.item_click_callback = search_recent_wrapper
        self.add_widget(self.home_screen)
    
    def perform_search(self, query):
        if not query or not query.strip():
            return
        print(f"SearchScreen: Searching for: {query}")
        try:
            results = self.sara_api.search_objects_by_number(query)
            if results:
                print(f"SearchScreen: Found {len(results)} results")
                self.data_manager.add_to_recent_searches(results[0])
                self.home_screen.update_recent_carousel()
                
                # Get app instance to use navigation with history
                from kivy.app import App
                app = App.get_running_app()
                
                if len(results) == 1:
                    detail_screen = self.manager.get_screen('detail')
                    detail_screen.show_object(results[0])
                    app._navigate_to('detail')
                else:
                    results_screen = self.manager.get_screen('results')
                    results_screen.show_results(results, query)
                    app._navigate_to('results')
            else:
                print("SearchScreen: No results found")
                from kivy.app import App
                app = App.get_running_app()
                results_screen = self.manager.get_screen('results')
                results_screen.show_results([], query)
                app._navigate_to('results')
        except Exception as e:
            print(f"SearchScreen: Search error: {e}")

class SaraMuseumApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "DGB Assistent"
        self.sara_api = SaraAPI()  # Create shared instance
        self.connection_ready = False
        self.screen_history = []  # Track navigation history
        self._setup_android_ui()
        self._warm_up_connection()
    
    def _setup_android_ui(self):
        """Configure Android system UI (navigation bar color)"""
        try:
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            
            @run_on_ui_thread
            def set_navigation_bar_color():
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity
                window = activity.getWindow()
                
                # Set navigation bar color to white
                Color = autoclass('android.graphics.Color')
                window.setNavigationBarColor(Color.WHITE)
                
                # Set navigation bar to light mode (dark icons)
                View = autoclass('android.view.View')
                window.getDecorView().setSystemUiVisibility(
                    View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR
                )
            
            set_navigation_bar_color()
            print("Android navigation bar set to white")
        except Exception as e:
            # Not on Android or API < 26, ignore
            print(f"Could not set navigation bar color: {e}")
    
    def _warm_up_connection(self):
        """Pre-establish SARA API connection in background"""
        import threading
        
        def warm_up():
            try:
                print("App: Warming up SARA API connection...")
                # Use the shared instance
                self.sara_api.test_connection()
                self.connection_ready = True
                print("App: SARA API connection ready!")
                # Hide connection status on UI thread
                Clock.schedule_once(lambda dt: self._hide_connection_status(), 0)
            except Exception as e:
                print(f"App: Connection warm-up failed: {e}")
                self.connection_ready = False
                Clock.schedule_once(lambda dt: self._show_connection_error(), 0)
        
        threading.Thread(target=warm_up, daemon=True).start()
    
    def _show_connection_status(self):
        """Show connection status indicator"""
        if hasattr(self, 'home_screen'):
            self.home_screen._show_connection_status()
    
    def _hide_connection_status(self):
        """Hide connection status indicator"""
        if hasattr(self, 'home_screen'):
            self.home_screen._hide_connection_status()
    
    def _show_connection_error(self):
        """Show connection error"""
        if hasattr(self, 'home_screen'):
            self.home_screen._show_connection_error()
    
    def build(self):
        main_container = BoxLayout(orientation='vertical')
        self.screen_manager = ScreenManager()
        
        # Pass the shared sara_api instance to SearchScreen
        search_screen = SearchScreen(sara_api=self.sara_api)
        self.home_screen = search_screen.home_screen  # Get reference to home_screen
        self.screen_manager.add_widget(search_screen)
        self.screen_manager.add_widget(ResultsScreen())
        self.screen_manager.add_widget(DetailScreen())
        saved_screen_wrapper = Screen(name='saved')
        saved_screen_wrapper.add_widget(SavedScreen())
        self.screen_manager.add_widget(saved_screen_wrapper)
        main_container.add_widget(self.screen_manager)
        self.bottom_nav = BottomNavigation()
        
        def on_back_touch(instance, touch):
            if instance.collide_point(*touch.pos):
                self._go_back()
                return True
            return False
        def on_home_touch(instance, touch):
            if instance.collide_point(*touch.pos):
                self._navigate_to('search')
                return True
            return False
        def on_saved_touch(instance, touch):
            if instance.collide_point(*touch.pos):
                self._navigate_to('saved')
                return True
            return False
        self.bottom_nav.back_btn.bind(on_touch_down=on_back_touch)
        self.bottom_nav.home_btn.bind(on_touch_down=on_home_touch)
        self.bottom_nav.saved_btn.bind(on_touch_down=on_saved_touch)
        main_container.add_widget(self.bottom_nav)
        return main_container
    
    def _go_back(self):
        """Go back to previous screen in history"""
        if len(self.screen_history) > 1:
            # Remove current screen
            self.screen_history.pop()
            # Get previous screen
            previous_screen = self.screen_history[-1]
            # Navigate without adding to history
            self.screen_manager.current = previous_screen
            
            # Update bottom nav active state
            if previous_screen == 'search':
                self.bottom_nav.set_active_button('home')
            elif previous_screen == 'saved':
                self.bottom_nav.set_active_button('saved')
            else:
                # For detail/results screens, no button is active
                pass
        else:
            # No history, just go to home
            self._navigate_to('search')
    
    def _navigate_to(self, screen_name):
        # Add to history if it's a new screen
        if not self.screen_history or self.screen_history[-1] != screen_name:
            self.screen_history.append(screen_name)
        
        self.screen_manager.current = screen_name
        
        # Update bottom nav active state
        if screen_name == 'search':
            self.bottom_nav.set_active_button('home')
        elif screen_name == 'saved':
            self.bottom_nav.set_active_button('saved')
        
        # Refresh saved screen if navigating to it
        if screen_name == 'saved':
            saved_screen_wrapper = self.screen_manager.get_screen('saved')
            if saved_screen_wrapper.children:
                saved_screen = saved_screen_wrapper.children[0]
                if hasattr(saved_screen, 'refresh_saved_items'):
                    saved_screen.refresh_saved_items()

if __name__ == "__main__":
    SaraMuseumApp().run()
