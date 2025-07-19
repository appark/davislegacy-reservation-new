from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.db.models import Prefetch
from django.contrib import messages

from django.contrib.auth.models import User
from reservations.models import Reservation, Tournament
from reservations.decorators import IsSuperuser
from reservations.utils import clear_tokens
from reservations.api.forms import APITeamModifyFieldsForm, APIFieldModifyTeamsForm, APIManagerModifyTeamsForm
from reservations.api.serializers import ReservationSerializer, TournamentSerializer, TeamSerializer

class APIClearTokens(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        clear_tokens(request)

        messages.success(request._request, "The form was successfully canceled, because we noticed you navigated to another page.")
        return Response({ 'success': True })

class APIToggleSidebar(APIView):
    def get(self, request, format=None):
        current = request.session.get('sidebar_status', False)
        current = not current

        request.session['sidebar_status'] = current

        return Response({ 'sidebar_status': current })

class APITeamModifyFields(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsSuperuser]

    def post(self, request, format=None):
        form = APITeamModifyFieldsForm(request.POST)

        if form.is_valid():
            form.save()

            return Response({ 'status': 'success' })
        else:
            return Response({ 'status': 'error', 'errors': form.errors })

class APIFieldModifyTeams(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsSuperuser]

    def post(self, request, format=None):
        form = APIFieldModifyTeamsForm(request.POST)

        if form.is_valid():
            form.save()

            return Response({ 'status': 'success' })
        else:
            return Response({ 'status': 'error', 'errors': form.errors })

class APIGameTypeModifyTeams(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsSuperuser]

    def post(self, request, format=None):
        form = APIGameTypeModifyTeamsForm(request.POST)

        if form.is_valid():
            form.save()

            return Response({ 'status': 'success' })
        else:
            return Response({ 'status': 'error', 'errors': form.errors })

class APIManagerModifyTeams(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsSuperuser]

    def post(self, request, format=None):
        form = APIManagerModifyTeamsForm(request.POST)

        if form.is_valid():
            form.save()

            return Response({ 'status': 'success' })
        else:
            return Response({ 'status': 'error', 'errors': form.errors })

class APIReservationList(generics.ListAPIView):
    queryset = Reservation.objects.filter(active=True, approved=True).select_related('timeslot', 'team', 'gametype', 'location')
    serializer_class = ReservationSerializer

class APIReservationDetail(generics.RetrieveAPIView):
    queryset = Reservation.objects.filter(active=True, approved=True).select_related('timeslot', 'team', 'gametype', 'location')
    serializer_class = ReservationSerializer

class APITournamentList(generics.ListAPIView):
    queryset = Tournament.objects.filter(active=True).select_related('gametype')
    serializer_class = TournamentSerializer

class APITournamentDetail(generics.RetrieveAPIView):
    queryset = Tournament.objects.filter(active=True).select_related('gametype')
    serializer_class = TournamentSerializer

class APITeamList(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True, groups__name='Team').prefetch_related(Prefetch('reservation_set', queryset=Reservation.objects.filter(active=True, approved=True)))
    serializer_class = TeamSerializer

class APITeamDetail(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True, groups__name='Team').prefetch_related(Prefetch('reservation_set', queryset=Reservation.objects.filter(active=True, approved=True)))
    serializer_class = TeamSerializer
