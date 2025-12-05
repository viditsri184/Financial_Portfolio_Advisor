# frontend/components/chat_box.py

import streamlit as st
from typing import List, Dict
from utils.lottie_loaders import render_lottie
st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
render_lottie("assets/animations/advisor_bot.json", height=180, key="chatbot_anim_header")
st.markdown("</div>", unsafe_allow_html=True)


def chat_interface(api, session_id: str):
    """
    Streamlit chat UI component.
    Handles:
      - Displaying message history
      - User input message box
      - Sending messages to backend
      - Showing AI responses
    """

    # -------------------------------------------------------------
    # Initialize chat history in session state
    # -------------------------------------------------------------
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []   # List of dicts: {"role": "user/assistant", "content": "..."}

    from utils.lottie_loaders import render_lottie

    # Place hero animation above chat UI once per page
    render_lottie("assets/animations/advisor_bot.json", height=180, key="chatbot_anim_header")

    st.subheader("Your Conversation")

    # -------------------------------------------------------------
    # Display chat messages
    # -------------------------------------------------------------
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-bubble'>{msg['content']}</div>", unsafe_allow_html=True)


    # -------------------------------------------------------------
    # User Input Box
    # -------------------------------------------------------------
    user_input = st.chat_input("Ask the financial advisor...")

    if user_input:
        # Add to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.write(user_input)

        # ---------------------------------------------------------
        # Send message to backend
        # ---------------------------------------------------------
        with st.spinner("Advisor is thinking..."):
            response = api.send_chat_message(session_id, user_input)

        assistant_reply = response.get("reply", "No response from advisor.")

        # Add reply to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})

        # Display assistant response
        with st.chat_message("assistant"):
            st.write(assistant_reply)

    # Optional: Clear chat button
    if st.button("Clear Conversation"):
        st.session_state.chat_history = []
        st.experimental_rerun()
