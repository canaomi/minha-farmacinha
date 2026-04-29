import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES VISUAIS ---
st.set_page_config(page_title="Farmacinha", layout="centered")

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

# CSS com chaves duplas para evitar erro de f-string
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {PALETTE['fundo']};
    }}
    .remedio-row {{
        background-color: {PALETTE['card']};
        padding: 14px 16px;
        border-bottom: 1px solid {PALETTE['borda']};
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .left-content {{ display: flex; align-items: center; }}
    .mobile-icon {{
        width: 38px; height: 38px;
        background-color: #F1F3F5;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; margin-right: 12px;
    }}
    .nome-texto {{ color: {PALETTE['texto_preto']}; font-weight: 600; font-size: 0.95rem; margin: 0; }}
    .cat-texto {{ color: {PALETTE['texto_cinza']}; font-size: 0.75rem; text-transform: uppercase; }}
    .right-content {{ text-align: right; }}
    .qtd-texto {{ color: {PALETTE['texto_preto']}; font-weight: 700; }}
    .data-texto {{ color: {PALETTE['texto_cinza']}; font-size: 0.8rem; }}
    
    @media (min-width: 768px) {{
        .mobile-icon {{ display: none !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE DADOS (GITHUB) ---
# Centralizei o acesso ao GitHub para ser mais robusto
def get_github_repo():
    g = Github(st.secrets["GITHUB_TOKEN"])
    return g.get_repo(st.secrets["REPO_NAME"])

def load_data():
    repo = get_github_repo()
    try:
        content = repo.get_contents("dados_remedios.csv")
        df = pd.read_csv(io.StringIO(content.decoded_content.decode()))
        return df, content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha):
    repo = get_github_repo()
    csv_data = df.to_csv(index=False)
    if sha:
        repo.update_file("dados_remedios.csv", "Update", csv_data, sha)
    else:
        repo.create_file("dados_remedios.csv", "Initial", csv_data)

# --- 3. INTERFACE ---
st.title("Farmacinha")

# Carregar dados uma vez no início
df, sha = load_data()

if st.button("＋ Incluir medicamento", use_container_width=True):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("form_add", clear_on_submit=True):
        nome = st.text_input("Nome")
        c1, c2 = st.columns(2)
        val = c1.date_input("Vencimento")
        qtd = c2.number_input("Qtd", min_value=1)
        cat = st.selectbox("Categoria", list(MOTIVOS.keys()))
        if st.form_submit_button("Salvar"):
            new_item = pd.DataFrame([{"nome": nome, "validade": str(val), "quantidade": int(qtd), "motivo": cat}])
            df = pd.concat([df, new_item], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.rerun()

st.divider()
busca = st.text_input("Buscar", placeholder="Filtrar por nome...")
tabs = st.tabs(list(MOTIVOS.keys()))

for idx, cat_name in enumerate(MOTIVOS.keys()):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca:
            subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info("Nenhum item encontrado.")
        else:
            for i, r in subset.iterrows():
                emoji = MOTIVOS.get(r['motivo'], "💊")
                try:
                    dt_str = datetime.strptime(r['validade'], '%Y-%m-%d').strftime('%d/%b/%y')
                except:
                    dt_str = r['validade']

                st.markdown(f"""
                    <div class="remedio-row">
                        <div class="left-content">
                            <div class="mobile-icon">{emoji}</div>
                            <div>
                                <p class="nome-texto">{r['nome']}</p>
                                <span class="cat-texto">{r['motivo']}</span>
                            </div>
                        </div>
                        <div class="right-content">
                            <div class="qtd-texto">{r['quantidade']} un</div>
                            <div class="data-texto">{dt_str}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Remover {r['nome']}", key=f"del_{i}", use_container_width=True):
                    df = df.drop(i)
                    save_data(df, sha)
                    st.rerun()

# --- FIM DO ARQUIVO ---
