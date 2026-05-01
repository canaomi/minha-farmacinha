import streamlit as st
import pandas as pd
from github import Github
import io
import google.generativeai as genai
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES E IA ---
st.set_page_config(page_title="Farmacinha de Bolso", layout="wide")

def get_ai_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = get_ai_model()

# --- 2. PALETA ZEN (MATCH & CREAM) ---
COLORS = {
    "fundo": "#F9F7F2",       # Creme Papel (Original)
    "matcha": "#587058",      # Verde Matcha
    "areia": "#E8D5C4",       # Bege Areia
    "grafite": "#2C2C2C",     # Texto
    "branco": "#FFFFFF",
    "preto": "#000000"
}

st.markdown(f"""
    <style>
    /* Reset Global */
    .stApp {{ background-color: {COLORS['fundo']}; color: {COLORS['grafite']}; }}
    h1 {{ color: {COLORS['matcha']} !important; font-weight: 800 !important; }}

    /* 1. ABA DE CADASTRO (EXPANDER) - VOLTA PARA O CREME ORIGINAL */
    .stExpander {{
        background-color: {COLORS['fundo']} !important;
        border: 1px solid {COLORS['areia']} !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}
    .stExpander [data-testid="stExpanderSummary"] {{
        color: {COLORS['grafite']} !important;
    }}
    .stExpander [data-testid="stExpanderSummary"] svg {{
        fill: {COLORS['grafite']} !important;
    }}

    /* 2. CAMPOS DE ENTRADA (MANTÉM O VERDE MATCHA) */
    .stTextInput input, .stDateInput input, .stSelectbox [data-baseweb="select"], .stNumberInput input {{
        background-color: {COLORS['matcha']} !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
    }}

    /* Placeholder do Nome (Fonte Preta conforme pedido) */
    .stTextInput input::placeholder {{
        color: {COLORS['preto']} !important;
        opacity: 0.9;
    }}

    /* 3. BOTÕES DE CONTROLE (+/- E CALENDÁRIO) EM VERDE */
    .stNumberInput button {{
        background-color: {COLORS['matcha']} !important;
        color: white !important;
    }}
    
    /* 4. BOTÃO SALVAR (MANTÉM O VERDE) */
    form .stButton > button {{
        background-color: {COLORS['matcha']} !important;
        color: white !important;
        width: 100% !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }}

    /* Labels e Títulos em Grafite */
    label, .titulo-lista {{ color: {COLORS['grafite']} !important; font-weight: 700; }}

    /* Pills / Tabs */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['areia']} !important;
        border-radius: 50px !important;
        color: {COLORS['grafite']} !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['matcha']} !important;
        color: white !important;
    }}
    [data-testid="stIcon"] {{ display: none !important; }}

    /* Estado Vazio */
    .empty-state {{ color: {COLORS['grafite']}; opacity: 0.4; text-align: center; padding: 30px; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS ---
def load_data():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        content = repo.get_contents("dados_remedios.csv")
        return pd.read_csv(io.StringIO(content.decoded_content.decode())), content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha, msg="Remédio salvo!"):
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
    csv_data = df.to_csv(index=False)
    if sha: repo.update_file("dados_remedios.csv", "Sync", csv_data, sha)
    else: repo.create_file("dados_remedios.csv", "Init", csv_data)
    st.toast(msg)

# --- 4. INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

# Incluir remédio no topo
if st.button("➕ Incluir remédio", use_container_width=True):
    st.session_state.show_form = True

# JORNADA DE CADASTRO (Aba Creme, Conteúdo Verde)
if st.session_state.get("show_form"):
    with st.expander("📝 Novo Cadastro", expanded=True):
        with st.form("form_cadastro", clear_on_submit=True):
            nome_f = st.text_input("Nome do medicamento", placeholder="Digite o nome do seu remédio")
            
            c1, c2 = st.columns(2)
            val_f = c1.date_input("Vencimento") 
            qtd_f = c2.number_input("Quantidade", min_value=1, step=1)
            
            cat_f = st.selectbox("Motivo (Categoria)", ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"])
            
            if st.form_submit_button("Salvar remédio"):
                new_row = {"nome": nome_f, "validade": str(val_f), "quantidade": int(qtd_f), "motivo": cat_f}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df, sha, "Remédio salvo!")
                st.session_state.show_form = False
                st.rerun()

st.divider()

# Busca
busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...")

st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca: subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.markdown(f'<div class="empty-state">Nenhum remédio em {cat_name}.</div>', unsafe_allow_html=True)
        else:
            # Cabeçalho da Listagem
            h_cols = st.columns([2.5, 1.5, 1, 1.5, 1.5])
            headers = ["Medicamento", "Categoria", "Estoque", "Validade", "Ações"]
            for h, text in zip(h_cols, headers):
                h.markdown(f'<div style="font-size:0.7rem; font-weight:700; opacity:0.5; text-transform:uppercase;">{text}</div>', unsafe_allow_html=True)

            for i, r in subset.iterrows():
                row = st.columns([2.5, 1.5, 1, 1.5, 1.5])
                row[0].write(f"**{r['nome']}**")
                row[1].write(r['motivo'])
                row[2].write(f"{r['quantidade']} un")
                
                dt = datetime.strptime(r['validade'], '%Y-%m-%d').date()
                row[3].write(dt.strftime('%d/%m/%Y'))

                acts = row[4].columns(3)
                if acts[0].button("📓", key=f"bula_{i}"):
                    if model:
                        with st.spinner("Consultando..."):
                            res = model.generate_content(f"Resuma a bula de {r['nome']}.")
                            st.info(res.text)
                
                if acts[1].button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_item = i
                    st.session_state.show_form = True
                    st.rerun()
                
                if acts[2].button("🗑️", key=f"del_{i}"):
                    df = df.drop(i)
                    save_data(df, sha, "Excluído!")
                    st.rerun()
