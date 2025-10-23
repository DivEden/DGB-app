#!/usr/bin/env python3
"""
Bottom Navigation Bar Component for SARA Museum App
Mobile-optimized navigation bar with Home and Saved buttons
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp


class BottomNavigation(BoxLayout):
    """Mobile-optimized bottom navigation bar"""
    
    def __init__(self, home_callback=None, saved_callback=None, **kwargs):
        # Extract callbacks before calling super to avoid passing them to Kivy
        self.home_callback = home_callback
        self.saved_callback = saved_callback
        
        # Remove callback parameters from kwargs to avoid Kivy errors
        kwargs.pop('home_callback', None)
        kwargs.pop('saved_callback', None)
        
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)  # Optimized height for mobile
        self.spacing = dp(10)
        self.padding = [dp(15), dp(8), dp(15), dp(8)]
        
        # Create navigation background
        with self.canvas.before:
            Color(1, 1, 1, 0.95)  # White background with slight transparency
            self.bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[15, 15, 0, 0]  # Rounded top corners only
            )
            # Add subtle shadow
            Color(0, 0, 0, 0.1)  # Light shadow
            self.shadow_rect = RoundedRectangle(
                pos=[self.pos[0], self.pos[1] + dp(2)],
                size=[self.size[0], dp(3)],
                radius=[15, 15, 0, 0]
            )
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Create Home button
        self.home_btn = self._create_nav_button(
            text='Hjem',
            is_active=True  # Default active state
        )
        
        # Create Gemte (Saved) button
        self.gemte_btn = self._create_nav_button(
            text='Gemte',
            is_active=False
        )
        
        self.add_widget(self.home_btn)
        self.add_widget(self.gemte_btn)
    
    def _create_nav_button(self, text, is_active=False):
        """Create a navigation button with text"""
        btn_container = BoxLayout(
            orientation='vertical',
            spacing=dp(2),
            padding=[dp(5), dp(3), dp(5), dp(3)]
        )
        
        # Button background color based on active state
        bg_color = (0.15, 0.25, 0.4, 1) if is_active else (0.9, 0.9, 0.9, 1)
        text_color = (1, 1, 1, 1) if is_active else (0.5, 0.5, 0.5, 1)
        
        # Create button
        nav_btn = Button(
            text=text,
            font_size='14sp',
            halign='center',
            valign='middle',
            background_color=bg_color,
            color=text_color,
            size_hint=(1, 1)
        )
        
        # Add rounded corners
        with nav_btn.canvas.before:
            Color(*bg_color)
            nav_btn.bg_rect = RoundedRectangle(
                pos=nav_btn.pos,
                size=nav_btn.size,
                radius=[8, 8, 8, 8]
            )
        
        nav_btn.bind(pos=self._update_button_bg, size=self._update_button_bg)
        
        # Store button state
        nav_btn.is_active = is_active
        nav_btn.button_text = text
        nav_btn.active_color = (0.15, 0.25, 0.4, 1)
        nav_btn.inactive_color = (0.9, 0.9, 0.9, 1)
        
        return nav_btn
    
    def _update_bg(self, instance, value):
        """Update background position and size"""
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size
        if hasattr(self, 'shadow_rect'):
            self.shadow_rect.pos = [self.pos[0], self.pos[1] + dp(2)]
            self.shadow_rect.size = [self.size[0], dp(3)]
    
    def _update_button_bg(self, instance, value):
        """Update button background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def set_active_button(self, button_name):
        """Set which button is active ('hjem' or 'gemte')"""
        if button_name.lower() == 'hjem' or button_name.lower() == 'home':
            self._activate_button(self.home_btn)
            self._deactivate_button(self.gemte_btn)
        elif button_name.lower() == 'gemte':
            self._activate_button(self.gemte_btn)
            self._deactivate_button(self.home_btn)
    
    def _activate_button(self, button):
        """Activate a navigation button"""
        button.is_active = True
        button.background_color = button.active_color
        button.color = (1, 1, 1, 1)  # White text
        
        # Update canvas background
        if hasattr(button, 'bg_rect'):
            with button.canvas.before:
                Color(*button.active_color)
                button.bg_rect.pos = button.pos
                button.bg_rect.size = button.size
    
    def _deactivate_button(self, button):
        """Deactivate a navigation button"""
        button.is_active = False
        button.background_color = button.inactive_color
        button.color = (0.5, 0.5, 0.5, 1)  # Gray text
        
        # Update canvas background
        if hasattr(button, 'bg_rect'):
            with button.canvas.before:
                Color(*button.inactive_color)
                button.bg_rect.pos = button.pos
                button.bg_rect.size = button.size
    
    def bind_button_callbacks(self, home_callback=None, gemte_callback=None):
        """Bind callbacks to navigation buttons"""
        if home_callback:
            self.home_btn.bind(on_release=lambda x: (
                self.set_active_button('hjem'),
                home_callback()
            ))
        
        if gemte_callback:
            self.gemte_btn.bind(on_release=lambda x: (
                self.set_active_button('gemte'),
                gemte_callback()
            ))