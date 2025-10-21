import pytest
import urllib3

from cli.config import Config
from hafnia.dataset.dataset_names import OPS_REMOVE_CLASS
from hafnia.dataset.dataset_recipe.dataset_recipe import (
    DatasetRecipe,
)
from hafnia.platform.dataset_recipe import (
    delete_dataset_recipe_by_id,
    delete_dataset_recipe_by_name,
    get_dataset_recipe_by_id,
)
from hafnia.utils import is_hafnia_configured


def test_dataset_recipe_on_platform():
    if not is_hafnia_configured():
        pytest.skip("Hafnia is not configured, skipping build dataset recipe tests.")

    # Prepare test
    cfg = Config()
    endpoint = cfg.get_platform_endpoint("dataset_recipes")
    dataset_recipe_name = "test-complex-recipe"
    # Ensure dataset recipe is deleted before test
    delete_dataset_recipe_by_name(name=dataset_recipe_name, endpoint=endpoint, api_key=cfg.api_key)

    mappings_coco = {
        "person": "Person",
        "bicycle": "Vehicle",
        "car": "Vehicle",
        "motorcycle": "Vehicle",
        "bus": "Vehicle",
        "train": "Vehicle",
        "truck": "Vehicle",
    }
    mapping_midwest = {
        "Person": "Person",
        "Vehicle.*": "Vehicle",
        "Vehicle.Trailer": OPS_REMOVE_CLASS,
    }

    # Recreate as recipe
    dataset_recipe = DatasetRecipe.from_merger(
        recipes=[
            DatasetRecipe.from_name(name="midwest-vehicle-detection-tiny").class_mapper(
                class_mapping=mapping_midwest, task_name="bboxes"
            ),
            DatasetRecipe.from_name(name="coco-2017-tiny").class_mapper(
                class_mapping=mappings_coco, method="remove_undefined", task_name="bboxes"
            ),
        ]
    )

    # Test case1: Upload and return dataset recipe on platform
    response = dataset_recipe.as_platform_recipe(recipe_name=dataset_recipe_name)
    dataset_recipe_again = DatasetRecipe.from_recipe_name(name=dataset_recipe_name)
    dataset_recipe_id = response["id"]
    assert dataset_recipe == dataset_recipe_again

    # Test case 2: Uploading again will return the same dataset recipe id
    response = dataset_recipe.as_platform_recipe(recipe_name=dataset_recipe_name)
    dataset_recipe_id_again = response["id"]
    assert dataset_recipe_id == dataset_recipe_id_again

    # Test case 3: Get dataset recipe by id
    response = get_dataset_recipe_by_id(dataset_recipe_id, endpoint=endpoint, api_key=cfg.api_key)

    # Test case 4: Delete recipe by id
    delete_dataset_recipe_by_id(dataset_recipe_id, endpoint=endpoint, api_key=cfg.api_key)

    # Verify deletion
    with pytest.raises(urllib3.exceptions.HTTPError, match="Request failed with status 404"):
        get_dataset_recipe_by_id(dataset_recipe_id, endpoint=endpoint, api_key=cfg.api_key)
