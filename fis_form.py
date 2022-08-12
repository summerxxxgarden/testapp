import streamlit as st

st.header('Кто на самом деле Жорик')

import vk_api as vk

session = vk.VkApi(token="vk1.a.ArZr8sr5xVNPBq9__me_03WaMdJCq6I-gU0TP3GR1BXil6_jFRraTzoV1iHu58vLAeRdMAKS3ifNQsSnPE37iXuoIjEQ8SXVD26izi6qoZRZG-qKtBXpjAOXFa18CNDBxMpTTSdGMG0VqCR4syzmEsxaEdZ8VLlEWGoVJyHpl9FOjnWhXFTH8VNcb20Kr5Sl")

def get_budget(account_id=1606616876):
    budget = session.method("ads.getBudget",{"account_id":account_id})
    st.write(budget)

run = st.button("Узнать!")

if run:
    st.write(':dog:')
