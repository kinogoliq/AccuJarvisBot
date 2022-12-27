# Working with the categories of the expenses
from typing import Dict, List, NamedTuple
import db


# Categories structure
class Category(NamedTuple):
    codename: str
    name: str
    is_base_expense: bool
    aliases: List[str]


# Fill the aliases of each category, ie all possible ways of writing
# the name of this category, which user may type in the text of the
# message. For example, the category "Cafe" may be written as coffee,
# кофе, ресторан, restaurant etc.

def _fill_aliases(categories: List[Dict]) -> List[Category]:
    categories_result = []
    for index, category in enumerate(categories):
        aliases = category["aliases"].split(",")
        aliases = list(filter(None, map(str.strip, aliases)))
        aliases.append(category["codename"])
        aliases.append(category["name"])
        categories_result.append(Category(
            codename=category['codename'],
            name=category['name'],
            is_base_expense=category['is_base_expense'],
            aliases=aliases
        ))
    return categories_result


class Categories:
    def __init__(self):
        self._categories = self._load_categories

    # This function is return the category from the DB
    @property
    def _load_categories(self) -> List[Category]:
        categories = db.fetchall(
            'category', 'codename name is_base_expense aliases'.split()
        )
        categories: list[Category] = _fill_aliases(categories)
        return categories

    # Return the list of all categories
    def get_all_categories(self) -> List[Dict]:
        return self._categories

    # Return the category by the one of the aliases
    def get_category(self, category_name: str) -> Category:
        founded: None = None
        other_category = None
        for category in self._categories:
            if category.codename == "other":
                other_category = category
            for alias in category.aliases:
                if category_name in alias:
                    founded = category
        if not founded:
            founded = other_category
        return founded
