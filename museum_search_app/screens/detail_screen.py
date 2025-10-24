#!/usr/bin/env python3
"""
Detail Screen for SARA Museum App
Full-screen immersive view with object details, images, and new fields (dating, location, context)
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp


class DetailScreen(Screen):
    """Full-screen detailed view of an object"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "detail"
        self.current_object = None
        self.current_image_index = 0  # Track which image is currently displayed
        self.all_images = []  # Store all available images
        self.main_image_widget = None  # Reference to the main image widget
        self.image_counter_widget = None  # Reference to the image counter
        
    def show_object(self, obj):
        """Display full details for an object"""
        self.current_object = obj
        self.clear_widgets()
        self.build_detail_screen()
        
    def build_detail_screen(self):
        """Build the detailed object view"""
        if not self.current_object:
            return
            
        # Main container
        main_layout = BoxLayout(
            orientation="vertical",
            spacing=dp(0),
            padding=[0, 0, 0, 0]
        )
        
        # Clean white background
        with main_layout.canvas.before:
            Color(1, 1, 1, 1)  # White background
            main_layout.bg = Rectangle(size=main_layout.size, pos=main_layout.pos)
        main_layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Header with back button
        header_layout = BoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            spacing=dp(15),
            padding=[dp(20), dp(10), dp(20), dp(10)]
        )
        
        # Back arrow button
        back_button = Button(
            text='< Tilbage',
            size_hint=(None, 1),
            width=dp(100),
            font_size='16sp',
            background_color=(0, 0, 0, 0)  # Transparent background
        )
        
        # Style back button
        with back_button.canvas.before:
            Color(0.15, 0.25, 0.4, 1)  # Navy blue background
            back_button.bg_rect = RoundedRectangle(
                pos=back_button.pos,
                size=back_button.size,
                radius=[8, 8, 8, 8]
            )
        
        back_button.bind(pos=self._update_button_bg, size=self._update_button_bg)
        back_button.bind(on_press=self.go_back)
        back_button.color = [1, 1, 1, 1]  # White text
        
        header_layout.add_widget(back_button)
        
        # Add spacer to push back button to left
        header_spacer = Widget()
        header_layout.add_widget(header_spacer)
        
        main_layout.add_widget(header_layout)
        
        # Scrollable content area
        scroll = ScrollView()
        content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(20),
            size_hint_y=None,
            padding=[dp(20), dp(20), dp(20), dp(20)]
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # 1. Images section first - full width display
        self.add_images_section(content_layout)
        
        # 2. Main info card with title, number, and description together
        self.add_main_info_card(content_layout)
        
        # 3. Basic info cards at the bottom (classification, dating, location, context)
        self.add_basic_info_cards(content_layout)
        
        # 4. Save button
        self.add_save_button(content_layout)
        
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        
    def add_images_section(self, parent_layout):
        """Add images section with large primary image and clickable thumbnails"""
        obj = self.current_object
        primary_image_url = obj.get('primaryImage', '')
        additional_images = obj.get('additionalImages', [])
        has_image = obj.get('hasImage', False)
        
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
            
            # Main image - now stored as instance variable for updating
            self.main_image_widget = AsyncImage(
                source=self.all_images[self.current_image_index],
                size_hint_y=None,
                height=dp(280),
                fit_mode="contain"
            )
            image_container.add_widget(self.main_image_widget)
            
            # Image counter if multiple images - also stored for updating
            total_images = len(self.all_images)
            if total_images > 1:
                self.image_counter_widget = Label(
                    text=f"Billede {self.current_image_index + 1} af {total_images}",
                    size_hint_y=None,
                    height=dp(20),
                    font_size='12sp',
                    color=(0.5, 0.5, 0.5, 1),
                    halign='center'
                )
                image_container.add_widget(self.image_counter_widget)
            
            parent_layout.add_widget(image_container)
            
            # Add thumbnails for all images if there are multiple images
            if total_images > 1:
                self.add_thumbnail_section(parent_layout, self.all_images)
        else:
            # No image placeholder
            no_image_container = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(150)
            )
            
            # Placeholder background
            with no_image_container.canvas.before:
                Color(0.95, 0.95, 0.95, 1)  # Light gray
                no_image_container.bg_rect = RoundedRectangle(
                    pos=no_image_container.pos,
                    size=no_image_container.size,
                    radius=[10, 10, 10, 10]
                )
            no_image_container.bind(pos=self._update_placeholder_bg, size=self._update_placeholder_bg)
            
            no_image_label = Label(
                text="Intet billede tilgængeligt",
                font_size='16sp',
                color=(0.6, 0.6, 0.6, 1),
                halign='center',
                valign='middle'
            )
            no_image_container.add_widget(no_image_label)
            parent_layout.add_widget(no_image_container)
    
    def add_thumbnail_section(self, parent_layout, all_images):
        """Add thumbnails for all images"""
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
        
        # Add thumbnails for ALL images - now clickable and scrollable
        for i, img_url in enumerate(all_images):
            try:
                thumbnail = AsyncImage(
                    source=img_url,
                    size_hint_x=None,
                    width=dp(70),
                    fit_mode="cover"
                )
                
                # Store the correct image index (0-based, matching self.all_images)
                thumbnail.image_index = i
                
                # Make thumbnail clickable with proper closure
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
        parent_layout.add_widget(thumb_scroll)
    
    def switch_to_image(self, new_index):
        """Switch the main image to a different one"""
        if 0 <= new_index < len(self.all_images):
            old_index = self.current_image_index
            self.current_image_index = new_index
            
            # Update main image
            if self.main_image_widget:
                self.main_image_widget.source = self.all_images[new_index]
            
            # Update counter
            if self.image_counter_widget:
                total_images = len(self.all_images)
                self.image_counter_widget.text = f"Billede {new_index + 1} af {total_images}"
            
            print(f"Switched from image {old_index + 1} to image {new_index + 1}")
    
    def add_main_info_card(self, parent_layout):
        """Add main info card with title, object number, and description together"""
        obj = self.current_object
        
        # Calculate height based on content
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        estimated_lines = max(3, len(description) // 50 + 1)
        desc_height = min(dp(150), dp(20 * estimated_lines))
        total_height = dp(30) + dp(30) + desc_height + dp(60)  # Title section + number section + description + padding
        
        # Create card container
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=total_height,
            spacing=dp(8),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        
        # Card background - no shadow
        with card_container.canvas.before:
            Color(1, 1, 1, 1)
            card_container.bg = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[10, 10, 10, 10]
            )
        
        card_container.bind(pos=self._update_card_bg, size=self._update_card_bg)
        
        # Title with small label
        title_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(2)
        )
        
        title_label_small = Label(
            text='Titel:',
            size_hint_y=None,
            height=dp(15),
            font_size='12sp',
            bold=True,
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        title_label_small.bind(size=title_label_small.setter('text_size'))
        
        title_value = Label(
            text=obj.get('title', 'Ingen titel'),
            size_hint_y=None,
            height=dp(15),
            font_size='12sp',
            bold=False,
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        title_value.bind(size=title_value.setter('text_size'))
        
        title_section.add_widget(title_label_small)
        title_section.add_widget(title_value)
        card_container.add_widget(title_section)
        
        # Object number with small label
        number_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(30),
            spacing=dp(2)
        )
        
        number_label_small = Label(
            text='Objektnummer:',
            size_hint_y=None,
            height=dp(15),
            font_size='12sp',
            bold=True,
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        number_label_small.bind(size=number_label_small.setter('text_size'))
        
        obj_num = obj.get('objectNumber', 'Ukendt')
        number_value = Label(
            text=obj_num,
            size_hint_y=None,
            height=dp(15),
            font_size='12sp',
            halign='left',
            color=(0.3, 0.3, 0.3, 1)
        )
        number_value.bind(size=number_value.setter('text_size'))
        
        number_section.add_widget(number_label_small)
        number_section.add_widget(number_value)
        card_container.add_widget(number_section)
        
        # Description with small label
        desc_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=desc_height + dp(15),
            spacing=dp(2)
        )
        
        desc_label_small = Label(
            text='Beskrivelse:',
            size_hint_y=None,
            height=dp(15),
            font_size='12sp',
            bold=True,
            halign='left',
            color=(0.5, 0.5, 0.5, 1)
        )
        desc_label_small.bind(size=desc_label_small.setter('text_size'))
        
        desc_value = Label(
            text=description,
            size_hint_y=None,
            height=desc_height,
            font_size='14sp',
            halign='left',
            valign='top',
            color=(0.3, 0.3, 0.3, 1),
            text_size=(None, None)
        )
        desc_value.bind(size=desc_value.setter('text_size'))
        
        desc_section.add_widget(desc_label_small)
        desc_section.add_widget(desc_value)
        card_container.add_widget(desc_section)
        
        parent_layout.add_widget(card_container)
    
    def _update_card_bg(self, instance, value):
        """Update card background"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def add_basic_info_cards(self, parent_layout):
        """Add basic information cards (classification, dating, location, context)"""
        obj = self.current_object
        
        # Object details card with basic fields
        details_info = []
        
        # Classification
        classification = obj.get('classification', '')
        if classification and classification != 'Ukendt':
            details_info.append(f"Klassifikation: {classification}")
        
        # Dating
        dating = obj.get('dating', '')
        if dating and dating != 'Ukendt datering':
            details_info.append(f"Datering: {dating}")
        
        # Current Location
        current_location = obj.get('currentLocation', '')
        if current_location and current_location != 'Placering ikke registreret':
            details_info.append(f"Aktuel placering: {current_location}")
        
        # Context
        context = obj.get('context', '')
        if context and context != 'Ukendt kontekst':
            details_info.append(f"Kontekst: {context}")
        
        # Add basic info card if we have any info
        if details_info:
            details_text = "\n".join(details_info)
            details_card = self.create_info_card("Grundlæggende information", details_text)
            parent_layout.add_widget(details_card)
    
    def add_description_and_other_cards(self, parent_layout):
        """Add description and remaining detail cards"""
        obj = self.current_object
        
        # Description card
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        if description and description != 'Ingen beskrivelse tilgængelig':
            desc_card = self.create_info_card("Beskrivelse", description)
            parent_layout.add_widget(desc_card)
        
        # Additional details card (old fields as fallback)
        additional_info = []
        
        object_type = obj.get('objectName', '')
        if object_type:
            additional_info.append(f"Type: {object_type}")
            
        department = obj.get('department', '')
        if department and department != 'Ukendt afdeling':
            additional_info.append(f"Afdeling: {department}")
        
        if additional_info:
            additional_text = "\n".join(additional_info)
            additional_card = self.create_info_card("Yderligere information", additional_text)
            parent_layout.add_widget(additional_card)
    
    def add_detail_cards(self, parent_layout):
        """Add detailed information in clean card format"""
        obj = self.current_object
        
        # Description card
        description = obj.get('description', 'Ingen beskrivelse tilgængelig')
        if description and description != 'Ingen beskrivelse tilgængelig':
            desc_card = self.create_info_card("Beskrivelse", description)
            parent_layout.add_widget(desc_card)
        
        # Object details card with NEW fields
        details_info = []
        
        # Classification
        classification = obj.get('classification', '')
        if classification and classification != 'Ukendt':
            details_info.append(f"Klassifikation: {classification}")
        
        # Dating (NEW - DT field)
        dating = obj.get('dating', '')
        if dating and dating != 'Ukendt datering':
            details_info.append(f"Datering: {dating}")
        
        # Current Location (NEW - 2A field)
        current_location = obj.get('currentLocation', '')
        if current_location and current_location != 'Placering ikke registreret':
            details_info.append(f"Aktuel placering: {current_location}")
        
        # Context (NEW - C1 field)
        context = obj.get('context', '')
        if context and context != 'Ukendt kontekst':
            details_info.append(f"Kontekst: {context}")
        
        # Old fields (keep as fallback)
        object_type = obj.get('objectName', '')
        if object_type:
            details_info.append(f"Type: {object_type}")
            
        department = obj.get('department', '')
        if department and department != 'Ukendt afdeling':
            details_info.append(f"Afdeling: {department}")
            
        medium = obj.get('medium', '')
        if medium:
            details_info.append(f"Materiale: {medium}")
            
        technique = obj.get('technique', '')
        if technique:
            details_info.append(f"Teknik: {technique}")
            
        dimensions = obj.get('dimensions', '')
        if dimensions:
            details_info.append(f"Dimensioner: {dimensions}")
            
        if details_info:
            details_text = "\n".join(details_info)
            details_card = self.create_info_card("Objekt detaljer", details_text)
            parent_layout.add_widget(details_card)
        
        # Artist information if available
        artist = obj.get('artistDisplayName', '')
        if artist and artist != 'Ukendt kunstner':
            artist_info = []
            artist_info.append(f"Kunstner: {artist}")
            
            nationality = obj.get('artistNationality', '')
            if nationality:
                artist_info.append(f"Nationalitet: {nationality}")
                
            if artist_info:
                artist_text = "\n".join(artist_info)
                artist_card = self.create_info_card("Kunstner information", artist_text)
                parent_layout.add_widget(artist_card)
        
        # Collection information
        collection_info = []
        
        sara_id = obj.get('priref', '')
        if sara_id:
            collection_info.append(f"SARA ID: {sara_id}")
            
        repository = obj.get('repository', '')
        if repository:
            collection_info.append(f"Opbevaringssted: {repository}")
            
        acquisition_year = obj.get('acquisitionYear', '')
        if acquisition_year:
            collection_info.append(f"Erhvervelsesår: {acquisition_year}")
            
        if collection_info:
            collection_text = "\n".join(collection_info)
            collection_card = self.create_info_card("Samlings information", collection_text)
            parent_layout.add_widget(collection_card)
    
    def create_info_card(self, title, content):
        """Create a clean information card"""
        # Calculate dynamic height based on content length
        estimated_lines = max(2, len(content) // 50 + 1)
        content_height = min(dp(200), dp(20 * estimated_lines))
        total_height = dp(50) + content_height + dp(20)  # Title + content + padding
        
        card_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=total_height,
            spacing=dp(10),
            padding=[dp(15), dp(15), dp(15), dp(15)]
        )
        
        # Card background
        with card_container.canvas.before:
            Color(0.98, 0.98, 0.99, 1)  # Very light blue-gray
            card_container.bg_rect = RoundedRectangle(
                pos=card_container.pos,
                size=card_container.size,
                radius=[12, 12, 12, 12]
            )
        card_container.bind(pos=self._update_card_bg, size=self._update_card_bg)
        
        # Title
        title_label = Label(
            text=title,
            size_hint_y=None,
            height=dp(30),
            font_size='16sp',
            bold=True,
            color=(0.15, 0.25, 0.4, 1),  # Navy blue
            halign='left',
            valign='middle'
        )
        title_label.bind(size=title_label.setter('text_size'))
        
        # Content
        content_label = Label(
            text=content,
            size_hint_y=None,
            height=content_height,
            font_size='14sp',
            color=(0.3, 0.3, 0.3, 1),
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        content_label.bind(size=content_label.setter('text_size'))
        
        card_container.add_widget(title_label)
        card_container.add_widget(content_label)
        
        return card_container
    
    def go_back(self, *args):
        """Navigate back to search screen"""
        if self.manager:
            self.manager.current = 'search'
    
    def _update_bg(self, instance, value):
        """Update background"""
        if hasattr(instance, 'bg'):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
    
    def _update_button_bg(self, instance, value):
        """Update button background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_card_bg(self, instance, value):
        """Update card background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
    
    def _update_placeholder_bg(self, instance, value):
        """Update placeholder background"""
        if hasattr(instance, 'bg_rect'):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
