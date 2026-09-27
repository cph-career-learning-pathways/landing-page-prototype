from django.shortcuts import render
from .models import Resource

def format_duration(seconds):
    if seconds is None:
        return None
    if seconds < 60:
        return "Less than a minute"
    minutes = round(seconds / 60)
    if minutes < 60:
        return f"{minutes} min"
    hours = seconds / 3600
    if hours.is_integer():
        return f"{int(hours)} hr"
    return f"{hours:.1f} hr"

def index(request):
    resources = (
        Resource.objects
        .select_related("source", "curator")
        .prefetch_related("categories", "filters")
        .order_by("-resource_add_date")
    )
    for resource in resources:
        # Use the first associated filter as the card's skill.
        resource.display_skill = resource.filters.first()
        # Categories are displayed on the card.
        resource.display_categories = list(resource.categories.all())
        # Human-readable duration for the card/detail panel.
        resource.display_duration = format_duration(
            resource.resource_duration_seconds
        )
        # Useful for the detail panel.
        resource.display_source_domain = resource.source.source_domain
    context = {
        "resources": resources,
        "resource_count": len(resources),
    }
    return render(request, "landing/index.html", context)