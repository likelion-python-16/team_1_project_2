from django.urls import path
from . import views

urlpatterns = [
    path('', views.paymentCheckout),
    path('payment/checkout', views.paymentCheckout),
    path('payment/success', views.paymentSuccess),
    
    path('payment/billing', views.paymentBilling),
    path('issue-billing-key', views.issueBillingKey),
    path('confirm-billing', views.confirm_billing),

    path('fail', views.fail),
]

