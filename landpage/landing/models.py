from django.db import models


class User(models.Model):
    user_id = models.CharField(
        db_column="acc_id",
        max_length=8,
        primary_key=True,
    )
    user_fname = models.CharField(db_column="acc_fname", max_length=100)
    user_lname = models.CharField(db_column="acc_lname", max_length=100)
    user_email = models.CharField(
        db_column="acc_email",
        max_length=50,
        unique=True,
    )
    user_role = models.CharField(db_column="acc_role", max_length=10)
    user_status = models.CharField(db_column="acc_status", max_length=20)

    class Meta:
        managed = False
        db_table = "account"

    def __str__(self):
        return f"{self.user_fname} {self.user_lname}"


class Source(models.Model):
    source_id = models.CharField(max_length=8, primary_key=True)
    curator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="sources",
    )
    source_name = models.CharField(max_length=50, null=True, blank=True)
    source_domain = models.CharField(max_length=253, null=True, blank=True)
    source_trust = models.CharField(max_length=7)
    source_add_date = models.DateTimeField()
    source_up_date = models.DateTimeField(null=True, blank=True)
    is_active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "source"

    def __str__(self):
        return self.source_name or ""


class PriceModel(models.Model):
    price_model_id = models.CharField(max_length=8, primary_key=True)
    price_model_name = models.CharField(max_length=20, unique=True)
    is_active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "price_model"

    def __str__(self):
        return self.price_model_name


class Category(models.Model):
    category_id = models.CharField(max_length=8, primary_key=True)
    curator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="categories",
    )
    category_type = models.CharField(max_length=20)
    category_name = models.CharField(max_length=100)
    is_active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "category"
        unique_together = (("category_type", "category_name"),)

    def __str__(self):
        return self.category_name


class Filter(models.Model):
    filter_id = models.CharField(max_length=8, primary_key=True)
    curator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="filters",
    )
    filter_type = models.CharField(max_length=30)
    filter_name = models.CharField(max_length=30)
    is_active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "filter"
        unique_together = (("filter_type", "filter_name"),)

    def __str__(self):
        return self.filter_name


class Resource(models.Model):
    resource_id = models.CharField(max_length=8, primary_key=True)
    curator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="resources",
    )
    is_anonymous = models.CharField(max_length=1)
    source = models.ForeignKey(
        Source,
        on_delete=models.DO_NOTHING,
        related_name="resources",
    )
    resource_title = models.CharField(max_length=150)
    resource_url = models.CharField(max_length=767, unique=True)
    resource_type = models.CharField(max_length=15)
    resource_format = models.CharField(max_length=20)
    resource_snippet = models.TextField(null=True, blank=True)
    resource_pub_date = models.DateTimeField(null=True, blank=True)
    resource_refresh_date = models.DateTimeField()
    resource_duration = models.PositiveBigIntegerField(null=True, blank=True)
    price_model = models.ForeignKey(
        PriceModel,
        on_delete=models.DO_NOTHING,
        related_name="resources",
    )
    other_metadata = models.JSONField(null=True, blank=True)
    is_active = models.CharField(max_length=1)
    categories = models.ManyToManyField(
        Category,
        through="ResourceCategory",
        related_name="resources",
    )
    filters = models.ManyToManyField(
        Filter,
        through="ResourceFilter",
        related_name="resources",
    )
    collections = models.ManyToManyField(
        "CuratedCollection",
        through="CollectionResource",
        related_name="resources",
    )

    class Meta:
        managed = False
        db_table = "career_resource"

    def __str__(self):
        return self.resource_title


class CuratedCollection(models.Model):
    collection_id = models.CharField(max_length=8, primary_key=True)
    curator = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        related_name="collections",
    )
    collection_name = models.CharField(max_length=100)
    collection_description = models.TextField(null=True, blank=True)
    collection_add_date = models.DateTimeField()
    collection_up_date = models.DateTimeField(null=True, blank=True)
    is_active = models.CharField(max_length=1)

    class Meta:
        managed = False
        db_table = "curated_collection"

    def __str__(self):
        return self.collection_name


class ResourceCategory(models.Model):
    pk = models.CompositePrimaryKey("resource_id", "category_id")
    resource = models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "resource_category"

    def __str__(self):
        return f"{self.resource} - {self.category}"


class ResourceFilter(models.Model):
    pk = models.CompositePrimaryKey("resource_id", "filter_id")
    resource = models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
    filter = models.ForeignKey(Filter, on_delete=models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "resource_filter"

    def __str__(self):
        return f"{self.resource} - {self.filter}"


class CollectionResource(models.Model):
    pk = models.CompositePrimaryKey("collection_id", "resource_id")
    collection = models.ForeignKey(
        CuratedCollection,
        on_delete=models.DO_NOTHING,
    )
    resource = models.ForeignKey(Resource, on_delete=models.DO_NOTHING)
    sort_order = models.PositiveIntegerField()
    add_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = "collection_resources"

    def __str__(self):
        return f"{self.collection} - {self.resource}"
