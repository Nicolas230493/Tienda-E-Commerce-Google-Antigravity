from django.urls import reverse

def impulso_admin_context(request):
    """
    Inyecta el Dashboard como una 'App Virtual' en el contexto del admin.
    """
    if request.path.startswith('/admin/'):
        return {
            'impulso_dashboard_url': reverse('catalog:dashboard_products'),
            'show_impulso_link': True
        }
    return {}
