import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="Farmacinha", layout="centered")

# Cores da Referência (Dashboard Profissional)
PALETTE = {
    "fundo": "#F8F9FA",
    "card": "#FFFFFF",
    "texto_preto": "#121212",
    "texto_cinza": "#6C757D",
    "borda": "#E9ECEF"
}

MOTIVOS = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# CSS Blindado (Usando chaves duplas para não conflitar com f-strings)
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {PALETTE['fundo']};
    }}
    
    /* Layout da Linha estilo Dashboard */
    .remedio-row {{
        background-color: {PALETTE['card']};
        padding: 14px 16px;
        border-bottom: 1px solid {PALETTE['borda']};
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .left-content {{
        display: flex;
        align-items: center;
    }}

    /* Ícone circular: aparece no mobile, some no desktop */
    .mobile-icon {{
        width: 38px;
        height: 38px;
        background-color: #F1F3F5;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-right: 12px;
    }}

    .nome-texto {{
        color: {PALETTE['texto_preto']};
        font-weight: 600;
        font-size: 0.95rem;
        margin: 0;
    }}

    .cat-texto {{
        color: {PALETTE['texto_cinza']};
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }}

    .right-content {{
        text-align: right;
    }}

    .qtd-texto {{
        color: {PALETTE['texto_preto']};
        font-weight: 700;
        font-size: 0.95rem;
    }}

    .data-texto {{
        color: {PALETTE['texto_cinza']};
        font-size: 0.8rem;
    }}

    /* Regra para esconder ícone no Desktop */
    @media (min-width: 768px) {{
        .mobile-icon {{ display: none !important; }}
    }}

    /* Estilo das Abas (Clean) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{
        color: {PALETTE['texto_cinza']};
    }}
    .stTabs [aria-selected="true"] {{
        color: {PALETTE['texto_preto']} !important;
        font-weight: 700 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE DADOS (GITHUB) ---
try:
    token = st.secrets["GITHUB_TOKEN"]
    repo_name = st.secrets["REPO_NAME"]
    file_path = "dados_remedios.csv"

    def load_data():
        g = Github(token)
        repo = g.get_
