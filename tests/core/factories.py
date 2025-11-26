import factory

from app.core.models.category import CategoryModel
from app.core.models.ingredient import IngredientModel
from app.core.models.recipe import RecipeModel
from app.core.models.recipe_ingredient import RecipeIngredientModel
from app.core.models.saved_recipe import SavedRecipeModel
from app.core.models.user import UserModel

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserModel
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwkc.602/6k.z/B.x.b.x.b.x.b."

class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CategoryModel
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")


class IngredientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = IngredientModel
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("word")
    calories_per_100g = factory.Faker("random_int", positive=True)


class RecipeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RecipeModel
        sqlalchemy_session_persistence = "commit"

    author = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("text")
    instructions = factory.Faker("text")
    cooking_time_minutes = factory.Faker("random_int", min=10, max=120)
    image_url = factory.Faker("image_url")


class RecipeIngredientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RecipeIngredientModel
        sqlalchemy_session_persistence = "commit"

    recipe_id = factory.SubFactory(RecipeFactory)
    ingredient_id = factory.SubFactory(IngredientFactory)
    amount = factory.Faker(
        "random_element",
        elements=["100 г", "200 мл", "1 ст. л.", "2 шт.", "500 г", "1 ч. л.", "1.5 кг", "за смаком"]
    )




class SavedRecipeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SavedRecipeModel

    user = factory.SubFactory(UserFactory)
    recipe = factory.SubFactory(RecipeFactory)





