import pytest
import pytest_asyncio
from app.core.utils import get_password_hash
from tests.core.factories import (
    UserFactory,
    CategoryFactory,
    IngredientFactory,
    RecipeFactory,
    RecipeIngredientFactory,
    SavedRecipeFactory
)


# ФІКСТУРИ ДЛЯ FACTORIES

@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """Прив'язуємо сесію до фабрик перед кожним тестом"""
    UserFactory._meta.sqlalchemy_session = db_session
    CategoryFactory._meta.sqlalchemy_session = db_session
    IngredientFactory._meta.sqlalchemy_session = db_session
    RecipeFactory._meta.sqlalchemy_session = db_session
    RecipeIngredientFactory._meta.sqlalchemy_session = db_session
    SavedRecipeFactory._meta.sqlalchemy_session = db_session


@pytest_asyncio.fixture
async def user_factory(db_session):
    async def _factory(**kwargs):
        user = UserFactory(**kwargs)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    return _factory


@pytest_asyncio.fixture
async def category_factory(db_session):
    async def _factory(**kwargs):
        category = CategoryFactory(**kwargs)
        await db_session.commit()
        await db_session.refresh(category)
        return category

    return _factory


@pytest_asyncio.fixture
async def ingredient_factory(db_session):
    async def _factory(**kwargs):
        ingredient = IngredientFactory(**kwargs)
        await db_session.commit()
        await db_session.refresh(ingredient)
        return ingredient

    return _factory


@pytest_asyncio.fixture
async def recipe_factory(db_session, user_factory, category_factory):
    """Фікстура для створення рецептів з автоматичним створенням залежностей"""

    async def _factory(**kwargs):
        # Якщо не передали author_id, створюємо користувача
        if 'author_id' not in kwargs:
            user = await user_factory()
            kwargs['author_id'] = user.id

        # Якщо не передали category_id, створюємо категорію
        if 'category_id' not in kwargs:
            category = await category_factory()
            kwargs['category_id'] = category.id

        recipe = RecipeFactory(**kwargs)
        await db_session.commit()
        await db_session.refresh(recipe)
        return recipe

    return _factory


@pytest_asyncio.fixture
async def recipe_ingredient_factory(db_session, recipe_factory, ingredient_factory):
    """Фікстура для створення зв'язків рецепт-інгредієнт"""

    async def _factory(**kwargs):
        # Якщо не передали recipe_id, створюємо рецепт
        if 'recipe_id' not in kwargs:
            recipe = await recipe_factory()
            kwargs['recipe_id'] = recipe.id

        # Якщо не передали ingredient_id, створюємо інгредієнт
        if 'ingredient_id' not in kwargs:
            ingredient = await ingredient_factory()
            kwargs['ingredient_id'] = ingredient.id

        recipe_ingredient = RecipeIngredientFactory(**kwargs)
        await db_session.commit()
        await db_session.refresh(recipe_ingredient)
        return recipe_ingredient

    return _factory


@pytest_asyncio.fixture
async def saved_recipe_factory(db_session, user_factory, recipe_factory):
    """Фікстура для створення збережених рецептів"""

    async def _factory(**kwargs):
        # Якщо не передали user_id, створюємо користувача
        if 'user_id' not in kwargs:
            user = await user_factory()
            kwargs['user_id'] = user.id

        # Якщо не передали recipe_id, створюємо рецепт
        if 'recipe_id' not in kwargs:
            recipe = await recipe_factory()
            kwargs['recipe_id'] = recipe.id

        saved_recipe = SavedRecipeFactory(**kwargs)
        await db_session.commit()
        await db_session.refresh(saved_recipe)
        return saved_recipe

    return _factory


# ДОПОМІЖНІ ФІКСТУРИ

