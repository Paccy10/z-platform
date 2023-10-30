from django.urls import include, path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator


class SchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]

        return schema


schema_view = get_schema_view(
    openapi.Info(
        title="ZPlatform API Documentation",
        default_version="v1",
        description="This is ZPlatform API Documentation",
        contact=openapi.Contact(email="info@zplatform.com"),
    ),
    public=True,
    generator_class=SchemaGenerator,
)

urlpatterns = [
    path(
        "documentation/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="swagger-doc",
    ),
    path("users/", include("apps.users.urls")),
]
