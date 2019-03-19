from django.urls import path, include

from ui import views

urlpatterns = [
    path("", views.index, name="ui_index"),
    path("categories/", views.categories, name="ui_categories"),
    path("categories/<int:id>/edit", views.category_edit, name="ui_categories_edit"),
    path("categories/<int:id>/delete", views.category_delete, name="ui_category_delete"),
    path("categories/new", views.category_new, name="ui_category_new"),
    path("locations/", views.locations, name="ui_locations"),
    path("locations/<int:id>/edit", views.location_edit, name="ui_locations_edit"),
    path("locations/<int:id>/delete", views.location_delete, name="ui_location_delete"),
    path("locations/new", views.location_new, name="ui_location_new"),
    path("presets/", views.presets, name="ui_presets"),
    path("presets/<int:id>", views.preset_view, name="ui_presets_view"),
    path("presets/<int:id>/edit", views.preset_edit, name="ui_presets_edit"),
    # path("presets/<int:id>/delete", views.preset_delete, name="ui_preset_delete"),
    path("presets/new", views.preset_new, name="ui_preset_new"),
    path('accounts/', include('django.contrib.auth.urls')),
]
