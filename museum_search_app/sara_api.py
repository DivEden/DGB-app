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


class SaraAPI:
    """Interface til SARA database API"""
    
    def __init__(self):
        # SARA API konfiguration (fra sara_uploader.py)
        self.base_url = "https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx"
        self.username = r"adlibhosting\DGB-API-USER"
        self.password = "YxUyuzNLubfNKbx2"
        self.auth = HTTPBasicAuth(self.username, self.password)
    
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
                'limit': limit
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                auth=self.auth,
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
        # Prøv først at søge som objektnummer
        if query.strip():
            # Check om det ligner et objektnummer format
            import re
            object_number_patterns = [
                r'\d{4}[xX]\d{3,4}',     # 1234x4321
                r'\d+;\d{2,4}',          # 00073;15
                r'AAB\s+\d{4}',          # AAB 1234
                r'^\d{4}$'               # 1234
            ]
            
            for pattern in object_number_patterns:
                if re.search(pattern, query):
                    return self.search_objects_by_number(query, limit)
            
            # Hvis ikke objektnummer format, søg i alle felter
            try:
                params = {
                    'command': 'search',
                    'database': 'collection',
                    'search': f'all="{query}"',
                    'output': 'xml',
                    'limit': limit
                }
                
                response = requests.get(
                    self.base_url,
                    params=params,
                    auth=self.auth,
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
                'limit': 1
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                auth=self.auth,
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
        }
        
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
        
        Args:
            record: XML record element
        
        Returns:
            Liste af billede URLs
        """
        images = []
        
        # Find Reproduction elementer
        reproductions = record.findall('.//Reproduction')
        
        for repro in reproductions:
            # Find reference og publish flag within samme reproduction
            ref_elem = repro.find('.//reproduction.reference')
            publish_elem = repro.find('.//reproduction.publish_on_website')
            
            if ref_elem is not None and ref_elem.text:
                filename = ref_elem.text.strip()
                
                # Tjek om det er publiceret (default til True hvis ikke angivet)
                is_published = True
                if publish_elem is not None:
                    is_published = publish_elem.text == 'x'
                
                if is_published:
                    # SARA getcontent API URL format (baseret på brugerens link)
                    # https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx?command=getcontent&server=images&value=1568771.jpg
                    if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png'):
                        image_url = f"https://sara-api.adlibhosting.com/SARA-011-DGB/wwwopac.ashx?command=getcontent&server=images&value={filename}"
                        # Download med authentication og returner lokal filsti
                        local_path = self.download_image_with_auth(image_url)
                        if local_path:
                            images.append(local_path)
        
        return images
    
    def download_image_with_auth(self, image_url: str) -> Optional[str]:
        """
        Download billede med authentication og returner lokal filsti
        
        Args:
            image_url: URL til billede der skal downloades
        
        Returns:
            Lokal filsti til downloaded billede, eller None ved fejl
        """
        import os
        import tempfile
        import hashlib
        
        try:
            # Lav et unikt filnavn baseret på URL
            url_hash = hashlib.md5(image_url.encode()).hexdigest()[:8]
            filename_from_url = os.path.basename(image_url.split('value=')[1]) if 'value=' in image_url else 'image.jpg'
            safe_filename = f"{url_hash}_{filename_from_url}"
            
            # Temp mappe
            temp_dir = tempfile.gettempdir()
            local_path = os.path.join(temp_dir, safe_filename)
            
            # Tjek om vi allerede har downloaded det
            if os.path.exists(local_path):
                return local_path
            
            # Lav request med authentication
            request = urllib.request.Request(image_url)
            
            # Tilføj authentication header  
            auth_string = f"{self.username}:{self.password}"
            auth_bytes = base64.b64encode(auth_string.encode('utf-8'))
            request.add_header("Authorization", f"Basic {auth_bytes.decode('ascii')}")
            
            # Download billedet
            response = urllib.request.urlopen(request)
            image_data = response.read()
            
            # Gem til lokal fil
            with open(local_path, 'wb') as f:
                f.write(image_data)
            
            print(f"Downloaded image: {safe_filename}")
            return local_path
            
        except Exception as e:
            print(f"Fejl ved download af billede {image_url}: {e}")
            return None
    
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
                'limit': 1
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                auth=self.auth,
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
                'limit': limit
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                auth=self.auth,
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
            (r'^(\d{4})$', 'standalone')                 # 1234 (only if entire string)
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
                'output': 'xml'
            }
            
            response = requests.get(
                self.base_url,
                params=params,
                auth=self.auth,
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