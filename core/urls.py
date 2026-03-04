from django.urls import path
from .views import *


urlpatterns=[
    path('', indexView, name='index'),
    path('user/register/', registerView, name='register'),
    path('user/login/', loginView, name='login'),
    path('user/logout/', logoutView, name='logout'),
    path('user/dashboard', userDashboardView, name='dashboard'),
    path('user/add-Income/', addIncomeView, name='addIncome'),
    path('user/add-Expense/', addExpenseView, name='addExpense'),
    path('user/set-Budget/', setBudgetView, name='setBudget'),
    path('user/income/edit/<int:id>/' ,editIncome, name='editIncome'),
    path('user/income/delete/<int:id>/' ,deleteIncome, name='deleteIncome'),
    path('user/expense/edit/<int:id>/' ,editExpense, name='editExpense'),
    path('user/expense/delete/<int:id>/' ,deleteExpense, name='deleteExpense'),
    path('download-pdf/', download_pdf_report, name='download_pdf'),
]