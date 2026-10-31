
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

passed = 0
failed = 0


def record_test(name, success, details=""):
    global passed, failed

    if success:
        passed += 1
        print(f"[PASS] {name}")
    else:
        failed += 1
        print(f"[FAIL] {name}")

    if details:
        print(f"       {details}")


def test_home_endpoint():
    response = client.get("/")

    record_test(
        "Home endpoint",
        response.status_code == 200
        and response.json().get("status") == "running",
        f"Status code: {response.status_code}"
    )


def test_health_endpoint():
    response = client.get("/health")

    record_test(
        "Health endpoint",
        response.status_code == 200
        and response.json().get("status") == "healthy",
        f"Status code: {response.status_code}"
    )


def test_teams_endpoint():
    response = client.get("/teams")
    data = response.json() if response.status_code == 200 else {}

    teams = data.get("teams", [])
    total_teams = data.get("total_teams", 0)

    record_test(
        "Teams endpoint",
        response.status_code == 200
        and total_teams > 0
        and total_teams == len(teams)
        and len(teams) == len(set(teams)),
        f"Teams found: {total_teams}"
    )


def test_api_info_endpoint():
    response = client.get("/api-info")
    data = response.json() if response.status_code == 200 else {}

    record_test(
        "API information endpoint",
        response.status_code == 200
        and "prediction" in data.get("available_endpoints", {}),
        f"Status code: {response.status_code}"
    )


def test_valid_prediction():
    response = client.post(
        "/predict",
        json={
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "prediction_date": "2026-10-30"
        }
    )

    data = response.json() if response.status_code == 200 else {}

    record_test(
        "Valid match prediction",
        response.status_code == 200
        and data.get("status") == "success"
        and "prediction" in data,
        f"Status code: {response.status_code}"
    )


def test_unknown_team():
    response = client.post(
        "/predict",
        json={
            "home_team": "Unknown FC",
            "away_team": "Chelsea",
            "prediction_date": "2026-10-30"
        }
    )

    record_test(
        "Unknown team validation",
        response.status_code == 400,
        f"Status code: {response.status_code}"
    )


def test_same_team():
    response = client.post(
        "/predict",
        json={
            "home_team": "Arsenal",
            "away_team": "Arsenal",
            "prediction_date": "2026-10-30"
        }
    )

    record_test(
        "Same-team validation",
        response.status_code == 400,
        f"Status code: {response.status_code}"
    )


def test_invalid_date():
    response = client.post(
        "/predict",
        json={
            "home_team": "Arsenal",
            "away_team": "Chelsea",
            "prediction_date": "invalid-date"
        }
    )

    record_test(
        "Invalid date validation",
        response.status_code == 422,
        f"Status code: {response.status_code}"
    )


def test_missing_fields():
    response = client.post(
        "/predict",
        json={
            "home_team": "Arsenal"
        }
    )

    record_test(
        "Missing request fields validation",
        response.status_code == 422,
        f"Status code: {response.status_code}"
    )


def run_all_tests():
    print("\n====================================")
    print("EPL SPORTS ANALYTICS API TESTS")
    print("====================================\n")

    test_home_endpoint()
    test_health_endpoint()
    test_teams_endpoint()
    test_api_info_endpoint()
    test_valid_prediction()
    test_unknown_team()
    test_same_team()
    test_invalid_date()
    test_missing_fields()

    print("\n====================================")
    print("TEST SUMMARY")
    print("====================================")

    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")

    if failed == 0:
        print("\nAll API tests passed successfully!")
    else:
        print("\nSome API tests failed. Check the messages above.")


if __name__ == "__main__":
    run_all_tests()
