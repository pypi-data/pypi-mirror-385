from pathlib import Path

from rich import print as rprint

from hafnia import utils
from hafnia.dataset.dataset_names import OPS_REMOVE_CLASS
from hafnia.dataset.dataset_recipe.dataset_recipe import DatasetRecipe
from hafnia.dataset.dataset_recipe.recipe_transforms import (
    SelectSamples,
    Shuffle,
    SplitsByRatios,
)
from hafnia.dataset.hafnia_dataset import HafniaDataset

### Introducing DatasetRecipe ###
# A DatasetRecipe is a recipe for the dataset you want to create.
# The recipe itself is not executed - this is just a specification of the dataset you want!

# The 'DatasetRecipe' interface is similar to the 'HafniaDataset' interface.
# To demonstrate, we will first create a dataset with the regular 'HafniaDataset' interface.
# This line will get the "mnist" dataset, shuffle it, and select 20 samples.
dataset = HafniaDataset.from_name(name="mnist").shuffle().select_samples(n_samples=20)

# Now the same dataset is created using the 'DatasetRecipe' interface.
dataset_recipe = DatasetRecipe.from_name(name="mnist").shuffle().select_samples(n_samples=20)
dataset = dataset_recipe.build()
# Note that the interface is similar, but to actually create the dataset you need to call `build()` on the recipe.

# Unlike the HafniaDataset, a DatasetRecipe does not execute operations. It only registers
# the operations applied to the recipe and can be used to build the dataset later.
# You can print the dataset recipe to the operations that were applied to it.
rprint(dataset_recipe)

# The key for recipes is that they can be saved and loaded as a JSON.
# This also allows the recipe to be saved, shared, loaded and used later to build a dataset
# in a different environment.

# Example: Saving and loading a dataset recipe from file.
path_recipe = Path(".data/dataset_recipes/example_recipe.json")
json_str: str = dataset_recipe.as_json_file(path_recipe)
dataset_recipe_again: DatasetRecipe = DatasetRecipe.from_json_file(path_recipe)

# Verify that the loaded recipe is identical to the original recipe.
assert dataset_recipe_again == dataset_recipe

# It is also possible to generate the recipe as python code
dataset_recipe.as_python_code()

# The recipe also allows you to combine multiple datasets and transformations that can be
# executed in the TaaS platform. This is demonstrated below:
if utils.is_hafnia_configured():  # First ensure you are connected to the hafnia platform
    # Upload the dataset recipe - this will make it available for TaaS and for users of your organization
    dataset_recipe.as_platform_recipe(recipe_name="example-mnist-recipe", overwrite=True)

    # The recipe is now available in TaaS, for different environments and other users in your organization
    dataset_recipe_again = DatasetRecipe.from_recipe_name(name="example-mnist-recipe")

    # Launch an experiment with the dataset recipe using the CLI:
    # hafnia experiment create --dataset-recipe example-mnist-recipe --trainer-path ../trainer-classification

    # Coming soon: Dataset recipes will be included in the web platform to them to be shared, managed
    # and used in experiments.

### More examples dataset recipes ###
# Example: 'DatasetRecipe' by merging multiple dataset recipes
dataset_recipe = DatasetRecipe.from_merger(
    recipes=[
        DatasetRecipe.from_name(name="mnist"),
        DatasetRecipe.from_name(name="mnist"),
    ]
)

# Example: Recipes can be infinitely nested and combined.
dataset_recipe = DatasetRecipe.from_merger(
    recipes=[
        DatasetRecipe.from_merger(
            recipes=[
                DatasetRecipe.from_name(name="mnist"),
                DatasetRecipe.from_name(name="mnist"),
            ]
        ),
        DatasetRecipe.from_path(path_folder=Path(".data/datasets/mnist"))
        .select_samples(n_samples=30)
        .splits_by_ratios(split_ratios={"train": 0.8, "val": 0.1, "test": 0.1}),
        DatasetRecipe.from_name(name="mnist").select_samples(n_samples=20).shuffle(),
    ]
)

