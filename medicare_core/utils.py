import requests
from django.core.files.base import ContentFile

def generate_profile_image(name_seed):
    """
    Generates a profile image using the DiceBear API based on the provided name seed.
    Returns a ContentFile object that can be saved to an ImageField.
    """
    # Using the 'avataaars' style for a nice cartoonish look, or 'initials' for simple ones.
    # 'bottts' is also good for a techy feel, but 'avataaars' is more human-like.
    # Let's use 'avataaars' for now.
    url = f"https://api.dicebear.com/7.x/avataaars/png?seed={name_seed}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return ContentFile(response.content, name=f"{name_seed}.png")
    except Exception as e:
        print(f"Error generating image: {e}")
    
    return None
