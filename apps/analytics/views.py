"""
Analytics and reporting views.
"""
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Avg, Sum, F, FloatField, Case, When, IntegerField
from django.db.models.functions import TruncMonth, TruncDate, ExtractMonth, ExtractYear
from django_filters.views import FilterView
from datetime import datetime, timedelta
from collections import defaultdict
import json

from apps.users.decorators import admin_required
from apps.users.mixins import AdminRequiredMixin
from apps.testing.models import TestRequest, TestResult
from apps.products.models import ProductMaster, Supplier
from apps.quality.models import TestParameter, TestMethod
from apps.users.models import User
from .filters import TestRequestFilter, TestResultFilter
from services.export_service import generate_pdf_report, generate_csv_report


@admin_required
def analytics_dashboard(request):
    """
    Main analytics dashboard with comprehensive statistics and charts.
    """
    test_filter = TestRequestFilter(request.GET, queryset=TestRequest.objects.filter(is_active=True))
    result_filter = TestResultFilter(request.GET, queryset=TestResult.objects.filter(is_active=True))
    
    filtered_tests = test_filter.qs
    filtered_results = result_filter.qs
    
    # Basic Statistics
    total_tests = filtered_tests.count()
    passed_tests = filtered_results.filter(pass_fail_status=True).count()
    failed_tests = filtered_results.filter(pass_fail_status=False).count()
    pending_tests = filtered_results.filter(pass_fail_status__isnull=True).count()
    
    # Pass rate
    total_with_status = passed_tests + failed_tests
    pass_rate = (passed_tests / total_with_status * 100) if total_with_status > 0 else 0
    
    # 1. Status Distribution (Pie Chart)
    status_distribution = (
        filtered_tests.values('status')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    status_data = {
        'labels': [item['status'] for item in status_distribution],
        'counts': [item['count'] for item in status_distribution]
    }
    
    # 2. Tests Over Time (Line Chart - Last 12 months)
    twelve_months_ago = datetime.now() - timedelta(days=365)
    tests_over_time = (
        filtered_tests.filter(created_at__gte=twelve_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    time_data = {
        'labels': [item['month'].strftime('%b %Y') for item in tests_over_time],
        'counts': [item['count'] for item in tests_over_time]
    }
    
    # 3. Product Performance (Bar Chart - Top 10)
    product_performance = (
        ProductMaster.objects.filter(
            test_requests__in=filtered_tests,
            is_active=True
        )
        .annotate(
            total_tests=Count('test_requests', distinct=True),
            passed_results=Count('test_requests__results', filter=Q(test_requests__results__pass_fail_status=True), distinct=True),
            failed_results=Count('test_requests__results', filter=Q(test_requests__results__pass_fail_status=False), distinct=True)
        )
        .filter(total_tests__gt=0)
        .order_by('-total_tests')[:10]
    )
    product_data = {
        'labels': [p.name[:20] for p in product_performance],
        'total': [p.total_tests for p in product_performance],
        'passed': [p.passed_results for p in product_performance],
        'failed': [p.failed_results for p in product_performance]
    }
    
    # 4. Controller Performance (Bar Chart)
    controller_performance = (
        User.objects.filter(
            test_requests__in=filtered_tests,
            role='CONTROLLER',
            is_active=True
        )
        .annotate(
            total_tests=Count('test_requests', distinct=True),
            completed_tests=Count('test_requests', filter=Q(test_requests__status__in=['Completed', 'Approved']), distinct=True),
            submitted_tests=Count('test_requests', filter=Q(test_requests__status='Submitted for Review'), distinct=True)
        )
        .filter(total_tests__gt=0)
        .order_by('-total_tests')[:10]
    )
    controller_data = {
        'labels': [c.username for c in controller_performance],
        'total': [c.total_tests for c in controller_performance],
        'completed': [c.completed_tests for c in controller_performance],
        'submitted': [c.submitted_tests for c in controller_performance]
    }
    
    # 5. Parameter Pass/Fail Rates (Bar Chart)
    parameter_stats = (
        TestParameter.objects.filter(
            test_results__in=filtered_results,
            is_active=True
        )
        .annotate(
            total_tests=Count('test_results', distinct=True),
            passed=Count('test_results', filter=Q(test_results__pass_fail_status=True), distinct=True),
            failed=Count('test_results', filter=Q(test_results__pass_fail_status=False), distinct=True)
        )
        .filter(total_tests__gt=0)
        .order_by('-total_tests')[:10]
    )
    parameter_data = {
        'labels': [p.name[:20] for p in parameter_stats],
        'passed': [p.passed for p in parameter_stats],
        'failed': [p.failed for p in parameter_stats],
        'pass_rate': [
            round((p.passed / p.total_tests * 100) if p.total_tests > 0 else 0, 1)
            for p in parameter_stats
        ]
    }
    
    # 6. Monthly Trends (Line Chart - Last 6 months)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_trends = (
        filtered_tests.filter(created_at__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month', 'status')
        .annotate(count=Count('id'))
        .order_by('month', 'status')
    )
    
    # Organize by month and status
    trends_dict = defaultdict(lambda: {'Approved': 0, 'Completed': 0, 'Submitted for Review': 0, 'In-Progress': 0, 'Pending': 0, 'Rejected': 0})
    for item in monthly_trends:
        month_key = item['month'].strftime('%b %Y')
        trends_dict[month_key][item['status']] = item['count']
    
    sorted_months = sorted(trends_dict.keys())
    trends_data = {
        'labels': sorted_months,
        'approved': [trends_dict[m]['Approved'] for m in sorted_months],
        'completed': [trends_dict[m]['Completed'] for m in sorted_months],
        'submitted': [trends_dict[m]['Submitted for Review'] for m in sorted_months],
        'in_progress': [trends_dict[m]['In-Progress'] for m in sorted_months],
        'pending': [trends_dict[m]['Pending'] for m in sorted_months],
        'rejected': [trends_dict[m]['Rejected'] for m in sorted_months]
    }
    
    # 7. Supplier Performance (Bar Chart)
    supplier_performance = (
        Supplier.objects.filter(
            test_requests__in=filtered_tests,
            is_active=True
        )
        .annotate(
            total_tests=Count('test_requests', distinct=True),
            approved_tests=Count('test_requests', filter=Q(test_requests__status='Approved'), distinct=True)
        )
        .filter(total_tests__gt=0)
        .order_by('-total_tests')[:10]
    )
    supplier_data = {
        'labels': [s.name[:20] for s in supplier_performance],
        'total': [s.total_tests for s in supplier_performance],
        'approved': [s.approved_tests for s in supplier_performance],
        'approval_rate': [
            round((s.approved_tests / s.total_tests * 100) if s.total_tests > 0 else 0, 1)
            for s in supplier_performance
        ]
    }
    
    # 8. Test Method Usage (Pie Chart)
    # Get products from filtered tests, then get specifications for those products, then get test methods
    product_ids = list(filtered_tests.values_list('product_id', flat=True).distinct())
    if product_ids:
        method_usage = (
            TestMethod.objects.filter(
                specifications__product_id__in=product_ids,
                is_active=True
            )
            .annotate(usage_count=Count('specifications', distinct=True))
            .filter(usage_count__gt=0)
            .order_by('-usage_count')[:10]
        )
        method_data = {
            'labels': [m.code for m in method_usage],
            'counts': [m.usage_count for m in method_usage]
        }
    else:
        method_data = {'labels': [], 'counts': []}
    
    # 9. Daily Test Volume (Last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    daily_volume = (
        filtered_tests.filter(created_at__gte=thirty_days_ago)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    daily_data = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in daily_volume],
        'counts': [item['count'] for item in daily_volume]
    }
    
    # 10. Progress Distribution (Pie Chart) - Based on actual progress percentage
    # Calculate using the get_progress_percentage method logic
    progress_0_25 = sum(1 for t in filtered_tests if t.get_progress_percentage() <= 25)
    progress_26_50 = sum(1 for t in filtered_tests if 26 <= t.get_progress_percentage() <= 50)
    progress_51_75 = sum(1 for t in filtered_tests if 51 <= t.get_progress_percentage() <= 75)
    progress_76_100 = sum(1 for t in filtered_tests if t.get_progress_percentage() >= 76)
    
    progress_data = {
        'labels': [],
        'counts': []
    }
    if progress_0_25 > 0:
        progress_data['labels'].append('0-25%')
        progress_data['counts'].append(progress_0_25)
    if progress_26_50 > 0:
        progress_data['labels'].append('26-50%')
        progress_data['counts'].append(progress_26_50)
    if progress_51_75 > 0:
        progress_data['labels'].append('51-75%')
        progress_data['counts'].append(progress_51_75)
    if progress_76_100 > 0:
        progress_data['labels'].append('76-100%')
        progress_data['counts'].append(progress_76_100)
    
    context = {
        'test_filter': test_filter,
        'result_filter': result_filter,
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'pending_tests': pending_tests,
        'pass_rate': round(pass_rate, 2),
        'filtered_tests': filtered_tests[:20],
        # Chart data (JSON serialized)
        'status_data': json.dumps(status_data),
        'time_data': json.dumps(time_data),
        'product_data': json.dumps(product_data),
        'controller_data': json.dumps(controller_data),
        'parameter_data': json.dumps(parameter_data),
        'trends_data': json.dumps(trends_data),
        'supplier_data': json.dumps(supplier_data),
        'method_data': json.dumps(method_data),
        'daily_data': json.dumps(daily_data),
        'progress_data': json.dumps(progress_data),
    }
    
    return render(request, 'analytics/dashboard.html', context)


@admin_required
def export_pdf(request):
    """
    Export analytics report as PDF.
    """
    test_filter = TestRequestFilter(request.GET, queryset=TestRequest.objects.filter(is_active=True))
    result_filter = TestResultFilter(request.GET, queryset=TestResult.objects.filter(is_active=True))
    
    # Generate PDF
    pdf_buffer = generate_pdf_report(test_filter.qs, result_filter.qs, request.GET)
    
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="qms_report.pdf"'
    return response


@admin_required
def export_csv(request):
    """
    Export analytics report as CSV.
    """
    test_filter = TestRequestFilter(request.GET, queryset=TestRequest.objects.filter(is_active=True))
    result_filter = TestResultFilter(request.GET, queryset=TestResult.objects.filter(is_active=True))
    
    # Generate CSV
    csv_buffer = generate_csv_report(test_filter.qs, result_filter.qs)
    
    response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="qms_report.csv"'
    return response
