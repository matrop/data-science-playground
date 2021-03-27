import streamlit as st
import numpy as np
import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt

from typing import List, Dict

model = joblib.load("../notebooks/rf_regressor.joblib")
df_raw = {}
df_raw["is_GK"] = False  # We do not built GKs in this demo

dict_positions = {
    "defender": ['LWB', 'LB', 'CB', 'RB', 'RWB'],
    "midfielder": ['LM', 'CDM', 'CM', 'CAM', 'RM'],
    "striker": ['LW', 'CF', 'ST', 'RW'],
}

# List of skills to average in order to obtain the overall skill of the player. Since I don't know
# this is computed in detail, I try to guess the features
overall_skills = {
    "defender": [
        'defending_marking', 'defending_standing_tackle', 'defending_sliding_tackle',
        'mentality_aggression', 'mentality_interceptions', 'mentality_positioning',
        'movement_sprint_speed', 'movement_agility', 'movement_reactions', 'movement_balance',
        'skill_long_passing', 'power_strength',
    ],
    "midfielder": [
        'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
        'skill_ball_control', 'power_shot_power', 'power_jumping', 'power_stamina',
        'power_strength', 'power_long_shots', 'attacking_crossing', 'attacking_short_passing',
        'movement_acceleration', 'movement_sprint_speed', 'movement_agility',
        'mentality_positioning', 'mentality_vision'
    ],
    "striker": [
        'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
        'attacking_short_passing', 'attacking_volleys', 'movement_acceleration',
        'movement_sprint_speed', 'movement_agility', 'power_shot_power', 'power_jumping',
        'power_stamina', 'power_strength', 'power_long_shots', 'mentality_positioning',
        'mentality_penalties', 'mentality_composure'
    ],
}

preffered_foot_map = {
    "Left": 0,
    "Right": 1,
}


def get_position_flags(positions: List["str"]) -> None:
    position_aliases = [position for key in dict_positions for position in dict_positions[key]]
    for pos in position_aliases:
        if pos in positions:
            df_raw["is_" + pos] = True
        else:
            df_raw["is_" + pos] = False


def get_position_groups(positions: List["str"]) -> None:
    for key in ["is_defender", "is_midfielder", "is_striker"]:
        df_raw[key] = False

    for key in dict_positions:
        if len(set(positions).intersection(set(dict_positions[key]))) > 0:
            df_raw["is_" + key] = True


def get_overall_rating() -> float:
    pos_group_overall = []

    for pos_group in ["defender", "midfielder", "striker"]:
        if not df_raw["is_" + pos_group]:
            continue

        pos_group_overall.append(
            np.mean([df_raw[skill] for skill in overall_skills[pos_group]])
        )

    return np.mean(pos_group_overall)

# =============================================================================
# Website Widgets
# =============================================================================


# TODO: Can this be done nicer?
positions = st.sidebar.multiselect(
    "Positions",
    [position for key in dict_positions for position in dict_positions[key]]
)

get_position_groups(positions)
get_position_flags(positions)

st.sidebar.write("---")

with st.sidebar.beta_expander("Player Information"):
    df_raw["age"] = st.slider("Age", min_value=16, max_value=42, value=16)
    df_raw["height_cm"] = st.slider("Height (cm)", min_value=156, max_value=205)
    df_raw["weight_kg"] = st.slider("Weight (kg)", min_value=50, max_value=110)

with st.sidebar.beta_expander("Technical Details"):
    selected_foot = st.selectbox("Preferred foot", ["Left", "Right"])
    df_raw["preferred_foot"] = preffered_foot_map[selected_foot]

    df_raw["weak_foot"] = st.slider("Weak Foot Skill", min_value=1, max_value=5)
    df_raw["skill_moves"] = st.slider("Skill moves", min_value=1, max_value=5)

with st.sidebar.beta_expander("Organizational Details"):
    df_raw["international_reputation"] = st.slider("Int. Reputation", min_value=1, max_value=5)
    df_raw["contract_valid_until"] = int(st.selectbox("Contract Expiration", np.arange(2019, 2027)))

with st.sidebar.beta_expander("Attacking"):
    for col in [
        'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
        'attacking_short_passing', 'attacking_volleys'
    ]:
        df_raw[col] = st.slider(col[10:], min_value=40, max_value=100)

with st.sidebar.beta_expander("Skill"):
    for col in [
            'skill_dribbling', 'skill_curve', 'skill_fk_accuracy', 'skill_long_passing',
            'skill_ball_control',
    ]:
        df_raw[col] = st.slider(col[6:], min_value=40, max_value=100)


with st.sidebar.beta_expander("Movement"):
    for col in [
        'movement_acceleration', 'movement_sprint_speed', 'movement_agility', 'movement_reactions',
        'movement_balance',
    ]:
        df_raw[col] = st.slider(col[9:], min_value=40, max_value=100)

with st.sidebar.beta_expander("Power"):
    for col in [
        'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength', 'power_long_shots'
    ]:
        df_raw[col] = st.slider(col[6:], min_value=40, max_value=100)

with st.sidebar.beta_expander("Mentality"):
    for col in [
        'mentality_aggression', 'mentality_interceptions', 'mentality_positioning',
        'mentality_vision', 'mentality_penalties', 'mentality_composure'
    ]:
        df_raw[col] = st.slider(col[10:], min_value=40, max_value=100)

with st.sidebar.beta_expander("Defending"):
    for col in [
        'defending_marking', 'defending_standing_tackle', 'defending_sliding_tackle'
    ]:
        df_raw[col] = st.slider(col[10:], min_value=40, max_value=100)

with st.sidebar.beta_expander("Goalkeeping"):
    for col in [
            'goalkeeping_diving', 'goalkeeping_handling', 'goalkeeping_kicking',
            'goalkeeping_positioning', 'goalkeeping_reflexes'
    ]:
        df_raw[col] = st.slider(col, min_value=40, max_value=100)

df_raw["overall"] = get_overall_rating()

"""
# FIFA 20 Data Set - Value Prediction Demo

### Note

This project is focused on EDA. Because of this, the model to predict players values hasn't received
as much attention as it could have. Nevertheless, this demo shows how one could deploy such a model
to potential users.

### Skill overview
"""

if np.isnan(df_raw["overall"]):
    st.write(
        "(Hint: In order for the overall skill to be computed, you need to select at least "
        "one player position)"
    )


df = pd.DataFrame(df_raw, index=[0])

# Plot skill overview
sns.set()
palette = [  # Plot overall bar orange, the rest blue
    "CornFlowerBlue" if col != "overall" else "DarkOrange"
    for col in df.iloc[:, 30:].columns
]

fig, ax = plt.subplots(figsize=(10, 5))
ax = sns.barplot(data=df.iloc[:, 30:], palette=palette)
plt.xticks(rotation=90)
plt.yticks(np.arange(0, 110, 10))

st.pyplot(fig)

"""
---
"""

if st.button("Predict value"):
    st.write("Predicted player value: ", np.floor(np.exp(model.predict(df)[0])))
