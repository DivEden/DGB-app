#!/usr/bin/env python3
"""
Bottom Navigation Bar Component for SARA Museum App
Mobile-optimized navigation bar with Home and Saved buttons
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp


class BottomNavigation(BoxLayout):
    """Bottom navigation bar with home and saved buttons"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        # 1.4 cm = 14mm, convert to dp (approximately 53 dp for most phones)
        self.height = dp(53)
        self.spacing = 0
        self.padding = [0, 0, 0, 0]
        
        # White background with top border
        with self.canvas.before:
            # Top border line
            Color(0, 0, 0, 1)  # Black line
            self.border_line = Line(points=[], width=0.5)
            
            # White background
            Color(1, 1, 1, 1)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_graphics, size=self._update_graphics)
        
        # Home button
        self.home_btn = self._create_nav_button('utils/Images/home.png', 'home')
        self.add_widget(self.home_btn)
        
        # Saved button
        self.saved_btn = self._create_nav_button('utils/Images/bookmark-white.png', 'saved')
        self.add_widget(self.saved_btn)
    
    def _create_nav_button(self, icon_path, button_id):
        """Create a navigation button with icon and label"""
        # Create a simple button-like container
        btn_container = BoxLayout(
            orientation='vertical',
            padding=[dp(5), dp(5), dp(5), dp(5)],
            spacing=dp(2)
        )
        btn_container.button_id = button_id
        
        # Add spacer to push icon down a bit
        btn_container.add_widget(Widget(size_hint_y=0.2))
        
        # Icon (centered, smaller size)
        try:
            icon = Image(
                source=icon_path,
                size_hint=(None, None),
                size=(dp(24), dp(24)),  # Smaller icon size
                allow_stretch=True,
                keep_ratio=True,
                mipmap=True  # Better quality scaling
            )
            # Center the icon using a container
            icon_wrapper = BoxLayout(size_hint_y=0.5)
            icon_wrapper.add_widget(Widget())  # Left spacer
            icon_wrapper.add_widget(icon)
            icon_wrapper.add_widget(Widget())  # Right spacer
            btn_container.add_widget(icon_wrapper)
        except Exception as e:
            print(f"Error loading icon {icon_path}: {e}")
            # Fallback to emoji
            label = Label(
                text='🏠' if 'home' in icon_path else '⭐',
                font_size='20sp',
                color=(0.2, 0.2, 0.2, 1),
                size_hint_y=0.5
            )
            btn_container.add_widget(label)
        
        # Label text below icon
        label_text = 'Hjem' if button_id == 'home' else 'Gemte'
        text_label = Label(
            text=label_text,
            size_hint_y=0.3,
            font_size='11sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='center',
            valign='top'
        )
        text_label.bind(size=text_label.setter('text_size'))
        btn_container.add_widget(text_label)
        
        return btn_container
    
    def _update_graphics(self, *args):
        """Update background and border line"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        
        # Update top border line
        self.border_line.points = [
            self.x, self.top,
            self.right, self.top
        ]
    
    def bind_button_callbacks(self, home_callback=None, saved_callback=None):
        """Bind callbacks to navigation buttons - bind to touch events"""
        if home_callback:
            self.home_btn.bind(on_touch_down=lambda instance, touch: 
                home_callback() if instance.collide_point(*touch.pos) else None)
        
        if saved_callback:
            self.saved_btn.bind(on_touch_down=lambda instance, touch: 
                saved_callback() if instance.collide_point(*touch.pos) else None)