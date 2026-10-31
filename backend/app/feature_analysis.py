
import pandas as pd
import joblib

# Load trained models
logistic_model = joblib.load(
    "backend/app/models/logistic_regression_multi.pkl"
)

forest_model = joblib.load(
    "backend/app/models/random_forest_multi.pkl"
)

# Define the features
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

# Extract Random Forest feature importance
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

# Extract Logistic Regression coefficients
classifier = logistic_model.named_steps["model"]

coefficient_df = pd.DataFrame(
    classifier.coef_,
    columns=features,
    index=classifier.classes_
)

print("\nLOGISTIC REGRESSION COEFFICIENTS")
print("=" * 50)
print(coefficient_df.round(4))

# Save results
importance_df.to_csv(
    "datasets/random_forest_feature_importance.csv",
    index=False
)

coefficient_df.to_csv(
    "datasets/logistic_regression_coefficients.csv"
)

print("\nFeature analysis completed successfully!")
