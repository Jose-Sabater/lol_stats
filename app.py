import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# TODO add a sidebar to select the page
# TODO move the data into a database
# TODO: move this to a separate file
matches = pd.read_csv("./data/historic_matches_db.csv")
# rename columns
matches = matches.rename(
    columns={
        "game_date": "date",
        "game_mode": "mode",
        "teamPosition": "position",
        "championName": "champion",
    }
)
players = pd.read_csv("./data/historic_players.csv")


st.markdown(
    "<h1 style='text-align: center; color: white; padding-bottom: 40px;'>⚔️ Totis League History 🛡️</h1>",
    unsafe_allow_html=True,
)


# Main stats secion
st.write("## **📖General Stats**")
st.sidebar.write("Game mode")
aram = st.sidebar.checkbox("Aram", value=True)
classic = st.sidebar.checkbox("Classic", value=True)
# ---------------------------------------------df filtering-------------------------------------------------
s_gm = []  # Selected game modes
if aram:
    s_gm.append("ARAM")
if classic:
    s_gm.append("CLASSIC")
s_matches = matches[matches["mode"].isin(s_gm)].copy()
# ---------------------------------------------------------------------------------------------------------------


col1, col2 = st.columns([3, 1])
with col1:
    # TODO: move this into a function
    intro_table = pd.DataFrame(
        {
            "Total matches": [s_matches.shape[0]],
            "Wins": [s_matches["win"].sum()],
            "Losses": [s_matches.shape[0] - s_matches["win"].sum()],
            "Winrate": [s_matches["win"].sum() / s_matches.shape[0]],
            "Total kills": [s_matches["kills"].sum()],
            "Total deaths": [s_matches["deaths"].sum()],
            "K/D": [s_matches["kills"].sum() / s_matches["deaths"].sum()],
            # "Pentakills": [s_matches["pentaKills"].sum()],
            # "Quadrakills": [s_matches["quadraKills"].sum()],
        },
        index=[""],
    )
    st.table(intro_table)
with col2:
    pentakills = s_matches["pentaKills"].sum()
    quadrakills = s_matches["quadraKills"].sum()
    kills_data = {"Amount": [pentakills, quadrakills]}
    kills_df = pd.DataFrame(kills_data, index=["Pentakills", "Quadrakills"])
    st.bar_chart(kills_df, height=200)

col1, col2, col3 = st.columns(3)
with col1:
    game_mode_counts = matches["mode"].value_counts()
    game_mode_labels = ["ARAM", "CLASSIC", "URF", "CHERRY", "NEXUS"]

    fig = px.pie(
        game_mode_counts,
        values=game_mode_counts,
        names=game_mode_labels,
        labels=game_mode_labels,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="Game type")

    st.plotly_chart(fig)
with col2:
    position_counts = matches["position"].value_counts()

    fig = px.pie(
        position_counts,
        values=position_counts,
        names=position_counts.index,
        labels=position_counts.index,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="Position")

    st.plotly_chart(fig)

with col3:
    most_played_friends = players["summoner_name"].value_counts().head(15)
    # make a pie chart
    fig = px.pie(
        most_played_friends,
        values=most_played_friends,
        names=most_played_friends.index,
        labels=most_played_friends.index,
        hole=0.4,
    )
    fig.update_traces(textinfo="percent+label", textposition="inside")
    fig.update_layout(title="Most played friends")
    # remove the legend
    fig.update_layout(showlegend=False)

    st.plotly_chart(fig)


st.write("## 🤖**Champions**")
col1, col2, col3 = st.columns([1, 2, 2])
with col1:
    champion_winrate = (
        s_matches.groupby("champion")["win"].sum()
        / s_matches.groupby("champion")["win"].count()
    ).mul(100)
    champion_winrate = champion_winrate.sort_values(ascending=False)
    champion_winrate = champion_winrate.reset_index()
    champion_winrate.columns = ["champion", "winrate"]
    champion_winrate["winrate"] = champion_winrate["winrate"].round(2)
    champion_info = champion_winrate.copy()
    champion_counts = s_matches["champion"].value_counts()
    champion_info["played"] = champion_info["champion"].map(champion_counts)
    champion_kda = (
        (
            s_matches.groupby("champion")["kills"].sum()
            + s_matches.groupby("champion")["assists"].sum()
        )
        / s_matches.groupby("champion")["deaths"].sum()
    ).round(2)
    champion_info["kda"] = champion_info["champion"].map(champion_kda)
    st.write(champion_info)

