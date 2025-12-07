"""
Jinja2 environment configuration for Django integration.
"""
from jinja2 import Environment, pass_context
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.template.defaultfilters import date, floatformat
from django.middleware.csrf import get_token
from django.utils.safestring import mark_safe
from urllib.parse import urlencode

from apps.users.templatetags.role_tags import register_filters


@pass_context
def csrf_input(context):
    """
    Generate CSRF token input for Jinja2 templates.
    Gets request from the template context.
    
    Usage in template:
        {{ csrf_input() }}
    """
    request = context.get('request')
    if request:
        token = get_token(request)
        return mark_safe(f'<input type="hidden" name="csrfmiddlewaretoken" value="{token}">')
    return mark_safe('')


@pass_context
def query_string(context):
    """
    Get query string from request.GET for Jinja2 templates.
    
    Usage in template:
        {{ query_string() }}
    """
    request = context.get('request')
    if request and request.GET:
        return urlencode(request.GET)
    return ''


def url_helper(name, *args, **kwargs):
    """
    Generate URL with optional parameters for Jinja2 templates.
    Handles both simple URLs and URLs with parameters.
    
    Usage in template:
        {{ url('dashboard') }}
        {{ url('testing:pipeline_step', test_id=test.id, step=1) }}
    """
    if kwargs:
        return reverse(name, kwargs=kwargs)
    elif args:
        return reverse(name, args=args)
    return reverse(name)


def environment(**options):
    """
    Create and configure Jinja2 environment with Django helpers.
    """
    env = Environment(**options)
    
    # Add Django URL reverse function
    env.globals.update({
        'static': staticfiles_storage.url,
        'url': url_helper,  # Use helper that handles kwargs
        'csrf_input': csrf_input,
        'query_string': query_string,
        'range': range,  # Add Python range function for Jinja2
    })
    
    # Add Django filters
    env.filters.update({
        'date': date,
        'floatformat': floatformat,
    })
    
    # Register custom role-based filters
    register_filters(env)
    
    return env
