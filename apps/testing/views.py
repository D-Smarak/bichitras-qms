"""
Testing pipeline views for the QMS application.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.db import transaction
from typing import Dict, Any

from apps.users.decorators import controller_required
from apps.users.mixins import ControllerRequiredMixin, RoleRequiredMixin
from .models import TestRequest, TestResult
from .forms import TestRequestForm, TestParameterSelectionForm, TestResultForm, TestReviewForm
from apps.products.models import ProductMaster
from apps.quality.models import ProductSpecification


@controller_required
def pipeline_start(request):
    """
    Step 1: Initialize new test request - Sample Registration.
    """
    if request.method == 'POST':
        form = TestRequestForm(request.POST)
        if form.is_valid():
            test_request = form.save(commit=False)
            test_request.controller_user = request.user
            test_request.status = 'Pending'
            test_request.current_step = 1
            test_request.save()
            messages.success(request, 'Test request created. Proceed to step 2.')
            return redirect('testing:pipeline_step', test_id=test_request.id, step=2)
    else:
        form = TestRequestForm()
    
    return render(request, 'testing/pipeline_step_1.html', {'form': form})


@controller_required
def pipeline_step(request, test_id, step):
    """
    Handle steps 2-4 of the testing pipeline.
    """
    test_request = get_object_or_404(TestRequest, id=test_id, is_active=True)
    
    # Verify user owns this test or is admin
    if test_request.controller_user != request.user and not request.user.is_admin():
        messages.error(request, 'You do not have permission to access this test.')
        return redirect('testing:list')
    
    # Step 2: Test Parameters Selection
    if step == 2:
        if request.method == 'POST':
            form = TestParameterSelectionForm(request.POST, test_request=test_request)
            if form.is_valid():
                selected_params = form.cleaned_data.get('parameters')
                # Store selected parameters in session or advance to next step
                request.session[f'test_{test_id}_params'] = [str(p.id) for p in selected_params]
                test_request.current_step = 2
                test_request.status = 'In-Progress'
                test_request.save()
                messages.success(request, 'Parameters selected. Proceed to step 3.')
                return redirect('testing:pipeline_step', test_id=test_id, step=3)
        else:
            # Get available specifications for this product
            specifications = ProductSpecification.objects.filter(
                product=test_request.product,
                is_active=True
            ).select_related('parameter')
            form = TestParameterSelectionForm(test_request=test_request)
        
        return render(request, 'testing/pipeline_step_2.html', {
            'test_request': test_request,
            'form': form,
            'specifications': specifications,
        })
    
    # Step 3: Results Entry
    elif step == 3:
        # Get selected parameters from session
        param_ids = request.session.get(f'test_{test_id}_params', [])
        if not param_ids:
            messages.error(request, 'Please select parameters first.')
            return redirect('testing:pipeline_step', test_id=test_id, step=2)
        
        from apps.quality.models import TestParameter
        parameters = TestParameter.objects.filter(id__in=param_ids, is_active=True)
        
        if request.method == 'POST':
            # Process results for each parameter
            with transaction.atomic():
                for param in parameters:
                    value_key = f'value_{param.id}'
                    if value_key in request.POST:
                        actual_value = request.POST[value_key]
                        result, created = TestResult.objects.get_or_create(
                            test_request=test_request,
                            parameter=param,
                            defaults={
                                'actual_value': actual_value,
                                'tested_by': request.user,
                            }
                        )
                        if not created:
                            result.actual_value = actual_value
                            result.tested_by = request.user
                            result.save()
                        # Calculate pass/fail
                        result.calculate_pass_fail()
                
                test_request.current_step = 3
                test_request.save()
                messages.success(request, 'Results entered. Proceed to review.')
                return redirect('testing:pipeline_step', test_id=test_id, step=4)
        
        # Get existing results
        existing_results = {
            r.parameter_id: r.actual_value 
            for r in TestResult.objects.filter(
                test_request=test_request,
                parameter__in=parameters
            )
        }
        
        return render(request, 'testing/pipeline_step_3.html', {
            'test_request': test_request,
            'parameters': parameters,
            'existing_results': existing_results,
        })
    
    # Step 4: Review & Submit
    elif step == 4:
        results = TestResult.objects.filter(
            test_request=test_request
        ).select_related('parameter')
        
        if request.method == 'POST':
            form = TestReviewForm(request.POST)
            if form.is_valid():
                action = form.cleaned_data.get('action')
                if action == 'submit':
                    # Submit for Review: 75% complete
                    test_request.current_step = 4
                    test_request.status = 'Submitted for Review'
                    test_request.save()
                    messages.success(request, 'Test request submitted for review. Progress: 75%')
                    return redirect('testing:detail', test_id=test_id)
                elif action == 'approve':
                    # Controller approves: 100% complete
                    test_request.current_step = 4
                    test_request.status = 'Approved'
                    test_request.save()
                    messages.success(request, 'Test request approved. Progress: 100%')
                    return redirect('testing:detail', test_id=test_id)
                elif action == 'reject':
                    test_request.status = 'Rejected'
                    test_request.save()
                    messages.warning(request, 'Test request rejected.')
                    return redirect('testing:detail', test_id=test_id)
        else:
            form = TestReviewForm()
        
        return render(request, 'testing/pipeline_step_4.html', {
            'test_request': test_request,
            'results': results,
            'form': form,
        })
    
    else:
        messages.error(request, 'Invalid step.')
        return redirect('testing:list')


class TestRequestListView(RoleRequiredMixin, ListView):
    """
    List view for test requests.
    
    Business Logic:
    - Admin sees all tests from all controllers
    - Controller sees only their own tests
    """
    model = TestRequest
    template_name = 'testing/test_list.html'
    context_object_name = 'test_requests'
    paginate_by = 20
    required_roles = ['ADMIN', 'CONTROLLER']
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return TestRequest.objects.filter(is_active=True).order_by('-created_at')
        return TestRequest.objects.filter(
            controller_user=self.request.user,
            is_active=True
        ).order_by('-created_at')


class TestRequestDetailView(RoleRequiredMixin, DetailView):
    """
    Detail view for a test request.
    
    Business Logic:
    - Admin can view all tests and approve submitted tests
    - Controller can view only their own tests
    """
    model = TestRequest
    template_name = 'testing/test_detail.html'
    context_object_name = 'test_request'
    pk_url_kwarg = 'test_id'
    required_roles = ['ADMIN', 'CONTROLLER']
    
    def get_queryset(self):
        if self.request.user.is_admin():
            return TestRequest.objects.filter(is_active=True)
        return TestRequest.objects.filter(
            controller_user=self.request.user,
            is_active=True
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['results'] = TestResult.objects.filter(
            test_request=self.object
        ).select_related('parameter')
        # Admin can approve tests submitted for review
        context['can_approve'] = (
            self.request.user.is_admin() and 
            self.object.status == 'Submitted for Review'
        )
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Handle admin approval of submitted tests.
        """
        self.object = self.get_object()
        
        # Only admin can approve submitted tests
        if not request.user.is_admin():
            messages.error(request, 'Only admins can approve tests.')
            return redirect('testing:detail', test_id=self.object.id)
        
        if self.object.status == 'Submitted for Review':
            action = request.POST.get('action')
            if action == 'approve':
                self.object.status = 'Approved'
                self.object.save()
                messages.success(request, 'Test request approved. Progress: 100%')
            elif action == 'reject':
                self.object.status = 'Rejected'
                self.object.save()
                messages.warning(request, 'Test request rejected.')
            else:
                messages.error(request, 'Invalid action.')
        
        return redirect('testing:detail', test_id=self.object.id)
