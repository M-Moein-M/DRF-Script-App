from scripts import views
from django.urls import path

urlpatterns = [
    path('scripts/', views.ScriptList.as_view()),
    path('scripts/<int:pk>', views.ScriptDetail.as_view()),
]
