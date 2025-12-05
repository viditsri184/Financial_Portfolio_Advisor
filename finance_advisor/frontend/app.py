# frontend/app.py

import streamlit as st

# MUST be the first Streamlit command:
st.set_page_config(
    page_title="AI Financial Advisor",
    page_icon="💹",
    layout="wide"
)
# Load Custom Styles
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load CSS AFTER set_page_config but BEFORE any UI layout
try:
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        @keyframes fadeInPage {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .main {
            animation: fadeInPage 0.6s ease-out;
        }
        </style>
        """, unsafe_allow_html=True)
except:
    pass

from utils.api_client import APIClient
from utils.session_handler import init_session
from components.chat_box import chat_interface
from components.risk_form import risk_profile_form
from components.portfolio_charts import show_portfolio_chart
from components.simulation_charts import show_simulation_results
from streamlit_lottie import st_lottie
import json
from utils.lottie_loaders import render_lottie

def load_lottie(path):
    with open(path) as f:
        return json.load(f)
#st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
#render_lottie("assets/animations/portfolio_animation.json", height=220, key="portfolio_anim")
#st.markdown("</div>", unsafe_allow_html=True)



# -------------------------------------------------------------
# Initialize Session
# -------------------------------------------------------------
session_id = init_session()
api = APIClient()

# -------------------------------------------------------------
# Sidebar Navigation
# -------------------------------------------------------------
st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Navigate",
    ["Chat Advisor", "Risk Profiling", "Portfolio", "Simulation", "Download Report"]
)

# -------------------------------------------------------------
# PAGE LOGIC
# -------------------------------------------------------------
if page == "Chat Advisor":
    st.title("💬 AI Financial Advisor")
    chat_interface(api, session_id)

elif page == "Risk Profiling":
    
    from utils.lottie_loaders import render_lottie
    st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
    render_lottie("assets/animations/risk_profile.json", height=180, key="risk_anim_header")
    st.markdown("</div>", unsafe_allow_html=True)
    st.title("🧭 Risk Assessment")
    risk_profile_form(api, session_id)

elif page == "Portfolio":
    from utils.lottie_loaders import render_lottie
    render_lottie("assets/animations/portfolio_animation.json", height=220, key="portfolio_anim")

    st.title("📊 Recommended Portfolio")

    result = api.fetch_portfolio(session_id)
    if result:
        allocation = result["allocation"]
        explanation = result["explanation"]

        show_portfolio_chart(allocation)
        st.subheader("Explanation")
        st.write(explanation)
    else:
        st.warning("Complete your Risk Profiling first.")

elif page == "Simulation":
    from utils.lottie_loaders import render_lottie
    render_lottie("assets/animations/simulation_graph.json", height=220, key="simulation_anim")

    st.title("📈 Monte Carlo Simulation")
    output = api.run_simulation(session_id)
    if output:
        show_simulation_results(output)
    else:
        st.warning("Please complete Portfolio first.")

elif page == "Download Report":
    st.title("📄 Download Your Financial Plan")

    pdf_bytes = api.download_report(session_id)
    if pdf_bytes:
        st.download_button(
            label="⬇️ Download Financial Plan PDF",
            data=pdf_bytes,
            file_name="financial_plan.pdf",
            mime="application/pdf"
        )
    else:
        st.warning("Generate your portfolio & simulation first.")
