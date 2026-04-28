import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="Minha Farmacinha", layout="centered")

# CSS para cards que funcionam no Dark e Light mode
st.markdown("""
    <style>
    .remedio-card {
        background-color: rgba(150, 150, 150, 0.1);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(150, 150, 150, 0.2);
        margin-bottom: 15px;
    }
    .nome-remedio {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .info-remedio {
        font-size: 0.9rem;
        opacity: 0.8;
    }
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES GITHUB ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "dados_remedios.csv"

MOTIVOS_ICONES = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# --- FUNÇÕES DE DADOS ---
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
        repo.update_file(FILE_PATH, "update data", csv_buffer.getvalue(), sha)
    else:
        repo.create_file(FILE_PATH, "initial create", csv_buffer.getvalue())

# --- INTERFACE ---
st.title("💊 Minha Farmacinha")

df, sha = load_data()

# Botão de inclusão
if st.button("➕ Incluir novo remédio", use_container_width=True, type="primary"):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("add_form", clear_on_submit=True):
        nome = st.text_input("Nome do remédio")
        col1, col2 = st.columns(2)
        validade = col1.date_input("Vencimento")
        quantidade = col2.number_input("Qtd", min_value=1)
        motivo = st.selectbox("Categoria", list(MOTIVOS_ICONES.keys()))
        
        if st.form_submit_button("Salvar na Farmacinha", use_container_width=True):
            new_data = pd.DataFrame([{"nome": nome, "validade": str(validade), "quantidade": quantidade, "motivo": motivo}])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.rerun()

st.divider()

# Listagem de Cards
if df.empty:
    st.info("Sua farmacinha está vazia. Comece cadastrando um remédio!")
else:
    for i, r in df.iterrows():
        icone = MOTIVOS_ICONES.get(r['motivo'], "💊")
        st.markdown(f"""
            <div class="remedio-card">
                <div class="nome-remedio">{icone} {r['nome']}</div>
                <div class="info-remedio">
                    📅 Vence em: {r['validade']} <br>
                    📦 Quantidade: {r['quantidade']} unidades
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Botão de remover fora do HTML para funcionar o clique
        if st.button(f"Remover {r['nome']}", key=f"del_{i}", use_container_width=True):
            df = df.drop(i)
            save_data(df, sha)
            st.rerun()
