#!/usr/bin/env python3
"""
Saved Item Grid Component for SARA Museum App
Displays saved items in a grid format with image thumbnails
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.metrics import dp
from kivy.clock import Clock


class SavedItemGrid(GridLayout):
    """Grid layout for saved items with thumbnails"""
    
    def __init__(self, saved_items=None, remove_callback=None, view_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.cols = 3  # Three columns
        self.spacing = dp(10)  # Reduced spacing
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        self.saved_items = saved_items or []
        self.remove_callback = remove_callback
        self.view_callback = view_callback
        
        self._populate_grid()
        
    def safe_set_image_source(self, image_widget, local_path):
        """Sæt billede source sikkert på UI-tråden (Android-compatible)"""
        def _apply_source(dt):
            if image_widget and local_path:
                image_widget.source = str(local_path)
                image_widget.reload()
        Clock.schedule_once(_apply_source, 0)
        
    def _populate_grid(self):
        """Populate the grid with saved items"""
        self.clear_widgets()
        
        for item in self.saved_items:
            grid_item = SavedGridItem(
                obj_data=item,
                remove_callback=self.remove_callback,
                view_callback=self.view_callback
            )
            self.add_widget(grid_item)


class SavedGridItem(BoxLayout):
    """Individual grid item for saved objects - styled like carousel cards"""
    
    def __init__(self, obj_data=None, remove_callback=None, view_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.size_hint_x = None
        self.width = dp(100)  # Reduced to fit 3 per row on phone
        self.height = dp(140)  # 90 image + 50 text
        self.spacing = dp(0)
        self.padding = [dp(2), dp(2), dp(2), 0]
        
        self.obj_data = obj_data or {}
        self.remove_callback = remove_callback
        self.view_callback = view_callback
        self.remove_btn = None  # Will be set when button is created
        
        # Create card container with white background (no shadow)
        self.card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(140),
            spacing=dp(0)
        )
        
        # Add white background with square corners - same as carousel
        with self.card_container.canvas.before:
            Color(1, 1, 1, 1)  # White background
            self.bg_rect = RoundedRectangle(
                pos=self.card_container.pos,
                size=self.card_container.size,
                radius=[dp(0), dp(0), dp(0), dp(0)]  # Square corners
            )
        
        self.card_container.bind(pos=self._update_bg, size=self._update_bg)
        
        self._create_item()
        self.add_widget(self.card_container)
    
    def _update_bg(self, instance, value):
        """Update background"""
        self.bg_rect.pos = self.card_container.pos
        self.bg_rect.size = self.card_container.size
    
    def _create_item(self):
        """Create the grid item content - styled like recent searches"""
        # Image section (top 2/3, similar to recent searches)
        self._create_image_section()
        
        # Text section (bottom 1/3, similar to recent searches)
        self._create_text_section()
    
    def _create_image_section(self):
        """Create image section - 100x90dp with button overlay"""
        # Use FloatLayout to overlay button on image
        image_container = FloatLayout(
            size_hint_y=None,
            height=dp(90)
        )
        
        # Image section background
        image_section = BoxLayout(
            orientation='vertical',
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        
        primary_image_url = self.obj_data.get('primaryImage', '')
        has_image = self.obj_data.get('hasImage', False)
        
        if has_image and primary_image_url:
            # Real image with cover mode like carousel
            image = AsyncImage(
                source=primary_image_url,
                fit_mode="cover",
                size_hint=(1, 1),
                mipmap=True
            )
            image_section.add_widget(image)
            
            # Add rounded corner overlay same as carousel
            with image_section.canvas.after:
                Color(1, 1, 1, 1)  # White color
                image_section.corner_border = Line(
                    rounded_rectangle=(
                        image_section.x, 
                        image_section.y, 
                        image_section.width, 
                        image_section.height, 
                        dp(8)  # radius
                    ),
                    width=dp(3)  # Same as carousel
                )
            
            image_section.bind(pos=self._update_image_overlay, size=self._update_image_overlay)
        else:
            # No image placeholder with rounded corners
            placeholder_container = BoxLayout(
                orientation='vertical',
                size_hint_y=1.0
            )
            
            with placeholder_container.canvas.before:
                Color(0.96, 0.97, 0.98, 1)  # Same as carousel
                placeholder_container.placeholder_rect = RoundedRectangle(
                    pos=placeholder_container.pos,
                    size=placeholder_container.size,
                    radius=[dp(8), dp(8), dp(8), dp(8)]  # Same as carousel
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
        
        image_container.add_widget(image_section)
        
        # Add circular remove button on top - with custom background
        self.remove_btn = Button(
            text='×',
            size_hint=(None, None),
            size=(dp(28), dp(28)),
            pos_hint={'right': 0.92, 'top': 0.92},
            font_size='20sp',
            background_normal='',
            background_down='',
            background_color=(0, 0, 0, 0),  # Transparent, we'll draw custom circle
            color=(1, 1, 1, 1),
            bold=True
        )
        
        # Draw circular background for button
        with self.remove_btn.canvas.before:
            Color(0.9, 0.2, 0.2, 0.95)  # Red background
            self.remove_btn.circle_bg = RoundedRectangle(
                pos=self.remove_btn.pos,
                size=self.remove_btn.size,
                radius=[dp(14), dp(14), dp(14), dp(14)]  # Full radius for circle
            )
        
        self.remove_btn.bind(pos=self._update_remove_btn_bg, size=self._update_remove_btn_bg)
        self.remove_btn.bind(on_press=lambda x: self._handle_remove())
        image_container.add_widget(self.remove_btn)
        
        # Add touch handler to image_container to handle clicks
        def on_container_touch(touch):
            # Check if touch is on remove button first
            if self.remove_btn and self.remove_btn.collide_point(*touch.pos):
                # Let button handle it
                return self.remove_btn.on_touch_down(touch)
            # Otherwise, check if touch is on card for viewing
            elif self.card_container.collide_point(*touch.pos):
                if self.view_callback:
                    self.view_callback(self.obj_data)
                return True
            return False
        
        image_container.on_touch_down = on_container_touch
        
        self.card_container.add_widget(image_container)
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_rect'):
            instance.placeholder_rect.pos = instance.pos
            instance.placeholder_rect.size = instance.size
    
    def _update_remove_btn_bg(self, instance, value):
        """Update remove button circular background"""
        if hasattr(instance, 'circle_bg'):
            instance.circle_bg.pos = instance.pos
            instance.circle_bg.size = instance.size
    
    def _create_text_section(self):
        """Create text section - smaller for compact grid"""
        text_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            size_hint_x=1,
            height=dp(50),  # Reduced height
            padding=[dp(5), dp(5), dp(5), dp(5)],
            spacing=dp(2)
        )
        
        # Title - smaller font
        title_text = self.obj_data.get('title', 'No title')
        if len(title_text) > 20:
            title_text = title_text[:17] + '...'
        
        title_label = Label(
            text=title_text,
            font_size='12sp',  # Smaller font
            bold=True,
            color=(0.2, 0.2, 0.2, 1),
            halign='center',
            valign='top',
            text_size=(dp(90), None),
            shorten=True,
            shorten_from='right',
            max_lines=1
        )
        
        # Subtitle (object number) - smaller font
        objektnummer = self.obj_data.get('objectNumber', '')
        if objektnummer:
            subtitle_label = Label(
                text=objektnummer,
                font_size='10sp',  # Smaller font
                color=(0.46, 0.46, 0.46, 1),
                halign='center',
                valign='top',
                text_size=(dp(90), None)
            )
            text_section.add_widget(title_label)
            text_section.add_widget(subtitle_label)
        else:
            text_section.add_widget(title_label)
        
        self.card_container.add_widget(text_section)
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'placeholder_rect'):
            instance.placeholder_rect.pos = instance.pos
            instance.placeholder_rect.size = instance.size
    
    def _update_image_overlay(self, instance, value):
        """Update image overlay border with rounded corners"""
        if hasattr(instance, 'corner_border'):
            instance.corner_border.rounded_rectangle = (
                instance.x,
                instance.y, 
                instance.width,
                instance.height,
                dp(8)
            )
    
    def _handle_remove(self):
        """Handle remove button press"""
        if self.remove_callback:
            self.remove_callback(self.obj_data)