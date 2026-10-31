
import pandas as pd
import joblib

from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss
)

# Load the multi-season features
df = pd.read_csv(
    "datasets/prediction_features_multi_season.csv"
)

df["Date"] = pd.to_datetime(df["Date"])

# Define model inputs and target
# HomeAdvantage removed because it is always 1
features = [
    "HomeFormPoints",
    "AwayFormPoints",
    "HomeAvgGoalsScored",
    "AwayAvgGoalsScored",
    "HomeAvgGoalsConceded",
    "AwayAvgGoalsConceded",
    "HomeMatchesPlayed",
    "AwayMatchesPlayed",
    "HomeVenueFormPoints",
    "AwayVenueFormPoints",
    "HomeVenueAvgGoalsScored",
    "AwayVenueAvgGoalsScored",
    "HomeVenueAvgGoalsConceded",
    "AwayVenueAvgGoalsConceded",
    "HomeVenueMatchesPlayed",
    "AwayVenueMatchesPlayed"
]

X = df[features]
y = df["Result"]

# Train on 2025/2026 and test on 2026/2027
season_cutoff = pd.Timestamp("2026-08-01")

train_mask = df["Date"] < season_cutoff
test_mask = df["Date"] >= season_cutoff

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print("\nSEASON-BASED MODEL TRAINING")
print("=" * 50)

print("Total matches:", len(df))
print("Training matches:", len(X_train))
print("Testing matches:", len(X_test))

print("\nTraining season: 2025/2026")
print("Testing season: 2026/2027")

print("\nTraining result distribution:")
print(y_train.value_counts())

print("\nTesting result distribution:")
print(y_test.value_counts())

# Define the models
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("model", LogisticRegression(max_iter=1000))
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=300,
        max_depth=8,
        random_state=42,
        class_weight="balanced"
    )
}

# Create model storage folder
model_directory = Path("backend/app/models")
model_directory.mkdir(parents=True, exist_ok=True)

results = {}

# Train and evaluate each model
for model_name, model in models.items():

    print("\n" + "=" * 50)
    print(model_name.upper())
    print("=" * 50)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)

    accuracy = accuracy_score(y_test, predictions)

    balanced_accuracy = balanced_accuracy_score(
        y_test, predictions
    )

    loss = log_loss(
        y_test,
        probabilities,
        labels=model.classes_
    )

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Balanced Accuracy: {balanced_accuracy:.4f}")
    print(f"Log Loss: {loss:.4f}")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        predictions,
        labels=["H", "D", "A"],
        zero_division=0
    ))

    print("Confusion Matrix (H, D, A):")
    print(confusion_matrix(
        y_test,
        predictions,
        labels=["H", "D", "A"]
    ))

    # Save trained model
    filename = (
        "logistic_regression_multi.pkl"
        if model_name == "Logistic Regression"
        else "random_forest_multi.pkl"
    )

    joblib.dump(
        model,
        model_directory / filename
    )

    results[model_name] = {
        "Accuracy": accuracy,
        "Balanced Accuracy": balanced_accuracy,
        "Log Loss": loss
    }

# Majority-class baseline
majority_class = y_train.mode()[0]

baseline_predictions = [majority_class] * len(y_test)

baseline_accuracy = accuracy_score(
    y_test,
    baseline_predictions
)

baseline_balanced_accuracy = balanced_accuracy_score(
    y_test,
    baseline_predictions
)

results["Majority-Class Baseline"] = {
    "Accuracy": baseline_accuracy,
    "Balanced Accuracy": baseline_balanced_accuracy,
    "Log Loss": None
}

# Compare models
print("\n" + "=" * 50)
print("MODEL COMPARISON")
print("=" * 50)

comparison = pd.DataFrame(results).T
print(comparison.round(4))

comparison.to_csv(
    "datasets/model_comparison_multi_season.csv"
)

print("\nSaved models in:", model_directory)
print(
    "Saved comparison to:",
    "datasets/model_comparison_multi_season.csv"
)

print("\nMODEL TRAINING COMPLETED!")
