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

from rest_framework import viewsets, permissions, routers
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import *


class UserList(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class TechniciansList(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Person.objects.all().filter(is_technician=True)
    serializer_class = PersonSerializer


class NormalPersonsList(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Person.objects.all().filter(is_technician=False)
    serializer_class = PersonSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CheckProcessViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = CheckOutProcess.objects.all()
    serializer_class = CheckProcessSerializer

    @action(detail=True, methods=["post"])
    def add(self, request, pk=None):
        msg = ""
        msg_type = "success"

        process = self.get_object()

        if not request.data.get("scan", False):
            msg = "Fehlendes Argument."
            msg_type = "bad"
        scan = request.data["scan"]
        item = None

        try:
            id = int(scan)
            item = Item.objects.get(id=id)
        except (Item.DoesNotExist, ValueError):
            try:
                item = Item.objects.get(barcode=scan)
            except Item.DoesNotExist:
                msg = "Es gibt kein Objekt mit dieser ID oder diesem Barcode: {}".format(scan)
                msg_type = "bad"

        if msg_type == "success":
            if not item.is_available():
                if item.checks.all()[0].check_out == process:
                    msg = "Dieses Objekt ist bereits zur Check-Out-Liste hinzugefügt worden."
                    msg_type = "bad"
                else:
                    msg = "Dieses Objekt ist aktuell ausgecheckt. Bitte vor dem Check-Out wieder Einchecken."
                    msg_type = "bad"
        if msg_type == "success":
            check = process.checks.create(item=item)
            msg = "Das Objekt wurde erfolgreich zur Check-Out-Liste hinzugefügt."

        return Response({"msg": msg, "msg_type": msg_type})

    @action(detail=True, methods=["get"])
    def checks(self, request, pk=None):
        process = self.get_object()
        checks = process.checks
        serializer = CheckSerializer(checks, many=True)
        return Response(serializer.data)


class CheckViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Check.objects.all()
    serializer_class = CheckSerializer


router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'users', UserList)
router.register(r'persons/technicians', TechniciansList)
router.register(r'persons/normal', NormalPersonsList)
router.register(r'check_processes', CheckProcessViewSet)
router.register(r'checks', CheckViewSet)
