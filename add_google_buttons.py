"""
Script to add Google OAuth buttons to login and signup templates
"""
import re

templates_to_update = {
    'e:/MediCare/medicare_core/templates/patient_signup.html': {
        'button_text': 'Sign up with Google',
        'button_class': 'btn-outline-danger'
    },
    'e:/MediCare/medicare_core/templates/patient_login.html': {
        'button_text': 'Log in with Google',
        'button_class': 'btn-outline-danger'
    },
    'e:/MediCare/medicare_core/templates/doctor_signup.html': {
        'button_text': 'Sign up with Google',
        'button_class': 'btn-outline-danger'
    },
    'e:/MediCare/medicare_core/templates/doctor_login.html': {
        'button_text': 'Log in with Google',
        'button_class': 'btn-outline-danger'
    },
}

google_button_template = '''
                    <div class="text-center mt-3">
                        <p class="text-muted">OR</p>
                        <a href="{{% provider_login_url 'google' %}}" class="btn {button_class} w-100">
                            <i class="fab fa-google me-2"></i> {button_text}
                        </a>
                    </div>'''

for template_path, config in templates_to_update.items():
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add {% load socialaccount %} if not present
        if '{% load socialaccount %}' not in content:
            content = content.replace(
                "{% extends 'base.html' %}",
                "{% extends 'base.html' %}\n{% load socialaccount %}"
            )
        
        # Find the last </form> tag and add Google button after it
        if google_button_template.format(**config) not in content:
            # Pattern to find the closing form tag followed by closing div
            pattern = r'(</form>)\s*(</div>)'
            button_html = google_button_template.format(**config)
            replacement = r'\1' + button_html + r'\n                \2'
            content = re.sub(pattern, replacement, content, count=1)
        
        # Write updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"[OK] Updated {template_path}")
    except Exception as e:
        print(f"[ERROR] Error updating {template_path}: {e}")

print("\nAll templates updated successfully!")