# Now you can build the dataset from the recipe.
dataset: HafniaDataset = dataset_recipe.build()
assert len(dataset) == 450  # 2x200 + 30 + 20

# Finally, you can print the dataset recipe to see what it contains.
rprint(dataset_recipe)  # as a python object
print(dataset_recipe.as_json_str())  # as a JSON string


### Real-world Example: Merge datasets to create a Person+Vehicle dataset ###
# 1) The first step is to use the regular 'HafniaDataset' interface to investigate and understand the datasets

# 1a) Explore 'coco-2017'
coco = HafniaDataset.from_name("coco-2017")
coco.print_stats()  # Print dataset statistics
coco_class_names = coco.info.get_task_by_primitive("Bbox").class_names  # Get the class names for the bbox task
# You will notice coco has 80 classes including 'person' and various vehicle classes such as 'car', 'bus', 'truck', etc.
# but also many unrelated classes such as 'toaster', 'hair drier', etc.

# 1b) Explore 'midwest-vehicle-detection'
midwest = HafniaDataset.from_name("midwest-vehicle-detection")
midwest.print_stats()  # Print dataset statistics
midwest_class_names = midwest.info.get_task_by_primitive("Bbox").class_names
# You will also notice midwest has similar classes, but they are named differently, e.g. 'Persons',
# 'Vehicle.Car', 'Vehicle.Bicycle', etc.

# 2) We will now use the 'HafniaDataset' interface to verify operations (class remapping, merging, filtering)

# 2a) Remap class names to have the same class names across datasets
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
    "Vehicle*": "Vehicle",  # Wildcard mapping. Selects class names starting with 'Vehicle.' e.g. 'Vehicle.Bicycle', "Vehicle.Car', etc.
    "Vehicle.Trailer": OPS_REMOVE_CLASS,  # Use this to remove a class
}
coco_remapped = coco.class_mapper(class_mapping=mappings_coco, method="remove_undefined", task_name="bboxes")
midwest_remapped = midwest.class_mapper(class_mapping=mapping_midwest, task_name="bboxes")

# 2b) Merge datasets
merged_dataset_all_images = HafniaDataset.from_merge(dataset0=coco_remapped, dataset1=midwest_remapped)

# 2c) Remove images without 'Person' or 'Vehicle' annotations
merged_dataset = merged_dataset_all_images.select_samples_by_class_name(name=["Person", "Vehicle"], task_name="bboxes")
merged_dataset.print_stats()

# 3) Once you have verified operations using the 'HafniaDataset' interface, you can convert
# the operations to a single 'DatasetRecipe'
merged_recipe = DatasetRecipe.from_merge(
    recipe0=DatasetRecipe.from_name("coco-2017").class_mapper(
        class_mapping=mappings_coco, method="remove_undefined", task_name="bboxes"
    ),
    recipe1=DatasetRecipe.from_name("midwest-vehicle-detection").class_mapper(
        class_mapping=mapping_midwest, task_name="bboxes"
    ),
).select_samples_by_class_name(name=["Person", "Vehicle"], task_name="bboxes")

# 3a) Verify again on the sample datasets, that the recipe works and can build as a dataset
merged_dataset = merged_recipe.build()
merged_dataset.print_stats()

# 3b) Optionally: Save the recipe to file
path_recipe = Path(".data/dataset_recipes/example-merged-person-vehicle-recipe.json")
merged_recipe.as_json_file(path_recipe)
if utils.is_hafnia_configured():
    # 3c) Upload dataset recipe to Training-aaS platform
    recipe_response = merged_recipe.as_platform_recipe(recipe_name="person-vehicle-detection", overwrite=True)
    print(f"Recipe Name: '{recipe_response['name']}', Recipe id: '{recipe_response['id']}'")

    # 4) The recipe is now available in TaaS for you and other users in your organization
    # 4a) View recipes from your terminal with 'hafnia dataset-recipe ls'
    # 4b) (Coming soon) Or go to 'Dataset Recipes' in the TaaS web platform:  https://hafnia.milestonesys.com/training-aas/dataset-recipes

    # 5) Launch an experiment with the dataset:
    # 5a) Using the CLI:
    #   'hafnia experiment create --dataset-recipe person-vehicle-detection --trainer-path ../trainer-classification'
    # 5b) (Coming soon) Or through the TaaS web platform:  https://hafnia.milestonesys.com/training-aas/experiments

