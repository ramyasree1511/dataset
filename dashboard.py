# ipl_interactive_exact_columns.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="IPL — Exact Columns Interactive Dashboard", layout="wide")
st.title("🏏 IPL — Interactive Dashboard (uses exact CSV column names)")

st.markdown(
    """

Click any question to expand and view results (table + chart where helpful).
"""
)

# Load data: upload or fallback to /mnt/data/matches.csv
uploaded = st.file_uploader("Upload IPL matches CSV (or leave empty to use /mnt/data/matches.csv)", type=["csv"])
if uploaded:
    df = pd.read_csv(uploaded)
    st.success("File uploaded.")
else:
    try:
        df = pd.read_csv("/mnt/data/matches.csv")
        st.info("Loaded /mnt/data/matches.csv")
    except Exception as e:
        st.error("Could not load dataset. Please upload a CSV file.")
        st.stop()

# Convenience: a function to safely get series or None
def col(c):
    return c if c in df.columns else None

# Qs — each in an expander with chart/table
# 1) Which team won the most matches in 2008?
with st.expander("🏆 Which team won the most matches in 2008?"):
    if col("Season") and col("Winner"):
        d2008 = df[df["Season"] == 2008].dropna(subset=["Winner"])
        if d2008.empty:
            st.write("No data for Season == 2008")
        else:
            wins_2008 = d2008["Winner"].value_counts()
            st.write(wins_2008)
            st.bar_chart(wins_2008)
            st.success(f"Top: {wins_2008.index[0]} ({wins_2008.iloc[0]} wins)")
    else:
        st.warning("Columns 'Season' and/or 'Winner' missing.")

# 2) Which city hosted the highest number of matches?
with st.expander("🌆 Which city hosted the highest number of matches?"):
    if col("City"):
        city_counts = df["City"].value_counts()
        st.write(city_counts.head(20))
        st.bar_chart(city_counts.head(10))
        st.success(f"Top city: {city_counts.index[0]} ({city_counts.iloc[0]} matches)")
    else:
        st.warning("Column 'City' missing.")

# 3) Which team won more often while batting first?
with st.expander("🔥 Which team won more often while batting first?"):
    if col("Win_By_Runs") and col("Winner"):
        bat_first = df[df["Win_By_Runs"] > 0]["Winner"].value_counts()
        st.write(bat_first.head(20))
        st.bar_chart(bat_first.head(10))
        if not bat_first.empty:
            st.success(f"Top batting-first winner: {bat_first.index[0]} ({bat_first.iloc[0]} wins)")
    else:
        st.warning("Columns 'Win_By_Runs' and/or 'Winner' missing.")

# 4) Which team won more often while fielding first?
with st.expander("🎯 Which team won more often while fielding first?"):
    if col("Win_By_Wickets") and col("Winner"):
        field_first = df[df["Win_By_Wickets"] > 0]["Winner"].value_counts()
        st.write(field_first.head(20))
        st.bar_chart(field_first.head(10))
        if not field_first.empty:
            st.success(f"Top fielding-first winner: {field_first.index[0]} ({field_first.iloc[0]} wins)")
    else:
        st.warning("Columns 'Win_By_Wickets' and/or 'Winner' missing.")

# 5) Does winning the toss increase the chance of winning the match?
with st.expander("🪙 Does winning the toss increase the chance of winning the match?"):
    if col("Toss_Winner") and col("Winner"):
        toss_same = (df["Toss_Winner"] == df["Winner"])
        pct = toss_same.mean() * 100
        st.metric("Toss-winner also match-winner", f"{pct:.2f}%")
        st.write("Counts (True = toss-winner won match):")
        st.write(toss_same.value_counts())
        if pct > 50:
            st.success("Yes — toss winners win >50% of the time.")
        else:
            st.info("No strong advantage observed (≤50%).")
    else:
        st.warning("Columns 'Toss_Winner' and/or 'Winner' missing.")

# 6) Which toss decision (bat or field) leads to more wins?
with st.expander("📊 Which toss decision (bat or field) leads to more wins?"):
    if col("Toss_Decision") and col("Toss_Winner") and col("Winner"):
        decision_rates = df.groupby("Toss_Decision").apply(lambda x: (x["Toss_Winner"] == x["Winner"]).mean()).sort_values(ascending=False)
        st.write(decision_rates)
        st.bar_chart(decision_rates)
        st.success(f"Most successful toss decision: {decision_rates.index[0]}")
    else:
        st.warning("Columns 'Toss_Decision', 'Toss_Winner' or 'Winner' missing.")

