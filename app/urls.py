

from django.urls import path,include
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from drf_yasg import openapi
from .views import UserViewSet, StockViewSet, TransactionViewSet

router = DefaultRouter()
router.register('users',UserViewSet,basename='users')
router.register('stocks',StockViewSet,basename='stocks')
router.register('transactions',TransactionViewSet,basename='transactions')

# Swagger schema view
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v1',
        description="API documentation for my app",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(AllowAny,),
)


urlpatterns = [
    path('api/',include(router.urls)),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
