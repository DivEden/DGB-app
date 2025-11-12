"""
SARA API Modul til Museum Søge App
Håndterer kommunikation med SARA database API
"""

import requests
import json
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from requests.auth import HTTPBasicAuth
import urllib.request
import base64
from utils.android_logger import android_logger


class SaraAPI:
    """Interface til SARA database API"""
    
    def __init__(self):
        # SARA API konfiguration (fra sara_uploader.py)
        self.base_url = "https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx"
        self.username = r"adlibhosting\DGB-API-USER"
        self.password = "YxUyuzNLubfNKbx2"
        self.auth = HTTPBasicAuth(self.username, self.password)
        
        # Create persistent session for connection reuse
        self.session = requests.Session()
        self.session.auth = self.auth
        # Pre-warm the connection pool
        self.session.headers.update({
            'User-Agent': 'DGB-Assistent/1.0',
            'Connection': 'keep-alive'
        })
        
        # Definér ønskede felter fra SARA API
        self.search_fields = [
            'priref',
            'object_number',
            'title',
            'object_category',
            'object_name',
            'technique',
            'material',
            'dimensions',
            'description',
            'dating.date.start',
            'dating.date.end',
            'location.default.name',       # Placering (navn) - NL
            'location.default.context',    # Placering (kontekst) - C2
            'acquisition.number',          # Accession nr. - HF
            'acquisition.source',          # Giver - VN
            'acquisition.reason',          # Begrundelse - VR
            'acquisition.date',            # Dato - VD
            'event.type',                  # Proveniens-type - 1T
            'event.name',                  # Proveniens-betegnelse - 1N
            'event.description',           # Proveniens-beskrivelse - 1S
            'craftsman',                   # Ophavsmand - VO
            'reproduction',                # For at få billeder
            'reproduction.reference',
            'reproduction.type',
            'reproduction.format',
            'reproduction.identifier_URL',
            'reproduction.publish_on_website'
        ]
    
    def search_objects_by_number(self, object_number: str, limit: int = 20) -> List[Dict]:
        """
        Søg efter objekter i SARA databasen efter objektnummer
        
        Args:
            object_number: Objektnummer (f.eks. 0054x0007, 12345;15, AAB 1234)
            limit: Maksimum antal resultater
        
        Returns:
            Liste af objekt ordbøger med detaljer
        """
        try:
            # Søg i SARA databasen efter objektnummer (samme som sara_uploader.py)
            params = {
                'command': 'search',
                'database': 'collection',
                'search': f'object_number="{object_number}"',
                'output': 'xml',
                'limit': limit,
                'fields': ','.join(self.search_fields)
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.text)
            
            # Tjek om vi fandt objekter
            diagnostic = root.find('.//diagnostic')
            hits = 0
            if diagnostic is not None:
                hits_elem = diagnostic.find('hits')
                if hits_elem is not None:
                    hits = int(hits_elem.text or '0')
            
            if hits == 0:
                return []
            
            # Parse objekter fra XML
            objects = []
            records = root.findall('.//record')
            
            for record in records:
                obj_data = self._parse_object_record(record)
                if obj_data:
                    objects.append(obj_data)
            
            return objects
            
        except requests.RequestException as e:
            print(f"SARA API fejl: {e}")
            return []
        except ET.ParseError as e:
            print(f"XML parsing fejl: {e}")
            return []
        except Exception as e:
            print(f"Uventet fejl i søgning: {e}")
            return []
    
    def search_objects(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Søg efter objekter i SARA databasen (generel søgning)
        
        Args:
            query: Søgeterm (kan være objektnummer eller andre felter)
            limit: Maksimum antal resultater
        
        Returns:
            Liste af objekt ordbøger med detaljer
        """
        # Søg altid som objektnummer først
        if query.strip():
            # Prøv først objektnummer søgning
            object_results = self.search_objects_by_number(query, limit)
            if object_results:
                return object_results
            
            # Hvis ingen resultater som objektnummer, søg i alle felter
            try:
                params = {
                    'command': 'search',
                    'database': 'collection',
                    'search': f'all="{query}"',
                    'output': 'xml',
                    'limit': limit,
                    'fields': ','.join(self.search_fields)
                }
                
                response = self.session.get(
                    self.base_url,
                    params=params,
                    timeout=30
                )
                response.raise_for_status()
                
                # Parse XML response
                root = ET.fromstring(response.text)
                
                # Tjek om vi fandt objekter
                diagnostic = root.find('.//diagnostic')
                hits = 0
                if diagnostic is not None:
                    hits_elem = diagnostic.find('hits')
                    if hits_elem is not None:
                        hits = int(hits_elem.text or '0')
                
                if hits == 0:
                    return []
                
                # Parse objekter fra XML
                objects = []
                records = root.findall('.//record')
                
                for record in records:
                    obj_data = self._parse_object_record(record)
                    if obj_data:
                        objects.append(obj_data)
                
                return objects
                
            except Exception as e:
                print(f"Generel søgning fejl: {e}")
                return []
        
        return []
    
    def get_object_detail(self, priref: str) -> Optional[Dict]:
        """
        Hent detaljerede oplysninger om et specifikt objekt
        
        Args:
            priref: SARA objekt ID
        
        Returns:
            Ordbog med objekt detaljer eller None hvis ikke fundet
        """
        try:
            params = {
                'command': 'search',
                'database': 'collection',
                'search': f'priref={priref}',
                'output': 'xml',
                'limit': 1,
                'fields': ','.join(self.search_fields)
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            record = root.find('.//record')
            
            if record is not None:
                return self._parse_object_record(record, detailed=True)
            
            return None
            
        except Exception as e:
            print(f"Fejl ved hentning af objekt {priref}: {e}")
            return None
    
    def _parse_object_record(self, record, detailed: bool = False) -> Dict:
        """
        Parse et objekt record fra SARA XML
        
        Args:
            record: XML element med objekt data
            detailed: Om der skal hentes detaljerede oplysninger
        
        Returns:
            Ordbog med objekt oplysninger
        """
        def get_text(xpath, default=""):
            """Hjælpefunktion til at hente tekst fra XML"""
            elem = record.find(xpath)
            return elem.text if elem is not None and elem.text else default
        
        def get_multilang_text(xpath_pattern, default=""):
            """Hent tekst med sprogstøtte (dansk først)"""
            # Prøv først dansk (lang="0" eller "11")
            for lang in ["0", "11", "neutral"]:
                elem = record.find(f"{xpath_pattern}/value[@lang='{lang}']")
                if elem is not None and elem.text:
                    return elem.text
            
            # Hvis ingen sprogversion, prøv direkte tekst
            elem = record.find(xpath_pattern)
            if elem is not None and elem.text:
                return elem.text
            
            return default
        
        # Grundlæggende objektoplysninger
        obj_data = {
            'priref': record.get('priref', ''),
            'objectID': record.get('priref', ''),
            'title': self._extract_title(record),
            'objectName': get_multilang_text('.//object_name', ''),
            'objectNumber': get_text('.//object_number', ''),
            'department': get_multilang_text('.//institution_name', 'Ukendt afdeling'),
            'classification': get_multilang_text('.//object_category', ''),
            'description': self._extract_description(record),
            'dating': self._extract_dating(record),
            'currentLocation': self._extract_current_location(record),
            'context': self._extract_context(record),
        }
        
        # Tilføj de nye ønskede felter
        obj_data.update({
            # Placering
            'location_name': get_multilang_text('.//location.default.name', ''),  # NL
            'location_context': get_multilang_text('.//location.default.context', ''),  # C2
            
            # Erhvervelse
            'acquisition_number': get_text('.//acquisition.number', ''),  # HF
            'acquisition_source': get_multilang_text('.//acquisition.source', ''),  # VN - Giver
            'acquisition_reason': get_multilang_text('.//acquisition.reason', ''),  # VR - Begrundelse
            'acquisition_date': get_text('.//acquisition.date', ''),  # VD - Dato
            
            # Proveniens
            'event_type': get_multilang_text('.//event.type', ''),  # 1T - Proveniens-type
            'event_name': get_multilang_text('.//event.name', ''),  # 1N - Proveniens-betegnelse
            'event_description': get_multilang_text('.//event.description', ''),  # 1S - Proveniens-beskrivelse
            
            # Ophavsmand
            'craftsman': get_multilang_text('.//craftsman', ''),  # VO - Ophavsmand
        })
        
        # Kunstner information
        artist_name = get_multilang_text('.//production.creator', '')
        if not artist_name:
            artist_name = get_multilang_text('.//creator', '')
        
        obj_data.update({
            'artistDisplayName': artist_name or 'Ukendt kunstner',
            'artistDisplayBio': '',  # SARA har typisk ikke biografier
            'artistNationality': get_multilang_text('.//production.creator.nationality', ''),
        })
        
        # Datoer
        date_str = get_multilang_text('.//production.date', '')
        if not date_str:
            date_str = get_text('.//production.date.start', '')
        
        obj_data.update({
            'objectDate': date_str or 'Ukendt dato',
            'objectBeginDate': self._extract_year(date_str),
            'objectEndDate': self._extract_year(date_str),
        })
        
        # Materiale og dimensioner
        obj_data.update({
            'medium': get_multilang_text('.//material', ''),
            'technique': get_multilang_text('.//technique', ''),
            'dimensions': get_multilang_text('.//dimension', ''),
            'culture': get_multilang_text('.//production.place', ''),
        })
        
        # Billeder fra reproductions
        images = self._extract_images(record)
        obj_data.update({
            'images': images,  # Tilføj images listen også
            'primaryImage': images[0] if images else '',
            'primaryImageSmall': images[0] if images else '',  # SARA har ikke separate small images
            'additionalImages': images[1:] if len(images) > 1 else [],
            'hasImage': len(images) > 0,
        })
        
        # SARA specifikke felter
        obj_data.update({
            'isPublicDomain': True,  # Antag at SARA objekter er public domain
            'isHighlight': False,  # SARA har ikke highlight system som Met
            'creditLine': get_multilang_text('.//credit_line', ''),
            'acquisitionYear': get_text('.//acquisition.date', '').split('-')[0] if get_text('.//acquisition.date', '') else '',
            'repository': 'SARA Museum Database',
            'objectURL': f"https://sara.dk/object/{obj_data['priref']}" if obj_data['priref'] else '',
        })
        
        # Hvis detaljeret visning, tilføj mere info
        if detailed:
            obj_data.update({
                'provenance': get_multilang_text('.//acquisition.source', ''),
                'exhibition_history': get_multilang_text('.//exhibition.title', ''),
                'bibliography': get_multilang_text('.//documentation.title', ''),
                'notes': get_multilang_text('.//notes', ''),
            })
        
        return obj_data
    
    def _extract_dating(self, record) -> str:
        """
        Udtræk datering fra SARA record
        Henter produktionsdato (når objektet blev lavet), ikke sagsdato
        
        Args:
            record: XML record element
        
        Returns:
            Datering tekst
        """
        # Prøv production.date.start og production.date.end (VIGTIGST - objektets alder)
        prod_date_start = record.find('.//Production_date/production.date.start')
        prod_date_end = record.find('.//Production_date/production.date.end')
        
        if prod_date_start is not None and prod_date_start.text:
            start = prod_date_start.text.strip()
            if prod_date_end is not None and prod_date_end.text:
                end = prod_date_end.text.strip()
                if start != end:
                    return f"{start}-{end}"
            return start
        
        # Prøv at finde årstal i titlen (f.eks. "Scrapbog, 1954")
        title_elem = record.find('.//Title/title/value')
        if title_elem is not None and title_elem.text:
            import re
            # Søg efter 4-cifret årstal i titlen
            match = re.search(r'\b(1[0-9]{3}|20[0-9]{2})\b', title_elem.text)
            if match:
                return match.group(1)
        
        # Prøv event.date_from (fra Event sektion)
        event_date_from = record.find('.//Event/event.date_from')
        event_date_to = record.find('.//Event/event.date_to')
        
        if event_date_from is not None and event_date_from.text:
            date_from = event_date_from.text.strip()
            if event_date_to is not None and event_date_to.text:
                date_to = event_date_to.text.strip()
                if date_from != date_to:
                    return f"{date_from}-{date_to}"
            return date_from
        
        return 'Ukendt datering'
    
    def _extract_current_location(self, record) -> str:
        """
        Udtræk aktuel placering fra SARA record
        Viser fysisk placeringsnummer (f.eks. 09605, 09810)
        
        Args:
            record: XML record element
        
        Returns:
            Aktuel placering tekst
        """
        # Check først om objektet er udlånt
        loan_out_elem = record.find('.//Loan_out/loan.out.number')
        if loan_out_elem is not None and loan_out_elem.text:
            loan_number = loan_out_elem.text.strip()
            # Check status
            loan_status_elem = record.find('.//Loan_out/loan.out.status/value')
            if loan_status_elem is not None and loan_status_elem.text:
                status = loan_status_elem.text.strip()
                if 'APPROVED' in status or 'approved' in status:
                    return f"Udlånt (nr. {loan_number})"
            return f"Udlånt (lånenr. {loan_number})"
        
        # Prøv location.default.name (det primære placeringsnummer)
        location_name_elem = record.find('.//location.default.name')
        if location_name_elem is not None and location_name_elem.text and location_name_elem.text.strip():
            return location_name_elem.text.strip()
        
        # Prøv Object_location sektion
        obj_location_elem = record.find('.//Object_location/current.location')
        if obj_location_elem is not None and obj_location_elem.text and obj_location_elem.text.strip():
            return obj_location_elem.text.strip()
        
        # Prøv direkte current.location
        current_loc_elem = record.find('.//current.location')
        if current_loc_elem is not None and current_loc_elem.text and current_loc_elem.text.strip():
            return current_loc_elem.text.strip()
        
        # Prøv storage.location
        storage_elem = record.find('.//storage.location')
        if storage_elem is not None and storage_elem.text and storage_elem.text.strip():
            return storage_elem.text.strip()
        
        # Fallback: Vis institution og samling
        institution_elem = record.find('.//institution.name/value')
        collection_elem = record.find('.//collection/value')
        
        if institution_elem is not None and institution_elem.text:
            institution = institution_elem.text.strip()
            if collection_elem is not None and collection_elem.text:
                collection = collection_elem.text.strip()
                return f"{collection}, {institution}"
            return institution
        elif collection_elem is not None and collection_elem.text:
            return f"Samling: {collection_elem.text.strip()}"
        
        return 'Placering ikke registreret'
    
    def _extract_context(self, record) -> str:
        """
        Udtræk kontekst fra SARA record
        Viser location.default.context (f.eks. "09804/Trige 800/09810")
        
        Args:
            record: XML record element
        
        Returns:
            Kontekst tekst
        """
        # Prøv location.default.context (det primære kontekst felt)
        location_context_elem = record.find('.//location.default.context')
        if location_context_elem is not None and location_context_elem.text and location_context_elem.text.strip():
            return location_context_elem.text.strip()
        
        # Prøv case.description fra Museumcase (vigtigste kontekst info)
        case_desc_elem = record.find('.//Museumcase/case.description/value')
        if case_desc_elem is not None and case_desc_elem.text:
            return case_desc_elem.text.strip()
        
        # Alternativ case.description placering
        case_desc_elem = record.find('.//case.description')
        if case_desc_elem is not None and case_desc_elem.text:
            return case_desc_elem.text.strip()
        
        # Prøv case.title fra Museumcase
        case_title_elem = record.find('.//Museumcase/case.title')
        if case_title_elem is not None and case_title_elem.text:
            case_title = case_title_elem.text.strip()
            # Check også case.place hvis det findes
            case_place_elem = record.find('.//Museumcase/case.geo.place')
            if case_place_elem is not None and case_place_elem.text and case_place_elem.text.strip():
                return f"{case_title} - {case_place_elem.text.strip()}"
            return case_title
        
        # Prøv acquisition.place
        acq_place_elem = record.find('.//Acquisition/acquisition.place')
        if acq_place_elem is not None and acq_place_elem.text:
            return f"Erhvervet fra: {acq_place_elem.text.strip()}"
        
        # Prøv acquisition.reason
        acq_reason_elem = record.find('.//Acquisition/acquisition.reason')
        if acq_reason_elem is not None and acq_reason_elem.text:
            return acq_reason_elem.text.strip()
        
        return 'Ukendt kontekst'

    def _extract_title(self, record) -> str:
        """
        Udtræk titel fra SARA record (baseret på XML struktur vi fandt)
        
        Args:
            record: XML record element
        
        Returns:
            Titel tekst
        """
        # Baseret på debug output: title/value strukturen
        title_elems = record.findall('.//title')
        for title_elem in title_elems:
            value_elem = title_elem.find('.//value')
            if value_elem is not None and value_elem.text:
                return value_elem.text.strip()
        
        # Prøv også Title/title struktur
        title_containers = record.findall('.//Title')
        for title_container in title_containers:
            title_elem = title_container.find('.//title')
            if title_elem is not None:
                value_elem = title_elem.find('.//value')
                if value_elem is not None and value_elem.text:
                    return value_elem.text.strip()
        
        # Prøv TI feltet (som brugeren nævnte)
        ti_elem = record.find('.//TI')
        if ti_elem is not None and ti_elem.text:
            return ti_elem.text.strip()
        
        # Fallback til direkte title tekst
        title_elem = record.find('.//title')
        if title_elem is not None and title_elem.text:
            return title_elem.text.strip()
        
        return 'Uden titel'

    def _extract_description(self, record) -> str:
        """
        Udtræk fuld beskrivelse fra SARA record (baseret på JSON struktur)
        
        Args:
            record: XML record element
        
        Returns:
            Fuld beskrivelse tekst (ingen begrænsning)
        """
        descriptions = []
        
        # Hent hovedbeskrivelse fra Description felt
        desc_elems = record.findall('.//Description')
        for desc_elem in desc_elems:
            desc_text_elem = desc_elem.find('.//description')
            if desc_text_elem is not None and desc_text_elem.text:
                descriptions.append(desc_text_elem.text.strip())
        
        # Hent museumssag beskrivelse 
        case_elems = record.findall('.//Museumcase')
        for case_elem in case_elems:
            case_desc_elem = case_elem.find('.//case.description')
            if case_desc_elem is not None and case_desc_elem.text:
                case_desc = case_desc_elem.text.strip()
                if case_desc and case_desc not in descriptions:
                    descriptions.append(f"Museumssag: {case_desc}")
        
        # Hent materiale noter
        material_elems = record.findall('.//Material')
        for material_elem in material_elems:
            material_notes_elem = material_elem.find('.//material.notes')
            if material_notes_elem is not None and material_notes_elem.text:
                material_notes = material_notes_elem.text.strip()
                if material_notes:
                    descriptions.append(f"Materiale: {material_notes}")
        
        # Hent teknik noter
        technique_elems = record.findall('.//Technique')
        for technique_elem in technique_elems:
            technique_notes_elem = technique_elem.find('.//technique.notes')
            if technique_notes_elem is not None and technique_notes_elem.text:
                technique_notes = technique_notes_elem.text.strip()
                if technique_notes:
                    descriptions.append(f"Teknik: {technique_notes}")
        
        # Kombiner alle beskrivelser uden begrænsning
        full_description = "\n\n".join(descriptions) if descriptions else "Ingen beskrivelse tilgængelig"
        return full_description

    def _extract_images(self, record) -> List[str]:
        """
        Udtræk billede URLs fra SARA record med SARA API getcontent format
        Download billeder da AsyncImage ikke kan håndtere Basic Auth
        
        Args:
            record: XML record element
        
        Returns:
            Liste af lokale billedstier (downloadede med auth)
        """
        images = []
        
        # Find Reproduction elementer
        reproductions = record.findall('.//Reproduction')
        print(f"DEBUG _extract_images: Found {len(reproductions)} Reproduction elements")
        
        for idx, repro in enumerate(reproductions, 1):
            # Find reference og publish flag within samme reproduction
            ref_elem = repro.find('.//reproduction.reference')
            publish_elem = repro.find('.//reproduction.publish_on_website')
            
            if ref_elem is not None and ref_elem.text:
                filename = ref_elem.text.strip()
                print(f"DEBUG _extract_images: Reproduction #{idx}: filename='{filename}'")
                
                # Tjek om det er publiceret (default til True hvis ikke angivet)
                is_published = True
                if publish_elem is not None:
                    is_published = publish_elem.text == 'x'
                    print(f"DEBUG _extract_images: publish_on_website='{publish_elem.text}' -> is_published={is_published}")
                else:
                    print(f"DEBUG _extract_images: No publish_on_website element, defaulting to published")
                
                if is_published:
                    # SARA getcontent API URL format - download med auth
                    filename_lower = filename.lower()
                    if filename_lower.endswith('.jpg') or filename_lower.endswith('.jpeg') or filename_lower.endswith('.png'):
                        image_url = f"https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx?command=getcontent&server=images&value={filename}"
                        print(f"DEBUG _extract_images: Downloading from {image_url}")
                        # Download med authentication og returner lokal filsti
                        local_path = self.download_image_with_auth(image_url)
                        if local_path:
                            print(f"DEBUG _extract_images: SUCCESS - local path: {local_path}")
                            images.append(local_path)
                        else:
                            print(f"DEBUG _extract_images: FAILED to download")
                    else:
                        print(f"DEBUG _extract_images: Skipping (not jpg/jpeg/png): {filename}")
                else:
                    print(f"DEBUG _extract_images: Skipping (not published): {filename}")
            else:
                print(f"DEBUG _extract_images: Reproduction #{idx}: No filename found")
        
        print(f"DEBUG _extract_images: Total images downloaded: {len(images)}")
        return images
    
    def download_image_with_auth(self, image_url: str) -> Optional[str]:
        """
        Download billede med authentication og returner lokal filsti
        Android-sikker version med app data directory
        
        Args:
            image_url: URL til billede der skal downloades
        
        Returns:
            Lokal filsti til downloaded billede, eller None ved fejl
        """
        import os
        import hashlib
        from pathlib import Path
        from kivy.app import App
        
        try:
            # Log Android miljø info (kun første gang)
            if not hasattr(self, '_logged_environment'):
                android_logger.log_android_environment()
                self._logged_environment = True
            
            android_logger.log_image_download_start(image_url)
            
            # Brug appens sikre data directory (virker på Android)
            app_instance = App.get_running_app()
            if app_instance:
                base_dir = Path(app_instance.user_data_dir)
            else:
                # Fallback for test uden app
                base_dir = Path.cwd()
            
            cache_dir = base_dir / "temp_images"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            # Lav sikkert filnavn baseret på URL hash
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:12]
            filename_from_url = os.path.basename(image_url.split('value=')[1]) if 'value=' in image_url else 'image.jpg'
            
            # Sikker extension
            ext = Path(filename_from_url).suffix.lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                ext = '.jpg'
            
            safe_filename = f"{url_hash}{ext}"
            local_path = cache_dir / safe_filename
            
            # Tjek om vi allerede har downloaded det
            if local_path.exists() and local_path.stat().st_size > 0:
                android_logger.log_image_cache_hit(safe_filename)
                return str(local_path)
            
            # Android SSL/HTTPS Fix - Opret SSL context der accepterer alle certificater
            import ssl
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            android_logger.log_ssl_context_creation()
            
            # Lav request med authentication og Android-venlige headers
            request = urllib.request.Request(image_url)
            
            # Tilføj authentication header  
            auth_string = f"{self.username}:{self.password}"
            auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
            request.add_header("Authorization", f"Basic {auth_bytes.decode('ascii')}")
            
            # Android-venlige headers for at undgå mobile blocking
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "da,en;q=0.9",
                "Cache-Control": "no-cache"
            }
            
            for key, value in headers.items():
                request.add_header(key, value)
            
            android_logger.log_network_request(image_url, headers)
            
            # Download billedet med SSL context
            android_logger.log("DEBUG", f"Starter download med SSL context...")
            response = urllib.request.urlopen(request, timeout=15, context=ssl_context)
            image_data = response.read()
            
            # Gem til lokal fil med atomisk skrivning
            temp_path = local_path.with_suffix(local_path.suffix + '.part')
            with open(temp_path, 'wb') as f:
                f.write(image_data)
                f.flush()
                os.fsync(f.fileno())  # Sørg for at data er skrevet til disk
            
            # Atomisk rename når filen er færdig
            temp_path.replace(local_path)
            
            android_logger.log_image_download_success(image_url, len(image_data), str(local_path))
            
            # Returner absolut sti
            return str(local_path)
            
        except Exception as e:
            android_logger.log_image_download_error(image_url, str(e))
            return None
    
    def test_image_download_capability(self) -> bool:
        """
        Test billede download funktionalitet med public HTTPS billede
        
        Returns:
            True hvis download virker, False ellers
        """
        android_logger.log("INFO", "Tester billede download funktionalitet...")
        
        # Test URL - public billede der ikke kræver authentication  
        test_url = "https://httpbin.org/image/jpeg"
        
        try:
            import ssl
            import urllib.request
            
            # Samme SSL setup som normal download
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            request = urllib.request.Request(test_url)
            request.add_header("User-Agent", "Mozilla/5.0 (compatible; TestAgent)")
            
            android_logger.log("DEBUG", f"Tester download fra: {test_url}")
            response = urllib.request.urlopen(request, timeout=10, context=ssl_context)
            test_data = response.read()
            
            if len(test_data) > 1000:  # Minimum størrelse for et gyldigt billede
                android_logger.log("INFO", f"Test download succesfuld: {len(test_data)} bytes")
                return True
            else:
                android_logger.log("WARNING", f"Test download for lille: {len(test_data)} bytes")
                return False
                
        except Exception as e:
            android_logger.log("ERROR", f"Test download fejlede: {e}")
            return False
    
    def _extract_year(self, date_string: str) -> int:
        """
        Udtræk årstal fra dato string
        
        Args:
            date_string: Dato som string
        
        Returns:
            År som integer, eller 0 hvis ikke fundet
        """
        if not date_string:
            return 0
        
        # Søg efter 4-cifret årstal
        import re
        match = re.search(r'\b(\d{4})\b', date_string)
        if match:
            return int(match.group(1))
        
        return 0
    
    def search_by_object_number(self, object_number: str) -> Optional[Dict]:
        """
        Søg efter objekt ved objektnummer
        
        Args:
            object_number: Objektnummer
        
        Returns:
            Objekt data eller None
        """
        try:
            params = {
                'command': 'search',
                'database': 'collection',
                'search': f'object_number="{object_number}"',
                'output': 'xml',
                'limit': 1,
                'fields': ','.join(self.search_fields)
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            record = root.find('.//record')
            
            if record is not None:
                return self._parse_object_record(record, detailed=True)
            
            return None
            
        except Exception as e:
            print(f"Fejl ved søgning efter objektnummer {object_number}: {e}")
            return None
    
    def search_by_category(self, category: str, limit: int = 20) -> List[Dict]:
        """
        Søg efter objekter i en specifik kategori
        
        Args:
            category: Objektkategori
            limit: Maksimum antal resultater
        
        Returns:
            Liste af objekter
        """
        try:
            params = {
                'command': 'search',
                'database': 'collection',
                'search': f'object_category="{category}"',
                'output': 'xml',
                'limit': limit,
                'fields': ','.join(self.search_fields)
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            objects = []
            records = root.findall('.//record')
            
            for record in records:
                obj_data = self._parse_object_record(record)
                if obj_data:
                    objects.append(obj_data)
            
            return objects
            
        except Exception as e:
            print(f"Kategori søgning fejl: {e}")
            return []
    
    def extract_object_number(self, filename_or_input: str) -> str:
        """
        Udtræk objektnummer fra filnavn eller input (samme som sara_uploader.py)
        
        Args:
            filename_or_input: Filnavn eller input string
        
        Returns:
            Objektnummer hvis fundet, ellers tom string
        """
        import re
        import os
        
        # Fjern fil extension hvis det er et filnavn
        if '.' in filename_or_input and len(filename_or_input.split('.')[-1]) <= 4:
            stem = os.path.splitext(filename_or_input)[0]
        else:
            stem = filename_or_input
        
        # Understøt multiple formater (samme som sara_uploader.py):
        # 1. Traditional: 0054x0007, 1234X4321
        # 2. Genstands format: 00073;15, 12345;2015
        # 3. AAB format: AAB 1234
        # 4. Standalone: 1234
        
        patterns = [
            (r'(\d{4}[xX]\d{3,4})', 'traditional'),      # 1234x4321
            (r'(\d+;\d{2,4})', 'genstands'),             # 00073;15
            (r'AAB\s+(\d{4})', 'aab'),                   # AAB 1234
            (r'^(\d{4})$', 'standalone'),                # 1234 (only if entire string)
            (r'(\d+/\d+[xX]?\d*)', 'slash_format')       # 118/98x4, 123/456, 118/98
        ]
        
        for pattern, format_type in patterns:
            match = re.search(pattern, stem)
            if match:
                return match.group(1)
        
        return ""  # Intet gyldigt objektnummer fundet

    def test_connection(self) -> bool:
        """
        Test forbindelse til SARA API
        
        Returns:
            True hvis forbindelse virker
        """
        try:
            params = {
                'command': 'search',
                'database': 'collection',
                'search': 'all',
                'limit': 1,
                'output': 'xml',
                'fields': ','.join(self.search_fields)
            }
            
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"Forbindelsestest fejl: {e}")
            return False

# Test funktion
if __name__ == "__main__":
    api = SaraAPI()
    
    print("Tester SARA API forbindelse...")
    if api.test_connection():
        print("✓ SARA API forbindelse succesfuld")
        
        # Test søgning
        print("\nTester søgning efter 'fossil'...")
        results = api.search_objects("fossil", limit=3)
        print(f"Fandt {len(results)} objekter")
        
        if results:
            first_obj = results[0]
            print(f"Første resultat: {first_obj.get('title')} (ID: {first_obj.get('priref')})")
    else:
        print("❌ SARA API forbindelse fejlede")