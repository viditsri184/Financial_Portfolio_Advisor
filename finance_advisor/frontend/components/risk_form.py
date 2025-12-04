# frontend/components/risk_form.py

import streamlit as st


def risk_profile_form(api, session_id: str):
    """
    UI for user risk profiling.
    Uses backend /risk_profile endpoint.
    """

    st.write("Please fill in the details below to determine your risk profile.")

    with st.form("risk_profile_form"):

        # -----------------------------
        # Basic User Information
        # -----------------------------
        age = st.number_input("Age", min_value=18, max_value=90, value=30)

        income_stability = st.selectbox(
            "Income Stability",
            ["high", "medium", "low"],
            index=0
        )

        liquidity_needs = st.selectbox(
            "Liquidity Needs (How often do you need easy access to cash?)",
            ["low", "medium", "high"],
            index=1
        )

        investment_knowledge = st.selectbox(
            "Investment Knowledge",
            ["high", "medium", "low"],
            index=1
        )

        st.markdown("### Questionnaire")

        # -----------------------------
        # Risk MCQ Questions (1-5 score)
        # -----------------------------
        q1 = st.slider(
            "Q1: How comfortable are you with short-term losses?",
            1, 5, 3
        )
        q2 = st.slider(
            "Q2: How long can you stay invested without needing the money?",
            1, 5, 3
        )
        q3 = st.slider(
            "Q3: How familiar are you with equity markets?",
            1, 5, 3
        )
        q4 = st.slider(
            "Q4: How much volatility can you tolerate?",
            1, 5, 3
        )

        submitted = st.form_submit_button("Calculate Risk Profile")

    # -----------------------------------------------------------------
    # On Submit → Call Backend
    # -----------------------------------------------------------------
    if submitted:
        with st.spinner("Evaluating your risk profile..."):

            payload = {
                "session_id": session_id,
                "age": age,
                "income_stability": income_stability,
                "liquidity_needs": liquidity_needs,
                "investment_knowledge": investment_knowledge,
                "answers": {
                    "q1": q1,
                    "q2": q2,
                    "q3": q3,
                    "q4": q4
                }
            }

            result = api.send_risk_profile(payload)

        if result:
            st.success(f"Your Risk Category: **{result['risk_category'].title()}**")
            st.write(result["explanation"])

            # Save in session state
            st.session_state["risk_profile"] = result
