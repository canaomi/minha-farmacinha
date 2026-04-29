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

# --- 2. PALETA MATCHA & CREAM (TOTAL FLAT) ---
COLORS = {
    "fundo": "#F9F7F2",       # Creme Papel
    "matcha": "#587058",      # Verde Matcha (Ações)
    "areia": "#E8D5C4",       # Bege Areia (Secundários)
    "grafite": "#2C2C2C",     # Texto Principal
    "branco": "#FFFFFF",
    "status_vencido": "#A64B4B", 
    "status_atencao": "#C49A6C"
}

st.markdown(f"""
    <style>
    /* Configurações Globais */
    .stApp {{ background-color: {COLORS['fundo']}; color: {COLORS['grafite']}; }}
    
    /* Título do App */
    h1 {{ color: {COLORS['matcha']} !important; font-weight: 800 !important; }}

    /* Título Secundário (Lista de remédios) */
    .titulo-lista {{ 
        font-weight: 600; 
        font-size: 1.4rem; 
        color: {COLORS['grafite']}; 
        margin: 25px 0 10px 0; 
    }}

    /* Inputs e Busca (Matcha Style) */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"], .stDateInput input {{
        background-color: {COLORS['branco']} !important;
        color: {COLORS['grafite']} !important;
        border: 1px solid {COLORS['areia']} !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}
    
    /* Remove bordas de foco */
    input:focus {{ border: 1px solid {COLORS['matcha']} !important; outline: none !important; }}

    /* Pills (Abas) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; border: none !important; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['areia']} !important;
        border-radius: 50px !important;
        padding: 8px 20px !important;
        color: {COLORS['grafite']} !important;
        border: none !important;
        opacity: 0.7;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['matcha']} !important;
        color: white !important;
        opacity: 1 !important;
    }}
    [data-testid="stIcon"] {{ display: none !important; }}

    /* Botão Principal Matcha */
    .stButton > button {{
        background-color: {COLORS['matcha']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}

    /* Estado Vazio (Transparente e Grafite) */
    .empty-state {{
        color: {COLORS['grafite']};
        opacity: 0.5;
        font-style: italic;
        padding: 40px 0;
        text-align: center;
        background: transparent !important;
    }}

    /* Cabeçalho da Listagem */
    .label-col {{
        font-weight: 700;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: {COLORS['grafite']};
        opacity: 0.4;
        border-bottom: 1px solid {COLORS['areia']};
        padding-bottom: 8px;
    }}
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

if st.session_state.get("show_form"):
    with st.expander("📝 Novo Cadastro", expanded=True):
        with st.form("form_cadastro", clear_on_submit=True):
            nome_f = st.text_input("Nome do medicamento")
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

# Busca (Label Grafite)
busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...")

st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca: subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            # AQUI: O novo placeholder de estado vazio, transparente e grafite
            st.markdown(f'<div class="empty-state">Nenhum remédio em {cat_name}.</div>', unsafe_allow_html=True)
        else:
            # Cabeçalho da Listagem
            h1, h2, h3, h4, h5 = st.columns([2.5, 1.5, 1, 1.5, 1.5])
            h1.markdown('<div class="label-col">Medicamento</div>', unsafe_allow_html=True)
            h2.markdown('<div class="label-col">Categoria</div>', unsafe_allow_html=True)
            h3.markdown('<div class="label-col">Estoque</div>', unsafe_allow_html=True)
            h4.markdown('<div class="label-col">Validade</div>', unsafe_allow_html=True)
            h5.markdown('<div class="label-col">Ações</div>', unsafe_allow_html=True)

            for i, r in subset.iterrows():
                row = st.columns([2.5, 1.5, 1, 1.5, 1.5])
                row[0].write(f"**{r['nome']}**")
                row[1].write(r['motivo'])
                row[2].write(f"{r['quantidade']} un")
                
                # Validade
                dt = datetime.strptime(r['validade'], '%Y-%m-%d').date()
                dias = (dt - date.today()).days
                status_color = COLORS['status_vencido'] if dias < 0 else (COLORS['status_atencao'] if dias <= 30 else COLORS['grafite'])
                row[3].markdown(f"<span style='color:{status_color}; font-weight:600;'>{dt.strftime('%d/%m/%Y')}</span>", unsafe_allow_html=True)

                # Ações
                acts = row[4].columns(3)
                if acts[0].button("📓", key=f"bula_{i}"):
                    if model:
                        with st.spinner("IA..."):
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
