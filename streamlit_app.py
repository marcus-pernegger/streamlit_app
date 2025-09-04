import streamlit as st
import pandas as pd
import requests
import json
from pathlib import Path


############################ GIFs ############################

APP_DIR = Path(__file__).parent
ASSETS = APP_DIR / "assets"
GIF_SUCCESS = ASSETS / "success.gif"
GIF_LOSER = ASSETS / "loser.gif"

def show_gif(path):
    if path.exists():
        st.image(str(path), use_container_width=True)

############################ CONSTANTS ############################

DATABASE_PATH = "./all_data/"

API_URL = st.secrets["api_url"]


############################ FONT SIZE ############################

st.markdown("""
<style>
/* Increase font size inside Streamlit alert boxes */
div.stAlert, div.stAlert p {
  font-size: 1.4rem;   /* ~20px; adjust as needed */
  line-height: 1.4;
}
</style>
""", unsafe_allow_html=True)

############################ HEADING ############################

def spinning_basketballs(n: int = 6, size_px: int = 52, spin_s: float = 1.2, bounce_s: float = 1.6):
    balls = "".join(
        f'<span class="ball-bounce" style="animation-delay:{i*0.12}s">'
        f'  <span class="ball-spin" style="font-size:{size_px}px">🏀</span>'
        f'</span>'
        for i in range(n)
    )
    st.markdown(
        f"""
        <style>
          .balls-wrap {{
            display:flex; gap:12px; justify-content:center; align-items:center;
            margin: 8px 0 24px;
          }}
          .ball-bounce {{
            display:inline-block;
            animation: bounce {bounce_s}s ease-in-out infinite;
          }}
          .ball-spin {{
            display:inline-block;
            animation: spin {spin_s}s linear infinite;
            filter: drop-shadow(0 2px 2px rgba(0,0,0,.15));
          }}
          @keyframes spin {{
            to {{ transform: rotate(360deg); }}
          }}
          @keyframes bounce {{
            0%,100% {{ transform: translateY(0); }}
            50%     {{ transform: translateY(-8px); }}
          }}
        </style>
        <div class="balls-wrap">{balls}</div>
        """,
        unsafe_allow_html=True,
    )

spinning_basketballs(n=1, size_px=100)

st.markdown("# What is your NBA dream team?")

st.markdown("")

st.markdown("### Team examples")

st.session_state["preselect_team"] = {
    "C": {
        "team": 0,
        "player": 0
    },
    "SG": {
        "team": 0,
        "player": 0
    },
    "PF": {
        "team": 0,
        "player": 0
    },
    "PG": {
        "team": 0,
        "player": 0
    },
    "SF": {
        "team": 0,
        "player": 0
    }
}

col_weak, col_average = st.columns([1, 2], vertical_alignment="center")

with col_weak:
    if st.button("'Weak' team"):
        st.session_state["preselect_team"] = {
            "C": {
                "team": 9,
                "player": 1
            },
            "SG": {
                "team": 17,
                "player": 6
            },
            "PF": {
                "team": 3,
                "player": 0
            },
            "PG": {
                "team": 28,
                "player": 1
            },
            "SF": {
                "team": 10,
                "player": 1
            }
        }

with col_average:
    if st.button("'Average' team"):
        st.session_state["preselect_team"] = {
            "C": {
                "team": 7,
                "player": 2
            },
            "SG": {
                "team": 23,
                "player": 2
            },
            "PF": {
                "team": 16,
                "player": 1
            },
            "PG": {
                "team": 20,
                "player": 0
            },
            "SF": {
                "team": 24,
                "player": 1
            }
        }

st.markdown("")
st.markdown("### Build your dream team ! 🏀")

############################ DROPDOWNS ############################

@st.cache_data
def load_pickles_to_df(pos):
    return pd.read_pickle(f"{DATABASE_PATH}X_2025_{pos}.pkl")

def team_player_picker(df: pd.DataFrame, pos_label: str, key_prefix: str):
    """Render two selectboxes side-by-side: Team (left) -> Player (right)."""
    teams = sorted(df["team"].unique())

    col_team, col_player = st.columns([1, 2], vertical_alignment="center")
    with col_team:
        team = st.selectbox(f"{pos_label} — Team", teams, key=f"{key_prefix}_team", index=st.session_state["preselect_team"][key_prefix]["team"])

    # Players filtered by the selected team
    players = (
        df.loc[df["team"] == team, "player"]
          .dropna()
          .sort_values()
          .unique()
    )

    # Key depends on team so the player box resets when team changes
    with col_player:
        player = st.selectbox(f"{pos_label} — Player", players, key=f"{key_prefix}_player_{team}", index=st.session_state["preselect_team"][key_prefix]["player"])

    return player, team

def get_select_dream_team():
    df_2025_C  = load_pickles_to_df("C")
    df_2025_SG = load_pickles_to_df("SG")
    df_2025_PF = load_pickles_to_df("PF")
    df_2025_PG = load_pickles_to_df("PG")
    df_2025_SF = load_pickles_to_df("SF")

    player_C_name,  player_C_team  = team_player_picker(df_2025_C,  "Select your Center",         "C")
    player_SG_name, player_SG_team = team_player_picker(df_2025_SG, "Select your Shooting Guard", "SG")
    player_PF_name, player_PF_team = team_player_picker(df_2025_PF, "Select your Power Forward",  "PF")
    player_PG_name, player_PG_team = team_player_picker(df_2025_PG, "Select your Point Guard",    "PG")
    player_SF_name, player_SF_team = team_player_picker(df_2025_SF, "Select your Small Forward",  "SF")

    dream_team = {
        player_C_name:  player_C_team,
        player_SG_name: player_SG_team,
        player_PF_name: player_PF_team,
        player_PG_name: player_PG_team,
        player_SF_name: player_SF_team
    }
    return dream_team

selected_dream_team = get_select_dream_team()

############################ PREDICT BUTTON & CALL API ############################

# # BUTTON

if st.button("Get my dream teams' winning rate", icon= "🌟"):

    response = requests.post(API_URL, json = selected_dream_team)


    if float(response.text) <= 0.3:

        st.error(f"Loser team - probability to win is between **{int(float(response.text)*100)}** % 🫠")

        show_gif(GIF_LOSER)

    elif float(response.text) > 1:

        st.success(f"🔥 🎉 Dream team - probability to win is 99% 🔥 🎉")

        show_gif(GIF_SUCCESS)

    elif float(response.text) >= 0.95:

        st.success(f"🔥 🎉 Dream team - probability to win is **{int(float(response.text)*100)}** %  🔥 🎉")

        show_gif(GIF_SUCCESS)

    elif float(response.text) >= 0.65:

        st.success(f"Nice team - probability to win is **{int(float(response.text)*100)}** %  🔥 🎉")

    else:
        st.warning(f"Average team - probability to win is **{int(float(response.text)*100)}** % 🫤")
