from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import *
from django.db.models import Sum
import json
from datetime import datetime
from decimal import Decimal
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import io


# Create your views here.

def indexView(request):
    return render(request, 'index.html')
def registerView(request):
    if request.method=='POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "User Name already exists. Try using different User Name")
            return redirect('register')
        
        user=User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.save()

        messages.success(request, "Account created Successfully")

        return redirect('login')
    
    return render(request, 'registerUser.html')

def loginView(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user= authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')
        
    return render(request, 'loginUser.html')



@login_required
def logoutView(request):
    logout(request)
    return redirect('login')

@login_required
def userDashboardView(request):

    selectedMonth=request.GET.get('month')
    budget=None
    warning=None
    remaining=None

    incomes=Income.objects.filter(user=request.user)
    expenses=Expense.objects.filter(user=request.user)

    if selectedMonth:
        incomes=incomes.filter(date__month=selectedMonth)
        expenses=expenses.filter(date__month=selectedMonth)

    totalIncome=incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    totalExpense=expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    balance=totalIncome-totalExpense

    categoryData=(
        expenses.values('category')
        .annotate(total=Sum('amount'))
    )

    categories=[item['category'] for item in categoryData]
    amounts=[float(item['total']) for item in categoryData]

    recentIncomes=incomes.order_by('-date')[:5]
    recentExpenses=expenses.order_by('-date')[:5]

    try:
        budget=Budget.objects.get(user=request.user)
        remaining=budget.monthlyLimit-totalExpense

        if totalExpense>budget.monthlyLimit:
            warning="You have exceeded your monthly budget"
        elif remaining<= (budget.monthlyLimit*Decimal('0.2')):
            warning="You are close to Budget Limit"
    except Budget.DoesNotExist:
        budget=None


    context={
        'totalIncome':totalIncome,
        'totalExpense':totalExpense,
        'balance':balance,
        'recentIncomes':recentIncomes,
        'recentExpenses':recentExpenses,
        'categories':json.dumps(categories),    
        'amounts':json.dumps(amounts),
        'selectedMonth': selectedMonth,
        'budget':budget,
        'warning':warning,
        'remaining':remaining,
    }
    return render(request,'userDashboard.html', context)

@login_required
def addIncomeView(request):
    if request.method=='POST':
        amount=request.POST.get('amount')
        source=request.POST.get('source')
        date=request.POST.get('date')

        if not amount or not source or not date:
            messages.error(request, "All fields are required")
            return redirect('addIncome')

        Income.objects.create(
            user=request.user,
            amount=amount,
            source=source, 
            date=date
        )

        return redirect('dashboard')
    
    return render(request, 'addIncome.html')

def addExpenseView(request):
    if request.method == "POST":
        amount = request.POST.get('amount')
        category = request.POST.get('category')
        description = request.POST.get('description')
        date = request.POST.get('date')

        if not amount or not category or not date:
            messages.error(request, "All fields are required")
            return redirect('addIncome')

        Expense.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            description=description,
            date=date
        )

        return redirect('dashboard')

    return render(request, 'addExpense.html')

def setBudgetView(request):
    budget, created =Budget.objects.get_or_create(user=request.user, defaults={'monthlyLimit': 0})

    if request.method=="POST":
        limit=request.POST.get('monthlyLimit')
        budget.monthlyLimit=limit
        budget.save()

        return redirect('dashboard')
    
    return render(request, 'setBudget.html', {'budget': budget})

def editIncome(request, id):
    income=get_object_or_404(Income, id=id, user=request.user)

    if request.method=='POST':
        income.amount=request.POST.get('amount')
        income.source=request.POST.get('source')
        income.date=request.POST.get('date')
        income.save()

        return redirect('dashboard')
    
    return render(request, 'editIncome.html', {'income': income})

def deleteIncome(request, id):
    income=get_object_or_404(Income, user=request.user, id=id)
    income.delete()

    return redirect('dashboard')

def editExpense(request, id):
    expense=get_object_or_404(Expense, id=id, user=request.user)

    if request.method=='POST':
        expense.amount=request.POST.get('amount')
        expense.category=request.POST.get('category')
        expense.description=request.POST.get('description')
        expense.date=request.POST.get('date')
        expense.save()

        return redirect('dashboard')
    
    return render(request, 'editExpense.html', {'expense': expense})

def deleteExpense(request, id):
    expense=get_object_or_404(Expense, user=request.user, id=id)
    expense.delete()

    return redirect('dashboard')


@login_required
def download_pdf_report(request):

    incomes = Income.objects.filter(user=request.user)
    expenses = Expense.objects.filter(user=request.user)

    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    category_data = (
        expenses.values('category')
        .annotate(total=Sum('amount'))
    )

    # Create chart
    categories = [item['category'] for item in category_data]
    amounts = [float(item['total']) for item in category_data]

    plt.figure(figsize=(5,5))
    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title("Expense Distribution")

    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png')
    chart_buffer.seek(0)
    plt.close()

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expense_report.pdf"'

    pdf = SimpleDocTemplate(response, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Monthly Expense Report", styles['Title']))
    elements.append(Spacer(1,20))

    elements.append(Paragraph(f"Total Income: ₹{total_income}", styles['Normal']))
    elements.append(Paragraph(f"Total Expense: ₹{total_expense}", styles['Normal']))
    elements.append(Paragraph(f"Balance: ₹{balance}", styles['Normal']))

    elements.append(Spacer(1,20))

    elements.append(Paragraph("Expense Distribution", styles['Heading2']))
    elements.append(Image(chart_buffer, 4*inch, 4*inch))

    elements.append(Spacer(1,20))

    data = [["Type","Category/Source","Amount","Date"]]

    for income in incomes:
        data.append(["Income", income.source, income.amount, str(income.date)])

    for expense in expenses:
        data.append(["Expense", expense.category, expense.amount, str(expense.date)])

    table = Table(data)
    elements.append(table)

    pdf.build(elements)

    return response