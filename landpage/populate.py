import os

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "landpage.settings",
)

import django

django.setup()

from django.contrib.auth import get_user_model
from django.apps import apps
from django.utils import timezone
from datetime import timedelta



# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

User = apps.get_model("landing", "User")
Source = apps.get_model("landing", "Source")
PriceModel = apps.get_model("landing", "PriceModel")
Category = apps.get_model("landing", "Category")
Filter = apps.get_model("landing", "Filter")
Resource = apps.get_model("landing", "Resource")
CuratedCollection = apps.get_model("landing", "CuratedCollection")
ResourceCategory = apps.get_model("landing", "ResourceCategory")
ResourceFilter = apps.get_model("landing", "ResourceFilter")
CollectionResource = apps.get_model("landing", "CollectionResource")


# ---------------------------------------------------------
# Clear existing prototype data
# ---------------------------------------------------------

print("Clearing existing prototype data...")

CollectionResource.objects.all().delete()
ResourceFilter.objects.all().delete()
ResourceCategory.objects.all().delete()
Resource.objects.all().delete()
CuratedCollection.objects.all().delete()
Category.objects.all().delete()
Filter.objects.all().delete()
Source.objects.all().delete()
PriceModel.objects.all().delete()
User.objects.all().delete()


# ---------------------------------------------------------
# Users
# ---------------------------------------------------------

print("Creating users...")

curator_1 = User.objects.create(
    user_fname="Alex",
    user_lname="Morgan",
    user_email="alex.morgan@example.com",
    user_role="curator",
    user_status="active",
)

curator_2 = User.objects.create(
    user_fname="Jamie",
    user_lname="Rivera",
    user_email="jamie.rivera@example.com",
    user_role="curator",
    user_status="active",
)

student_1 = User.objects.create(
    user_fname="Taylor",
    user_lname="Chen",
    user_email="taylor.chen@example.com",
    user_role="student",
    user_status="active",
)

student_2 = User.objects.create(
    user_fname="Jordan",
    user_lname="Brooks",
    user_email="jordan.brooks@example.com",
    user_role="student",
    user_status="active",
)


# ---------------------------------------------------------
# Price Models
# ---------------------------------------------------------

print("Creating price models...")

free = PriceModel.objects.create(
    price_model_name="free",
    is_active=True,
)

freemium = PriceModel.objects.create(
    price_model_name="freemium",
    is_active=True,
)

paid_subscription = PriceModel.objects.create(
    price_model_name="paid_subscription",
    is_active=True,
)

paid_one_time = PriceModel.objects.create(
    price_model_name="paid_one_time",
    is_active=True,
)


# ---------------------------------------------------------
# Sources
# ---------------------------------------------------------

print("Creating sources...")

sources = {}

source_data = [
    ("CareerHub", "careerhub.example.com"),
    ("SkillForge", "skillforge.example.com"),
    ("University Career Center", "career.example.edu"),
    ("Professional Pathways", "pathways.example.org"),
    ("TechLaunch", "techlaunch.example.com"),
    ("Science Careers Network", "sciencecareers.example.org"),
]

for name, domain in source_data:
    sources[name] = Source.objects.create(
        curator=curator_1,
        source_name=name,
        source_domain=domain,
        source_trust="trusted",
        is_active=True,
    )


# ---------------------------------------------------------
# Categories
# ---------------------------------------------------------

print("Creating categories...")

categories = {}

category_data = [
    ("Skill", "Resume Writing"),
    ("Skill", "CV Writing"),
    ("Skill", "Interview Skills"),
    ("Skill", "Networking"),
    ("Skill", "Job Searching"),
    ("Skill", "Professional Communication"),
    ("Skill", "LinkedIn"),
    ("Skill", "Cover Letters"),
    ("Skill", "Portfolio Development"),
    ("Skill", "Career Planning"),

    ("Degree Program", "Computer Science"),
    ("Degree Program", "Forestry"),
    ("Degree Program", "Biology"),
    ("Degree Program", "Marine Biology"),
    ("Degree Program", "Data Science"),
    ("Degree Program", "Mathematics"),

    ("Career Field", "Software Development"),
    ("Career Field", "Environmental Science"),
    ("Career Field", "Biological Science"),
    ("Career Field", "Data Analytics"),
]

for category_type, category_name in category_data:
    categories[category_name] = Category.objects.create(
        curator=curator_1,
        category_type=category_type,
        category_name=category_name,
        is_active=True,
    )


# ---------------------------------------------------------
# Filter
# ---------------------------------------------------------

print("Creating filter...")

beginner_filter = Filter.objects.create(
    curator=curator_1,
    filter_type="Difficulty",
    filter_name="Beginner Friendly",
    is_active=True,
)