# 7) Which stadium hosted the most matches in the dataset?
with st.expander("🏟️ Which stadium hosted the most matches in the dataset?"):
    if col("Venue"):
        venue_counts = df["Venue"].value_counts()
        st.write(venue_counts.head(20))
        st.bar_chart(venue_counts.head(10))
        st.success(f"Top venue: {venue_counts.index[0]} ({venue_counts.iloc[0]} matches)")
    else:
        st.warning("Column 'Venue' missing.")

# 8) Which venue saw the most wins for home teams?
with st.expander("🏠 Which venue saw the most wins for home teams?"):
    if col("Venue") and col("Team1") and col("Winner"):
        home_wins = df[df["Team1"] == df["Winner"]]["Venue"].value_counts()
        st.write(home_wins.head(20))
        st.bar_chart(home_wins.head(10))
        if not home_wins.empty:
            st.success(f"Top for home wins: {home_wins.index[0]} ({home_wins.iloc[0]} wins)")
    else:
        st.warning("Columns 'Venue'/'Team1'/'Winner' missing.")

# 9) Which venue saw the most wins for away teams?
with st.expander("🚀 Which venue saw the most wins for away teams?"):
    if col("Venue") and col("Team2") and col("Winner"):
        away_wins = df[df["Team2"] == df["Winner"]]["Venue"].value_counts()
        st.write(away_wins.head(20))
        st.bar_chart(away_wins.head(10))
        if not away_wins.empty:
            st.success(f"Top for away wins: {away_wins.index[0]} ({away_wins.iloc[0]} wins)")
    else:
        st.warning("Columns 'Venue'/'Team2'/'Winner' missing.")

# 10) Is there any relationship between toss winner and match winner?
with st.expander("🔗 Is there any relationship between toss winner and match winner?"):
    if col("Toss_Winner") and col("Winner"):
        rel = df.groupby(["Toss_Winner", "Winner"]).size().reset_index(name="count").sort_values("count", ascending=False)
        st.write(rel.head(20))
        st.success("Shown top toss->match winner conversions.")
    else:
        st.warning("Columns 'Toss_Winner' and/or 'Winner' missing.")

# 11) Which team had the highest win percentage in this dataset?
with st.expander("📈 Which team had the highest win percentage in this dataset?"):
    if col("Winner") and col("Team1") and col("Team2"):
        appearances = pd.concat([df["Team1"], df["Team2"]]).value_counts()
        wins = df["Winner"].value_counts()
        teams = sorted(set(appearances.index).union(set(wins.index)))
        stats = []
        for t in teams:
            a = appearances.get(t, 0)
            w = wins.get(t, 0)
            pct = (w / a * 100) if a > 0 else np.nan
            stats.append((t, int(a), int(w), pct))
        stats_df = pd.DataFrame(stats, columns=["team","appearances","wins","win_pct"]).sort_values("win_pct", ascending=False)
        st.dataframe(stats_df.head(20))
        st.success(f"Top win% team: {stats_df.iloc[0]['team']} ({stats_df.iloc[0]['win_pct']:.2f}%)")
    else:
        st.warning("Columns 'Team1'/'Team2'/'Winner' missing.")

# 12) How often did the team winning the toss lose the match?
with st.expander("❓ How often did the team winning the toss lose the match?"):
    if col("Toss_Winner") and col("Winner"):
        toss_lost_pct = (df["Toss_Winner"] != df["Winner"]).mean() * 100
        st.metric("Toss-winner lost (%)", f"{toss_lost_pct:.2f}%")
        st.write((df["Toss_Winner"] != df["Winner"]).value_counts())
    else:
        st.warning("Columns 'Toss_Winner'/'Winner' missing.")

# 13) Which city's teams performed the best overall?
with st.expander("🏙️ Which city's teams performed the best overall?"):
    if col("City") and col("Winner"):
        city_team = df.groupby(["City","Winner"]).size().reset_index(name="wins")
        top_per_city = city_team.loc[city_team.groupby("City")["wins"].idxmax()].sort_values("wins", ascending=False)
        st.dataframe(top_per_city.head(20))
    else:
        st.warning("Columns 'City'/'Winner' missing.")

