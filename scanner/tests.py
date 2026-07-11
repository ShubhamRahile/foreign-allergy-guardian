from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from profiles.models import MedicalProfile
from scanner.models import ScanHistory
from agents.dietary_defender import DietaryDefenderAgent
from unittest.mock import patch
import json

# Monkeypatch BaseContext and subclasses copy to fix Python 3.14 + Django 5.0 compatibility issue in test suite
from django.template.context import BaseContext, Context, RequestContext
def safe_context_copy(self):
    if hasattr(self, 'request'):
        duplicate = self.__class__(self.request)
    else:
        duplicate = self.__class__()
    duplicate.dicts = self.dicts[:]
    return duplicate
BaseContext.__copy__ = safe_context_copy
Context.__copy__ = safe_context_copy
RequestContext.__copy__ = safe_context_copy


class ForeignAllergyGuardianTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create a test user
        self.user = User.objects.create_user(
            username='traveler',
            email='traveler@example.com',
            phone='+15550199',
            password='testpassword123'
        )
        # Update user's medical profile
        self.profile = self.user.medical_profile
        self.profile.allergies = 'peanuts, gluten'
        self.profile.emergency_contact = 'Brother Bob: +1 555-0100'
        self.profile.save()

    def test_allergy_detection_logic(self):
        """
        1. Test Allergy Detection logic with synonyms and standard matches
        """
        agent = DietaryDefenderAgent()
        
        # Test direct matching
        allergies = ['peanuts', 'milk']
        ingredients_1 = "Sugar, whole milk powder, cocoa mass, roasted peanuts, wheat flour"
        detected = agent.detect_allergens(allergies, ingredients_1)
        self.assertIn('peanuts', detected)
        self.assertIn('milk', detected) # direct mapping or synonym mapping works

        # Test Case A inputs directly
        test_case_a_allergies = ['peanuts', 'gluten']
        test_case_a_ingredients = "Sugar, whole milk powder, cocoa mass, roasted peanuts, wheat flour, vegetable oil, emulsifier (soy lecithin), artificial flavor."
        detected_a = agent.detect_allergens(test_case_a_allergies, test_case_a_ingredients)
        self.assertIn('peanuts', detected_a)
        # Gluten should match via wheat flour synonym
        self.assertIn('gluten', detected_a)

        # Test Case B inputs directly
        test_case_b_allergies = ['peanuts', 'gluten']
        test_case_b_ingredients = "Seaweed, sesame oil, corn oil, refined sea salt."
        detected_b = agent.detect_allergens(test_case_b_allergies, test_case_b_ingredients)
        self.assertEqual(len(detected_b), 0)

    def test_dietary_defender_decision_logic(self):
        """
        Test decision formatting of agent
        """
        agent = DietaryDefenderAgent()
        
        # Danger decision
        decision_danger = agent.generate_decision(['peanuts', 'gluten'])
        self.assertEqual(decision_danger['status'], 'danger')
        self.assertEqual(decision_danger['message'], 'DO NOT EAT')
        self.assertEqual(decision_danger['allergens'], ['peanuts', 'gluten'])

        # Safe decision
        decision_safe = agent.generate_decision([])
        self.assertEqual(decision_safe['status'], 'safe')
        self.assertEqual(decision_safe['message'], 'Safe to Eat')
        self.assertEqual(decision_safe['allergens'], [])

    @patch('agents.dietary_defender.requests.get')
    def test_api_integration_off_lookup(self, mock_get):
        """
        2. Test API Integration - verify that external calls are handled or mock works
        """
        agent = DietaryDefenderAgent()

        # Mock mock GET request response for an arbitrary barcode
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 1,
            "product": {
                "product_name": "Test Energy Bar",
                "ingredients_text": "Contains organic rolled oats, peanut butter, organic honey, dairy protein",
                "countries_tags": ["en:united-states"]
            }
        }

        # Query arbitrary barcode (should perform HTTP call and call mock)
        info = agent.get_product_information("1234567890123")
        self.assertEqual(info["product_name"], "Test Energy Bar")
        self.assertIn("peanut butter", info["ingredients"])

        # Query Test Case A barcode (should hit offline mock database directly without calling API)
        info_a = agent.get_product_information("4902777005510")
        self.assertEqual(info_a["product_name"], "Choco-Peanut Crispy Bar")
        self.assertIn("roasted peanuts", info_a["ingredients"])

    def test_user_registration(self):
        """
        3. Test User Registration view and DRF endpoints
        """
        # Test web registration redirection
        response = self.client.post(reverse('register'), {
            'username': 'newtraveler',
            'email': 'new@example.com',
            'phone': '+15559999',
            'password1': 'secretpassword123',
            'password2': 'secretpassword123'
        }, follow=True)
        self.assertContains(response, "Hello, Newtraveler")

        # Test DRF API register endpoint
        api_url = reverse('api_register')
        api_response = self.client.post(api_url, {
            'username': 'apijohn',
            'email': 'john@example.com',
            'phone': '+12223333',
            'password': 'apisecretpassword999'
        }, content_type='application/json')
        self.assertEqual(api_response.status_code, 201)
        self.assertEqual(api_response.data['username'], 'apijohn')

    def test_barcode_scanning_views(self):
        """
        4. Test Barcode scanning view redirects and page load
        """
        self.client.login(username='traveler', password='testpassword123')
        
        # Test scanner view load
        response = self.client.get(reverse('scan'))
        self.assertEqual(response.status_code, 200)

        # Test scanning result redirect from manual form post
        response_post = self.client.post(reverse('scan'), {
            'barcode': '4902777005510'
        })
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(response_post.url.endswith('/scanner/scan/result/4902777005510/'))

        # Test scanning page results
        response_result = self.client.get(reverse('scan_result', kwargs={'barcode': '4902777005510'}))
        self.assertEqual(response_result.status_code, 200)
        self.assertContains(response_result, 'DO NOT EAT')
        self.assertContains(response_result, 'peanuts')
        self.assertContains(response_result, 'gluten')

    def test_dashboard_statistics(self):
        """
        5. Test dashboard counters increment correctly
        """
        self.client.login(username='traveler', password='testpassword123')

        # Generate a history entry
        ScanHistory.objects.create(
            user=self.user,
            barcode='4902777005510',
            product_name='Choco-Peanut Crispy Bar',
            ingredients='roasted peanuts, wheat flour',
            detected_allergens=['peanuts', 'gluten'],
            result='danger'
        )
        ScanHistory.objects.create(
            user=self.user,
            barcode='8801007142410',
            product_name='Premium Roasted Seaweed',
            ingredients='Seaweed, sesame oil',
            detected_allergens=[],
            result='safe'
        )

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_scans'], 2)
        self.assertEqual(response.context['dangerous_scans'], 1)
        self.assertEqual(response.context['safe_scans'], 1)
