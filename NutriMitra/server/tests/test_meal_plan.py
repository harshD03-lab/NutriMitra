"""End to end tests for the profile -> meal plan workflow."""

import pytest

from app.api.v1.routes.recommendations import generate_plan
from app.core.database import SessionLocal
from app.models.food_item import FoodItem
from app.models.user import User
from app.schemas.recommendation import UserProfile
from fastapi import HTTPException

from .conftest import PROFILE, register_and_login

MEAL_SLOTS = {"Breakfast", "Lunch", "Dinner", "Snacks"}


# --- dataset ---------------------------------------------------------------

def test_dataset_is_loaded(client):
    """The bundled dataset must be imported on startup."""
    response = client.get("/v1/food/?limit=1")
    assert response.status_code == 200
    assert response.json()["total"] > 500


def test_food_records_have_nutrition_values(client):
    response = client.get("/v1/food/?limit=50")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items
    for item in items:
        assert item["energy_kcal"] is not None
        assert item["energy_kcal"] > 0
        assert item["serving_size_g"]


# --- authentication and profile -------------------------------------------

def test_register_login_and_profile(client):
    token = register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == "tester@example.com"

    # The profile can be saved.
    response = client.patch(
        "/v1/users/me",
        headers=headers,
        json={
            "age": 31,
            "gender": "female",
            "height_cm": 168,
            "weight_kg": 62,
            "activity_level": "light",
            "diet_type": "vegetarian",
            "allergies": "peanut",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["age"] == 31
    assert body["diet_type"] == "vegetarian"
    assert body["allergies"] == "peanut"

    # ... and it is persisted.
    response = client.get("/v1/users/me", headers=headers)
    assert response.json()["weight_kg"] == 62


def test_invalid_profile_values_are_rejected(client):
    token = register_and_login(client, "invalid@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.patch("/v1/users/me", headers=headers, json={"age": 900})
    assert response.status_code == 422
    response = client.patch(
        "/v1/users/me", headers=headers, json={"diet_type": "carnivore"}
    )
    assert response.status_code == 422


# --- meal generation -------------------------------------------------------

def test_valid_profile_returns_a_food_based_plan(client):
    token = register_and_login(client, "plan@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/v1/recommendations/", headers=headers, json=PROFILE)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["meal_plan"], "meal plan must not be empty"
    assert {slot["meal"] for slot in body["meal_plan"]} == MEAL_SLOTS
    assert body["total_calories"] > 0
    assert body["target_calories"] > 0

    for slot in body["meal_plan"]:
        assert slot["items"]
        for item in slot["items"]:
            assert item["food_name"]
            assert item["serving_size"]
            assert item["calories"] > 0


def test_totals_match_the_displayed_food_records(client):
    token = register_and_login(client, "totals@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    body = client.post("/v1/recommendations/", headers=headers, json=PROFILE).json()

    calories = sum(item["calories"] for slot in body["meal_plan"] for item in slot["items"])
    protein = sum(item["protein_g"] for slot in body["meal_plan"] for item in slot["items"])
    carbs = sum(item["carbs_g"] for slot in body["meal_plan"] for item in slot["items"])
    fat = sum(item["fat_g"] for slot in body["meal_plan"] for item in slot["items"])

    assert abs(body["total_calories"] - calories) < 0.5
    assert abs(body["total_protein"] - protein) < 0.5
    assert abs(body["total_carbs"] - carbs) < 0.5
    assert abs(body["total_fat"] - fat) < 0.5

    for slot in body["meal_plan"]:
        slot_calories = sum(item["calories"] for item in slot["items"])
        assert abs(slot["totals"]["calories"] - slot_calories) < 0.5


def test_calorie_target_depends_on_the_profile(client):
    token = register_and_login(client, "targets@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    small = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "weight_kg": 55, "height_cm": 160, "age": 25},
    ).json()
    large = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "weight_kg": 95, "height_cm": 185, "age": 40},
    ).json()

    assert large["target_calories"] > small["target_calories"]
    assert small["target_calories"] != large["target_calories"]

    # An inactive person needs less than an active one of the same size.
    inactive = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "activity_level": "sedentary"},
    ).json()
    active = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "activity_level": "active"},
    ).json()
    assert active["target_calories"] > inactive["target_calories"]


