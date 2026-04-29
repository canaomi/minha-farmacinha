import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES VISUAIS E PALETA PINK ---
st.set_page_config(page_title="Farmacinha", layout="centered")

# Paleta Rosa Profissional
PINK_PALETTE = {
    "fundo_tela": "#FDE2E4",      # Rosa Pastel Suave (Fundo)
    "botao_cor": "#FB6F92",       # Rosa Vibrante (Botões)
    "card_branco": "#FFFFFF",     # Branco (Para os itens saltarem)
    "texto_preto": "#000000",     # Preto (Contraste máximo)
    "texto_cinza": "#4A4A4A",     # Cinza escuro (Apoio)
    "borda": "#FFC2D1"            # Rosa médio (Divisores)
}

MOTIVOS = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# CSS Responsivo e Tematizado
st.markdown(f"""
    <style>
    /* Fundo do App */
    .stApp {{
        background-color: {PINK_PALETTE['fundo_tela']};
        color: {PINK_PALETTE['texto_preto']};
    }}
    
    /* Títulos e Labels */
    h1, h2, label, .stMarkdown p {{
        color: {PINK_PALETTE['texto_preto']} !important;
    }}

    /* Estilo das Linhas (Cards) */
    .remedio-row {{
        background-color: {PINK_PALETTE['card_branco']};
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {PINK_PALETTE['borda']};
    }}
    
    .left-content {{ display: flex; align-items: center; }}

    /* Ícone Mobile (Emoji no círculo) */
    .mobile-icon {{
        width: 42px; height: 42px;
        background-color: {PINK_PALETTE['fundo_tela']};
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; margin-right: 12px;
    }}

    .nome-texto {{ font-weight: 700; font-size: 1rem; margin: 0; }}
    .cat-texto {{ color: {PINK_PALETTE['texto_cinza']}; font-size: 0.75rem; text-transform: uppercase; }}
    .right-content {{ text-align: right; }}
    .qtd-texto {{ font-weight: 800; font-size: 1rem; }}
    .data-texto {{ color: {PINK_PALETTE['texto_cinza']}; font-size: 0.8rem; }}

    /* Responsividade: Esconde o ícone no Desktop */
    @media (min-width: 768px) {{
        .mobile-icon {{
