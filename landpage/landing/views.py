from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.urls import reverse

from resource_discovery.search import search_resources

from .models import Category, CuratedCollection


LAST_COLLECTION_SEARCH = "last_collection_search"
LAST_WEB_SEARCH = "last_web_search"


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
    """Load the three topbar taxonomy groups from the database."""
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


def apply_collection_category_filters(
    collections,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Filter collections through the categories of their contained resources.

    Values within one taxonomy group are OR choices via __in. Chaining the
    groups gives AND behavior across Skill, Degree Program, and Career Field.
    """
    if selected_skills:
        collections = collections.filter(
            resources__categories__category_type="Skill",
            resources__categories__category_name__in=selected_skills,
        )

    if selected_degree_programs:
        collections = collections.filter(
            resources__categories__category_type="Degree Program",
            resources__categories__category_name__in=selected_degree_programs,
        )

    if selected_career_fields:
        collections = collections.filter(
            resources__categories__category_type="Career Field",
            resources__categories__category_name__in=selected_career_fields,
        )

    return collections


def prepare_collection_cards(collections):
    """Add compact preview data used by the stacked collection cards."""
    collections = list(collections)

    for collection in collections:
        # ADDED: Show a small taxonomy preview without duplicating every category
        # present in the collection. The full collection detail view can expose
        # more later when that route is implemented.
        category_names = []
        seen_names = set()

        for resource in collection.resources.all():
            for category in resource.categories.all():
                if category.category_name not in seen_names:
                    seen_names.add(category.category_name)
                    category_names.append(category.category_name)

        collection.display_categories = category_names[:4]

    return collections


def search_local_collections(
    search_query,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Return active CuratedCollection objects for Collections mode.

    ADDED: Collections mode now renders one card per collection rather than
    flattening matching collections into individual Resource cards. This makes
    the stacked-card presentation semantically represent a group of resources.
    """
    collections = (
        CuratedCollection.objects
        .filter(is_active=True)
        .prefetch_related("resources__categories")
    )

    if search_query:
        collections = collections.filter(
            Q(collection_name__icontains=search_query)
            | Q(collection_description__icontains=search_query)
        )

    collections = apply_collection_category_filters(
        collections,
        selected_skills,
        selected_degree_programs,
        selected_career_fields,
    )

    collections = (
        collections
        .annotate(resource_count=Count("resources", distinct=True))
        .distinct()
        .order_by("collection_name")
    )

    return prepare_collection_cards(collections)


def restore_local_collections(collection_ids):
    """Restore cached Collections results using inexpensive local IDs."""
    if not collection_ids:
        return []

    collections = (
        CuratedCollection.objects
        .filter(collection_id__in=collection_ids, is_active=True)
        .prefetch_related("resources__categories")
        .annotate(resource_count=Count("resources", distinct=True))
    )

    collections_by_id = {
        collection.collection_id: collection
        for collection in collections
    }

    ordered_collections = [
        collections_by_id[collection_id]
        for collection_id in collection_ids
        if collection_id in collections_by_id
    ]

    return prepare_collection_cards(ordered_collections)


def search_web_resources(
    search_query,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Call Resource Discovery and return transient normalized dictionaries."""
    discovery_filters = {
        "skills": selected_skills,
        "degree_programs": selected_degree_programs,
        "career_fields": selected_career_fields,
    }

    results = search_resources(
        search_query,
        filters=discovery_filters,
    )

    for result in results:
        result["display_duration"] = format_duration(
            result.get("duration_seconds")
        )

    return results


def build_search_state(
    search_query,
    selected_skills,
    selected_degree_programs,
    selected_career_fields,
):
    """Return the serializable form state shared by both cached search modes."""
    return {
        "query": search_query,
        "skills": list(selected_skills),
        "degree_programs": list(selected_degree_programs),
        "career_fields": list(selected_career_fields),
    }


def index(request):
    """Coordinate new searches and instant swaps to cached previous results."""
    # Existing behavior: swap_to restores the previous result set instead of
    # executing either search backend again.
    swap_to = request.GET.get("swap_to")
    if swap_to in {"collections", "web"}:
        session_key = (
            LAST_COLLECTION_SEARCH
            if swap_to == "collections"
            else LAST_WEB_SEARCH
        )
        cached_search = request.session.get(session_key)

        if cached_search:
            request.session["display_cached_search"] = {
                "mode": swap_to,
                "cache_key": session_key,
            }
            return redirect(reverse("index"))

    displayed_cache = request.session.pop("display_cached_search", None)
    cached_search = None

    if displayed_cache and not request.GET:
        search_mode = displayed_cache.get("mode", "collections")
        cached_search = request.session.get(displayed_cache.get("cache_key"))
    else:
        search_mode = request.GET.get("search_mode", "collections")

    if search_mode not in {"collections", "web"}:
        search_mode = "collections"

    if cached_search:
        search_query = cached_search.get("query", "")
        selected_skills = cached_search.get("skills", [])
        selected_degree_programs = cached_search.get("degree_programs", [])
        selected_career_fields = cached_search.get("career_fields", [])
    else:
        search_query = request.GET.get("search", "").strip()
        selected_skills = request.GET.getlist("skill")
        selected_degree_programs = request.GET.getlist("degree_program")
        selected_career_fields = request.GET.getlist("career_field")

    category_options = get_category_options()

    collections = []
    discovery_results = []
    discovery_error = None

    has_discovery_intent = any(
        (
            selected_skills,
            selected_degree_programs,
            selected_career_fields,
        )
    )
    discovery_attempted = bool(search_query or has_discovery_intent)

    if search_mode == "web":
        if cached_search:
            # Reuse normalized Resource Discovery dictionaries. This performs no
            # Brave API request and no candidate-page scraping.
            discovery_results = cached_search.get("results", [])
            discovery_attempted = cached_search.get("attempted", True)
        elif discovery_attempted:
            try:
                discovery_results = search_web_resources(
                    search_query,
                    selected_skills,
                    selected_degree_programs,
                    selected_career_fields,
                )

                web_cache = build_search_state(
                    search_query,
                    selected_skills,
                    selected_degree_programs,
                    selected_career_fields,
                )
                web_cache.update(
                    {
                        "results": discovery_results,
                        "attempted": True,
                    }
                )
                request.session[LAST_WEB_SEARCH] = web_cache
            except Exception as exc:
                discovery_error = f"Web resource search failed: {exc}"
    else:
        if cached_search:
            # UPDATED: Collections cache now stores collection IDs because the
            # Collections view renders collection cards rather than resources.
            collections = restore_local_collections(
                cached_search.get("collection_ids", [])
            )
        else:
            collections = search_local_collections(
                search_query,
                selected_skills,
                selected_degree_programs,
                selected_career_fields,
            )

            collection_cache = build_search_state(
                search_query,
                selected_skills,
                selected_degree_programs,
                selected_career_fields,
            )
            collection_cache["collection_ids"] = [
                collection.collection_id
                for collection in collections
            ]
            request.session[LAST_COLLECTION_SEARCH] = collection_cache

    # Existing yellow swap button remains available only when the other mode has
    # a cached result set in this user's session.
    if search_mode == "web":
        swap_target = (
            "collections"
            if request.session.get(LAST_COLLECTION_SEARCH)
            else None
        )
        swap_label = "Last Collection Search" if swap_target else None
    else:
        swap_target = (
            "web"
            if request.session.get(LAST_WEB_SEARCH)
            else None
        )
        swap_label = "Last Web Search" if swap_target else None

    context = {
        # ADDED: Collections mode now exposes collection-level cards/counts.
        "collections": collections,
        "collection_count": len(collections),
        "discovery_results": discovery_results,
        "discovery_count": len(discovery_results),
        "discovery_error": discovery_error,
        "discovery_attempted": discovery_attempted,
        "selected_skills": selected_skills,
        "selected_degree_programs": selected_degree_programs,
        "selected_career_fields": selected_career_fields,
        "search_query": search_query,
        "search_mode": search_mode,
        "swap_target": swap_target,
        "swap_label": swap_label,
        **category_options,
    }

    return render(request, "landing/index.html", context)
