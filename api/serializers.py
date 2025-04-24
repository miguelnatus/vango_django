from rest_framework import serializers
from accounts.models import User, DriverDocument
from vehicles.models import Vehicle, VehicleImage
from routes.models import Route, RouteSchedule, RouteStop
from bookings.models import Booking, Payment
from reviews.models import Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'user_type', 'phone', 'profile_picture', 'is_verified', 'bio']
        read_only_fields = ['is_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class DriverDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverDocument
        fields = ['id', 'driver', 'document_type', 'document_file', 'is_verified', 'uploaded_at']
        read_only_fields = ['is_verified', 'uploaded_at']

class VehicleImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleImage
        fields = ['id', 'vehicle', 'image', 'caption']

class VehicleSerializer(serializers.ModelSerializer):
    images = VehicleImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Vehicle
        fields = ['id', 'driver', 'vehicle_type', 'model', 'year', 'license_plate', 
                  'capacity', 'has_air_conditioning', 'has_wifi', 'has_usb_ports', 
                  'has_tv', 'has_accessibility', 'is_verified', 'is_active', 
                  'main_image', 'images', 'created_at', 'updated_at']
        read_only_fields = ['is_verified', 'created_at', 'updated_at']

class RouteStopSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStop
        fields = ['id', 'route', 'name', 'description', 'order', 
                  'latitude', 'longitude', 'duration']

class RouteScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteSchedule
        fields = ['id', 'route', 'weekday', 'departure_time']

class RouteSerializer(serializers.ModelSerializer):
    stops = RouteStopSerializer(many=True, read_only=True)
    schedules = RouteScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Route
        fields = ['id', 'driver', 'vehicle', 'route_type', 'title', 'description',
                  'origin', 'destination', 'origin_latitude', 'origin_longitude',
                  'destination_latitude', 'destination_longitude', 'distance',
                  'duration', 'price', 'is_active', 'is_featured', 'stops',
                  'schedules', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_method', 'status',
                  'transaction_id', 'payment_date', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'passenger', 'route', 'schedule', 'booking_date',
                  'num_passengers', 'total_price', 'status', 'booking_reference',
                  'special_requests', 'pickup_location', 'dropoff_location',
                  'payment', 'created_at', 'updated_at']
        read_only_fields = ['booking_reference', 'created_at', 'updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'passenger', 'driver', 'route', 'booking', 'rating',
                  'comment', 'punctuality_rating', 'vehicle_rating', 'driver_rating',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
