# streamlit_app.py

import streamlit as st

# App title
st.set_page_config(page_title="My Streamlit App", layout="centered")

# Title and intro text
st.title("Welcome to My Streamlit App")
st.write("This is a simple Streamlit application. Customize it to suit your project!")

# Example input and output
name = st.text_input("Enter your name", "")
if name:
    st.success(f"Hello, {name}! 👋")

# Example chart
st.subheader("Sample Line Chart")
st.line_chart({
    'data': [1, 5, 2, 6, 2, 1]
})

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit")
