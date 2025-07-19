from django.urls import path
from ninja import NinjaAPI

from .views import router as polls_router


api = NinjaAPI()

api.add_router("/", polls_router)

urlpatterns = [
    path("", api.urls),
]
