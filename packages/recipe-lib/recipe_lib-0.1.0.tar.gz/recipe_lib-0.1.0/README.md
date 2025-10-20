# Recipe Lib

A Python library to manage, explore, and plan recipes.

## Installation

\\\ash
pip install recipe_lib
\\\

## Usage

\\\python
from recipe_lib import RecipeManager

manager = RecipeManager()
manager.add_recipe(
    name='Pasta',
    ingredients=['pasta', 'tomato', 'cheese'],
    steps=['Boil pasta', 'Add tomato sauce', 'Sprinkle cheese']
)
recipe = manager.get_recipe('Pasta')
print(recipe)
\\\
"@