with col2:
    # most played champs bar
    most_played_champs = s_matches["champion"].value_counts().head(15)
    fig = px.bar(
        most_played_champs,
        x=most_played_champs.index,
        y=most_played_champs,
        labels={"x": "Champion", "y": "Matches played"},
    )
    fig.update_layout(title="Most played champions")
    fig.update_traces(text=most_played_champs, textposition="outside")
    st.plotly_chart(fig)

with col3:
    # most successful champs (winrate) if played more than 5 times
    # Filter out champions played 5 times or less
    champions_played_more_than_5 = champion_counts[champion_counts > 5].index
    most_successful_champs = champion_winrate[
        champion_winrate["champion"].isin(champions_played_more_than_5)
    ]

    # Take the top 15 champions
    most_successful_champs = most_successful_champs.head(15)

    fig = px.bar(
        most_successful_champs,
        x=most_successful_champs["champion"],
        y=most_successful_champs["winrate"],
        labels={"x": "Champion", "y": "Winrate (%)"},
    )
    fig.update_layout(title="Most successful champions (played at least 5 times)")
    fig.update_traces(text=most_successful_champs["winrate"], textposition="outside")
    st.plotly_chart(fig)


# ---------------------------------------------Champion details -------------------------------------------------
st.write("## 📊**Champion details**")
# Create a multiselect widget
champion_list = matches["champion"].unique()
champion_list.sort()
# TODO if in the future interested in adding all champions
# champion_list = np.insert(champion_list, 0, "All champions")
col1, _ = st.columns([1, 2])
with col1:
    s_champion = st.selectbox(
        "Select a champion", champion_list, placeholder="Choose a champion"
    )
    sc_matches = matches[matches["champion"] == s_champion]
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.write(
        matches[matches["champion"] == s_champion][
            ["date", "mode", "win", "kills", "deaths"]
        ]
    )
    # TODO move this logic out of the app
    sc_matches.rename(
        columns={
            "spell1Casts": "Q",
            "spell2Casts": "W",
            "spell3Casts": "E",
            "spell4Casts": "R",
        },
        inplace=True,
    )

    # Columns to be plotted
    cast_columns = ["Q", "W", "E", "R"]

    # Reshape the data
    melted_data = sc_matches.melt(
        value_vars=cast_columns, var_name="Spell", value_name="Casts"
    )

    # Calculate the average casts for each spell
    average_casts = melted_data.groupby("Spell")["Casts"].mean().reset_index()

    # Plotting the bar chart for average casts
    st.plotly_chart(
        px.bar(
            average_casts,
            x="Spell",
            y="Casts",
            color="Spell",
            labels={"Spell": "Spell", "Casts": "Average Casts"},
        ),
        use_container_width=True,
    )
with col2:
    fig = px.line(sc_matches, x="date", y=["kills", "deaths"], title="Kills vs Deaths")

    st.plotly_chart(fig, use_container_width=True)
with col3:
    fig = px.line(
        sc_matches,
        x="date",
        y=["totalDamageDealtToChampions", "totalDamageTaken"],
    )
    fig.data[0].name = "Total Damage Dealt"
    fig.data[1].name = "Total Damage Taken"

    fig.update_layout(
        title="Damage Dealt vs Damage Taken",
        xaxis_title="Date",
        yaxis_title="Damage",
        legend_title="Type of Damage",
    )

    # Plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)
# ---------------------------------------------------------------------------------------------------------------

st.write("## **📈Other Stats**")
col1, col2, col3 = st.columns(3)
# Use the first column to place the multiselect, making it 1/3 of the screen space
with col1:
    s_gt = st.multiselect(
        label="Select Game Mode",
        options=["ARAM", "CLASSIC"],
        default=["ARAM", "CLASSIC"],
    )

s_matches = matches[matches["mode"].isin(s_gt)]
st.write("Total matches registered for Totis: ", s_matches.shape[0])


st.write(
    # s_matches
    s_matches[
        [
            "date",
            "mode",
            "win",
            "champion",
            "kills",
            "deaths",
            "assists",
            "position",
        ]
    ],
)
