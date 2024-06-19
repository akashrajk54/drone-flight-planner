from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
import matplotlib.pyplot as plt

from waypoint_generator.models import FlightPath
from waypoint_generator.serializers import FlightPathSerializer
from accounts_engine.utils import success_true_response, success_false_response


import logging

from waypoint_generator.utils import generate_horizontal_waypoints, generate_vertical_waypoints, decimal_to_dms, \
    generate_all_points, get_bounding_box, plot_waypoints

logger = logging.getLogger(__name__)
logger_info = logging.getLogger("info")
logger_error = logging.getLogger("error")


@api_view(["GET"])
def Home(request):
    return Response({"success": True})


class FlightPathViewSet(ModelViewSet):
    authentication_classes = [JWTAuthentication]
    queryset = FlightPath.objects.all().order_by("-created_datetime")
    serializer_class = FlightPathSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        return super(FlightPathViewSet, self).get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action in ["list", "retrieve"]:
            context["exclude_user"] = True
        return context

    def get_queryset(self):
        if self.action == "list":
            sorted_queryset = FlightPath.objects.all().order_by("-created_datetime")
            return sorted_queryset

    def create(self, request, *args, **kwargs):
        try:
            user = request.user

            requested_data = request.data.copy()
            requested_data["user"] = user.id
            serializer = self.get_serializer(data=requested_data)

            try:
                serializer.is_valid(raise_exception=True)
                polygon = requested_data['polygon_lat_lon']
                bounding_box = get_bounding_box(polygon)
                overlapping_percentage = requested_data['overlapping_percentage']
                altitude = requested_data['altitude']

                vertical_waypoints = generate_vertical_waypoints(bounding_box, altitude, overlapping_percentage)
                horizontal_waypoints = generate_horizontal_waypoints(bounding_box, altitude, overlapping_percentage)

                # Now generate all points
                all_points = generate_all_points(vertical_waypoints, horizontal_waypoints)

                plot_waypoints(bounding_box, all_points)

                flight_path = serializer.save(user=user, waypoints=all_points)
                message = "Waypoints created successfully."
                logger_info.info(f"{message} by {user.username}")
                return Response(
                    success_true_response(data={"id": flight_path.id}, message=message),
                    status=status.HTTP_201_CREATED,
                )

            except ValidationError as e:
                error_detail = e.detail
                for field_name, errors in error_detail.items():
                    for error in errors:
                        message = str(error)
                        logger_error.error(message)
                        return Response(
                            success_false_response(message=message),
                            status=e.status_code,
                        )

        except Exception as e:
            message = str(e)
            logger_error.error(message)
            return Response(
                success_false_response(message="An unexpected error occurred. Please try again later."),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )