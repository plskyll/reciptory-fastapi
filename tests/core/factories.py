import factory
from factory import Faker, Sequence

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

    username = Sequence(lambda n: f"user{n}")
    email = Sequence(lambda n: f"user{n}@example.com")
    password = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxwkc.602/6k.z/B.x.b.x.b.x.b."


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CategoryModel
        sqlalchemy_session_persistence = "commit"

    name = Sequence(lambda n: f"category{n}")


class IngredientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = IngredientModel
        sqlalchemy_session_persistence = "commit"

    name = Sequence(lambda n: f"ingredient{n}")
    calories_per_100g = Faker("random_int", min=0, max=500)


class RecipeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RecipeModel
        sqlalchemy_session_persistence = "commit"

    author_id = None
    category_id = None

    name = Faker("sentence", nb_words=3)
    description = Faker("text", max_nb_chars=200)
    instructions = Faker("text", max_nb_chars=500)
    cooking_time_minutes = Faker("random_int", min=10, max=120)
    image_url = Faker("image_url")


class RecipeIngredientFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RecipeIngredientModel
        sqlalchemy_session_persistence = "commit"

    recipe_id = None
    ingredient_id = None
    amount = Faker(
        "random_element",
        elements=["100 г", "200 мл", "1 ст. л.", "2 шт.", "500 г", "1 ч. л.", "1.5 кг", "за смаком"]
    )


class SavedRecipeFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = SavedRecipeModel
        sqlalchemy_session_persistence = "commit"

    user_id = None
    recipe_id = None