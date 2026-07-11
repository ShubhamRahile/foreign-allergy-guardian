from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from accounts.models import User
from profiles.models import MedicalProfile
from scanner.models import ScanHistory

class Command(BaseCommand):
    help = "Seeds database with traveler profile and the repository of 6 Emergency Medical Profiles."

    def handle(self, *args, **options):
        self.stdout.write("Seeding database profiles...")

        # 1. Seed Traveler Profile
        user, created = User.objects.get_or_create(
            username='traveler',
            defaults={
                'email': 'traveler@example.com',
                'phone': '+1 555-0199',
            }
        )
        if created:
            user.set_password('traveler123')
            user.save()
        profile, created_p = MedicalProfile.objects.get_or_create(user=user)
        profile.emergency_contact = "Dr. Helen Cho\nPhone: +1 555-9111"
        profile.allergies = "peanuts, dairy, wheat"
        profile.dietary_restrictions = "Avoid high fructose corn syrup."
        profile.uploaded_file.save('traveler_allergy_list.txt', ContentFile("soy\nshellfish\n"))
        profile.save()
        self.stdout.write(self.style.SUCCESS("Seeded 'traveler' account."))

        # Clean traveler history first to have clean stats
        ScanHistory.objects.filter(user=user).delete()
        ScanHistory.objects.create(
            user=user,
            barcode="4902777005510",
            product_name="Choco-Peanut Crispy Bar",
            ingredients="Sugar, whole milk powder, cocoa mass, roasted peanuts, wheat flour, vegetable oil, emulsifier (soy lecithin), artificial flavor.",
            detected_allergens=["peanuts", "dairy", "gluten"],
            result="danger"
        )
        ScanHistory.objects.create(
            user=user,
            barcode="8801007142410",
            product_name="Premium Roasted Seaweed",
            ingredients="Seaweed, sesame oil, corn oil, refined sea salt.",
            detected_allergens=[],
            result="safe"
        )

        # 2. Seed Repository of 6 Emergency Medical Profiles
        profiles_to_seed = [
            {
                'username': 'sarah',
                'password': 'sarah123',
                'email': 'sarah@example.com',
                'phone': '+1 (555) 012-3456',
                'allergies': 'shellfish, strawberries',
                'restrictions': 'Patient follows a strict vegan diet.',
                'file_content': 'shrimp, crab, lobster, vegan\n'
            },
            {
                'username': 'david',
                'password': 'david123',
                'email': 'david@example.com',
                'phone': '+1 (555) 987-6543',
                'allergies': 'soy, walnuts, cashews',
                'restrictions': 'Patient has a mild intolerance to eggs.',
                'file_content': 'eggs\n'
            },
            {
                'username': 'elena',
                'password': 'elena123',
                'email': 'elena@example.com',
                'phone': '+1 (555) 456-7890',
                'allergies': 'sesame seeds, wheat',
                'restrictions': 'Severe allergy to latex.',
                'file_content': 'latex\n'
            },
            {
                'username': 'michael',
                'password': 'michael123',
                'email': 'michael@example.com',
                'phone': '+1 (555) 321-9876',
                'allergies': 'peanuts, walnuts, almonds',
                'restrictions': 'Gluten-free diet due to intolerance.',
                'file_content': 'gluten\n'
            },
            {
                'username': 'amara',
                'password': 'amara123',
                'email': 'amara@example.com',
                'phone': '+1 (555) 777-2233',
                'allergies': 'latex',
                'restrictions': 'Lactose sensitive.',
                'file_content': 'dairy\n'
            },
            {
                'username': 'samuel',
                'password': 'samuel123',
                'email': 'samuel@example.com',
                'phone': '+1 (555) 111-4455',
                'allergies': 'soy, eggs',
                'restrictions': 'Life-threatening allergy to soy and derivatives.',
                'file_content': 'shellfish\n'
            }
        ]

        for p_data in profiles_to_seed:
            u, u_created = User.objects.get_or_create(
                username=p_data['username'],
                defaults={
                    'email': p_data['email'],
                    'phone': p_data['phone'],
                }
            )
            u.set_password(p_data['password'])
            u.save()

            prof, p_created = MedicalProfile.objects.get_or_create(user=u)
            prof.emergency_contact = f"Contact: {p_data['phone']}"
            prof.allergies = p_data['allergies']
            prof.dietary_restrictions = p_data['restrictions']
            prof.uploaded_file.save(f"{p_data['username']}_allergies.txt", ContentFile(p_data['file_content']))
            prof.save()

            self.stdout.write(self.style.SUCCESS(f"Seeded Patient Profile: {p_data['username'].capitalize()}"))

        self.stdout.write(self.style.SUCCESS("All medical profiles successfully seeded!"))
