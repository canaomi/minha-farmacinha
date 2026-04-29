import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- CONFIGURAÇÕES VISUAIS (Dashboard Style) ---
st.set_page_config(page_title="Farmacinha", layout="centered")

# Paleta baseada na referência: Contraste alto e neutralidade profissional
COLOR_PALETTE = {
    "fundo_app": "#F8F9FA",      # Cinza gelo bem claro
    "branco_card": "#FFFFFF",    # Pure White para os itens
    "texto_principal": "#121212",# Preto profundo para nomes
    "texto_apoio": "#6C757D",    # Cinza médio para categorias e datas
    "borda": "#E9ECEF",          # Divisores sutis
    "azul_acao": "#0056B3"       # Azul sóbrio para botões
}

MOTIVOS_EMOJIS = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# CSS para UI de Listagem Profissional
st.markdown(f"""
    <style>
    /* Reset e Fundo */
    .stApp {{
        background-color: {COLOR_PALETTE['fundo_app']};
    }}
    
    /* Estrutura da Linha (Estilo Explore Tokens) */
    .remedio-row {{
        background-color: {COLOR_PALETTE['branco_card']};
        padding: 14px 16px;
        border-bottom: 1px solid {COLOR_PALETTE['borda']};
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: background 0.2s;
    }}
    
    .remedio-row:hover {{
        background-color: #FAFAFA;
    }}

    /* Container de Info (Lado Esquerdo) */
    .info-container {{
        display: flex;
        align-items: center;
    }}

    /* Ícone Circular (Apenas Mobile) */
    .icon-mobile {{
        width: 36px;
        height: 36px;
        background-color: #F1F3F5;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        margin-right: 12px;
    }}

    .texto-nome {{
        color: {COLOR_PALETTE['texto_principal']};
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 2px;
    }}

    .texto-categoria {{
        color: {COLOR_PALETTE['texto_apoio']};
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* Valores (Lado Direito) */
    .valor-container {{
        text-align: right;
    }}

    .texto-qtd {{
        color: {COLOR_PALETTE['texto_principal']};
        font-weight: 700;
        font-size: 0.95rem;
    }}

    .texto-data {{
        color: {COLOR_PALETTE['texto_apoio']};
        font-size: 0.8rem;
    }}

    /* Media Query: Esconde o círculo no Desktop, mostra no Mobile */
    @media (min-width: 769px) {{
        .icon-mobile {{ display: none; }}
    }}

    /* Estilização de Inputs e Abas Clean */
    .stTabs [data-baseweb="tab-list"] {{ gap: 20px; }}
    .stTabs [data-baseweb="tab"] {{
        padding: 10px 0px;
        color: {COLOR_PALETTE['texto_apoio']};
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLOR_PALETTE['texto_principal']} !important;
        font-weight: 700 !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- LOGICA GITHUB (Plano B) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "dados_remedios.csv"

def load_data():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file_content = repo.get_contents(FILE_PATH)
        return pd.read_csv(io.StringIO(file_content.decoded_content.decode())), file_content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    if sha:
        repo.update_file(FILE_PATH, "Stock update", csv_buffer.getvalue(), sha)
    else:
        repo.create_file(FILE_PATH, "Initial stock", csv_buffer.getvalue())

# --- INTERFACE ---
st.title("Farmacinha")

df, sha = load_data()

# Botão de Cadastro (UI limpa)
if st.button("＋ Incluir medicamento", use_container_width=True):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("add_form", clear_on_submit=True):
        nome = st.text_input("Nome do medicamento")
        c1, c2 = st.columns(2)
        validade = c1.date_input("Vencimento")
        quantidade = c2.number_input("Qtd", min_value=1)
        motivo = st.selectbox("Categoria", list(MOTIVOS_EMOJIS.keys()))
        if st.form_submit_button("Salvar no inventário"):
            new_data = pd.DataFrame([{"nome": nome, "validade": str(validade), "quantidade": int(quantidade), "motivo": motivo}])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.rerun()

# Busca e Categorias (Sem emojis, texto puro e direto)
busca = st.text_input("Buscar", placeholder="Filtrar por nome...")
tabs = st.tabs(list(MOTIVOS_EMOJIS.keys()))

for idx, motivo_nome in enumerate(MOTIVOS_EMOJIS
