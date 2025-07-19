import random

def colorizer(request):
    colors = ["#9C27B0", "#E91E63", "#673AB7", "#3F51B5", "#2196F3", "#009688", "#FF5722", "#795548", "#607D8B"]
    color = request.session.get('colorizer', None)

    if not color:
        color = random.choice(colors)
        request.session['colorizer'] = color

    return { 'colorizer': color }

def sidebar(request):
    return { 'sidebar_status': request.session.get('sidebar_status', False) }

def site_context(request):
    from reservations.utils import get_website_setting
    return { 
        'site_name': get_website_setting('SITE_NAME', ''),
        'site_domain': get_website_setting('SITE_DOMAIN', '')
    }