# 14) Percentage won by batting first vs fielding first
with st.expander("⚖️ What percentage of matches were won by batting first versus fielding first?"):
    if col("Win_By_Runs") and col("Win_By_Wickets"):
        bat_wins = (df["Win_By_Runs"] > 0).sum()
        field_wins = (df["Win_By_Wickets"] > 0).sum()
        total_decisive = bat_wins + field_wins
        if total_decisive > 0:
            st.write({
                "bat_first_pct": f"{bat_wins/total_decisive*100:.2f}%",
                "field_first_pct": f"{field_wins/total_decisive*100:.2f}%"
            })
        else:
            st.info("No decisive Win_By_Runs/Win_By_Wickets data.")
    else:
        st.warning("Columns 'Win_By_Runs' and/or 'Win_By_Wickets' missing.")

# 15) Which team lost the most tosses but still won matches?
with st.expander("🏅 Which team lost the most tosses but still won matches?"):
    if col("Toss_Winner") and col("Winner") and col("Team1") and col("Team2"):
        played_counts = pd.concat([df["Team1"], df["Team2"]]).value_counts()
        rows = []
        for t in played_counts.index:
            played_mask = (df["Team1"] == t) | (df["Team2"] == t)
            toss_lost = ((df["Toss_Winner"] != t) & played_mask).sum()
            wins = (df["Winner"] == t).sum()
            rows.append((t, int(toss_lost), int(wins)))
        tl_df = pd.DataFrame(rows, columns=["team","tosses_lost_while_playing","wins"]).sort_values("tosses_lost_while_playing", ascending=False)
        st.dataframe(tl_df.head(20))
    else:
        st.warning("Required columns missing.")

# 16) Are there cities where fielding first gives a higher chance of winning?
with st.expander("🧭 Are there cities where fielding first gives a higher chance of winning?"):
    if col("City") and col("Toss_Decision") and col("Toss_Winner") and col("Winner"):
        temp = df.dropna(subset=["City","Toss_Decision","Toss_Winner","Winner"]).copy()
        temp["toss_winner_won"] = (temp["Toss_Winner"] == temp["Winner"]).astype(int)
        stats = temp.groupby(["City","Toss_Decision"])["toss_winner_won"].mean().unstack().fillna(0)
        # show cities where field rate > bat rate
        cond = stats[(stats.get("field",0) > stats.get("bat",0))]
        st.write(cond.sort_values("field", ascending=False).head(30))
        if cond.empty:
            st.info("No city where 'field' decision shows higher toss-winner success than 'bat'.")
    else:
        st.warning("Required columns missing.")

# 17) Which toss decision is more successful at each venue?
with st.expander("🏟️ Which toss decision is more successful at each venue?"):
    if col("Venue") and col("Toss_Decision") and col("Toss_Winner") and col("Winner"):
        t = df.dropna(subset=["Venue","Toss_Decision","Toss_Winner","Winner"]).copy()
        t["toss_winner_won"] = (t["Toss_Winner"] == t["Winner"]).astype(int)
        stats_v = t.groupby(["Venue","Toss_Decision"])["toss_winner_won"].mean().unstack().fillna(0)
        best = stats_v.idxmax(axis=1)
        st.dataframe(best.reset_index().rename(columns={0:"best_decision"}).head(200))
    else:
        st.warning("Required columns missing.")

# 18) Which team won matches most frequently in their home city?
with st.expander("🏘️ Which team won matches most frequently in their home city?"):
    if col("City") and col("Team1") and col("Winner"):
        home_city_wins = df[df["Team1"] == df["Winner"]].groupby(["City","Team1"]).size().reset_index(name="home_wins").sort_values("home_wins", ascending=False)
        st.dataframe(home_city_wins.head(30))
    else:
        st.warning("Required columns missing.")

# 19) Which opponent teams faced each other most often?
with st.expander("🔁 Which opponent teams faced each other most often?"):
    if col("Team1") and col("Team2"):
        pairs = df.apply(lambda r: tuple(sorted([r["Team1"], r["Team2"]])), axis=1)
        pair_counts = pairs.value_counts().reset_index()
        pair_counts.columns = ["pair","count"]
        st.dataframe(pair_counts.head(30))
    else:
        st.warning("Columns 'Team1'/'Team2' missing.")

