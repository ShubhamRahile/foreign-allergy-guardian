from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from .models import MedicalProfile
from .forms import MedicalProfileForm, UserUpdateForm
from io import BytesIO


# Import reportlab parts safely
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        profile_form = MedicalProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=request.user)
        return render(request, 'profile.html', {
            'profile_form': profile_form,
            'user_form': user_form,
            'profile': profile
        })

    def post(self, request):
        profile, created = MedicalProfile.objects.get_or_create(user=request.user)
        profile_form = MedicalProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Your medical profile has been updated successfully!")
            return redirect('profile')
            
        return render(request, 'profile.html', {
            'profile_form': profile_form,
            'user_form': user_form,
            'profile': profile
        })

class AllergyCardPDFView(LoginRequiredMixin, View):
    def get(self, request):
        profile = MedicalProfile.objects.filter(user=request.user).first()
        if not profile or not profile.allergies:
            messages.error(request, "Please add your allergies to generate an emergency card.")
            return redirect('profile')

        if not REPORTLAB_AVAILABLE:
            return HttpResponse("PDF generation library (reportlab) is not installed.", status=500)

        # Create PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="allergy_guardian_card_{request.user.username}.pdf"'

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CardTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#8B0000'),
            spaceAfter=10,
            alignment=1 # Centered
        )
        
        section_heading = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#2A3E5C'),
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'CardBody',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=8
        )

        translation_style = ParagraphStyle(
            'CardTranslation',
            parent=styles['Normal'],
            fontSize=9,
            fontName='Helvetica-Oblique',
            textColor=colors.HexColor('#4A4A4A'),
            spaceAfter=8
        )

        story = []

        # Header Warning Banner
        story.append(Paragraph("FOREIGN ALLERGY GUARDIAN - EMERGENCY TRAVEL CARD", title_style))
        story.append(Spacer(1, 10))

        # Personal Details Table
        allergy_list = [a.strip() for a in profile.allergies.split(',') if a.strip()]
        allergens_str = ", ".join(allergy_list)

        personal_data = [
            [Paragraph("<b>Traveler:</b>", body_style), Paragraph(request.user.username.capitalize(), body_style)],
            [Paragraph("<b>Email:</b>", body_style), Paragraph(request.user.email, body_style)],
            [Paragraph("<b>Emergency Contact:</b>", body_style), Paragraph(profile.emergency_contact.replace('\n', '<br/>') if profile.emergency_contact else "None", body_style)],
            [Paragraph("<b>Severe Allergies:</b>", body_style), Paragraph(f"<font color='red'><b>{allergens_str}</b></font>", body_style)],
            [Paragraph("<b>Dietary Restrictions:</b>", body_style), Paragraph(profile.dietary_restrictions or "None", body_style)]
        ]

        t = Table(personal_data, colWidths=[150, 350])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8F9FA')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DEE2E6')),
            ('PADDING', (0,0), (-1,-1), 8),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        # Translated Warnings Section
        story.append(Paragraph("<b>EMERGENCY TRANSLATED WARNINGS</b>", section_heading))
        story.append(Paragraph("Show this to restaurant staff, chefs, and market vendors.", body_style))
        story.append(Spacer(1, 10))

        # We'll translate the main allergy message
        # Let's map translations
        translations = [
            ("Spanish (Español)", 
             f"Hola. Tengo una alergia alimentaria grave a: <b>{allergens_str}</b>. "
             f"¿Este plato contiene alguno de estos ingredientes? Si como esto, puedo tener un choque anafiláctico."),
            ("French (Français)", 
             f"Bonjour. J'ai une allergie alimentaire grave à: <b>{allergens_str}</b>. "
             f"Ce plat contient-il l'un de ces ingrédients? Si je mange cela, je risque un choc anaphylactique."),
            ("German (Deutsch)", 
             f"Hallo. Ich habe eine schwere Nahrungsmittelallergie gegen: <b>{allergens_str}</b>. "
             f"Enthält dieses Gericht eine dieser Zutaten? Wenn ich das esse, kann ich einen anaphylaktischen Schock erleiden."),
            ("Italian (Italiano)", 
             f"Salve. Ho una grave allergia alimentare a: <b>{allergens_str}</b>. "
             f"Questo piatto contiene qualcuno di questi ingredienti? Se mangio questo, posso avere uno shock anafilattico."),
            ("Japanese (日本語) - Romanized/English Guide", 
             f"こんにちは。私は <b>{allergens_str}</b> に対する重い食物アレルギーがあります。 "
             f"この料理にそれらは入っていますか？食べると危険です。(Konnichiwa. Watashi wa {allergens_str} ni taisuru omoi shokumotsu arerugii ga arimasu. Kono ryori ni sore wa haitteimasu ka?)"),
        ]

        for lang, text in translations:
            story.append(Paragraph(f"<b>{lang}:</b>", body_style))
            story.append(Paragraph(text, translation_style))
            story.append(Spacer(1, 5))

        # Build PDF
        doc.build(story)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
