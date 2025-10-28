#!/usr/bin/env python3
"""
Home Screen for SARA Museum App
Main search interface with recent searches carousel
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.metrics import dp

from components.search_bar import SearchBar
from components.carousel import RecentSearchesCarousel
from components.result_card import ResultCard
from utils.data_manager import DataManager
from sara_api import SaraAPI


class HomeScreen(BoxLayout):
    """Main home screen with search and results"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Set white background
        with self.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Initialize managers
        self.data_manager = DataManager()
        self.sara_api = SaraAPI()
        
        self._create_layout()
    
    def _update_bg(self, *args):
        """Update background position and size"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
    
    def _create_layout(self):
        """Create the main layout"""
        # Main layout locked to top
        main_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,  # Fixed height to lock to top
            spacing=dp(10),
            padding=[0, dp(40), 0, dp(20)]  # No horizontal padding for centering
        )
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        # Search bar at the top - centered
        search_bar_container = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(35)
        )
        
        print("HomeScreen: Creating SearchBar component")
        self.search_bar = SearchBar(search_callback=self.search_objects)
        print(f"HomeScreen: SearchBar created, callback set to: {self.search_bar.search_callback}")
        
        # Center the search bar with proportional spacers
        # Left spacer takes up ~5.6% of width ((7.1-6.3)/2 / 7.1)
        left_spacer = BoxLayout(size_hint_x=0.056)
        right_spacer = BoxLayout(size_hint_x=0.056)
        
        search_bar_container.add_widget(left_spacer)
        search_bar_container.add_widget(self.search_bar)
        search_bar_container.add_widget(right_spacer)
        
        main_layout.add_widget(search_bar_container)
        
        # Recent searches carousel
        print("HomeScreen: Creating RecentSearchesCarousel component")
        self.carousel = RecentSearchesCarousel(item_click_callback=self.search_recent_item)
        print(f"HomeScreen: Carousel created, callback set to: {self.carousel.item_click_callback}")
        main_layout.add_widget(self.carousel)
        
        # Container to hold main_layout at top and spacer at bottom
        full_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(0)
        )
        
        # Add main content at top
        full_layout.add_widget(main_layout)
        
        # Add flexible spacer to push content to top
        spacer = BoxLayout()  # This will expand to fill remaining space
        full_layout.add_widget(spacer)
        
        # Update carousel with recent searches
        self.update_recent_carousel()
        
        self.add_widget(full_layout)
    
    def search_objects(self, query):
        """Search for objects using the API"""
        print(f"HomeScreen.search_objects called with: '{query}'")
        if not query:
            print("HomeScreen: Empty query, returning")
            return
        
        print("HomeScreen: Starting search, will navigate to results screen")
        
        # Perform search in thread
        def search_thread():
            try:
                results = self.sara_api.search_objects_by_number(query)
                # Update UI in main thread
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self._navigate_to_results(results, query), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self._show_search_error(str(e)), 0)
        
        import threading
        threading.Thread(target=search_thread, daemon=True).start()
    
    def _navigate_to_results(self, results, query):
        """Navigate to results screen with search results"""
        print(f"HomeScreen: Got {len(results)} results, navigating to results screen")
        
        try:
            # Add first result to recent searches if found
            if results:
                print("HomeScreen: Adding to recent searches")
                self.data_manager.add_to_recent_searches(results[0])
                self.update_recent_carousel()
                print("HomeScreen: Updated recent carousel")
            
            # Get the screen manager through parent hierarchy
            # Looking for 'manager' attribute which is the ScreenManager
            print(f"HomeScreen: Looking for screen manager")
            current = self
            screen_manager = None
            max_iterations = 10
            iteration = 0
            
            while current and iteration < max_iterations:
                print(f"HomeScreen: Iteration {iteration}, checking: {type(current)}")
                if hasattr(current, 'manager') and current.manager:
                    screen_manager = current.manager
                    print(f"HomeScreen: Found manager: {screen_manager}")
                    break
                current = current.parent if hasattr(current, 'parent') else None
                iteration += 1
            
            if not screen_manager:
                print("HomeScreen: ERROR - Could not find screen manager")
                return
            
            # Get the results screen and show results
            results_screen = screen_manager.get_screen('results')
            print(f"HomeScreen: Got results screen: {results_screen}")
            
            # ResultsScreen is a Screen, call show_results directly on it
            print("HomeScreen: Calling show_results")
            results_screen.show_results(results, query)
            print("HomeScreen: show_results completed")
            
            # Navigate to results screen
            print("HomeScreen: Changing screen to 'results'")
            screen_manager.current = 'results'
            print("HomeScreen: Navigation complete")
            
        except Exception as e:
            print(f"HomeScreen: ERROR in _navigate_to_results: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_search_error(self, error_msg):
        """Show search error message"""
        print(f"HomeScreen: Search error: {error_msg}")
        # Could add a popup or other error display here
    
    def search_recent_item(self, search_item):
        """Search for an item from recent searches"""
        print(f"HomeScreen.search_recent_item called with: {search_item}")
        obj_number = search_item.get('objectNumber', '')
        if obj_number:
            print(f"HomeScreen: Setting search text to '{obj_number}' and calling search")
            self.search_bar.search_input.text = obj_number
            self.search_objects(obj_number)
        else:
            print("HomeScreen: No objectNumber in search_item")
    
    def save_item(self, obj_data):
        """Save an item to saved items"""
        self.data_manager.add_to_saved_items(obj_data)
        print(f"Saved item: {obj_data.get('title', 'Unknown')}")
    
    def clear_search(self):
        """Clear search input"""
        self.search_bar.clear_search()
    
    def update_recent_carousel(self):
        """Update the recent searches carousel"""
        recent_searches = self.data_manager.get_recent_searches()
        self.carousel.update_carousel(recent_searches)