def test_plan_is_saved_in_the_history(client):
    token = register_and_login(client, "history@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/v1/recommendations/", headers=headers, json=PROFILE)

    response = client.get("/v1/plans/", headers=headers)
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 1
    assert plans[0]["item_count"] > 0
    assert plans[0]["total_calories"] > 0

    plan_id = plans[0]["id"]
    response = client.get(f"/v1/plans/{plan_id}", headers=headers)
    assert response.status_code == 200
    saved = response.json()
    assert saved["meal_plan"]
    assert saved["total_calories"] == plans[0]["total_calories"]

    # The saved plan belongs to the user that created it.
    other_token = register_and_login(client, "other@example.com")
    other_headers = {"Authorization": f"Bearer {other_token}"}
    assert client.get(f"/v1/plans/{plan_id}", headers=other_headers).status_code == 404

    assert client.delete(f"/v1/plans/{plan_id}", headers=headers).status_code == 200
    assert client.get("/v1/plans/", headers=headers).json() == []


# --- dietary filtering -----------------------------------------------------

def _names(body) -> list[str]:
    return [item["food_name"] for slot in body["meal_plan"] for item in slot["items"]]


@pytest.mark.parametrize("diet_type", ["vegetarian", "vegan"])
def test_vegetarian_and_vegan_plans_exclude_animal_foods(client, diet_type):
    from app.ml.diet_rules import classify_food

    token = register_and_login(client, f"{diet_type}@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    body = client.post(
        "/v1/recommendations/", headers=headers, json={**PROFILE, "diet_type": diet_type}
    ).json()

    assert body["meal_plan"]
    for name in _names(body):
        info = classify_food(name)
        assert info["is_vegetarian"], f"{name} is not vegetarian"
        if diet_type == "vegan":
            assert not info["is_dairy"], f"{name} contains dairy"
            assert not info["is_honey"], f"{name} contains honey"


def test_non_vegetarian_plan_may_include_meat(client):
    token = register_and_login(client, "nonveg@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    body = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "diet_type": "non-vegetarian"},
    ).json()
    assert body["meal_plan"]


def test_allergy_exclusions_are_respected(client):
    from app.ml.diet_rules import classify_food

    token = register_and_login(client, "allergy@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    body = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "diet_type": "non-vegetarian", "allergies": "peanut"},
    ).json()

    assert body["meal_plan"]
    for name in _names(body):
        assert "peanut" not in name.lower()
        assert "groundnut" not in name.lower()
    assert classify_food("Cashew Nuts")["is_vegetarian"]


def test_medical_condition_removes_matching_foods(client):
    token = register_and_login(client, "diabetes@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    body = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "medical_conditions": "diabetes"},
    ).json()
    assert body["meal_plan"]
    assert body["explanation"]
    # The guidance is general and does not claim to treat the condition.
    assert "doctor" in body["explanation"].lower() or "glucose" in body["explanation"].lower()


# --- error handling --------------------------------------------------------

def test_missing_profile_fields_report_what_is_missing(client):
    token = register_and_login(client, "missing@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={"age": 30, "gender": "male", "height_cm": 175, "weight_kg": 70},
    )
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert "activity level" in detail
    assert "diet type" in detail


def test_unsupported_diet_type_is_reported(client):
    token = register_and_login(client, "diet@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "diet_type": "carnivore"},
    )
    assert response.status_code == 422
    assert "carnivore" in response.json()["detail"]


def test_unsupported_gender_and_activity_are_reported(client):
    token = register_and_login(client, "gender@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/v1/recommendations/", headers=headers, json={**PROFILE, "gender": "other"}
    )
    assert response.status_code == 422

    response = client.post(
        "/v1/recommendations/",
        headers=headers,
        json={**PROFILE, "activity_level": "extreme"},
    )
    assert response.status_code == 422


def test_unauthenticated_requests_are_rejected(client):
    response = client.post("/v1/recommendations/", json=PROFILE)
    assert response.status_code in (401, 403)


def test_missing_dataset_reports_an_error_instead_of_zeros():
    """An empty food table must produce an explicit error, not empty totals."""
    db = SessionLocal()
    try:
        db.query(FoodItem).delete()
        db.commit()
        user = db.query(User).first()
        with pytest.raises(HTTPException) as excinfo:
            generate_plan(profile=UserProfile(**PROFILE), current=user, db=db)
        assert excinfo.value.status_code == 503
        assert "dataset" in str(excinfo.value.detail).lower()
    finally:
        db.rollback()
        db.close()


def test_database_failure_does_not_return_a_fake_plan():
    """A failing save must raise an error instead of reporting success."""
    from app.api.v1.routes import recommendations as recommendations_module

    db = SessionLocal()
    original_commit = db.commit

    def failing_commit():
        raise RuntimeError("database is gone")

    try:
        db.commit = failing_commit
        user = db.query(User).first()
        with pytest.raises(HTTPException) as excinfo:
            recommendations_module.generate_plan(
                profile=UserProfile(**PROFILE), current=user, db=db
            )
        assert excinfo.value.status_code == 503
    finally:
        db.commit = original_commit
        db.rollback()
        db.close()
