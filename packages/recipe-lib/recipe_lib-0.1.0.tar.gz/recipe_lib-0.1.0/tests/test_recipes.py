from recipe_lib.recipes import RecipeManager

def test_add_and_get_recipe():
    manager = RecipeManager()
    manager.add_recipe('Test Dish', ['ingredient1'], ['step1'])
    recipe = manager.get_recipe('Test Dish')
    assert recipe['name'] == 'Test Dish'
