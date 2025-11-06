import streamlit as st

# placeholder for streamlit frontend
st.title("Realtime Chat Server")
st.write("Frontend interface coming soon...")

# basic page structure
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.subheader("Authentication")
    st.write("Login and registration functionality will be implemented in task 6.")
else:
    st.subheader("Chat Interface")
    st.write("Chat functionality will be implemented in task 6.")