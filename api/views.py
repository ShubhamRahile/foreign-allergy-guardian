from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, login
from accounts.models import User
from profiles.models import MedicalProfile
from scanner.models import ScanHistory
from agents.dietary_defender import DietaryDefenderAgent
from .serializers import (
    RegisterSerializer, UserSerializer, MedicalProfileSerializer, 
    ScanHistorySerializer, ScanRequestSerializer
)

class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'anon'

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'anon'

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful", "user": UserSerializer(user).data})
        return Response({"error": "Invalid username or password"}, status=status.HTTP_400_BAD_REQUEST)

class ProfileAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        serializer = MedicalProfileSerializer(profile)
        return Response(serializer.data)

    def post(self, request):
        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        # Handle profile updates (partial update allowed)
        serializer = MedicalProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ScanAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ScanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        agent = DietaryDefenderAgent()
        user_allergies = agent.read_medical_profile(profile)

        barcode = serializer.validated_data.get('barcode')
        label_image = serializer.validated_data.get('label_image')

        if label_image:
            # OCR label scan pathway
            ocr_result = agent.analyze_label_ocr(label_image, user_allergies)
            
            # Save history
            ScanHistory.objects.create(
                user=request.user,
                barcode="OCR Label Scan",
                product_name=ocr_result["product_name"],
                ingredients=ocr_result["ingredients"],
                detected_allergens=ocr_result["matched_allergens"],
                result=ocr_result["status"]
            )

            return Response({
                "product_name": ocr_result["product_name"],
                "ingredients": ocr_result["ingredients"],
                "status": ocr_result["status"],
                "message": ocr_result["message"],
                "matched_allergens": ocr_result["matched_allergens"]
            })

        else:
            # Barcode lookup pathway
            product_info = agent.get_product_information(barcode)
            matched = agent.detect_allergens(user_allergies, product_info["ingredients"])
            decision = agent.generate_decision(matched)

            # Save history
            ScanHistory.objects.create(
                user=request.user,
                barcode=barcode,
                product_name=product_info["product_name"],
                ingredients=product_info["ingredients"],
                detected_allergens=decision["allergens"],
                result=decision["status"]
            )

            return Response({
                "product_name": product_info["product_name"],
                "ingredients": product_info["ingredients"],
                "status": decision["status"],
                "message": decision["message"],
                "matched_allergens": decision["allergens"]
            })

class HistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        history = ScanHistory.objects.filter(user=request.user)
        serializer = ScanHistorySerializer(history, many=True)
        return Response(serializer.data)
