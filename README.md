# MediCare - Clinic Management System

## 1. MediCare Project Summary
MediCare is a comprehensive, web-based clinic management system designed to streamline healthcare operations. It provides a robust platform for managing patients, doctors, appointments, prescriptions, and billing. Built with Django and Bootstrap, it ensures a secure, responsive, and user-friendly experience for all stakeholders including administrators, doctors, staff, and patients. The system emphasizes role-based access control, ensuring data privacy and efficient workflow management.

## 2. Features
- **Role-Based Portals**: Dedicated portals for Patients, Doctors, and Admins with strict permission isolation.
- **Patient Management**: Complete patient profiles, medical history tracking, and easy registration.
- **Doctor Management**: Doctor profiles, specialty management, and scheduling.
- **Appointment System**: Smart booking system with calendar integration and email notifications.
- **Prescription Management**: Digital prescription generation with PDF download capability (Doctor only).
- **Billing & Invoices**: Integrated billing system with support for multiple payment methods (Visa, bKash, Nagad) and PDF receipts.
- **Secure Authentication**: Robust login/signup system with role verification.
- **Google Sign-In**: Integrated Google OAuth 2.0 for fast and secure login/signup.
- **Responsive Design**: Mobile-friendly interface built with Bootstrap 5.
- **REST API**: Fully functional API for future mobile app integration.

## 3. Requirements
- **Python**: 3.10 or higher
- **Django**: 5.0+
- **Database**: SQLite (default) or PostgreSQL (recommended for production)
- **Dependencies**: Listed in `requirements.txt` (includes `reportlab` for PDF, `djangorestframework` for API)

## 4. Installation
Follow these steps to set up the project:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd MediCare
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create Superuser**:
   ```bash
   python manage.py createsuperuser
   ```

## 5. Environment Variables
Create a `.env` file in the root directory (same level as `manage.py`) to manage sensitive settings.
*Note: For local development, default settings are used if `.env` is missing.*

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
# Email Settings (Optional for testing)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 6. Google OAuth Setup
To enable "Log in with Google":
1.  **Google Cloud Console**:
    -   Create a project and configure the OAuth Consent Screen.
    -   Create OAuth Credentials (Client ID & Secret).
    -   Add `http://localhost:8000` to Authorized JavaScript origins.
    -   Add `http://localhost:8000/accounts/google/login/callback/` to Authorized redirect URIs.

2.  **Django Admin Configuration**:
    -   Go to [http://localhost:8000/admin/socialaccount/socialapp/](http://localhost:8000/admin/socialaccount/socialapp/).
    -   Add a new **Social Application**.
    -   **Provider**: Google
    -   **Name**: Google
    -   **Client ID**: (Your Google Client ID)
    -   **Secret Key**: (Your Google Client Secret)
    -   **Sites**: Add `localhost:8000` (or your site) to "Chosen sites".

3.  **Local Secrets Backup (Optional)**:
    -   Store your Client ID and Secret in a local `secrets.json` file (added to `.gitignore`) to keep them safe and accessible.

## 7. Settings Summary
The project settings are configured in `medicare_core/settings.py`. Key configurations include:
- **INSTALLED_APPS**: Includes custom apps `users`, `patients`, `doctors`, `appointments`, `prescriptions`, `billing`.
- **MIDDLEWARE**: Standard Django middleware plus custom role-based access controls.
- **TEMPLATES**: Configured to use project-level and app-level templates.
- **STATIC/MEDIA**: Configured for serving static files and user-uploaded media (profile pictures, reports).
- **AUTH_USER_MODEL**: Custom user model `users.User` used for authentication.

## 8. Run Locally
To run the development server:

```bash
python manage.py runserver
```
Access the application at: [http://localhost:8000](http://localhost:8000)

**Default Portals:**
- **Patient/Main**: [http://localhost:8000/](http://localhost:8000/)
- **Doctor Login**: [http://localhost:8000/login/doctor/](http://localhost:8000/login/doctor/)
- **Admin Login**: [http://localhost:8000/login/admin/](http://localhost:8000/login/admin/)

## 9. Project Structure
```
MediCare/
├── medicare_core/      # Project configuration & core views
├── users/              # Authentication & User models
├── patients/           # Patient management app
├── doctors/            # Doctor management app
├── appointments/       # Appointment booking app
├── prescriptions/      # Prescription generation app
├── billing/            # Invoicing & Payment app
├── templates/          # Global HTML templates
├── static/             # CSS, JS, Images
├── media/              # User uploaded files
├── manage.py           # Django management script
└── requirements.txt    # Project dependencies
```

## 10. Production Tips
- **Debug Mode**: Ensure `DEBUG=False` in production.
- **Database**: Switch to PostgreSQL for better performance and reliability.
- **Static Files**: Use `whitenoise` or Nginx to serve static files efficiently.
- **Security**: Set a strong `SECRET_KEY` and configure `ALLOWED_HOSTS`.
- **HTTPS**: Always use HTTPS (SSL) to secure user data.

## 11. Credits
Developed by Md. Shariful Islam Rony.
- **Frameworks**: Django, Bootstrap
- **Icons**: FontAwesome
- **PDF Generation**: ReportLab

---
*© 2025 MediCare. All Rights Reserved.*
