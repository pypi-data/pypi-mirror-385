import json
import os
import random

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'recipes.json')

class RecipeManager:
    def __init__(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                self.recipes = json.load(f)
        else:
            self.recipes = []

    def save(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.recipes, f, ensure_ascii=False, indent=4)

    def add_recipe(self, name, ingredients, steps):
        recipe = {
            "name": name,
            "ingredients": ingredients,
            "steps": steps
        }
        self.recipes.append(recipe)
        self.save()
        return recipe

    def delete_recipe(self, name):
        initial_len = len(self.recipes)
        self.recipes = [r for r in self.recipes if r['name'] != name]
        self.save()
        return len(self.recipes) < initial_len  # True əgər silinib

    def get_recipe(self, name):
        for r in self.recipes:
            if r['name'] == name:
                return r
        return None

    # ✅ Yeni metod: ad üzrə axtarış
    def search_recipe(self, query):
        return [r for r in self.recipes if query.lower() in r['name'].lower()]

    # ✅ Yeni metod: ingredient üzrə filter
    def filter_by_ingredient(self, ingredient):
        return [r for r in self.recipes if ingredient.lower() in map(str.lower, r['ingredients'])]

    # ✅ Mövcud metod: ingredient üzrə axtarış
    def search_by_ingredient(self, ingredient):
        return [r for r in self.recipes if ingredient.lower() in map(str.lower, r['ingredients'])]

    # Mövcud: random recipe
    def get_random_recipe(self):
        if not self.recipes:
            return None
        return random.choice(self.recipes)
