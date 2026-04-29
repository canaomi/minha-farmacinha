import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES VISUAIS E PALETA ---
st.set_page_config(page_title="Farmacinha de Bolso", layout="centered")

PINK_PALETTE = {
    "fundo": "#FDE2E4",      # Rosa Pastel
    "botao": "#FB6F92",      # Rosa Vibrante
    "card": "#FFFFFF",       # Branco
    "texto": "#000000",      # Preto
    "apoio": "#4A4A4A",      # Cinza
    "borda": "#FFC2D1"       # Rosa Médio
}

MOTIVOS_ICONES = {
    "Gases": "🎈", 
    "Diarréia": "🚽", 
    "Dor de cabeça": "🤕", 
    "Gripe": "🤧", 
    "Antiinflamatório": "🩹", 
    "Dor de estômago": "🤢", 
    "Outros": "➕"
}

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {PINK_PALETTE['fundo']};
        color: {PINK_PALETTE['texto']};
    }}
    
    h1, h2, label, .stMarkdown p {{
        color: {PINK_PALETTE['texto']} !important;
    }}

    .remedio-row {{
        background-color: {PINK_PALETTE['card']};
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {PINK_PALETTE['borda']};
    }}
    
    .left-content {{ display: flex; align-items: center; }}

    .mobile-icon {{
        width: 42px; height: 42px;
        background-color: {PINK_PALETTE['fundo']};
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; margin-right: 12px;
    }}

    .nome-texto {{ font-weight: 700; font-size: 1rem; margin: 0; }}
    .cat-texto {{ color: {PINK_PALETTE['apoio']}; font-size: 0.75rem; text-transform: uppercase; }}
    .right-content {{ text-align: right; }}
    .qtd-texto {{ font-weight: 800; font-size: 1rem; }}
    .data-texto {{ color: {PINK_PALETTE['apoio']}; font-size: 0.8rem; }}
    
    .status-badge {{
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 700;
        display: inline-block;
        margin-top: 4px;
    }}

    @media (min-width: 768px) {{
        .mobile-icon {{ display: none !important; }}
    }}

    div.stButton > button {{
        background-color: {PINK_PALETTE['botao']} !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }}

    .stTabs [aria-selected="true"] {{
        color: {PINK_PALETTE['texto']} !important;
        border-bottom: 3px solid {PINK_PALETTE['botao']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE DADOS ---
def get_repo():
    return Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["REPO_NAME"])

def load_data():
    repo = get_repo()
    try:
        content = repo.get_contents("dados_remedios.csv")
        df = pd.read_csv(io.StringIO(content.decoded_content.decode()))
        return df, content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha):
    repo = get_repo()
    csv_data = df.to_csv(index=False)
    if sha:
        repo.update_file("dados_remedios.csv", "Update", csv_data, sha)
    else:
        repo.create_file("dados_remedios.csv", "Initial", csv_data)

def get_status(validade_str):
    try:
        val = datetime.strptime(validade_str, '%Y-%m-%d').date()
        dias = (val - date.today()).days
        if dias < 0: return "Vencido 🚨", "#FEE2E2", "#991B1B"
        if dias <= 30: return "Atenção ⚠️", "#FEF3C7", "#92400E"
        return "Em dia", "#DCFCE7", "#166534"
    except:
        return "Sem data", "#F3F4F6", "#374151"

# --- 3. INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

if st.button("➕ Incluir remédio", use_container_width=True):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("form_remedio", clear_on_submit=True):
        nome = st.text_input("Nome do medicamento")
        c1, c2 = st.columns(2)
        validade = c1.date_input("Vencimento")
        quantidade = c2.number_input("Quantidade", min_value=1)
        motivo = st.selectbox("Motivo (Categoria)", list(MOTIVOS_ICONES.keys()))
        if st.form_submit_button("Salvar remédio"):
            new_item = pd.DataFrame([{"nome": nome, "validade": str(validade), "quantidade": int(quantidade), "motivo": motivo}])
            df = pd.concat([df, new_item], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.rerun()

st.divider()
busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...")
tabs = st.tabs(list(MOTIVOS_ICONES.keys()))

for idx, cat_name in enumerate(MOTIVOS_ICONES.keys()):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca:
            subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info(f"Nenhum remédio em {cat_name}.")
        else:
            for i, r in subset.iterrows():
                emoji = MOTIVOS_ICONES.get(r['motivo'], "💊")
                status_txt, bg, txt = get_status(r['validade'])
                val_br = datetime.strptime(r['validade'], '%Y-%m-%d').strftime('%d/%m/%Y')

                st.markdown(f"""
                    <div class="remedio-row">
                        <div class="left-content">
                            <div class="mobile-icon">{emoji}</div>
                            <div>
                                <p class="nome-texto">{r['nome']}</p>
                                <span class="cat-texto">{r['motivo']}</span><br>
                                <span class="status-badge" style="background-color: {bg}; color: {txt};">{status_txt}</span>
                            </div>
                        </div>
                        <div class="right-content">
                            <div class="qtd-texto">{r['quantidade']} un</div>
                            <div class="data-texto">{val_br}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"🗑️ Excluir {r['nome']}", key=f"del_{i}", use_container_width=True):
                    df = df.drop(i)
                    save_data(df, sha)
                    st.rerun()