# 20) Are there stadiums where the same team keeps winning?
with st.expander("🏆 Are there stadiums where the same team keeps winning?"):
    if col("Venue") and col("Winner"):
        v = df.groupby(["Venue","Winner"]).size().reset_index(name="wins")
        total_v = df.groupby("Venue").size().reset_index(name="total")
        merged = v.merge(total_v, on="Venue")
        merged["prop"] = merged["wins"] / merged["total"]
        dom = merged[(merged["prop"] >= 0.6) & (merged["total"] >= 6)].sort_values(["prop","wins"], ascending=False)
        st.dataframe(dom.head(50))
        if dom.empty:
            st.info("No strong stadium dominance found with thresholds prop>=0.6 & total>=6.")
    else:
        st.warning("Columns 'Venue'/'Winner' missing.")

# 21) Average number of matches per city
with st.expander("📊 What is the average number of matches played per city?"):
    if col("City"):
        city_counts = df["City"].value_counts()
        st.write("Average matches per city:", round(city_counts.mean(),2))
        st.write("Std dev:", round(city_counts.std(),2))
        st.dataframe(city_counts.describe())
    else:
        st.warning("Column 'City' missing.")

# 22) Which teams appeared in the most matches?
with st.expander("🔎 Which teams appeared in the most matches?"):
    if col("Team1") and col("Team2"):
        appearances = pd.concat([df["Team1"], df["Team2"]]).value_counts()
        st.dataframe(appearances.head(30))
    else:
        st.warning("Columns 'Team1'/'Team2' missing.")

# 23) Which team won the most matches after losing the toss?
with st.expander("🥇 Which team won the most matches after losing the toss?"):
    if col("Toss_Winner") and col("Winner"):
        lost_toss_but_won = df[df["Toss_Winner"] != df["Winner"]]["Winner"].value_counts()
        st.dataframe(lost_toss_but_won.head(30))
    else:
        st.warning("Columns 'Toss_Winner'/'Winner' missing.")

# 24) Are there cities or venues where toss winner always won?
with st.expander("🔒 Are there cities or venues where the toss winner always won the match?"):
    if col("City") and col("Toss_Winner") and col("Winner"):
        city_all = df.groupby("City").apply(lambda x: (x["Toss_Winner"] == x["Winner"]).all()).reset_index(name="always")
        always_city = city_all[city_all["always"]==True]
        if not always_city.empty:
            st.write(always_city)
        else:
            st.info("No city where toss winner always won (in this dataset).")
    else:
        st.warning("Columns for city-level check missing.")
    if col("Venue") and col("Toss_Winner") and col("Winner"):
        venue_all = df.groupby("Venue").apply(lambda x: (x["Toss_Winner"] == x["Winner"]).all()).reset_index(name="always")
        always_venue = venue_all[venue_all["always"]==True]
        if not always_venue.empty:
            st.write(always_venue)
        else:
            st.info("No venue where toss winner always won (in this dataset).")
    else:
        st.warning("Columns for venue-level check missing.")

# 25) % matches where toss-winner chose bat and won
with st.expander("⚖️ What percentage of matches were won by the team that chose to bat?"):
    if col("Toss_Decision") and col("Toss_Winner") and col("Winner"):
        chosen_bat_and_won = df[(df["Toss_Decision"].str.lower()=="bat") & (df["Toss_Winner"] == df["Winner"])].shape[0]
        chosen_bat_total = df[df["Toss_Decision"].str.lower()=="bat"].shape[0]
        pct_bat = chosen_bat_and_won / chosen_bat_total * 100 if chosen_bat_total>0 else np.nan
        st.metric("Pct toss-winner chose bat and won", f"{pct_bat:.2f}%" if not np.isnan(pct_bat) else "N/A")
    else:
        st.warning("Required columns missing.")

# 26) % matches where toss-winner chose field and won
with st.expander("⚖️ What percentage of matches were won by the team that chose to field?"):
    if col("Toss_Decision") and col("Toss_Winner") and col("Winner"):
        chosen_field_and_won = df[(df["Toss_Decision"].str.lower()=="field") & (df["Toss_Winner"] == df["Winner"])].shape[0]
        chosen_field_total = df[df["Toss_Decision"].str.lower()=="field"].shape[0]
        pct_field = chosen_field_and_won / chosen_field_total * 100 if chosen_field_total>0 else np.nan
        st.metric("Pct toss-winner chose field and won", f"{pct_field:.2f}%" if not np.isnan(pct_field) else "N/A")
    else:
        st.warning("Required columns missing.")