# ---------------------------------------------------------
# Curated Collections
# ---------------------------------------------------------

print("Creating collections...")

career_collection = CuratedCollection.objects.create(
    curator=curator_1,
    collection_name="Career Foundations",
    collection_description=(
        "Essential resources for students beginning their career "
        "and professional development journey."
    ),
    is_active=True,
)

job_search_collection = CuratedCollection.objects.create(
    curator=curator_2,
    collection_name="Job Search Essentials",
    collection_description=(
        "Resources covering resumes, interviews, networking, "
        "applications, and professional communication."
    ),
    is_active=True,
)

stem_collection = CuratedCollection.objects.create(
    curator=curator_2,
    collection_name="STEM Career Paths",
    collection_description=(
        "Career resources tailored toward STEM degree programs "
        "and related professional fields."
    ),
    is_active=True,
)


# ---------------------------------------------------------
# Resources
# ---------------------------------------------------------

print("Creating resources...")


resource_data = [

    # -----------------------------------------------------
    # General Career Skills
    # -----------------------------------------------------

    {
        "title": "Building a Strong Entry-Level Resume",
        "type": "article",
        "format": "webpage",
        "source": "CareerHub",
        "price": free,
        "categories": ["Resume Writing", "Job Searching"],
        "description": "A practical guide to creating a resume for early-career job seekers.",
    },

    {
        "title": "Resume Achievement Statements",
        "type": "tutorial",
        "format": "webpage",
        "source": "SkillForge",
        "price": free,
        "categories": ["Resume Writing"],
        "description": "Learn how to turn responsibilities into measurable resume accomplishments.",
    },

    {
        "title": "Creating an Effective CV",
        "type": "article",
        "format": "PDF",
        "source": "University Career Center",
        "price": free,
        "categories": ["CV Writing"],
        "description": "An introductory guide to academic and professional CV structure.",
    },

    {
        "title": "Interview Preparation Fundamentals",
        "type": "course",
        "format": "video",
        "source": "CareerHub",
        "price": freemium,
        "categories": ["Interview Skills"],
        "description": "Practice common interview questions and prepare concise responses.",
    },

    {
        "title": "Behavioral Interview Questions",
        "type": "tutorial",
        "format": "webpage",
        "source": "Professional Pathways",
        "price": free,
        "categories": ["Interview Skills"],
        "description": "Strategies for answering behavioral interview questions using structured examples.",
    },

    {
        "title": "Technical Interview Preparation",
        "type": "course",
        "format": "video",
        "source": "TechLaunch",
        "price": paid_subscription,
        "categories": ["Interview Skills"],
        "description": "Practice technical interview preparation and problem-solving techniques.",
    },

    {
        "title": "Networking Without Feeling Awkward",
        "type": "article",
        "format": "webpage",
        "source": "CareerHub",
        "price": free,
        "categories": ["Networking"],
        "description": "Practical approaches to building professional relationships.",
    },

    {
        "title": "How to Search for Your First Professional Job",
        "type": "tutorial",
        "format": "webpage",
        "source": "University Career Center",
        "price": free,
        "categories": ["Job Searching", "Career Planning"],
        "description": "A beginner-friendly job search process from identifying roles to applying.",
    },

    {
        "title": "Writing a Professional Cover Letter",
        "type": "article",
        "format": "webpage",
        "source": "CareerHub",
        "price": free,
        "categories": ["Cover Letters"],
        "description": "Learn how to write concise and targeted cover letters.",
    },

    {
        "title": "Building Your Professional LinkedIn Profile",
        "type": "tutorial",
        "format": "webpage",
        "source": "Professional Pathways",
        "price": free,
        "categories": ["LinkedIn", "Networking"],
        "description": "Improve your LinkedIn profile and professional online presence.",
    },

    {
        "title": "Creating a Student Portfolio",
        "type": "course",
        "format": "video",
        "source": "SkillForge",
        "price": freemium,
        "categories": ["Portfolio Development"],
        "description": "Build a portfolio that demonstrates projects, skills, and accomplishments.",
    },

    {
        "title": "Professional Email Communication",
        "type": "article",
        "format": "webpage",
        "source": "University Career Center",
        "price": free,
        "categories": ["Professional Communication"],
        "description": "Guidelines for writing clear and professional workplace emails.",
    },

    {
        "title": "Planning Your Career After Graduation",
        "type": "tutorial",
        "format": "webpage",
        "source": "Professional Pathways",
        "price": free,
        "categories": ["Career Planning"],
        "description": "A framework for exploring career options and planning post-graduation goals.",
    },

    {
        "title": "Translating Class Projects Into Resume Experience",
        "type": "article",
        "format": "webpage",
        "source": "CareerHub",
        "price": free,
        "categories": ["Resume Writing", "Portfolio Development"],
        "description": "How students can turn academic projects into compelling professional experience.",
    },

    {
        "title": "Job Application Tracking for Students",
        "type": "tutorial",
        "format": "webpage",
        "source": "SkillForge",
        "price": free,
        "categories": ["Job Searching"],
        "description": "Simple methods for organizing applications, interviews, and follow-ups.",
    },

    {
        "title": "Professional Communication Basics",
        "type": "course",
        "format": "video",
        "source": "Professional Pathways",
        "price": paid_one_time,
        "categories": ["Professional Communication"],
        "description": "Fundamental communication skills for entering the workplace.",
    },

    {
        "title": "Preparing Questions for an Interview",
        "type": "article",
        "format": "webpage",
        "source": "CareerHub",
        "price": free,
        "categories": ["Interview Skills"],
        "description": "How to prepare thoughtful questions to ask employers during interviews.",
    },

    {
        "title": "Finding Entry-Level Opportunities",
        "type": "tutorial",
        "format": "webpage",
        "source": "University Career Center",
        "price": free,
        "categories": ["Job Searching"],
        "description": "Strategies for finding internships, entry-level positions, and graduate opportunities.",
    },

    {
        "title": "Career Fair Preparation Guide",
        "type": "article",
        "format": "PDF",
        "source": "University Career Center",
        "price": free,
        "categories": ["Networking", "Job Searching"],
        "description": "Prepare for career fairs and make meaningful connections with employers.",
    },

    {
        "title": "Building Confidence in Professional Settings",
        "type": "course",
        "format": "video",
        "source": "Professional Pathways",
        "price": freemium,
        "categories": ["Professional Communication", "Career Planning"],
        "description": "Strategies for becoming more comfortable in professional environments.",
    },

    {
        "title": "Evaluating a Job Offer",
        "type": "article",
        "format": "webpage",
        "source": "CareerHub",
        "price": free,
        "categories": ["Career Planning"],
        "description": "Factors to consider when comparing compensation, benefits, responsibilities, and growth opportunities.",
    },


    # -----------------------------------------------------
    # Computer Science
    # -----------------------------------------------------

    {
        "title": "Software Developer Career Guide",
        "type": "article",
        "format": "webpage",
        "source": "TechLaunch",
        "price": free,
        "categories": ["Computer Science", "Software Development", "Career Planning"],
        "description": "Overview of common software development careers and entry-level expectations.",
    },

    {
        "title": "Building a Software Development Portfolio",
        "type": "tutorial",
        "format": "webpage",
        "source": "TechLaunch",
        "price": free,
        "categories": ["Computer Science", "Portfolio Development"],
        "description": "How computer science students can present projects and technical skills.",
    },

    {
        "title": "Preparing for Coding Interviews",
        "type": "course",
        "format": "video",
        "source": "TechLaunch",
        "price": paid_subscription,
        "categories": ["Computer Science", "Interview Skills"],
        "description": "Practice algorithms, data structures, and common coding interview patterns.",
    },


    # -----------------------------------------------------
    # Forestry
    # -----------------------------------------------------

    {
        "title": "Careers in Forestry",
        "type": "article",
        "format": "webpage",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Forestry", "Environmental Science", "Career Planning"],
        "description": "Explore careers in forest management, conservation, and natural resources.",
    },

    {
        "title": "Forestry Field Skills and Career Preparation",
        "type": "tutorial",
        "format": "PDF",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Forestry", "Environmental Science"],
        "description": "Career preparation resources for students pursuing forestry field positions.",
    },


    # -----------------------------------------------------
    # Biology
    # -----------------------------------------------------

    {
        "title": "Biology Career Paths",
        "type": "article",
        "format": "webpage",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Biology", "Biological Science", "Career Planning"],
        "description": "Overview of career options available to biology graduates.",
    },

    {
        "title": "Laboratory Skills for Biology Graduates",
        "type": "tutorial",
        "format": "webpage",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Biology", "Biological Science"],
        "description": "Professional skills commonly used in laboratory environments.",
    },


    # -----------------------------------------------------
    # Marine Biology
    # -----------------------------------------------------

    {
        "title": "Careers in Marine Biology",
        "type": "article",
        "format": "webpage",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Marine Biology", "Biological Science"],
        "description": "Explore research, conservation, fieldwork, and environmental careers in marine biology.",
    },

    {
        "title": "Marine Science Field Research Careers",
        "type": "tutorial",
        "format": "PDF",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Marine Biology", "Biological Science"],
        "description": "Career preparation for marine science field research positions.",
    },


    # -----------------------------------------------------
    # Data Science
    # -----------------------------------------------------

    {
        "title": "Starting a Data Science Career",
        "type": "article",
        "format": "webpage",
        "source": "TechLaunch",
        "price": free,
        "categories": ["Data Science", "Data Analytics", "Career Planning"],
        "description": "An introduction to data science career paths and entry-level roles.",
    },

    {
        "title": "Data Science Portfolio Projects",
        "type": "tutorial",
        "format": "webpage",
        "source": "TechLaunch",
        "price": freemium,
        "categories": ["Data Science", "Portfolio Development"],
        "description": "Ideas and guidance for creating data science projects for a professional portfolio.",
    },


    # -----------------------------------------------------
    # Mathematics
    # -----------------------------------------------------

    {
        "title": "Careers for Mathematics Graduates",
        "type": "article",
        "format": "webpage",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Mathematics", "Career Planning"],
        "description": "Explore career options in education, analytics, finance, technology, and research.",
    },

    {
        "title": "Mathematics Skills in the Workplace",
        "type": "tutorial",
        "format": "webpage",
        "source": "Science Careers Network",
        "price": free,
        "categories": ["Mathematics", "Data Analytics"],
        "description": "Examples of how mathematical reasoning translates into professional skills.",
    },
]


