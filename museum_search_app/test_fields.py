#!/usr/bin/env python3
"""Test script to check new fields"""

from sara_api import SaraAPI

api = SaraAPI()

# Test object with many fields
result = api.search_objects_by_number('0054x0007', 1)

if result:
    obj = result[0]
    print("=== Testing new fields for 0054x0007 ===")
    
    new_fields = [
        ('location_name', 'Placering (navn)'),
        ('location_context', 'Placering (kontekst)'),
        ('acquisition_number', 'Accession nr.'),
        ('acquisition_source', 'Giver'),
        ('acquisition_reason', 'Begrundelse'),
        ('acquisition_date', 'Erhvervelsesdato'),
        ('event_type', 'Proveniens-type'),
        ('event_name', 'Proveniens-betegnelse'),
        ('event_description', 'Proveniens-beskrivelse'),
        ('craftsman', 'Ophavsmand')
    ]
    
    for field_key, field_name in new_fields:
        value = obj.get(field_key, '')
        if value:
            print(f"{field_name}: {value}")
        else:
            print(f"{field_name}: [EMPTY]")
    
    print(f"\nImages: {len(obj.get('images', []))}")
else:
    print("No results found")