# 27) Most balanced win distribution among teams in a city
with st.expander("⚖️ Which city has the most balanced win distribution among teams?"):
    if col("City") and col("Winner"):
        city_team_counts = df.groupby(["City","Winner"]).size().reset_index(name="wins")
        balanced = []
        for city, g in city_team_counts.groupby("City"):
            counts = g["wins"].values
            if counts.sum() >= 10:
                rel_std = counts.std() / counts.mean() if counts.mean()>0 else np.nan
                balanced.append((city, int(counts.sum()), rel_std))
        bal_df = pd.DataFrame(balanced, columns=["city","total_matches","rel_std"]).dropna().sort_values("rel_std")
        st.dataframe(bal_df.head(20))
    else:
        st.warning("Columns 'City'/'Winner' missing.")

# 28) Cities where one team dominated completely
with st.expander("🔔 Are there any cities where one team dominated completely?"):
    if col("City") and col("Winner"):
        city_tot = df.groupby("City").size().reset_index(name="total")
        city_team = df.groupby(["City","Winner"]).size().reset_index(name="wins")
        merged = city_team.merge(city_tot, on="City")
        merged["prop"] = merged["wins"] / merged["total"]
        dominates = merged[(merged["prop"] >= 0.75) & (merged["total"] >= 8)].sort_values("prop", ascending=False)
        st.dataframe(dominates.head(50))
        if dominates.empty:
            st.info("No city meets dominance threshold (>=75% wins & >=8 matches).")
    else:
        st.warning("Columns missing.")

# 29) Overall toss-winning trends for top-performing teams
with st.expander("📈 What are the overall toss-winning trends for top-performing teams?"):
    if col("Winner") and col("Toss_Winner"):
        top_teams = df["Winner"].value_counts().head(10).index
        toss_trends = df[df["Toss_Winner"].isin(top_teams)]["Toss_Winner"].value_counts()
        st.write("Top teams by wins (top 10):")
        st.write(df["Winner"].value_counts().head(10))
        st.write("Toss wins among those teams:")
        st.dataframe(toss_trends)
    else:
        st.warning("Columns missing.")

# 30) Ideal toss decision for each city
with st.expander("🧠 Based on current data, what would be the ideal toss decision for a team playing in each city?"):
    if col("City") and col("Toss_Decision") and col("Toss_Winner") and col("Winner"):
        t = df.dropna(subset=["City","Toss_Decision","Toss_Winner","Winner"]).copy()
        t["decision_lc"] = t["Toss_Decision"].str.lower().str.strip()
        t["toss_winner_won"] = (t["Toss_Winner"] == t["Winner"]).astype(int)
        stats = t.groupby(["City","decision_lc"])["toss_winner_won"].agg(["mean","count"]).reset_index()
        pivot = stats.pivot(index="City", columns="decision_lc", values="mean").fillna(0)
        counts = stats.pivot(index="City", columns="decision_lc", values="count").fillna(0)
        rows = []
        for city in pivot.index:
            row = pivot.loc[city]
            cnt = counts.loc[city]
            # prefer decision with >=3 samples
            best = None
            best_rate = -1
            for dec in pivot.columns:
                if cnt.get(dec,0) >= 3 and row.get(dec,0) > best_rate:
                    best_rate = row.get(dec,0)
                    best = dec
            if best is None:
                best = row.idxmax()
                best_rate = row.max()
            rows.append((city, best, float(best_rate),
                         int(cnt.get("bat",0) if "bat" in cnt else 0),
                         int(cnt.get("field",0) if "field" in cnt else 0)))
        ideal_df = pd.DataFrame(rows, columns=["City","ideal_decision","win_rate","bat_n","field_n"]).sort_values("win_rate", ascending=False)
        st.dataframe(ideal_df.head(200))
    else:
        st.warning("Required columns missing for city-level ideal decision.")

st.markdown("---")
st.caption("App uses exact column names provided. If a column is missing, the related analysis is skipped with a warning.")

