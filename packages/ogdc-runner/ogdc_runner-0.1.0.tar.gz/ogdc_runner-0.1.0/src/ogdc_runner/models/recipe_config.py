from __future__ import annotations

from functools import cached_property
from typing import Literal

from pydantic import AnyUrl, BaseModel, Field, computed_field, field_validator


# Input parameter with type and value
class InputParam(BaseModel):
    value: AnyUrl | str
    type: Literal["url", "pvc_mount", "file_system"]


# Create a model for the recipe input
class RecipeInput(BaseModel):
    params: list[InputParam]

    @field_validator("params")
    def validate_params(cls, params: list[InputParam]) -> list[InputParam]:
        """Ensure there's at least one input parameter."""
        if not params:
            error_msg = "At least one input parameter is required"
            raise ValueError(error_msg)
        return params


class RecipeOutput(BaseModel):
    dataone_id: str = "TODO"


class RecipeMeta(BaseModel):
    """Model for a recipe's metadata (`meta.yaml`)."""

    # Allow alphanumeric characters, `.`, ` ` (space), and `,`.
    # The name is used to create an ID for the recipe that must be k8s-compliant
    # (lower-case, alphanumeric characters, `.`, and `,`).
    name: str = Field(..., pattern=r"^[a-zA-Z0-9 .-]+$")

    # Type of recipe, e.g., "shell", "visualization", etc.
    type: Literal["shell", "visualization"]

    input: RecipeInput
    output: RecipeOutput = RecipeOutput()

    # Optional Docker image (supports both local and hosted images)
    # Examples: "my-local-image", "ghcr.io/owner/image:latest"
    image: str | None = Field(
        default=None, description="Docker image with optional tag"
    )


class RecipeConfig(RecipeMeta):
    """Model for a recipe's configuration.

    This includes the data in `meta.yaml`, plus some internal metadata/config
    that is generated dynamically at runtime (e.g., `recipe_directory`).
    """

    # ffspec-compatible recipe directory string.
    # This is where the rest of the config was set from.
    recipe_directory: str

    @computed_field  # type: ignore[misc]
    @cached_property
    def id(self) -> str:
        k8s_name = self.name.lower().replace(" ", "-")

        return k8s_name


class RecipeImage(BaseModel):
    """
    Image configuration for the recipe.

    Supports both local and hosted Docker images.
    """

    image: str = Field(..., description="Docker image name")
    tag: str = Field(default="latest", description="Docker image tag")

    @property
    def full_image_path(self) -> str:
        """Return the full image path including tag."""
        return f"{self.image}:{self.tag}"
