import streamlit as st
import pandas as pd
from github import Github
import io
import google.generativeai as genai
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES INICIAIS ---
st.set_page_config(page_title="Farmacinha de Bolso", layout="wide")

def get_ai_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except: return None

model = get_ai_model()

# --- 2. ESTILO E PALETA DE CORES (Pink & Flat) ---
COLORS = {
    "fundo": "#FDE2E4",
    "vibrante": "#FB6F92",
    "branco": "#FFFFFF",
    "preto": "#000000",
    "status_vencido": "#991B1B",
    "status_atencao": "#92400E",
    "status_em_dia": "#166534"
}

st.markdown(f"""
    <style>
    /* Configurações Gerais */
    .stApp {{ background-color: {COLORS['fundo']}; color: {COLORS['preto']}; }}
    h1 {{ color: {COLORS['vibrante']} !important; font-weight: 800 !important; }}
    
    /* Título Secundário */
    .titulo-lista {{
        font-weight: 600;
        font-size: 1.6rem;
        color: {COLORS['preto']};
        margin-top: 30px;
    }}

    /* Input de Busca e Campos do Formulário */
    .stTextInput input, .stNumberInput input, .stSelectbox select, .stDateInput input {{
        background-color: {COLORS['branco']} !important;
        color: {COLORS['preto']} !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}
    
    /* Remoção de bordas pretas de foco */
    .stTextInput input:focus, .stSelectbox div:focus {{
        border: none !important;
        outline: none !important;
    }}

    /* Pills e Tabs (Sem Chevron) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; border: none !important; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.4) !important;
        border-radius: 50px !important;
        padding: 8px 20px !important;
        color: {COLORS['preto']} !important;
        border: none !important;
    }}
    [data-testid="stIcon"] {{ display: none !important; }} /* Remove setas/chevrons */
    
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['vibrante']} !important;
        color: white !important;
    }}

    /* Botão Principal e do Formulário */
    .stButton > button {{
        background-color: {COLORS['vibrante']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }}

    /* Cabeçalho da Listagem */
    .label-col {{
        font-weight: 700;
        font-size: 0.75rem;
        text-transform: uppercase;
        color: {COLORS['preto']};
        opacity: 0.6;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS (GITHUB) ---
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
    if sha: repo.update_file("dados_remedios.csv", "App Sync", csv_data, sha)
    else: repo.create_file("dados_remedios.csv", "App Init", csv_data)
    st.toast(msg)

# --- 4. INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

# Ação de Entrada: Botão no topo
if st.button("➕ Incluir remédio", use_container_width=True):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.expander("📝 Cadastro", expanded=True):
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

# Busca
busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...")

st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

# Tabs/Categorias
categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca: subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info(f"Nenhum remédio em {cat_name}.")
        else:
            # Cabeçalho da Listagem (Tabela Invisível)
            h1, h2, h3, h4, h5 = st.columns([2, 1.5, 1, 1.5, 1.5])
            h1.markdown('<div class="label-col">Nome</div>', unsafe_allow_html=True)
            h2.markdown('<div class="label-col">Motivo</div>', unsafe_allow_html=True)
            h3.markdown('<div class="label-col">Qtde</div>', unsafe_allow_html=True)
            h4.markdown('<div class="label-col">Vencimento</div>', unsafe_allow_html=True)
            h5.markdown('<div class="label-col">Ações</div>', unsafe_allow_html=True)

            for i, r in subset.iterrows():
                row = st.columns([2, 1.5, 1, 1.5, 1.5])
                
                # Dados
                row[0].write(f"**{r['nome']}**")
                row[1].write(r['motivo'])
                row[2].write(f"{r['quantidade']} un")
                
                # Status de Validade
                dt = datetime.strptime(r['validade'], '%Y-%m-%d').date()
                dias = (dt - date.today()).days
                if dias < 0:
                    status_txt, status_color = "Vencido 🚨", COLORS['status_vencido']
                elif dias <= 30:
                    status_txt, status_color = "Atenção ⚠️", COLORS['status_atencao']
                else:
                    status_txt, status_color = "Em dia", COLORS['status_em_dia']
                
                row[3].markdown(f"<span style='color:{status_color}; font-weight:600;'>{dt.strftime('%d/%m/%Y')}<br><small>{status_txt}</small></span>", unsafe_allow_html=True)

                # Ações
                actions = row[4].columns(3)
                if actions[0].button("📓", key=f"bula_{i}", help="Bula"):
                    if model:
                        with st.spinner("Consultando..."):
                            res = model.generate_content(f"Resuma a bula de {r['nome']}: indicação e como tomar.")
                            st.info(res.text)
                
                if actions[1].button("✏️", key=f"edit_{i}", help="Editar"):
                    st.session_state.edit_item = i
                    st.session_state.show_form = True # Reaproveita o fluxo
                
                if actions[2].button("🗑️", key=f"del_{i}", help="Excluir"):
                    df = df.drop(i)
                    save_data(df, sha, "Excluído!")
                    st.rerun()
