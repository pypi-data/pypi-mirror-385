"""
PACT v0.1 Constants - Single Source of Truth
All PACT terminology defined here, imported everywhere else.
Eliminates redundancy and ensures consistent terminology.
"""

# PACT v0.1 Canonical Node Types (updated from v0.0)
# Old: {'mt', 'mc', 'cb'} -> New: {'seg', 'cont', 'block'}
CANONICAL_TYPES = {'seg', 'cont', 'block'}

# Map egregore component types to PACT canonical types
# Used by metadata.ensure_id() and component validation
CANONICAL_TYPE_MAPPING = {
    # Segments (seg) - structural containers for turns
    'context_root': 'seg',
    'system_header': 'seg', 
    'conversation_history': 'seg',
    'active_message': 'seg',
    'message_turn': 'seg',
    'client_message': 'seg',
    'provider_message': 'seg',
    'active_provider_message': 'seg',
    
    # Containers (cont) - core message containers at offset=0
    'message_container': 'cont',
    
    # Blocks (block) - leaf content nodes
    'text_content': 'block',
    'image_content': 'block',
    'audio_content': 'block',
    'video_content': 'block',
    'document_content': 'block',
    'tool_result': 'block',
    'scaffold_result': 'block'
}

# Reverse mapping for selector engine: PACT types -> egregore component types
# Used by selector engine to match .seg, .cont, .block queries
SELECTOR_TYPE_MAPPING = {
    'seg': ['message_turn', 'client_message', 'provider_message', 'active_message'],
    'cont': ['message_container'], 
    'block': [
        'text_content', 'image_content', 'audio_content', 'video_content', 
        'document_content', 'tool_result', 'scaffold_result'
    ]
}

# PACT v0.1.0: Only ergonomic shorthands (legacy aliases removed)
LEGACY_TYPE_ALIASES = {
    # Ergonomic shorthands only
    'b': 'block',  # Accept .b as shorthand, normalize to .block
    'c': 'cont'    # Accept .c as shorthand, normalize to .cont
}

# Additional attribute aliases
ATTRIBUTE_ALIASES = {
    'cad': 'cadence'  # Accept cad shorthand, normalize to cadence canonical
}

def normalize_type_alias(input_type: str) -> str:
    """Normalize input type aliases to canonical PACT types."""
    return LEGACY_TYPE_ALIASES.get(input_type, input_type)

# Validation helper: ensure all component types are mapped
def validate_type_mappings():
    """Validate that all mappings are consistent"""
    # Check that all CANONICAL_TYPE_MAPPING values are in CANONICAL_TYPES
    for component_type, canonical_type in CANONICAL_TYPE_MAPPING.items():
        if canonical_type not in CANONICAL_TYPES:
            raise ValueError(f"Invalid canonical type '{canonical_type}' for component '{component_type}'")
    
    # Check that all SELECTOR_TYPE_MAPPING keys are in CANONICAL_TYPES
    for canonical_type in SELECTOR_TYPE_MAPPING.keys():
        if canonical_type not in CANONICAL_TYPES:
            raise ValueError(f"Invalid canonical type '{canonical_type}' in selector mapping")
    
    return True

# PACT Export Mappings (for PACT Node Foundation implementation)
# Maps egregore component types directly to PACT canonical types
EGREGORE_TO_PACT_MAPPING = CANONICAL_TYPE_MAPPING  # Reuse existing mapping

# Reverse mapping for PACT import and selector engine
PACT_TO_EGREGORE_MAPPING = SELECTOR_TYPE_MAPPING  # Reuse existing mapping

# Run validation on import
validate_type_mappings()