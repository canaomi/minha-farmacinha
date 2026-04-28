import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Minha Farmacinha", layout="centered")

# Pega as chaves dos Secrets
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "dados_remedios.csv"

MOTIVOS_ICONES = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# --- FUNÇÕES GITHUB ---
def load_data():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file_content = repo.get_contents(FILE_PATH)
        return pd.read_csv(io.StringIO(file_content.decoded_content.decode())), file_content.sha
    except:
        df_init = pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo", "criado_em"])
        return df_init, None

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

if st.button("➕ Incluir remédio", use_container_width=True, type="primary"):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("add_form"):
        nome = st.text_input("Nome")
        validade = st.date_input("Vencimento")
        quantidade = st.number_input("Qtd", min_value=1)
        motivo = st.selectbox("Motivo", list(MOTIVOS_ICONES.keys()))
        if st.form_submit_button("Salvar"):
            new_data = pd.DataFrame([{"nome": nome, "validade": validade.isoformat(), "quantidade": quantidade, "motivo": motivo, "criado_em": datetime.now().isoformat()}])
            updated_df = pd.concat([df, new_data], ignore_index=True)
            save_data(updated_df, sha)
            st.session_state.show_form = False
            st.rerun()

# Listagem (Layout de Cards igual ao anterior)
st.divider()
for i, r in df.iterrows():
    with st.container():
        st.markdown(f"""
            <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                <strong>{MOTIVOS_ICONES.get(r['motivo'], '💊')} {r['nome']}</strong><br>
                <small>Vence em: {r['validade']} | Qtd: {r['quantidade']}</small>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Remover", key=f"del_{i}"):
            updated_df = df.drop(i)
            save_data(updated_df, sha)
            st.rerun()
