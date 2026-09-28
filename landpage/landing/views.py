from django.db.models import Q
from django.shortcuts import render

from .models import Category, Resource


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
    # ADDED: Read the search text and the three topbar category selections from
    # the query string. getlist() allows more than one selection per group.
    search_query = request.GET.get("search", "").strip()

    # ADDED: Preserve the search source selected by the embedded search-mode
    # control. Web is accepted now as an integration point for Resource Discovery;
    # until that backend is connected, the existing local resource search remains
    # the execution path for submitted text.
    search_mode = request.GET.get("search_mode", "collections")
    if search_mode not in {"collections", "web"}:
        search_mode = "collections"

    selected_skills = request.GET.getlist("skill")
    selected_degree_programs = request.GET.getlist("degree_program")
    selected_career_fields = request.GET.getlist("career_field")

    # ADDED: Populate each topbar dropdown from active Category records rather
    # than hard-coding option names in the template.
    skill_options = Category.objects.filter(
        category_type="Skill",
        is_active=True,
    ).order_by("category_name")

    degree_program_options = Category.objects.filter(
        category_type="Degree Program",
        is_active=True,
    ).order_by("category_name")

    career_field_options = Category.objects.filter(
        category_type="Career Field",
        is_active=True,
    ).order_by("category_name")

    resources = (
        Resource.objects
        .select_related("source", "curator")
        .prefetch_related("categories", "filters")
    )

    # ADDED: Make the existing search field functional. The search covers the
    # resource itself, source/curator information, and category names.
    if search_query:
        resources = resources.filter(
            Q(resource_title__icontains=search_query)
            | Q(resource_snippet__icontains=search_query)
            | Q(source__source_name__icontains=search_query)
            | Q(source__source_domain__icontains=search_query)
            | Q(curator__user_fname__icontains=search_query)
            | Q(curator__user_lname__icontains=search_query)
            | Q(categories__category_name__icontains=search_query)
        )

    # ADDED: Values selected inside one group are OR choices because __in is
    # used. Chaining the three group filters gives AND behavior across groups.
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

    # ADDED: distinct() prevents duplicate resource cards when joins match more
    # than one category. Convert to a list before adding display-only fields.
    resources = list(
        resources
        .distinct()
        .order_by("-resource_add_date")
    )

    for resource in resources:
        # Existing behavior retained: this displays the first Filter associated
        # with the resource. In current prototype data this is a Difficulty filter.
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
        # ADDED: Dropdown options and selected values are passed back to the
        # template so selections remain visible after the GET form is submitted.
        "skill_options": skill_options,
        "degree_program_options": degree_program_options,
        "career_field_options": career_field_options,
        "selected_skills": selected_skills,
        "selected_degree_programs": selected_degree_programs,
        "selected_career_fields": selected_career_fields,
        "search_query": search_query,
        # ADDED: Returned to the template so the selected mode and matching
        # placeholder survive a submitted search or category-filter request.
        "search_mode": search_mode,
    }
    return render(request, "landing/index.html", context)
