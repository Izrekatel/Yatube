from django.shortcuts import render
from rest_framework.schemas.openapi import SchemaGenerator


def schema(request):
    """Функция, позволяющия генерировать схему доступных эндпоинтов."""
    generator = SchemaGenerator(title='Yatube API')
    getted_schema = generator.get_schema() or {
        'info': {'title': 'Yatube API'}, 'paths': {}
    }
    schema = {
        'title': getted_schema['info']['title'],
        'endpoints': []
    }
    for path in getted_schema['paths']:
        for method in getted_schema['paths'][path].keys():
            schema['endpoints'].append({'path': path, 'method': method})

    return render(request, 'schema.html', {'schema': schema})
