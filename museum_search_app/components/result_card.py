#!/usr/bin/env python3
"""
Result Card Component for SARA Museum App
Displays individual search results with image gallery, info, and save functionality
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp

from utils.data_manager import DataManager


class ResultCard(BoxLayout):
    """Card component for displaying individual search results"""
    
    def __init__(self, obj_data=None, index=1, save_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.spacing = dp(8)
        self.padding = [dp(15), dp(15), dp(15), dp(15)]
        
        self.obj_data = obj_data or {}
        self.index = index
        self.save_callback = save_callback
        
        # Initialize data manager for save functionality
        self.data_manager = DataManager()
        
        # Image gallery variables
        self.main_image_widget = None
        self.image_counter_widget = None
        self.all_images = []
        self.current_image_index = 0
        
        self._calculate_height()
        self._create_card()
    
    def _calculate_height(self):
        """Calculate card height based on content"""
        # Calculate description height
        description = self.obj_data.get('description', 'Ingen beskrivelse tilgængelig')
        estimated_lines = max(3, len(description) // 50 + 1)
        desc_height = min(dp(120), dp(20 * estimated_lines))
        
        base_height = dp(260) + desc_height  # Header + info (now with 5 fields) + description + buttons
        
        # Add height for images
        has_image = self.obj_data.get('hasImage', False)
        if has_image:
            base_height += dp(350)  # Large image + thumbnails
        else:
            base_height += dp(60)   # No image placeholder
            
        self.height = base_height
    
    def _create_card(self):
        """Create the complete result card"""
        # 1. IMAGES SECTION (TOP)
        self._create_images_section()
        
        # 2. INFO SECTION (Classification, dating, location, context)
        self._create_basic_info_section()
        
        # 3. TITLE (just above description)
        self._create_title_section()
        
        # 4. OBJECT NUMBER (right after title, before description)
        self._create_object_number_section()
        
        # 5. DESCRIPTION
        self._create_description_section()
        
        # 6. ACTION BUTTONS (BOTTOM)
        self._create_action_buttons()
    
    def _create_images_section(self):
        """Create image gallery section - copied from old main.py"""
        primary_image_url = self.obj_data.get('primaryImage', '')
        additional_images = self.obj_data.get('additionalImages', [])
        has_image = self.obj_data.get('hasImage', False)
        
        if has_image and primary_image_url:
            # Build complete images list (primary + additional)
            self.all_images = [primary_image_url] + additional_images
            self.current_image_index = 0
            
            # Primary image container - large display
            image_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(300),  # Large image display
                spacing=dp(10)
            )
            
            # Main image - stored as instance variable for updating
            self.main_image_widget = AsyncImage(
                source=self.all_images[self.current_image_index],
                size_hint_y=None,
                height=dp(280),
                allow_stretch=True,
                keep_ratio=True
            )
            image_container.add_widget(self.main_image_widget)
            
            # Image counter if multiple images
            total_images = len(self.all_images)
            if total_images > 1:
                self.image_counter_widget = Label(
                    text=f"Image {self.current_image_index + 1} of {total_images}",
                    size_hint_y=None,
                    height=dp(20),
                    font_size='12sp',
                    color=(0.5, 0.5, 0.5, 1),
                    halign='center'
                )
                image_container.add_widget(self.image_counter_widget)
            
            self.add_widget(image_container)
            
            # Add thumbnails for all images if there are multiple images
            if total_images > 1:
                self._create_thumbnail_section()
        else:
            # No image placeholder
            self._create_no_image_placeholder()
    
    def _create_thumbnail_section(self):
        """Create thumbnail section - copied from old main.py"""
        # Scrollable container for thumbnails
        thumb_scroll = ScrollView(
            size_hint_y=None,
            height=dp(80),
            do_scroll_y=False,
            do_scroll_x=True,
            bar_width=dp(0)  # Hide scrollbars
        )
        
        thumb_container = BoxLayout(
            orientation='horizontal',
            size_hint_x=None,
            spacing=dp(10),
            padding=[dp(5), 0, dp(5), 0]
        )
        thumb_container.bind(minimum_width=thumb_container.setter('width'))
        
        # Add thumbnails for ALL images - clickable and scrollable
        for i, img_url in enumerate(self.all_images):
            try:
                thumbnail = AsyncImage(
                    source=img_url,
                    size_hint_x=None,
                    width=dp(70),
                    allow_stretch=True,
                    keep_ratio=True
                )
                
                # Make thumbnail clickable
                def make_click_handler(index):
                    def thumbnail_touch_handler(instance, touch):
                        if instance.collide_point(*touch.pos):
                            self.switch_to_image(index)
                            return True
                        return False
                    return thumbnail_touch_handler
                
                thumbnail.bind(on_touch_down=make_click_handler(i))
                thumb_container.add_widget(thumbnail)
            except Exception as e:
                print(f"Failed to load thumbnail {i}: {e}")
                pass  # Skip failed thumbnails
        
        thumb_scroll.add_widget(thumb_container)
        self.add_widget(thumb_scroll)
    
    def _create_no_image_placeholder(self):
        """Create placeholder when no image available"""
        no_image_label = Label(
            text="Intet billede tilgængeligt",
            size_hint_y=None,
            height=dp(60),
            font_size='16sp',
            color=(0.6, 0.6, 0.6, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(no_image_label)
    
    def switch_to_image(self, new_index):
        """Switch the main image to a different one - copied from old main.py"""
        if 0 <= new_index < len(self.all_images):
            old_index = self.current_image_index
            self.current_image_index = new_index
            
            # Update main image
            if self.main_image_widget:
                self.main_image_widget.source = self.all_images[new_index]
            
            # Update counter
            if self.image_counter_widget:
                total_images = len(self.all_images)
                self.image_counter_widget.text = f"Image {new_index + 1} of {total_images}"
            
            print(f"Switched from image {old_index + 1} to image {new_index + 1}")
    
    def _create_object_number_section(self):
        """Create object number section (shown right after image)"""
        obj_num = self.obj_data.get('objectNumber', 'Ukendt')
        obj_num_label = Label(
            text=f'Objektnummer: {obj_num}',
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            halign='left',
            color=(0.4, 0.4, 0.4, 1)
        )
        obj_num_label.bind(size=obj_num_label.setter('text_size'))
        self.add_widget(obj_num_label)
    
    def _create_title_section(self):
        """Create title section"""
        title_label = Label(
            text=self.obj_data.get('title', 'Ingen titel'),
            size_hint_y=None,
            height=dp(30),
            font_size='16sp',
            bold=True,
            halign='left',
            color=(0.2, 0.2, 0.2, 1),
            shorten=True,
            shorten_from='right'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)
    
    def _create_basic_info_section(self):
        """Create basic info section with all new fields"""
        info_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(2)
        )
        
        # All fields to display - with the new ones included
        fields_to_show = [
            ('Klassifikation', self.obj_data.get('classification', '')),
            ('Datering', self.obj_data.get('dating', '')),
            ('Placering (navn)', self.obj_data.get('location_name', '')),
            ('Placering (kontekst)', self.obj_data.get('location_context', '')),
            ('Accession nr.', self.obj_data.get('acquisition_number', '')),
            ('Giver', self.obj_data.get('acquisition_source', '')),
            ('Begrundelse', self.obj_data.get('acquisition_reason', '')),
            ('Erhvervelsesdato', self.obj_data.get('acquisition_date', '')),
            ('Proveniens-type', self.obj_data.get('event_type', '')),
            ('Proveniens-betegnelse', self.obj_data.get('event_name', '')),
            ('Proveniens-beskrivelse', self.obj_data.get('event_description', '')),
            ('Ophavsmand', self.obj_data.get('craftsman', ''))
        ]
        
        displayed_fields = 0
        for field_name, field_value in fields_to_show:
            if field_value and field_value.strip():  # Only show non-empty fields
                field_label = Label(
                    text=f'{field_name}: {field_value}',
                    size_hint_y=None,
                    height=dp(20),
                    font_size='14sp',
                    halign='left',
                    color=(0.4, 0.4, 0.4, 1)
                )
                field_label.bind(size=field_label.setter('text_size'))
                info_layout.add_widget(field_label)
                displayed_fields += 1
        
        # Set dynamic height based on displayed fields
        info_layout.height = dp(max(20, displayed_fields * 22))
        
        self.add_widget(info_layout)
    
    def _create_description_section(self):
        """Create description section"""
        description = self.obj_data.get('description', 'Ingen beskrivelse tilgængelig')
        estimated_lines = max(3, len(description) // 50 + 1)
        desc_height = min(dp(120), dp(20 * estimated_lines))
        
        desc_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=desc_height,
            spacing=dp(2)
        )
        
        # Description label
        desc_label_text = Label(
            text='Beskrivelse:',
            size_hint_y=None,
            height=dp(20),
            font_size='14sp',
            bold=True,
            halign='left',
            color=(0.2, 0.2, 0.2, 1)
        )
        desc_label_text.bind(size=desc_label_text.setter('text_size'))
        
        # Description content
        desc_content = Label(
            text=description,
            size_hint_y=None,
            height=desc_height - dp(20),
            font_size='13sp',
            halign='left',
            valign='top',
            color=(0.3, 0.3, 0.3, 1),
            text_size=(None, None)
        )
        desc_content.bind(size=desc_content.setter('text_size'))
        
        desc_layout.add_widget(desc_label_text)
        desc_layout.add_widget(desc_content)
        self.add_widget(desc_layout)
    
    def _create_action_buttons(self):
        """Create action buttons section"""
        buttons_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(50),
            spacing=dp(10),
            padding=[dp(15), dp(10), dp(15), dp(10)]
        )
        
        # Check if item is already saved
        obj_number = self.obj_data.get('objectNumber', self.obj_data.get('NB', ''))
        is_saved = self.data_manager.is_item_saved(obj_number)
        
        # Save/Unsave button
        if is_saved:
            save_btn = Button(
                text='Fjern fra gemte',
                size_hint_x=1.0,  # Full width since it's the only button
                font_size='14sp',
                background_color=(0.8, 0.3, 0.3, 1),
                color=(1, 1, 1, 1)
            )
            save_btn.bind(on_press=lambda x: self._handle_unsave())
        else:
            save_btn = Button(
                text='Gem',
                size_hint_x=1.0,  # Full width since it's the only button
                font_size='14sp',
                background_color=(0.2, 0.6, 0.2, 1),
                color=(1, 1, 1, 1)
            )
            save_btn.bind(on_press=lambda x: self._handle_save())
        
        buttons_layout.add_widget(save_btn)
        self.add_widget(buttons_layout)
    
    def _handle_save(self):
        """Handle save button press"""
        self.data_manager.add_to_saved_items(self.obj_data)
        print(f"Saved item: {self.obj_data.get('title', 'Unknown')}")
        
        # Refresh the button to show unsave option
        self._refresh_action_buttons()
        
        # Call external callback if provided
        if self.save_callback:
            self.save_callback(self.obj_data)
    
    def _handle_unsave(self):
        """Handle unsave button press"""
        self.data_manager.remove_from_saved_items(self.obj_data)
        print(f"Removed item from saved: {self.obj_data.get('title', 'Unknown')}")
        
        # Refresh the button to show save option
        self._refresh_action_buttons()
    
    def _refresh_action_buttons(self):
        """Refresh action buttons to update save/unsave state"""
        # Remove current action buttons
        if len(self.children) > 0:
            last_child = self.children[0]  # Last added widget (action buttons)
            if hasattr(last_child, 'children') and len(last_child.children) == 2:
                self.remove_widget(last_child)
        
        # Re-create action buttons with updated state
        self._create_action_buttons()