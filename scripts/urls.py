from scripts.views import ScriptList
from django.urls import path

urlpatterns = [
    path('scripts/', ScriptList.as_view())
]
