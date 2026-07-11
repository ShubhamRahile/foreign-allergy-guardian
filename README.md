# Foreign Allergy Guardian

**Foreign Allergy Guardian** is an AI-powered Django web application and REST API designed to protect individuals with severe food allergies while traveling abroad. It scans barcodes, translates ingredients, runs OCR on labels, provides vocal alerts, and generates printable travel-ready translation cards.

---

## 🌟 Key Features

1. **User Registration & Login**: Custom security-focused authentication.
2. **AI Dietary Defender Agent**: Checks ingredients against database-listed allergies and uploaded allergy files, handling translations and allergen synonyms (e.g. mapping "dairy" -> "lactose/casein/whey").
3. **Double Allergy Input**: Evaluates allergies written in the profile as well as multi-line allergy files uploaded as `.txt` files.
4. **Barcode Scanning**: Real-time camera scan using the `html5-qrcode` library, with support for manual entry.
5. **AI OCR & Translation**: Extracts text from images of foreign food labels, translates them from Spanish, French, German, Italian, or Japanese, and screens for allergens.
6. **Voice Alerts**: Client-side speech synthesis warnings in real time (e.g., announcing *"Warning: contains peanuts and dairy"*).
7. **Emergency PDF Travel Card**: Generates a printable PDF detailing emergency contacts, allergies, and translations of allergy warning messages in Spanish, French, German, Italian, and Japanese.
8. **Interactive Dashboard**: Statistics for safe/dangerous scans, risk profiles, and recent scan logs.
9. **REST APIs**: Full Django REST Framework endpoint suite for easy mobile/third-party integrations.

---

## 🛠 Tech Stack

- **Backend**: Python 3.12, Django 5.0, Django REST Framework, SQLite (dev) / PostgreSQL (prod), Pillow, Requests, Reportlab
- **Frontend**: HTML5, CSS3, Bootstrap 5, AJAX, html5-qrcode
- **Deployment**: Docker, Docker Compose

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- (Optional) Docker

### Installation

1. **Clone the repository and enter the directory**:
   ```bash
   cd foreign_allergy_guardian
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Seed the database (Demo Data)**:
   This creates a test user (`traveler` / `traveler123`) with a preconfigured medical profile, an uploaded allergy file, and pre-loaded scan history matching the Test Cases:
   ```bash
   python manage.py seed_data
   ```

5. **Run the server**:
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 🧪 Running Unit Tests

Run the comprehensive unit test suite covering allergy detection synonyms, API integration, registration flow, scanning, and dashboard stats:

```bash
python manage.py test
```

---

## 🐳 Docker Deployment

To launch the Django application alongside a PostgreSQL database using Docker Compose:

```bash
docker-compose up --build
```
The app will be accessible at `http://localhost:8000`.

---

## 🔌 API Endpoints

All endpoints require authentication (Session/Basic Auth). Rates are limited by DRF throttling.

- `POST /api/register/`: Create a user account.
- `POST /api/login/`: Authenticate and start session.
- `POST /api/profile/`: Get or update the Medical Profile.
- `POST /api/scan/`: Scan a barcode or OCR label image. Returns:
  ```json
  {
      "product_name": "Choco-Peanut Crispy Bar",
      "ingredients": "Sugar, whole milk powder, cocoa mass, roasted peanuts, wheat flour...",
      "status": "danger",
      "message": "DO NOT EAT",
      "matched_allergens": ["peanuts", "gluten"]
  }
  ```
- `GET /api/history/`: Retrieve scan logs.