@pytest_asyncio.fixture
async def auth_headers(client, user_factory):
    """Створює юзера, логіниться і повертає заголовок з токеном"""
    password = "password"
    hashed_password = get_password_hash(password)
    user = await user_factory(username="tester", email="tester@example.com", password=hashed_password)

    response = await client.post("/auth/login", data={
        "username": "tester",
        "password": password
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# 1. ТЕСТИ AUTH & SYSTEM (/auth, /, /health)

@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_login_success(client, user_factory):
    password = "password"
    await user_factory(username="loginuser", email="login@test.com", password=get_password_hash(password))

    response = await client.post("/auth/login", data={
        "username": "loginuser",
        "password": password
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


# 2. ТЕСТИ USERS (/users)

@pytest.mark.asyncio
async def test_create_user(client):
    payload = {
        "username": "newuser",
        "email": "new@test.com",
        "password": "securepassword"
    }
    response = await client.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "new@test.com"
    assert response.json()["username"] == "newuser"


@pytest.mark.asyncio
async def test_get_users(client, user_factory):
    await user_factory()
    await user_factory()

    response = await client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_get_user_detail(client, user_factory):
    user = await user_factory()

    response = await client.get(f"/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == user.username
    assert response.json()["id"] == user.id


@pytest.mark.asyncio
async def test_patch_user(client, user_factory):
    user = await user_factory()

    response = await client.patch(f"/users/{user.id}", json={"username": "patched_name"})
    assert response.status_code == 200
    assert response.json()["username"] == "patched_name"


@pytest.mark.asyncio
async def test_delete_user(client, auth_headers, user_factory):
    user = await user_factory()

    response = await client.delete(f"/users/{user.id}", headers=auth_headers)
    assert response.status_code == 204

    # перевірка, що користувач видалений
    get_response = await client.get(f"/users/{user.id}")
    assert get_response.status_code == 404


# 3. ТЕСТИ CATEGORIES (/categories)

@pytest.mark.asyncio
async def test_crud_category(client, auth_headers):
    # CREATE
    response = await client.post("/categories/", json={"name": "Desserts"})
    assert response.status_code == 201
    cat_id = response.json()["id"]
    assert response.json()["name"] == "Desserts"

    # READ LIST
    list_response = await client.get("/categories/")
    assert list_response.status_code == 200
    assert len(list_response.json()) > 0

    # READ ONE
    get_response = await client.get(f"/categories/{cat_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Desserts"

    # UPDATE (PUT)
    update_response = await client.put(f"/categories/{cat_id}", json={"name": "Sweets"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Sweets"

    # DELETE (Authorized)
    delete_response = await client.delete(f"/categories/{cat_id}", headers=auth_headers)
    assert delete_response.status_code == 204



# 4. ТЕСТИ INGREDIENTS (/ingredients)

@pytest.mark.asyncio
async def test_crud_ingredient(client, auth_headers):
    # CREATE
    payload = {"name": "Salt", "calories_per_100g": 0}
    response = await client.post("/ingredients/", json=payload)
    assert response.status_code == 201
    ing_id = response.json()["id"]
    assert response.json()["name"] == "Salt"

    # READ
    get_response = await client.get(f"/ingredients/{ing_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Salt"

    # UPDATE (PUT)
    put_response = await client.put(
        f"/ingredients/{ing_id}",
        json={"name": "Sea Salt", "calories_per_100g": 0}
    )
    assert put_response.status_code == 200
    assert put_response.json()["name"] == "Sea Salt"

    # PARTIAL UPDATE (PATCH)
    patch_response = await client.patch(
        f"/ingredients/{ing_id}",
        json={"calories_per_100g": 1}
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["calories_per_100g"] == 1

    # DELETE
    delete_response = await client.delete(f"/ingredients/{ing_id}", headers=auth_headers)
    assert delete_response.status_code == 204


# 5. ТЕСТИ RECIPES (/recipes)

@pytest.mark.asyncio
async def test_create_recipe(client, auth_headers, category_factory):
    category = await category_factory()

    payload = {
        "category_id": category.id,
        "name": "Test Recipe",
        "description": "Desc",
        "instructions": "Do it",
        "cooking_time_minutes": 10
    }
    response = await client.post("/recipes/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Test Recipe"


@pytest.mark.asyncio
async def test_update_recipe(client, recipe_factory):
    recipe = await recipe_factory()

    # PUT
    new_data = {
        "category_id": recipe.category_id,
        "name": "New Name",
        "description": "New Desc",
        "instructions": "New Instr",
        "cooking_time_minutes": 20
    }
    put_response = await client.put(f"/recipes/{recipe.id}", json=new_data)
    assert put_response.status_code == 200
    assert put_response.json()["name"] == "New Name"

    # PATCH
    patch_response = await client.patch(f"/recipes/{recipe.id}", json={"name": "Patched Name"})
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Patched Name"


@pytest.mark.asyncio
async def test_delete_recipe(client, auth_headers, recipe_factory):
    recipe = await recipe_factory()

    response = await client.delete(f"/recipes/{recipe.id}", headers=auth_headers)
    assert response.status_code == 204


# 6. ТЕСТИ RECIPE INGREDIENTS (/recipe_ingredients)

@pytest.mark.asyncio
async def test_recipe_ingredients_flow(client, auth_headers, recipe_factory, ingredient_factory):
    recipe = await recipe_factory()
    ingredient = await ingredient_factory()

    # 1. Add ingredient to recipe
    payload = {
        "recipe_id": recipe.id,
        "ingredient_id": ingredient.id,
        "amount": "200 g"
    }
    create_response = await client.post("/recipe_ingredients/", json=payload, headers=auth_headers)
    assert create_response.status_code == 201

    # 2. Get list
    list_response = await client.get("/recipe_ingredients/")
    assert list_response.status_code == 200

    # 3. Get one
    get_response = await client.get(f"/recipe_ingredients/{recipe.id}/{ingredient.id}")
    assert get_response.status_code == 200
    assert get_response.json()["amount"] == "200 g"

    # 4. Patch
    patch_response = await client.patch(
        f"/recipe_ingredients/{recipe.id}/{ingredient.id}",
        json={"amount": "500 kg"},
        headers=auth_headers
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["amount"] == "500 kg"

    # 5. Delete
    delete_response = await client.delete(
        f"/recipe_ingredients/{recipe.id}/{ingredient.id}",
        headers=auth_headers
    )
    assert delete_response.status_code == 204



# 7. ТЕСТИ SAVED RECIPES

@pytest.mark.asyncio
async def test_saved_recipes_flow(client, auth_headers, recipe_factory):
    recipe = await recipe_factory()

    # 1. Save recipe (User ID береться автоматично з токена auth_headers)
    payload = {"recipe_id": recipe.id}
    create_response = await client.post("/saved_recipes/", json=payload, headers=auth_headers)
    assert create_response.status_code == 201
    saved_id = create_response.json()["id"]

    # 2. Get list
    list_response = await client.get("/saved_recipes/")
    assert list_response.status_code == 200
    assert len(list_response.json()) > 0

    # 3. Get one
    get_response = await client.get(f"/saved_recipes/{saved_id}")
    assert get_response.status_code == 200

    # 4. Delete
    delete_response = await client.delete(f"/saved_recipes/{saved_id}", headers=auth_headers)
    assert delete_response.status_code == 204