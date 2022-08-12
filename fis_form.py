import streamlit as st

st.header('Кто на самом деле Жорик')
run = st.button("Узнать!")

if run:
    st.write(':dog:')
