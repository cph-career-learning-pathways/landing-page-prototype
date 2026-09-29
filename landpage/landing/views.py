from django.db.models import Q
from django.shortcuts import render

from resource_discovery.search import search_resources

from .models import Category, CuratedCollection, Resource


def format_duration(seconds):
    """Convert a duration in seconds into a compact display string."""
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


def get_category_options():
    """Load the three topbar taxonomy groups from the database.

    Category remains the single source of truth for these options. Resource
    Discovery receives the user's selected values but does not maintain its
    own duplicate list.
    """
    return {
        "skill_options": Category.objects.filter(
            category_type="Skill",
            is_active=True,
        ).order_by("category_name"),
        "degree_program_options": Category.objects.filter(
            category_type="Degree Program",
            is_active=True,
        ).order_by("category_name"),
        "career_field_options": Category.objects.filter(
            category_type="Career Field",
            is_active=True,
        ).order_by("category_name"),
    }


def apply_category_filters(
    resources,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Apply topbar taxonomy filters to the local Resource queryset.

    Values within one group are OR choices via __in. Chaining the three groups
    produces AND behavior across Skill, Degree Program, and Career Field.
    """
    if selected_skills:
        resources = resources.filter(
            categories__category_type="Skill",
            categories__category_name__in=selected_skills,
        )

    if selected_degree_programs:
        resources = resources.filter(
            categories__category_type="Degree Program",
            categories__category_name__in=selected_degree_programs,
        )

    if selected_career_fields:
        resources = resources.filter(
            categories__category_type="Career Field",
            categories__category_name__in=selected_career_fields,
        )

    return resources


def search_local_collections(
    search_query,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Return database Resources for Collections-mode browsing/search.

    With no search text, preserve the prototype's existing catalog behavior and
    show local resources. With search text, search active CuratedCollection
    names/descriptions, then show resources that belong to matching collections.
    The three taxonomy selectors further constrain those resources.
    """
    resources = (
        Resource.objects
        .select_related("source", "curator")
        .prefetch_related("categories", "filters")
    )

    if search_query:
        matching_collections = CuratedCollection.objects.filter(
            is_active=True,
        ).filter(
            Q(collection_name__icontains=search_query)
            | Q(collection_description__icontains=search_query)
        )

        resources = resources.filter(
            collections__in=matching_collections,
        )

    resources = apply_category_filters(
        resources,
        selected_skills,
        selected_degree_programs,
        selected_career_fields,
    )

    resources = list(
        resources
        .distinct()
        .order_by("-resource_add_date")
    )

    # Add display-only fields expected by the existing resource-card template.
    for resource in resources:
        # Current prototype Filter data represents attributes such as Difficulty.
        resource.display_skill = resource.filters.first()
        resource.display_categories = list(resource.categories.all())
        resource.display_duration = format_duration(
            resource.resource_duration_seconds
        )
        resource.display_source_domain = resource.source.source_domain

    return resources


def search_web_resources(
    search_query,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Call the existing Resource Discovery pipeline for Web mode.

    Results remain transient normalized dictionaries. They are deliberately not
    inserted into the Django Resource table during discovery.
    """
    discovery_filters = {
        "skills": selected_skills,
        "degree_programs": selected_degree_programs,
        "career_fields": selected_career_fields,
    }

    results = search_resources(
        search_query,
        filters=discovery_filters,
    )

    # Add display-only duration text while preserving the normalized result
    # dictionaries returned by Resource Discovery.
    for result in results:
        result["display_duration"] = format_duration(
            result.get("duration_seconds")
        )

    return results


def index(request):
    """Coordinate local Collections search and external Web discovery."""
    search_query = request.GET.get("search", "").strip()

    # The embedded selector submits one of these two supported modes.
    search_mode = request.GET.get("search_mode", "collections")
    if search_mode not in {"collections", "web"}:
        search_mode = "collections"

    selected_skills = request.GET.getlist("skill")
    selected_degree_programs = request.GET.getlist("degree_program")
    selected_career_fields = request.GET.getlist("career_field")

    category_options = get_category_options()

    resources = []
    discovery_results = []
    discovery_error = None

    # Resource Discovery supports filter-only searches, so Web mode is allowed
    # to run when either free text OR at least one taxonomy selection is present.
    has_discovery_intent = any(
        (
            selected_skills,
            selected_degree_programs,
            selected_career_fields,
        )
    )
    discovery_attempted = bool(search_query or has_discovery_intent)

    if search_mode == "web":
        if discovery_attempted:
            try:
                discovery_results = search_web_resources(
                    search_query,
                    selected_skills,
                    selected_degree_programs,
                    selected_career_fields,
                )
            except Exception as exc:
                # Prototype-stage behavior: surface a readable error on the page
                # rather than taking down the whole landing page.
                discovery_error = f"Web resource search failed: {exc}"
    else:
        resources = search_local_collections(
            search_query,
            selected_skills,
            selected_degree_programs,
            selected_career_fields,
        )

    context = {
        "resources": resources,
        "resource_count": len(resources),
        "discovery_results": discovery_results,
        "discovery_count": len(discovery_results),
        "discovery_error": discovery_error,
        "discovery_attempted": discovery_attempted,
        "selected_skills": selected_skills,
        "selected_degree_programs": selected_degree_programs,
        "selected_career_fields": selected_career_fields,
        "search_query": search_query,
        "search_mode": search_mode,
        **category_options,
    }

    return render(request, "landing/index.html", context)
