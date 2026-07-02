from models import Document

def remove_duplicate_entities(document : Document) -> Document:
    unique = {}
    
    for entity in document.entities:
        key = (entity.category, entity.value, entity.start, entity.end)

        unique[key] = entity

    document.entities = list(unique.values())

    return document