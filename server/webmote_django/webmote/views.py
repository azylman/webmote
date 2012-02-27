from django.shortcuts import render_to_response
from django.template import RequestContext as RC

def home( request ):
    return render_to_response(
        'index.html',
        {},
        context_instance = RC( request, {} ),
    )
