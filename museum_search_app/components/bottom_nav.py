#!/usr/bin/env python3
"""
Bottom Navigation Bar - Ultra Clean Professional Design
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp


class BottomNavigation(BoxLayout):
    """Clean professional bottom navigation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(60)
        self.spacing = 0
        self.padding = [0, 0, 0, 0]
        
        # Background with subtle shadow
        with self.canvas.before:
            # Shadow effect
            Color(0, 0, 0, 0.05)
            self.shadow = RoundedRectangle(pos=self.pos, size=(self.width, dp(1)), radius=[0])
            
            # White background
            Color(0.99, 0.99, 0.99, 1)  # Off-white
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_bg, size=self._update_bg)
        
        # Buttons - 3 buttons now
        self.back_btn = self._create_button('utils/Images/back.png', 'Tilbage', 'back', False)
        self.add_widget(self.back_btn)
        
        self.home_btn = self._create_button('utils/Images/home.png', 'Hjem', 'home', True)
        self.add_widget(self.home_btn)
        
        self.saved_btn = self._create_button('utils/Images/bookmark-white.png', 'Gemte', 'saved', False)
        self.add_widget(self.saved_btn)
    
    def _create_button(self, icon_path, text, btn_id, active):
        """Create modern button with icon and text"""
        container = BoxLayout(orientation='vertical', padding=[0, dp(8), 0, dp(10)], spacing=dp(4))
        container.button_id = btn_id
        container.is_active = active
        
        # Icon with tint - high quality settings
        try:
            icon = Image(
                source=icon_path,
                size_hint=(None, None),
                size=(dp(24), dp(24)),
                pos_hint={'center_x': 0.5},
                allow_stretch=True,
                keep_ratio=True,
                mipmap=True,  # Enable mipmapping for better quality
                color=(0.15, 0.15, 0.15, 1) if active else (0.65, 0.65, 0.65, 1)
            )
            icon_wrapper = BoxLayout(size_hint_y=None, height=dp(24))
            icon_wrapper.add_widget(BoxLayout())  # Left spacer
            icon_wrapper.add_widget(icon)
            icon_wrapper.add_widget(BoxLayout())  # Right spacer
            container.add_widget(icon_wrapper)
            container.icon = icon
        except:
            # Fallback if icon fails to load
            pass
        
        # Label with better rendering
        label = Label(
            text=text,
            size_hint_y=None,
            height=dp(14),
            font_size='11sp',  # Slightly larger for crisper text
            bold=active,
            color=(0.15, 0.15, 0.15, 1) if active else (0.65, 0.65, 0.65, 1),
            halign='center',
            valign='middle'
        )
        label.texture_update()  # Force texture update for crisp rendering
        container.add_widget(label)
        container.label = label
        
        return container
    
    def set_active_button(self, button_id):
        """Switch active button"""
        for btn in [self.home_btn, self.saved_btn]:
            active = (btn.button_id == button_id)
            btn.is_active = active
            
            # Update icon color
            if hasattr(btn, 'icon'):
                btn.icon.color = (0.15, 0.15, 0.15, 1) if active else (0.65, 0.65, 0.65, 1)
                btn.icon.reload()  # Reload for crisp rendering
            
            # Update label with texture refresh
            if hasattr(btn, 'label'):
                btn.label.color = (0.15, 0.15, 0.15, 1) if active else (0.65, 0.65, 0.65, 1)
                btn.label.bold = active
                btn.label.texture_update()  # Force sharp text rendering
    
    def _update_bg(self, *args):
        """Update background"""
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.shadow.pos = (self.x, self.top)
        self.shadow.size = (self.width, dp(1))
    
    def bind_button_callbacks(self, back_callback=None, home_callback=None, saved_callback=None):
        """Bind touch events"""
        if back_callback:
            self.back_btn.bind(on_touch_down=lambda i, t: back_callback() if i.collide_point(*t.pos) else None)
        if home_callback:
            self.home_btn.bind(on_touch_down=lambda i, t: home_callback() if i.collide_point(*t.pos) else None)
        if saved_callback:
            self.saved_btn.bind(on_touch_down=lambda i, t: saved_callback() if i.collide_point(*t.pos) else None)