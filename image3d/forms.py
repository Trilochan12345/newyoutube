# image3d/forms.py
from django import forms

class GenerateForm(forms.Form):
    prompt = forms.CharField(
        label="Prompt",
        widget=forms.Textarea(attrs={
            "rows": 3,
            "class": "textarea",
            "placeholder": "Describe the figurine you want to generate (e.g. 'Futuristic robot with glowing armor')"
        })
    )

    negative_prompt = forms.CharField(
        label="Negative Prompt",
        required=False,
        widget=forms.Textarea(attrs={
            "rows": 2,
            "class": "textarea",
            "placeholder": "What to avoid in the image (e.g. blur, distortion, text)"
        })
    )

    num_images = forms.IntegerField(
        label="Number of Images",
        min_value=1, max_value=6, initial=1,
        widget=forms.NumberInput(attrs={"class": "input"})
    )

    width = forms.IntegerField(
        label="Width (px)",
        min_value=256, max_value=1024, initial=768,
        widget=forms.NumberInput(attrs={"class": "input"})
    )

    height = forms.IntegerField(
        label="Height (px)",
        min_value=256, max_value=1024, initial=768,
        widget=forms.NumberInput(attrs={"class": "input"})
    )

    steps = forms.IntegerField(
        label="Inference Steps",
        min_value=10, max_value=60, initial=28,
        widget=forms.NumberInput(attrs={"class": "input"})
    )

    guidance = forms.FloatField(
        label="Guidance Scale",
        min_value=1.0, max_value=20.0, initial=7.5,
        widget=forms.NumberInput(attrs={"class": "input", "step": "0.1"})
    )

    seed = forms.IntegerField(
        label="Seed (optional)",
        required=False,
        widget=forms.NumberInput(attrs={
            "class": "input",
            "placeholder": "Leave blank for random"
        })
    )
