
from pathlib import Path

import joblib
import pandas as pd


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = BASE_DIR / "backend" / "app" / "models"

DATA_PATH = BASE_DIR / "datasets" / "epl_multi_season.csv"


# --------------------------------------------------
# REQUIRED DATASET COLUMNS
# --------------------------------------------------

REQUIRED_COLUMNS = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR"
]


# --------------------------------------------------
# MODEL FEATURES
# Keep this order consistent with model training.
# --------------------------------------------------

FEATURES = [
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


# --------------------------------------------------
# LOAD TRAINED MODELS
# --------------------------------------------------

logistic_model = joblib.load(
    MODEL_DIR / "logistic_regression_multi.pkl"
)

random_forest_model = joblib.load(
    MODEL_DIR / "random_forest_multi.pkl"
)


# --------------------------------------------------
# LOAD AND VALIDATE HISTORICAL DATA
# --------------------------------------------------

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Historical dataset not found: {DATA_PATH}"
    )

matches = pd.read_csv(DATA_PATH)

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in matches.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset is missing required columns: {missing_columns}"
    )

matches["Date"] = pd.to_datetime(
    matches["Date"],
    errors="coerce"
)

matches["FTHG"] = pd.to_numeric(
    matches["FTHG"],
    errors="coerce"
)

matches["FTAG"] = pd.to_numeric(
    matches["FTAG"],
    errors="coerce"
)

matches = matches.dropna(
    subset=REQUIRED_COLUMNS
).copy()

matches = matches.sort_values(
    "Date"
).reset_index(drop=True)


# --------------------------------------------------
# AVAILABLE TEAMS
# --------------------------------------------------

AVAILABLE_TEAMS = sorted(
    set(matches["HomeTeam"].dropna()) |
    set(matches["AwayTeam"].dropna())
)


# Latest match date contained in the dataset
LATEST_DATA_DATE = matches["Date"].max()


# --------------------------------------------------
# VALIDATE PREDICTION INPUT
# --------------------------------------------------

def validate_prediction_input(
    home_team,
    away_team,
    prediction_date
):
    """
    Validate the two teams and prediction date.
    """

    if not isinstance(home_team, str) or not home_team.strip():
        raise ValueError(
            "Please provide a valid home team name."
        )

    if not isinstance(away_team, str) or not away_team.strip():
        raise ValueError(
            "Please provide a valid away team name."
        )

    home_team = home_team.strip()
    away_team = away_team.strip()

    if home_team not in AVAILABLE_TEAMS:
        raise ValueError(
            f"Unknown home team: {home_team}. "
            "Please use a team name from the dataset."
        )

    if away_team not in AVAILABLE_TEAMS:
        raise ValueError(
            f"Unknown away team: {away_team}. "
            "Please use a team name from the dataset."
        )

    if home_team == away_team:
        raise ValueError(
            "Home team and away team cannot be the same."
        )

    if not isinstance(prediction_date, str):
        raise ValueError(
            "Invalid prediction date. Use YYYY-MM-DD format."
        )

    try:
        prediction_date = pd.to_datetime(
            prediction_date,
            format="%Y-%m-%d",
            errors="raise"
        )

    except (TypeError, ValueError):
        raise ValueError(
            "Invalid prediction date. Use YYYY-MM-DD format."
        )

    return home_team, away_team, prediction_date


# --------------------------------------------------
# CALCULATE TEAM STATISTICS
# --------------------------------------------------

def get_team_statistics(
    team,
    prediction_date,
    venue=None
):
    """
    Calculate a team's recent statistics using only
    matches played before the prediction date.

    venue:
        None  = all matches
        home  = home matches only
        away  = away matches only
    """

    team_matches = matches[
        (matches["HomeTeam"] == team) |
        (matches["AwayTeam"] == team)
    ].copy()

    # Prevent future information from entering predictions.
    team_matches = team_matches[
        team_matches["Date"] < prediction_date
    ]

    if venue == "home":
        team_matches = team_matches[
            team_matches["HomeTeam"] == team
        ]

    elif venue == "away":
        team_matches = team_matches[
            team_matches["AwayTeam"] == team
        ]

    elif venue is not None:
        raise ValueError(
            "Venue must be None, 'home', or 'away'."
        )

    # Use the five most recent eligible matches.
    team_matches = team_matches.sort_values(
        "Date",
        ascending=False
    ).head(5)

    if team_matches.empty:
        return {
            "form_points": 0,
            "avg_scored": 0.0,
            "avg_conceded": 0.0,
            "matches_played": 0
        }

    scored = []
    conceded = []
    points = []

    for _, match in team_matches.iterrows():

        if match["HomeTeam"] == team:

            goals_for = match["FTHG"]
            goals_against = match["FTAG"]

        else:

            goals_for = match["FTAG"]
            goals_against = match["FTHG"]

        scored.append(float(goals_for))
        conceded.append(float(goals_against))

        if goals_for > goals_against:
            points.append(3)

        elif goals_for == goals_against:
            points.append(1)

        else:
            points.append(0)

    return {
        "form_points": sum(points),
        "avg_scored": sum(scored) / len(scored),
        "avg_conceded": sum(conceded) / len(conceded),
        "matches_played": len(team_matches)
    }