# ---------------------------------------------------------
# Create resources
# ---------------------------------------------------------

resources = []

for index, data in enumerate(resource_data, start=1):

    resource = Resource.objects.create(
        curator=curator_1 if index % 2 else curator_2,
        is_anonymous=False,
        source=sources[data["source"]],
        resource_title=data["title"],
        resource_url=f"https://{sources[data['source']].source_domain}/resource/{index}",
        resource_type=data["type"],
        resource_snippet=data["description"],
        resource_format=data["format"],
        resource_duration_seconds=(
            900 + (index * 137)
            if data["format"] == "video"
            else None
        ),
        price_model=data["price"],
        price_reviewed=True,
        price_reviewed_by=curator_1,
        price_reviewed_date=timezone.now(),
        other_metadata={
            "prototype": True,
            "difficulty": "beginner",
        },
    )

    resources.append(resource)

    # Categories
    for category_name in data["categories"]:
        ResourceCategory.objects.create(
            resource=resource,
            category=categories[category_name],
        )

    # Apply the one demonstration filter to some resources
    if index % 3 == 0:
        ResourceFilter.objects.create(
            resource=resource,
            filter=beginner_filter,
        )


# ---------------------------------------------------------
# Collections
# ---------------------------------------------------------

print("Adding resources to collections...")

