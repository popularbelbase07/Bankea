from django.urls import path
from . import views
from .views import AccountDetail, OneAccount, UserAPI, OneUserAPI,  CustomerAPI, OneCustomerAPI, RankAPI, OneRankAPI
app_name = 'bank_app'

urlpatterns = [
    path('', views.index, name='index'), 
    path('dashboard/', views.dashboard, name='dashboard'),
    # path('profile/', views.profile, name='),
    path('user_profile/<int:pk>/', views.user_profile, name='user_profile'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/new_customer/', views.new_customer, name='new_customer'),
    path('staff/search_partial/', views.search_partial, name='search_partial'),
    path('staff/customer_details/<int:pk>/', views.customer_details, name='customer_details'),
    path('staff/account_list_partial/<int:pk>/', views.account_list_partial, name='account_list_partial'),
    path('staff/staff_account_details/<int:pk>/', views.staff_account_details, name='staff_account_details'),
    path('staff/new_account_partial/<int:user>/', views.new_account_partial, name='new_account_partial'),
    
    path('customer_profile/<int:pk>/', views.customer_profile, name='customer_profile'),
    path('customer_account_details/<int:pk>/', views.customer_account_details, name='customer_account_details'),
    path('make_loan/', views.make_loan, name='make_loan'),
    path('make_transfer/', views.make_transfer, name='make_transfer'),

    path('transaction_details/<int:transaction>/',views.transaction_details, name='transaction_details'),
    path('make_external_transfer/', views.make_external_transfer, name='make_external_transfer'),
        # path('process_external_transfer/', views.process_external_transfer, name='process_external_transfer'),
    path('account/<int:pk>/', AccountDetail.as_view()),
    path('transfer_details/', views.transfer_details, name='transfer_details'),
    path('get_external_transfer_number/', views.get_external_transfer_number, name='get_external_transfer_number'),

    path('account/<int:pk>/', OneAccount.as_view()),
    path('account/', AccountDetail.as_view()),
    path('user/', UserAPI.as_view()),
    path('user/<int:pk>', OneUserAPI.as_view()),
    # path('deleteUser/<int:pk>', DeleteUser.as_view()),
    path('customer/<int:pk>', OneCustomerAPI.as_view()),
    path('customer/', CustomerAPI.as_view()),
    path('rank/', RankAPI.as_view()),
    path('rank/<int:pk>', OneRankAPI.as_view()),
    

]

