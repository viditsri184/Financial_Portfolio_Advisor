import streamlit as st
import plotly.graph_objects as go


def show_simulation_results(result):

    expected = result["expected_value"]
    best = result["best_case"]
    worst = result["worst_case"]
    prob = result["probability_of_goal_achievement"]
    values = result["final_values"]

    st.subheader("Simulation Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Expected Value", f"₹{expected:,.0f}")
    col2.metric("Best Case (95%)", f"₹{best:,.0f}")
    col3.metric("Worst Case (5%)", f"₹{worst:,.0f}")

    st.markdown(f"### 🎯 Goal Achievement Probability: **{prob * 100:.2f}%**")

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=values, nbinsx=50, marker_color="#0070C9"))
    fig.update_layout(
        title="Distribution of Final Portfolio Values",
        xaxis_title="Portfolio Value (₹)",
        yaxis_title="Frequency",
        template="plotly_white",
        height=450
    )

    st.plotly_chart(fig, use_container_width=True)
