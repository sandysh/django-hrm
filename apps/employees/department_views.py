"""
Web views for department and designation management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Department, Designation


@login_required
def department_list(request):
    """List all departments (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    departments = Department.objects.all().order_by('name')
    
    # Search
    search = request.GET.get('search')
    if search:
        departments = departments.filter(name__icontains=search)
    
    context = {
        'departments': departments,
        'search_query': search,
    }
    
    return render(request, 'employees/department_list.html', context)


@login_required
def department_create(request):
    """Create new department (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            Department.objects.create(
                name=request.POST['name'],
                code=request.POST['code'],
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on',
            )
            messages.success(request, 'Department created successfully!')
            return redirect('department_list')
        except Exception as e:
            messages.error(request, f'Error creating department: {str(e)}')
    
    return render(request, 'employees/department_form.html', {'action': 'Create'})


@login_required
def department_edit(request, pk):
    """Edit department (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        try:
            department.name = request.POST['name']
            department.code = request.POST['code']
            department.description = request.POST.get('description', '')
            department.is_active = request.POST.get('is_active') == 'on'
            department.save()
            
            messages.success(request, 'Department updated successfully!')
            return redirect('department_list')
        except Exception as e:
            messages.error(request, f'Error updating department: {str(e)}')
    
    context = {
        'department': department,
        'action': 'Edit',
    }
    
    return render(request, 'employees/department_form.html', context)


@login_required
def department_delete(request, pk):
    """Delete department (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        name = department.name
        department.delete()
        messages.success(request, f'Department "{name}" deleted successfully!')
        return redirect('department_list')
    
    return render(request, 'employees/department_confirm_delete.html', {'department': department})


@login_required
def designation_list(request):
    """List all designations (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    designations = Designation.objects.select_related('department').all().order_by('name')
    
    # Search
    search = request.GET.get('search')
    if search:
        designations = designations.filter(name__icontains=search)
    
    context = {
        'designations': designations,
        'search_query': search,
    }
    
    return render(request, 'employees/designation_list.html', context)


@login_required
def designation_create(request):
    """Create new designation (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            Designation.objects.create(
                name=request.POST['name'],
                code=request.POST['code'],
                department_id=request.POST.get('department') if request.POST.get('department') else None,
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on',
            )
            messages.success(request, 'Designation created successfully!')
            return redirect('designation_list')
        except Exception as e:
            messages.error(request, f'Error creating designation: {str(e)}')
    
    context = {
        'action': 'Create',
        'departments': departments,
    }
    
    return render(request, 'employees/designation_form.html', context)


@login_required
def designation_edit(request, pk):
    """Edit designation (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    designation = get_object_or_404(Designation, pk=pk)
    departments = Department.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            designation.name = request.POST['name']
            designation.code = request.POST['code']
            designation.department_id = request.POST.get('department') if request.POST.get('department') else None
            designation.description = request.POST.get('description', '')
            designation.is_active = request.POST.get('is_active') == 'on'
            designation.save()
            
            messages.success(request, 'Designation updated successfully!')
            return redirect('designation_list')
        except Exception as e:
            messages.error(request, f'Error updating designation: {str(e)}')
    
    context = {
        'designation': designation,
        'action': 'Edit',
        'departments': departments,
    }
    
    return render(request, 'employees/designation_form.html', context)


@login_required
def designation_delete(request, pk):
    """Delete designation (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    designation = get_object_or_404(Designation, pk=pk)
    
    if request.method == 'POST':
        name = designation.name
        designation.delete()
        messages.success(request, f'Designation "{name}" deleted successfully!')
        return redirect('designation_list')
    
    return render(request, 'employees/designation_confirm_delete.html', {'designation': designation})