# --------------------------------------------------
# PREPARE MODEL FEATURES
# --------------------------------------------------

def prepare_prediction_features(
    home_team,
    away_team,
    prediction_date
):
    """
    Build the 16 features required by the trained models.
    """

    home = get_team_statistics(
        home_team,
        prediction_date
    )

    away = get_team_statistics(
        away_team,
        prediction_date
    )

    home_venue = get_team_statistics(
        home_team,
        prediction_date,
        venue="home"
    )

    away_venue = get_team_statistics(
        away_team,
        prediction_date,
        venue="away"
    )

    feature_values = {
        "HomeFormPoints": home["form_points"],
        "AwayFormPoints": away["form_points"],

        "HomeAvgGoalsScored": home["avg_scored"],
        "AwayAvgGoalsScored": away["avg_scored"],

        "HomeAvgGoalsConceded": home["avg_conceded"],
        "AwayAvgGoalsConceded": away["avg_conceded"],

        "HomeMatchesPlayed": home["matches_played"],
        "AwayMatchesPlayed": away["matches_played"],

        "HomeVenueFormPoints": home_venue["form_points"],
        "AwayVenueFormPoints": away_venue["form_points"],

        "HomeVenueAvgGoalsScored": home_venue["avg_scored"],
        "AwayVenueAvgGoalsScored": away_venue["avg_scored"],

        "HomeVenueAvgGoalsConceded": home_venue["avg_conceded"],
        "AwayVenueAvgGoalsConceded": away_venue["avg_conceded"],

        "HomeVenueMatchesPlayed": home_venue["matches_played"],
        "AwayVenueMatchesPlayed": away_venue["matches_played"]
    }

    return pd.DataFrame(
        [feature_values],
        columns=FEATURES
    )


# --------------------------------------------------
# FORMAT MODEL PROBABILITIES
# --------------------------------------------------

def format_probabilities(model, input_data):
    """
    Generate and format model outcome probabilities.
    """

    probabilities = model.predict_proba(
        input_data
    )[0]

    return {
        str(label): round(float(probability), 4)
        for label, probability in zip(
            model.classes_,
            probabilities
        )
    }


# --------------------------------------------------
# MAIN MATCH PREDICTION FUNCTION
# --------------------------------------------------

def predict_match(
    home_team,
    away_team,
    prediction_date
):
    """
    Generate match outcome probabilities using
    Logistic Regression and Random Forest.

    Only historical matches before prediction_date
    are used to calculate team statistics.
    """

    # Validate prediction inputs.
    home_team, away_team, prediction_date = (
        validate_prediction_input(
            home_team,
            away_team,
            prediction_date
        )
    )

    # Prepare the model input.
    input_data = prepare_prediction_features(
        home_team,
        away_team,
        prediction_date
    )

    # Generate predictions from both models.
    logistic_probabilities = format_probabilities(
        logistic_model,
        input_data
    )

    random_forest_probabilities = format_probabilities(
        random_forest_model,
        input_data
    )

    # Return prediction results.
    return {
        "home_team": home_team,
        "away_team": away_team,

        "prediction_date": str(
            prediction_date.date()
        ),

        "latest_historical_data_date": str(
            LATEST_DATA_DATE.date()
        ),

        "logistic_regression": logistic_probabilities,

        "random_forest": random_forest_probabilities,

        "disclaimer": (
            "Predictions are statistical estimates, "
            "not guaranteed match outcomes."
        )
    }
