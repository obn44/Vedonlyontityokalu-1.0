import itertools
import numpy as np
import streamlit as st

st.title("Järjestelmävedonlyönnin kassanhallintatyökalu")

system_type = st.selectbox("Valitse järjestelmätyyppi:", ["2/3", "3/4"])
starting_bankroll = st.number_input("Alkukassa (€)", value=1000, step=100)
rounds = st.number_input("Kierrosten määrä", value=50, step=10)
hit_prob = st.slider("Osumaprosentti per kohde (%)", min_value=0, max_value=100, value=70) / 100
base_stake_per_bet = st.number_input("Peruspanos per rivi (€)", value=1.0, step=0.5)
progression_factor = st.slider("Panoksen muutosnopeus (% per 100 € kassanmuutos)", min_value=0, max_value=100, value=10) / 100

if system_type == "2/3":
    odds = [st.number_input(f"Kerroin kohteelle {i+1}", value=1.73, step=0.01) for i in range(3)]
elif system_type == "3/4":
    odds = [st.number_input(f"Kerroin kohteelle {i+1}", value=1.82, step=0.01) for i in range(4)]

def simulate_bankroll(starting_bankroll, system_type, odds, hit_probability, rounds, base_stake_per_bet, progression_factor):
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
        # Panos skaalataan suhteessa kassan kokoon
        stake_per_bet = base_stake_per_bet * (1 + ((bankroll - starting_bankroll) / 100) * progression_factor)
        stake_total = stake_per_bet * combos

        hits = np.sum(np.random.rand(len(odds)) < hit_probability)
        payout = win_multiplier(hits, stake_per_bet)
        bankroll += payout - stake_total
        bankroll_progress.append(bankroll)

        if bankroll <= 0:
            break

    return bankroll_progress

if st.button("Simuloi pelikassan kehitys"):
    results = simulate_bankroll(starting_bankroll, system_type, odds, hit_prob, rounds, base_stake_per_bet, progression_factor)
    st.line_chart(results)
    st.success(f"Simulointi valmis! Lopullinen pelikassa: {results[-1]:.2f} €")
