"""
Main project views.
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q

from apps.products.models import ProductMaster
from apps.testing.models import TestRequest


@login_required
def dashboard(request):
    """
    Unified dashboard view with permission-based sections.
    
    Business Logic:
    - Admin sees all tests from all controllers
    - Controller sees only their own tests
    """
    # Base queryset - admin sees all, controller sees own
    if request.user.is_admin():
        test_queryset = TestRequest.objects.filter(is_active=True)
    else:
        test_queryset = TestRequest.objects.filter(
            controller_user=request.user,
            is_active=True
        )
    
    context = {
        'total_products': ProductMaster.objects.filter(is_active=True).count(),
        'pending_tests': test_queryset.filter(status='Pending').count(),
        'submitted_tests': test_queryset.filter(status='Submitted for Review').count(),
        'completed_tests': test_queryset.filter(
            status__in=['Completed', 'Approved']
        ).count(),
    }
    
    # Get recent tests
    context['recent_tests'] = test_queryset.order_by('-created_at')[:10]
    
    # For admin: show tests submitted for review
    if request.user.is_admin():
        context['submitted_for_review'] = TestRequest.objects.filter(
            status='Submitted for Review',
            is_active=True
        ).order_by('-created_at')[:5]
    
    return render(request, 'dashboard.html', context)

