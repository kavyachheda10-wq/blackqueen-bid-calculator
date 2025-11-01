import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Black Queen Bid Calculator", layout="centered")
st.title("🃏 Black Queen Bid Calculator")

if "players" not in st.session_state:
    st.session_state.players = []
if "scores" not in st.session_state:
    st.session_state.scores = pd.DataFrame()

if not st.session_state.players:
    st.subheader("Add Players")

    num_players = st.number_input("Number of Players", min_value=3, max_value=10, value=4)
    player_names = [st.text_input(f"Player {i+1} Name:") for i in range(num_players)]

    if st.button("Start Game"):
        st.session_state.players = [name for name in player_names if name.strip()]
        if not st.session_state.players:
            st.warning("Please enter at least one valid player name before starting!")
        else:
            st.session_state.scores = pd.DataFrame(columns=["Round"] + st.session_state.players)
            st.success("✅ Game Started!")
            st.rerun()

else:
    st.subheader("Round Input")
    current_round = len(st.session_state.scores) + 1
    st.write(f"**Round {current_round}**")

    number_of_decks = st.number_input("Number of decks used:", min_value=1, max_value=3, value=1, step=1)

    if number_of_decks == 1:
        min_bid, max_bid = 75, 150
    elif number_of_decks == 2:
        min_bid, max_bid = 150, 300
    else:
        min_bid, max_bid = 225, 450

    bidder = st.selectbox("Who is making the bid?", st.session_state.players)
    teammates = st.multiselect(
        "Select teammates for this round (if any):",
        [p for p in st.session_state.players if p != bidder]
    )

    bid_amount = st.number_input(
        f"Enter bid amount ({min_bid} - {max_bid}):",
        min_value=min_bid,
        max_value=max_bid,
        step=5
    )

    result = st.radio("Did the bidder win the round?", ["Won", "Lost"], horizontal=True)

    if st.button("Submit Round"):
        round_data = {"Round": current_round}
        for player in st.session_state.players:
            round_data[player] = 0

        score_change = bid_amount if result == "Won" else -bid_amount
        involved_players = [bidder] + teammates

        for p in involved_players:
            round_data[p] = score_change

        st.session_state.scores = pd.concat(
            [st.session_state.scores, pd.DataFrame([round_data])],
            ignore_index=True
        )

        st.success(f"✅ Round {current_round} submitted! ({bidder} {'won' if result=='Won' else 'lost'} the bid)")
        st.rerun()

    if not st.session_state.scores.empty:
        st.subheader("📊 Game Summary")

        totals = st.session_state.scores[st.session_state.players].sum()
        total_df = pd.DataFrame({
            "Player": totals.index,
            "Total Points": totals.values
        }).sort_values(by="Total Points", ascending=False)

        st.dataframe(st.session_state.scores)
        st.write("🏆 **Current Leader:**", total_df.iloc[0]["Player"])
        st.bar_chart(total_df.set_index("Player"))

        # 🪄 NEW: Score history per player
        st.subheader("📈 Score History by Player")
        fig, ax = plt.subplots()
        for player in st.session_state.players:
            ax.plot(
                st.session_state.scores["Round"],
                st.session_state.scores[player].cumsum(),
                marker="o",
                label=player
            )

        ax.set_xlabel("Round")
        ax.set_ylabel("Total Points")
        ax.set_title("Score Progression")
        ax.legend()
        st.pyplot(fig)

    if st.button("Reset Game"):
        st.session_state.players = []
        st.session_state.scores = pd.DataFrame()
        st.rerun()
