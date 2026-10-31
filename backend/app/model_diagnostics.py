
import pandas as pd
import joblib

from sklearn.metrics import accuracy_score

# Load the dataset
df = pd.read_csv(
    "datasets/prediction_features_multi_season.csv"
)

df["Date"] = pd.to_datetime(df["Date"])

features = [
    "HomeFormPoints",
    "AwayFormPoints",
    "HomeAvgGoalsScored",
    "AwayAvgGoalsScored",
    "HomeAvgGoalsConceded",
    "AwayAvgGoalsConceded",
    "HomeMatchesPlayed",
    "AwayMatchesPlayed",
    "HomeAdvantage"
]

X = df[features]
y = df["Result"]

# Reproduce the chronological split
unique_dates = sorted(df["Date"].unique())
split_index = int(len(unique_dates) * 0.80)
split_date = unique_dates[split_index]

train_mask = df["Date"] < split_date
test_mask = df["Date"] >= split_date

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

# Load saved models
logistic_model = joblib.load(
    "backend/app/models/logistic_regression_multi.pkl"
)

forest_model = joblib.load(
    "backend/app/models/random_forest_multi.pkl"
)

# Compare training and testing accuracy
models = {
    "Logistic Regression": logistic_model,
    "Random Forest": forest_model
}

print("\nMODEL DIAGNOSTICS")
print("=" * 50)

for name, model in models.items():

    train_predictions = model.predict(X_train)
    test_predictions = model.predict(X_test)

    train_accuracy = accuracy_score(
        y_train, train_predictions
    )

    test_accuracy = accuracy_score(
        y_test, test_predictions
    )

    print(f"\n{name}")
    print("-" * 35)
    print(f"Training accuracy: {train_accuracy:.4f}")
    print(f"Testing accuracy:  {test_accuracy:.4f}")

# Logistic Regression coefficients
logistic_classifier = logistic_model.named_steps["model"]

coefficient_df = pd.DataFrame(
    logistic_classifier.coef_,
    columns=features,
    index=logistic_classifier.classes_
)

print("\nLOGISTIC REGRESSION COEFFICIENTS")
print("=" * 50)
print(coefficient_df.round(4))

coefficient_df.to_csv(
    "datasets/logistic_regression_coefficients.csv"
)

# Random Forest feature importance
importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": forest_model.feature_importances_
})

importance_df = importance_df.sort_values(
    by="Importance",
    ascending=False
)

print("\nRANDOM FOREST FEATURE IMPORTANCE")
print("=" * 50)
print(importance_df.to_string(index=False))

importance_df.to_csv(
    "datasets/random_forest_feature_importance.csv",
    index=False
)

print("\nDiagnostics saved successfully!")
