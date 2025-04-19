from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense
from .forms import ExpenseForm, RegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages  # Import messages module
from collections import defaultdict
import json

def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Registration successful! You can now log in.')  # Success message
        return redirect('login')
    return render(request, 'tracker/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            messages.success(request, 'Login successful!')  # Success message
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')  # Error message
    return render(request, 'tracker/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have logged out successfully.')  # Success message
    return redirect('login')

@login_required
def dashboard(request):
    section = request.GET.get('section', 'dashboard')  # default section
    expenses = Expense.objects.filter(user=request.user)
    total = sum(exp.amount for exp in expenses)

    form = ExpenseForm()
    edit_form = None
    edit_id = request.GET.get('edit_id')

    # Chart data
    category_data = defaultdict(float)
    for exp in expenses:
        category_data[exp.category] += float(exp.amount)

    categories = list(category_data.keys())
    amounts = list(category_data.values())

    # If editing
    if section == 'edit' and edit_id:
        expense = get_object_or_404(Expense, id=edit_id, user=request.user)
        edit_form = ExpenseForm(instance=expense)

    context = {
        'section': section,
        'form': form,
        'edit_form': edit_form,
        'edit_id': edit_id,
        'expenses': expenses,
        'total': total,
        'categories': json.dumps(categories),
        'amounts': json.dumps(amounts),
    }

    return render(request, 'tracker/dashboard.html', context)

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('/dashboard?section=dashboard')
        else:
            print(form.errors)  # 👈 Add this line to see the problem in the terminal
            messages.error(request, 'There was an error in the form.')
    return redirect('/dashboard?section=dashboard')





@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully!')  # Success message
    return redirect('/dashboard?section=dashboard')

@login_required
def delete_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully!')  # Success message
    return redirect('/dashboard?section=dashboard')
