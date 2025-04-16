# Päivitetty versio – pakotettu päivitys Streamlitille
import itertools
import numpy as np
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Järjestelmävedonlyönnin kassanhallintatyökalu")

system_type = st.selectbox("Valitse järjestelmätyyppi:", ["2/3", "3/4"])
starting_bankroll = st.number_input("Alkukassa (€)", value=1000, step=100)
rounds = st.number_input("Kierrosten määrä", value=50, step=10)
hit_prob = st.slider("Osumaprosentti per kohde (%)", min_value=0, max_value=100, value=70) / 100
base_stake_per_bet = st.number_input("Peruspanos per rivi (€)", value=1.0, step=0.5)
progression_factor = st.slider("Panoksen muutosnopeus (% per muutos)", min_value=0, max_value=100, value=10) / 100
stake_adjustment_method = st.selectbox("Panoksen säätö suhteessa:", ["100 € muutos", "Prosentuaalinen muutos"])
n_simulations = st.slider("Simulaatioiden määrä", min_value=10, max_value=1000, value=100, step=10)

if system_type == "2/3":
    odds = [st.number_input(f"Kerroin kohteelle {i+1}", value=1.73, step=0.01) for i in range(3)]
elif system_type == "3/4":
    odds = [st.number_input(f"Kerroin kohteelle {i+1}", value=1.82, step=0.01) for i in range(4)]

def simulate_bankroll(starting_bankroll, system_type, odds, hit_probability, rounds, base_stake_per_bet, progression_factor, stake_adjustment_method):
    bankroll = starting_bankroll
    bankroll_progress = [bankroll]

    if system_type == "2/3":
        combos = 3
        win_multiplier = lambda hits, stake: (
            np.prod([o for o in odds if o != 0][:2]) * stake if hits == 2 else
            sum(np.prod(c) * stake for c in itertools.combinations(odds, 2)) if hits == 3 else 0
        )
    elif system_type == "3/4":
        combos = 4
        win_multiplier = lambda hits, stake: (
            np.prod([o for o in odds if o != 0][:3]) * stake if hits == 3 else
            sum(np.prod(c) * stake for c in itertools.combinations(odds, 3)) if hits == 4 else 0
        )

    for _ in range(rounds):
        if stake_adjustment_method == "100 € muutos":
            stake_per_bet = base_stake_per_bet * (1 + ((bankroll - starting_bankroll) / 100) * progression_factor)
        else:  # Prosentuaalinen muutos
            stake_per_bet = base_stake_per_bet * (bankroll / starting_bankroll) ** progression_factor

        stake_total = stake_per_bet * combos
        hits = np.sum(np.random.rand(len(odds)) < hit_probability)
        payout = win_multiplier(hits, stake_per_bet)
        bankroll += payout - stake_total
        bankroll_progress.append(bankroll)

        if bankroll <= 0:
            break

    return bankroll_progress

if st.button("Simuloi pelikassan kehitys"):
    all_simulations = []
    for _ in range(n_simulations):
        result = simulate_bankroll(starting_bankroll, system_type, odds, hit_prob, rounds, base_stake_per_bet, progression_factor, stake_adjustment_method)
        if len(result) < rounds + 1:
            result += [np.nan] * (rounds + 1 - len(result))
        all_simulations.append(result)

    df = pd.DataFrame(all_simulations)
    mean_progress = df.mean()
    min_progress = df.min()
    max_progress = df.max()

    final_values = df.iloc[:, -1].dropna()
    mean_final = final_values.mean()
    std_final = final_values.std()

    tab1, tab2 = st.tabs(["Keskiarvokäyrä", "Kaikki simulaatiot"])

    with tab1:
        st.subheader("Keskimääräinen pelikassan kehitys min-max -alueella")
        fig, ax = plt.subplots()
        ax.plot(mean_progress.index, mean_progress, label="Keskiarvo")
        ax.fill_between(mean_progress.index, min_progress, max_progress, color='lightblue', alpha=0.4, label="Min-Max alue")
        ax.set_xlabel("Kierros")
        ax.set_ylabel("Pelikassa (€)")
        ax.legend()
        st.pyplot(fig)

    with tab2:
        st.subheader("Kaikki simulaatiot (Monte Carlo -tyyli)")
        st.line_chart(df.transpose())

    st.success(f"Simulointi valmis! Lopullinen pelikassa keskimäärin: {mean_final:.2f} €")
    st.info(f"Keskihajonta lopputuloksissa: {std_final:.2f} €")
