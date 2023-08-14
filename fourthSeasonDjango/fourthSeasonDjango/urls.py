"""fourthSeasonDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from App01 import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("eda/", views.eda),
    path("get_data/stacked_lines/", views.get_data_stacked_lines),
    path("get_data/boxplot/", views.get_data_box_plot),
    path("get_data/parallel_lines/", views.get_data_parallel_lines),
    path("get_data/calendar/", views.get_data_calendar),
    path("get_data/hist_3d/", views.get_3d_hist),
    path("get_data/water_fall/", views.get_water_fall),
    path("get_data/corr_matrix/", views.get_corr_matrix),
    path("get_data/scatter_matrix/",views.scatter_matrix)
]