# 6) Monitor and manage your experiments
# 6a) View experiments using the web platform https://staging02.mdi.milestonesys.com/training-aas/experiments
# 6b) Or use the CLI: 'hafnia experiment ls'
### DatasetRecipe Implicit Form ###
# Below we demonstrate the difference between implicit and explicit forms of dataset recipes.
# Example: Get dataset by name with implicit and explicit forms
recipe_implicit_form = "mnist"
recipe_explicit_form = DatasetRecipe.from_name(name="mnist")

# The implicit form can now be loaded and built as a dataset
dataset_implicit = DatasetRecipe.from_implicit_form(recipe_implicit_form).build()
# Or directly as a dataset
dataset_implicit = HafniaDataset.from_recipe(recipe_implicit_form)


# Example: Get dataset from path with implicit and explicit forms:
recipe_implicit_form = Path(".data/datasets/mnist")
recipe_explicit_form = DatasetRecipe.from_path(path_folder=Path(".data/datasets/mnist"))

# Example: Merge datasets with implicit and explicit forms
recipe_implicit_form = ("mnist", "mnist")
recipe_explicit_form = DatasetRecipe.from_merger(
    recipes=[
        DatasetRecipe.from_name(name="mnist"),
        DatasetRecipe.from_name(name="mnist"),
    ]
)

# Example: Define a dataset with transformations using implicit and explicit forms
recipe_implicit_form = ["mnist", SelectSamples(n_samples=20), Shuffle()]
recipe_explicit_form = DatasetRecipe.from_name(name="mnist").select_samples(n_samples=20).shuffle()


# Example: Complex nested example with implicit vs explicit forms
# Implicit form of a complex dataset recipe
split_ratio = {"train": 0.8, "val": 0.1, "test": 0.1}
recipe_implicit_complex = (
    ("mnist", "mnist"),
    [Path(".data/datasets/mnist"), SelectSamples(n_samples=30), SplitsByRatios(split_ratios=split_ratio)],
    ["mnist", SelectSamples(n_samples=20), Shuffle()],
)

# Explicit form of the same complex dataset recipe
recipe_explicit_complex = DatasetRecipe.from_merger(
    recipes=[
        DatasetRecipe.from_merger(
            recipes=[
                DatasetRecipe.from_name(name="mnist"),
                DatasetRecipe.from_name(name="mnist"),
            ]
        ),
        DatasetRecipe.from_path(path_folder=Path(".data/datasets/mnist"))
        .select_samples(n_samples=30)
        .splits_by_ratios(split_ratios=split_ratio),
        DatasetRecipe.from_name(name="mnist").select_samples(n_samples=20).shuffle(),
    ]
)

# The implicit form uses the following rules:
#    str: Will get a dataset by name -> In explicit form it becomes 'DatasetRecipe.from_name'
#    Path: Will get a dataset from path -> In explicit form it becomes 'DatasetRecipe.from_path'
#    tuple: Will merge datasets specified in the tuple -> In explicit form it becomes 'DatasetRecipe.from_merger'
#    list: Will define a dataset followed by a list of transformations -> In explicit form it becomes chained method calls
# Generally, we recommend using the explicit form over the implicit form when multiple datasets and transformations are involved.


# To convert from implicit to explicit recipe form, you can use the `from_implicit_form` method.
explicit_recipe_from_implicit = DatasetRecipe.from_implicit_form(recipe_implicit_complex)
rprint("Converted explicit recipe:")
rprint(explicit_recipe_from_implicit)

# Verify that the conversion produces the same result
assert explicit_recipe_from_implicit == recipe_explicit_complex
rprint("Conversion successful - recipes are equivalent!")
