from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from agents.dietary_defender import DietaryDefenderAgent
from profiles.models import MedicalProfile
from .models import ScanHistory
import json

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        history = ScanHistory.objects.filter(user=request.user)
        
        # Calculate stats
        total_scans = history.count()
        dangerous_scans = history.filter(result='danger').count()
        safe_scans = history.filter(result='safe').count()
        recent_scans = history.order_by('-created_at')[:5]

        # Process allergy lists for templates without custom tags
        has_allergies = bool(profile.allergies)
        allergy_list = [a.strip() for a in profile.allergies.split(',')] if profile.allergies else []
        import os
        uploaded_file_name = os.path.basename(profile.uploaded_file.name) if profile.uploaded_file else ""

        return render(request, 'dashboard.html', {
            'profile': profile,
            'total_scans': total_scans,
            'dangerous_scans': dangerous_scans,
            'safe_scans': safe_scans,
            'recent_scans': recent_scans,
            'has_allergies': has_allergies,
            'allergy_list': allergy_list,
            'uploaded_file_name': uploaded_file_name
        })

class ScanView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'scan.html')

    def post(self, request):
        # Process manual barcode entry
        barcode = request.POST.get('barcode', '').strip()
        if not barcode:
            messages.error(request, "Please enter a valid barcode.")
            return redirect('scan')
        return redirect('scan_result', barcode=barcode)

class ScanResultView(LoginRequiredMixin, View):
    def get(self, request, barcode):
        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        agent = DietaryDefenderAgent()
        
        # 1. Read user allergies
        user_allergies = agent.read_medical_profile(profile)
        
        # 2. Get product info
        product_info = agent.get_product_information(barcode)
        
        # 3. Detect matches
        matched = agent.detect_allergens(user_allergies, product_info["ingredients"])
        
        # 4. Generate decision
        decision = agent.generate_decision(matched)
        
        # 5. Detect cross contamination warnings
        cross_warnings = agent.detect_cross_contamination(product_info["ingredients"])
        
        # 6. Translate ingredients
        translated_ingredients, lang = agent.translate_ingredients(product_info["ingredients"])

        # Calculate risk score (0 to 100)
        risk_score = 0
        if decision["status"] == "danger":
            risk_score = 100
        elif cross_warnings:
            risk_score = 35
        elif not product_info["ingredients"] or "API Error" in product_info.get("source", ""):
            risk_score = 15

        # 7. Save to scan history
        history_entry = ScanHistory.objects.create(
            user=request.user,
            barcode=barcode,
            product_name=product_info["product_name"],
            ingredients=product_info["ingredients"],
            detected_allergens=decision["allergens"],
            result=decision["status"]
        )

        return render(request, 'result.html', {
            'barcode': barcode,
            'product_name': product_info["product_name"],
            'ingredients': product_info["ingredients"],
            'translated_ingredients': translated_ingredients,
            'detected_lang': lang,
            'matched_allergens': decision["allergens"],
            'status': decision["status"],
            'message': decision["message"],
            'cross_warnings': cross_warnings,
            'risk_score': risk_score,
            'source': product_info.get("source", "Open Food Facts"),
            'history_id': history_entry.id
        })

class OCRScanView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'ocr.html')

    def post(self, request):
        # Process OCR image upload
        image_file = request.FILES.get('label_image')
        if not image_file:
            messages.error(request, "Please select an image file to upload.")
            return redirect('ocr_scan')

        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        agent = DietaryDefenderAgent()
        
        # Read user allergies
        user_allergies = agent.read_medical_profile(profile)
        
        # Analyze using AI agent
        ocr_result = agent.analyze_label_ocr(image_file, user_allergies)
        
        # Save to scan history
        history_entry = ScanHistory.objects.create(
            user=request.user,
            barcode="OCR Label Scan",
            product_name=ocr_result["product_name"],
            ingredients=ocr_result["ingredients"],
            detected_allergens=ocr_result["matched_allergens"],
            result=ocr_result["status"]
        )

        # Detect cross contamination
        cross_warnings = agent.detect_cross_contamination(ocr_result["ingredients"])

        risk_score = 100 if ocr_result["status"] == "danger" else (35 if cross_warnings else 0)

        return render(request, 'result.html', {
            'barcode': "OCR Label Scan",
            'product_name': ocr_result["product_name"],
            'ingredients': ocr_result["ingredients"],
            'translated_ingredients': ocr_result["translated_ingredients"],
            'detected_lang': ocr_result["detected_lang"],
            'matched_allergens': ocr_result["matched_allergens"],
            'status': ocr_result["status"],
            'message': ocr_result["message"],
            'cross_warnings': cross_warnings,
            'risk_score': risk_score,
            'source': "AI OCR Engine",
            'history_id': history_entry.id
        })

class HistoryListView(LoginRequiredMixin, View):
    def get(self, request):
        history = ScanHistory.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'history.html', {'history': history})

    def post(self, request):
        # Clear all user history or delete individual entry
        action = request.POST.get('action')
        if action == 'clear_all':
            ScanHistory.objects.filter(user=request.user).delete()
            messages.success(request, "Your scan history has been cleared.")
        else:
            entry_id = request.POST.get('entry_id')
            if entry_id:
                entry = get_object_or_404(ScanHistory, id=entry_id, user=request.user)
                entry.delete()
                messages.success(request, "Scan entry deleted.")
        return redirect('history')
