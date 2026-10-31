
import os
import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix
)

# Load combined prediction features
df = pd.read_csv(
    "datasets/prediction_features_multi_season.csv"
)

df["Date"] = pd.to_datetime(df["Date"])

# Features used by the models
feature_columns = [
    "HomeFormPoints",
    "AwayFormPoints",
    "HomeAvgGoalsScored",
    "AwayAvgGoalsScored",
    "HomeAvgGoalsConceded",
    "AwayAvgGoalsConceded",
    "HomeMatchesPlayed",
    "AwayMatchesPlayed"
]

X = df[feature_columns]
y = df["Result"]

# Split by season
train_mask = df["Season"] == "2025/2026"
test_mask = df["Season"] == "2026/2027"

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

print("SEASON-BASED DATASET INFORMATION")
print("=" * 50)

print("Total matches:", len(df))
print("Training matches:", len(X_train))
print("Testing matches:", len(X_test))

print("\nTraining season:")
print(df.loc[train_mask, "Season"].unique())

print("\nTesting season:")
print(df.loc[test_mask, "Season"].unique())

print("\nTraining class distribution:")
print(y_train.value_counts())

print("\nTesting class distribution:")
print(y_test.value_counts())

# Define models
models = {
    "Logistic Regression": Pipeline([
        ("scaler", StandardScaler()),
        ("classifier", LogisticRegression(max_iter=1000))
    ]),

    "Random Forest": RandomForestClassifier(
        n_estimators=200,
        max_depth=5,
        random_state=42,
        class_weight="balanced"
    )
}

# Create model storage directory
os.makedirs("backend/app/models", exist_ok=True)

# Train and evaluate models
for name, model in models.items():

    print("\n" + "=" * 50)
    print(name.upper())
    print("=" * 50)

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    balanced_accuracy = balanced_accuracy_score(
        y_test, predictions
    )

    print(f"Accuracy: {accuracy:.4f}")
    print(f"Balanced Accuracy: {balanced_accuracy:.4f}")

    print("\nClassification Report:")

    print(classification_report(
        y_test,
        predictions,
        labels=["H", "D", "A"],
        target_names=["Home Win", "Draw", "Away Win"],
        zero_division=0
    ))

    print("Confusion Matrix:")

    print(confusion_matrix(
        y_test,
        predictions,
        labels=["H", "D", "A"]
    ))

    # Save model with season-based filename
    filename = name.lower().replace(" ", "_")
    model_path = (
        f"backend/app/models/{filename}_season_test.pkl"
    )

    joblib.dump(model, model_path)

    print("\nModel saved to:", model_path)

print("\nSEASON-BASED MODEL TRAINING COMPLETED!")