career_titles = {
    "Building a Strong Entry-Level Resume",
    "Resume Achievement Statements",
    "Creating an Effective CV",
    "Interview Preparation Fundamentals",
    "Behavioral Interview Questions",
    "Networking Without Feeling Awkward",
    "How to Search for Your First Professional Job",
    "Writing a Professional Cover Letter",
    "Building Your Professional LinkedIn Profile",
    "Creating a Student Portfolio",
    "Professional Email Communication",
    "Planning Your Career After Graduation",
}

job_search_titles = {
    "Building a Strong Entry-Level Resume",
    "Resume Achievement Statements",
    "Interview Preparation Fundamentals",
    "Behavioral Interview Questions",
    "Preparing Questions for an Interview",
    "Finding Entry-Level Opportunities",
    "Career Fair Preparation Guide",
    "Evaluating a Job Offer",
}

stem_titles = {
    "Software Developer Career Guide",
    "Building a Software Development Portfolio",
    "Preparing for Coding Interviews",
    "Careers in Forestry",
    "Biology Career Paths",
    "Careers in Marine Biology",
    "Starting a Data Science Career",
    "Data Science Portfolio Projects",
    "Careers for Mathematics Graduates",
}


for sort_order, resource in enumerate(resources, start=1):
    if resource.resource_title in career_titles:
        CollectionResource.objects.create(
            collection=career_collection,
            resource=resource,
            sort_order=sort_order,
        )

    if resource.resource_title in job_search_titles:
        CollectionResource.objects.create(
            collection=job_search_collection,
            resource=resource,
            sort_order=sort_order,
        )

    if resource.resource_title in stem_titles:
        CollectionResource.objects.create(
            collection=stem_collection,
            resource=resource,
            sort_order=sort_order,
        )


print()
print("=" * 50)
print("Prototype database populated successfully!")
print("=" * 50)
print(f"Users:       {User.objects.count()}")
print(f"Sources:     {Source.objects.count()}")
print(f"Categories:  {Category.objects.count()}")
print(f"Filters:     {Filter.objects.count()}")
print(f"Prices:      {PriceModel.objects.count()}")
print(f"Resources:   {Resource.objects.count()}")
print(f"Collections: {CuratedCollection.objects.count()}")
print("=" * 50)