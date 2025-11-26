import pytest
from app.core.utils import get_password_hash
from app.core.models.user import UserModel
from tests.core.factories import (
    UserFactory,
    CategoryFactory,
    IngredientFactory,
    RecipeFactory,
    RecipeIngredientFactory,
    SavedRecipeFactory
)


# ==========================================
# ФІКСТУРИ (НАЛАШТУВАННЯ)
# ==========================================

@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """Прив'язуємо сесію до фабрик перед кожним тестом"""
    UserFactory._meta.sqlalchemy_session = db_session
    CategoryFactory._meta.sqlalchemy_session = db_session
    IngredientFactory._meta.sqlalchemy_session = db_session
    RecipeFactory._meta.sqlalchemy_session = db_session
    RecipeIngredientFactory._meta.sqlalchemy_session = db_session
    SavedRecipeFactory._meta.sqlalchemy_session = db_session


@pytest.fixture
async def auth_headers(client):
    """Створює юзера, логіниться і повертає заголовок з токеном"""
    password = "password"
    hashed_password = get_password_hash(password)
    user = UserFactory(email="tester@example.com", password=hashed_password)

    response = await client.post("/auth/login", data={
        "username": "tester@example.com",
        "password": password
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def current_user(db_session):
    """Повертає об'єкт юзера, під яким ми залогінені (для перевірок ID)"""
    # Шукаємо того самого юзера, якого створює auth_headers
    # (оскільки база очищається, нам треба бути обережними,
    # краще створити і повернути його, але auth_headers робить це всередині)
    # Тому тут просто допоміжна функція, якщо треба буде ID
    pass


# ==========================================
# 1. ТЕСТИ AUTH & SYSTEM (/auth, /, /health)
# ==========================================

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
async def test_login_success(client):
    password = "password"
    UserFactory(email="login@test.com", password=get_password_hash(password))
    response = await client.post("/auth/login", data={"username": "login@test.com", "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()


# ==========================================
# 2. ТЕСТИ USERS (/users)
# ==========================================

@pytest.mark.asyncio
async def test_create_user(client):
    payload = {"username": "newuser", "email": "new@test.com", "password": "securepassword"}
    response = await client.post("/users/", json=payload)
    assert response.status_code == 201
    assert response.json()["email"] == "new@test.com"


@pytest.mark.asyncio
async def test_get_users(client):
    UserFactory.create_batch(2)
    response = await client.get("/users/")
    assert response.status_code == 200
    assert len(response.json()) >= 2


@pytest.mark.asyncio
async def test_get_user_detail(client):
    user = UserFactory()
    response = await client.get(f"/users/{user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == user.username


@pytest.mark.asyncio
async def test_patch_user(client):
    user = UserFactory()
    response = await client.patch(f"/users/{user.id}", json={"username": "patched_name"})
    assert response.status_code == 200
    assert response.json()["username"] == "patched_name"


@pytest.mark.asyncio
async def test_delete_user(client, auth_headers):
    user = UserFactory()
    # Видаляти може тільки авторизований (хоча у вас в коді будь-який авторизований може видалити будь-кого)
    response = await client.delete(f"/users/{user.id}", headers=auth_headers)
    assert response.status_code == 204
    assert (await client.get(f"/users/{user.id}")).status_code == 404


# ==========================================
# 3. ТЕСТИ CATEGORIES (/categories)
# ==========================================

@pytest.mark.asyncio
async def test_crud_category(client, auth_headers):
    # CREATE
    response = await client.post("/categories/", json={"name": "Desserts"})
    assert response.status_code == 201
    cat_id = response.json()["id"]

    # READ LIST
    assert (await client.get("/categories/")).status_code == 200

    # READ ONE
    assert (await client.get(f"/categories/{cat_id}")).status_code == 200

    # UPDATE (PUT)
    res = await client.put(f"/categories/{cat_id}", json={"name": "Sweets"})
    assert res.status_code == 200
    assert res.json()["name"] == "Sweets"

    # DELETE (Authorized)
    res = await client.delete(f"/categories/{cat_id}", headers=auth_headers)
    assert res.status_code == 204


# ==========================================
# 4. ТЕСТИ INGREDIENTS (/ingredients)
# ==========================================

@pytest.mark.asyncio
async def test_crud_ingredient(client, auth_headers):
    # CREATE
    payload = {"name": "Salt", "calories_per_100g": 0}
    response = await client.post("/ingredients/", json=payload)
    assert response.status_code == 201
    ing_id = response.json()["id"]

    # READ
    assert (await client.get(f"/ingredients/{ing_id}")).status_code == 200

    # UPDATE (PUT)
    res = await client.put(f"/ingredients/{ing_id}", json={"name": "Sea Salt", "calories_per_100g": 0})
    assert res.status_code == 200
    assert res.json()["name"] == "Sea Salt"

    # PARTIAL UPDATE (PATCH)
    res = await client.patch(f"/ingredients/{ing_id}", json={"calories_per_100g": 1})
    assert res.status_code == 200
    assert res.json()["calories_per_100g"] == 1

    # DELETE
    res = await client.delete(f"/ingredients/{ing_id}", headers=auth_headers)
    assert res.status_code == 204


# ==========================================
# 5. ТЕСТИ RECIPES (/recipes)
# ==========================================

@pytest.mark.asyncio
async def test_create_recipe(client, auth_headers):
    category = CategoryFactory()
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
async def test_update_recipe(client):
    recipe = RecipeFactory()
    # PUT
    new_data = {
        "category_id": recipe.category_id,
        "name": "New Name",
        "description": "New Desc",
        "instructions": "New Instr",
        "cooking_time_minutes": 20
    }
    res = await client.put(f"/recipes/{recipe.id}", json=new_data)
    assert res.status_code == 200
    assert res.json()["name"] == "New Name"

    # PATCH
    res = await client.patch(f"/recipes/{recipe.id}", json={"name": "Patched Name"})
    assert res.status_code == 200
    assert res.json()["name"] == "Patched Name"


@pytest.mark.asyncio
async def test_delete_recipe(client, auth_headers):
    recipe = RecipeFactory()
    res = await client.delete(f"/recipes/{recipe.id}", headers=auth_headers)
    assert res.status_code == 204


# ==========================================
# 6. ТЕСТИ RECIPE INGREDIENTS (/recipe_ingredients)
# ==========================================

@pytest.mark.asyncio
async def test_recipe_ingredients_flow(client, auth_headers):
    recipe = RecipeFactory()
    ingredient = IngredientFactory()

    # 1. Add ingredient to recipe
    payload = {
        "recipe_id": recipe.id,
        "ingredient_id": ingredient.id,
        "amount": "200 g"
    }
    res = await client.post("/recipe_ingredients/", json=payload, headers=auth_headers)
    assert res.status_code == 201

    # 2. Get list
    res = await client.get("/recipe_ingredients/")
    assert res.status_code == 200

    # 3. Get one (Composite key path)
    res = await client.get(f"/recipe_ingredients/{recipe.id}/{ingredient.id}")
    assert res.status_code == 200
    assert res.json()["amount"] == "200 g"

    # 4. Patch
    res = await client.patch(
        f"/recipe_ingredients/{recipe.id}/{ingredient.id}",
        json={"amount": "500 kg"},
        headers=auth_headers
    )
    assert res.status_code == 200
    assert res.json()["amount"] == "500 kg"

    # 5. Delete
    res = await client.delete(f"/recipe_ingredients/{recipe.id}/{ingredient.id}", headers=auth_headers)
    assert res.status_code == 204


# ==========================================
# 7. ТЕСТИ SAVED RECIPES (/saved_recipes)
# ==========================================

@pytest.mark.asyncio
async def test_saved_recipes_flow(client, auth_headers):
    # Спочатку треба створити рецепт, який ми будемо зберігати
    recipe = RecipeFactory()

    # 1. Save recipe (User ID береться автоматично з токена auth_headers)
    payload = {"recipe_id": recipe.id}
    res = await client.post("/saved_recipes/", json=payload, headers=auth_headers)
    assert res.status_code == 201
    saved_id = res.json()["id"]

    # 2. Get list
    res = await client.get("/saved_recipes/")
    assert res.status_code == 200
    assert len(res.json()) > 0

    # 3. Get one
    res = await client.get(f"/saved_recipes/{saved_id}")
    assert res.status_code == 200

    # 4. Delete
    res = await client.delete(f"/saved_recipes/{saved_id}", headers=auth_headers)
    assert res.status_code == 204