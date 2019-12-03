#  Copyright (c) 2019 Jonathan Weth, Lübeck.
#
#  This file is part of TInventory.
#
#  TInventory is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License.
#
#  TInventory is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with TInventory.  If not, see <http://www.gnu.org/licenses/>.

from django.urls import path, include

from ui import views

urlpatterns = [
    path("", views.index, name="ui_index"),
    path("license/", views.license, name="ui_license"),
    path("categories/", views.CategoryList.as_view(), name="ui_categories"),
    path("categories/<int:id>/edit", views.CategoryEditView.as_view(), name="ui_categories_edit"),
    path("categories/<int:id>/delete", views.CategoryDeleteView.as_view(), name="ui_category_delete"),
    path("categories/new", views.CategoryNewView.as_view(), name="ui_category_new"),
    path("locations/", views.LocationListView.as_view(), name="ui_locations"),
    path("locations/<int:pk>/", views.LocationDetailView.as_view(), name="ui_locations_detail"),
    path("locations/<int:id>/edit", views.location_edit, name="ui_locations_edit"),
    path("locations/<int:id>/delete", views.location_delete, name="ui_location_delete"),
    path("locations/new", views.location_new, name="ui_location_new"),
    path("locations/<int:pk>/items/add/", views.location_add_item, name="ui_location_add_item"),
    path("presets/", views.presets, name="ui_presets"),
    path("presets/<int:id>", views.preset_view, name="ui_presets_view"),
    path("presets/<int:id>/edit", views.preset_edit, name="ui_presets_edit"),
    path("presets/<int:id>/delete", views.preset_delete, name="ui_preset_delete"),
    path("presets/new", views.preset_new, name="ui_preset_new"),
    path("items/", views.items, name="ui_items"),
    path("items/<int:id>", views.item_view, name="ui_items_view"),
    path("items/<int:id>/edit", views.item_edit, name="ui_items_edit"),
    path("items/<int:id>/delete", views.item_delete, name="ui_item_delete"),
    path("items/<int:id>/barcode.pdf", views.item_barcode, name="ui_item_barcode"),
    path("items/new", views.item_new, name="ui_item_new"),
    path("persons/", views.persons, name="ui_persons"),
    path("persons/<int:id>", views.person_view, name="ui_persons_view"),
    path("persons/<int:id>/edit", views.person_edit, name="ui_persons_edit"),
    path("persons/<int:id>/delete", views.person_delete, name="ui_person_delete"),
    path("persons/new", views.person_new, name="ui_person_new"),
    path("inventory/", views.inventory, name="ui_inventory"),
    path("checks/out/", views.check_out, name="ui_check_out"),
    path("checks/<int:id>/loan-form.pdf", views.loan_form, name="ui_loan_form"),
    path("checks/", views.checks, name="ui_checks"),
    path("checks/<int:id>", views.check_view, name="ui_checks_view"),
    path("checks/<int:id>/edit", views.check_edit, name="ui_checks_edit"),
    path("checks/<int:id>/continue", views.check_continue, name="ui_check_continue"),
    path("checks/<int:id>/check-in.pdf", views.check_in_confirmation, name="ui_check_in_confirmation"),
    path("checks/in/", views.check_in, name="ui_check_in"),
    path("excuse/", views.excuse, name="ui_excuse"),
    path('accounts/', include('django.contrib.auth.urls')),
]
