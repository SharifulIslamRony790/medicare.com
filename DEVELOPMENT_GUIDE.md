# MediCare Development Guide

## Project Structure

- `medicare_core/`: Project settings and core templates.
- `users/`: Custom User model and authentication.
- `patients/`: Patient management logic.
- `doctors/`: Doctor management logic.
- `appointments/`: Appointment booking logic.
- `prescriptions/`: Prescription management.
- `billing/`: Invoice and billing logic.

## API Documentation

The API is available at `/api/`. It supports standard CRUD operations for all resources.

### Endpoints
- `/api/users/`
- `/api/patients/`
- `/api/doctors/`
- `/api/appointments/`
- `/api/prescriptions/`
- `/api/billing/`

## Frontend Development

Templates are located in `medicare_core/templates/`.
Base styles use Bootstrap 5.

## Testing

Run API tests:
```bash
python test_api.py
```

Run UI tests:
```bash
python test_ui.py
```
