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


class NormalPersonsList(viewsets.ModelViewSet):
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

        if msg_type == "success":
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
        serializer = CheckSerializer(checks, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def check_in(self, request):
        context = {}
        user = None
        msg = ""
        msg_type = "success"

        if not request.data.get("scan", False) or not request.data.get("user", False):
            msg = "Fehlendes Argument."
            msg_type = "bad"
        if msg_type == "success":
            try:
                user_id = int(request.data["user"])
                user = User.objects.get(id=user_id)
            except (User.DoesNotExist, ValueError):
                msg = "Es wird ein korrekter Nutzer benötigt."
                msg_type = "bad"

        if msg_type == "success":
            scan = request.data["scan"]
            print(scan)
            check = None

            try:
                id = int(scan)
                check = Check.objects.get(item_id=id, checked_in=False)
            except (Check.DoesNotExist, ValueError):
                try:
                    check = Check.objects.get(item__barcode=scan, checked_in=False)
                except Check.DoesNotExist:
                    msg = "Es wurde kein ausgeliehenes Objekt mit diesem Barcode oder dieser ID gefunden."
                    msg_type = "bad"

            if msg_type == "success":
                check.checked_in = True
                check.checked_in_at = timezone.now()
                check.checked_in_by = user
                check.save()

                serializer = CheckSerializer(check, many=False, context={'request': request})
                context["check"] = serializer.data
                msg = "Das Objekt {} {}wurde erfolgreich eingecheckt.".format(check.item.name, "({}) ".format(
                    check.item.preset.name) if check.item.preset else "")
        context["msg"] = msg
        context["msg_type"] = msg_type

        return Response(context)


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
