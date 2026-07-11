from rest_framework import serializers
from accounts.models import User
from profiles.models import MedicalProfile
from scanner.models import ScanHistory

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            phone=validated_data.get('phone', ''),
            password=validated_data['password']
        )
        return user

class MedicalProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MedicalProfile
        fields = ['user', 'emergency_contact', 'allergies', 'dietary_restrictions', 'uploaded_file', 'created_at']
        read_only_fields = ['created_at']

class ScanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScanHistory
        fields = ['id', 'barcode', 'product_name', 'ingredients', 'detected_allergens', 'result', 'created_at']
        read_only_fields = ['id', 'created_at']

class ScanRequestSerializer(serializers.Serializer):
    barcode = serializers.CharField(required=False, allow_blank=True)
    # Support direct OCR upload through API
    label_image = serializers.ImageField(required=False)

    def validate(self, attrs):
        if not attrs.get('barcode') and not attrs.get('label_image'):
            raise serializers.ValidationError("Either barcode or label_image must be provided.")
        return attrs
