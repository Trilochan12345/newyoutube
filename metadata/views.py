from django.shortcuts import render

# Create your views here.
from .utils.metadata import generate_title, generate_description, extract_keywords

def generate_metadata_view(request):
    if request.method == "POST":
        script_text = request.POST.get("script", "")
        credits = ["Pexels", "Midjourney AI", "OpenAI DALL·E"]

        title = generate_title(script_text)
        description = generate_description(script_text, credits=credits)
        tags = extract_keywords(script_text)

        return render(request, "metadata_preview.html", {
            "title": title,
            "description": description,
            "tags": ", ".join(tags)
        })

    return render(request, "generate_metadata.html")
