
from backend.app.prediction_service import (
    predict_match,
    AVAILABLE_TEAMS,
    LATEST_DATA_DATE
)


# --------------------------------------------------
# TEST UTILITIES
# --------------------------------------------------

passed_tests = 0
failed_tests = 0


def record_test(name, passed, message=""):
    global passed_tests, failed_tests

    if passed:
        passed_tests += 1
        print(f"[PASSED] {name}")
    else:
        failed_tests += 1
        print(f"[FAILED] {name}")

    if message:
        print("         ", message)


def display_prediction(result):
    print("\n" + "=" * 50)
    print("EPL MATCH PREDICTION")
    print("=" * 50)

    print("Home Team:", result["home_team"])
    print("Away Team:", result["away_team"])
    print("Prediction Date:", result["prediction_date"])

    print(
        "Latest Historical Data:",
        result["latest_historical_data_date"]
    )

    print("\nLOGISTIC REGRESSION")

    for outcome, probability in result["logistic_regression"].items():
        print(f"{outcome}: {probability * 100:.2f}%")

    print("\nRANDOM FOREST")

    for outcome, probability in result["random_forest"].items():
        print(f"{outcome}: {probability * 100:.2f}%")

    print("\nH = Home Win | D = Draw | A = Away Win")

    print("\nDisclaimer:", result["disclaimer"])


# --------------------------------------------------
# TEST 1: VALID PREDICTION
# --------------------------------------------------

print("\nTEST 1: Valid match prediction")

try:
    result = predict_match(
        "Arsenal",
        "Chelsea",
        "2026-10-30"
    )

    display_prediction(result)

    record_test(
        "Valid prediction",
        True
    )

except Exception as error:
    result = None

    record_test(
        "Valid prediction",
        False,
        str(error)
    )


# --------------------------------------------------
# TEST 2: PROBABILITY VALIDATION
# --------------------------------------------------

if result is not None:

    for model_name in [
        "logistic_regression",
        "random_forest"
    ]:

        probabilities = result[model_name]

        total = sum(probabilities.values())

        valid = (
            len(probabilities) == 3
            and all(
                0 <= value <= 1
                for value in probabilities.values()
            )
            and abs(total - 1.0) < 0.001
        )

        record_test(
            f"{model_name} probability validation",
            valid,
            f"Probability total: {total:.4f}"
        )


# --------------------------------------------------
# TEST 3: UNKNOWN HOME TEAM
# --------------------------------------------------

try:
    predict_match(
        "Unknown FC",
        "Chelsea",
        "2026-10-30"
    )

    record_test(
        "Unknown home team rejection",
        False
    )

except ValueError as error:
    record_test(
        "Unknown home team rejection",
        True,
        str(error)
    )


# --------------------------------------------------
# TEST 4: UNKNOWN AWAY TEAM
# --------------------------------------------------

try:
    predict_match(
        "Arsenal",
        "Unknown FC",
        "2026-10-30"
    )

    record_test(
        "Unknown away team rejection",
        False
    )

except ValueError as error:
    record_test(
        "Unknown away team rejection",
        True,
        str(error)
    )


# --------------------------------------------------
# TEST 5: SAME TEAM
# --------------------------------------------------

try:
    predict_match(
        "Arsenal",
        "Arsenal",
        "2026-10-30"
    )

    record_test(
        "Same team rejection",
        False
    )

except ValueError as error:
    record_test(
        "Same team rejection",
        True,
        str(error)
    )


# --------------------------------------------------
# TEST 6: INVALID DATE
# --------------------------------------------------

try:
    predict_match(
        "Arsenal",
        "Chelsea",
        "not-a-date"
    )

    record_test(
        "Invalid date rejection",
        False
    )

except ValueError as error:
    record_test(
        "Invalid date rejection",
        True,
        str(error)
    )


# --------------------------------------------------
# TEST 7: EMPTY TEAM NAME
# --------------------------------------------------

try:
    predict_match(
        "",
        "Chelsea",
        "2026-10-30"
    )

    record_test(
        "Empty team name rejection",
        False
    )

except ValueError as error:
    record_test(
        "Empty team name rejection",
        True,
        str(error)
    )


# --------------------------------------------------
# TEST 8: AVAILABLE TEAM DATA
# --------------------------------------------------

record_test(
    "Available teams loaded",
    len(AVAILABLE_TEAMS) == 20,
    f"Teams found: {len(AVAILABLE_TEAMS)}"
)


# --------------------------------------------------
# FINAL TEST SUMMARY
# --------------------------------------------------

print("\n" + "=" * 50)
print("PREDICTION SERVICE TEST SUMMARY")
print("=" * 50)

print("Total tests:", passed_tests + failed_tests)
print("Passed:", passed_tests)
print("Failed:", failed_tests)

print("=" * 50)

if failed_tests == 0:
    print("ALL TESTS PASSED!")
else:
    print("SOME TESTS FAILED. REVIEW THE OUTPUT ABOVE.")
