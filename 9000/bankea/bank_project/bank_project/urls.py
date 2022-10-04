"""bank_project URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from bank_app import urls
from two_factor.urls import urlpatterns as tf_urls
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )



urlpatterns = [
    path('admin/', admin.site.urls),
    #2fa url. Needs to be above accounts
    path('', include(tf_urls)),
    path('', include('bank_app.urls', namespace='bank_app')),
    # path('api/v1/', include('bank_app.urls', namespace='bank_app')),
    path('accounts/', include('django.contrib.auth.urls')),
    # path('', include('bank_app.urls', namespace='bank_app')),
    path('api-auth/', include('rest_framework.urls')),
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

