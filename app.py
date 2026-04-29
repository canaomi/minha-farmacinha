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

# --- 2. ESTILO E PALETA CROMÁTICA UNIFICADA ---
COLORS = {
    "fundo": "#FDE2E4",      # Rosa Pastel
    "vibrante": "#FB6F92",   # Rosa de Ação (Pills, Botões, Inputs)
    "branco": "#FFFFFF",
    "preto": "#000000"
}

st.markdown(f"""
    <style>
    /* Configurações Gerais */
    .stApp {{ background-color: {COLORS['fundo']}; color: {COLORS['preto']}; }}
    h1 {{ color: {COLORS['vibrante']} !important; font-weight: 800 !important; }}
    
    /* Pergunta da Busca e Labels em Preto */
    label, .stMarkdown p, .titulo-lista {{
        color: {COLORS['preto']} !important;
        font-weight: 600 !important;
    }}

    /* Inputs (Busca, Número, Seleção, Data) na cor Rosa Vibrante */
    .stTextInput input, .stNumberInput input, .stSelectbox [data-baseweb="select"], .stDateInput input {{
        background-color: {COLORS['vibrante']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        box-shadow: none !important;
    }}

    /* Estilo específico para o texto dentro dos inputs para garantir cor branca */
    input {{ color: white !important; }}
    div[role="listbox"] {{ color: {COLORS['preto']} !important; }} /* Lista de opções em preto para ler melhor */

    /* Placeholder da busca em branco translúcido */
    input::placeholder {{ color: rgba(255, 255, 255, 0.7) !important; }}

    /* Pills/Tabs (Todas em Rosa, Texto Branco) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; border: none !important; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['vibrante']} !important;
        border-radius: 50px !important;
        padding: 8px 20px !important;
        color: white !important;
        border: none !important;
        opacity: 0.7; /* Efeito de 'recolhida' */
    }}
    .stTabs [aria-selected="true"] {{
        opacity: 1 !important;
        font-weight: 700 !important;
    }}
    [data-testid="stIcon"] {{ display: none !important; }} /* Remove setas/chevrons */

    /* Botões (Incluir, Salvar, Ícones) */
    .stButton > button {{
        background-color: {COLORS['vibrante']} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }}

    /* Tabela Invisível */
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
    if sha: repo.update_file("dados_remedios.csv", "App Sync", csv_data, sha)
    else: repo.create_file("dados_remedios.csv", "App Init", csv_data)
    st.toast(msg)

# --- 4. INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

# Ação de Entrada
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
                df = pd.concat([df, new_row if isinstance(new_row, pd.DataFrame) else pd.DataFrame([new_row])], ignore_index=True)
                save_data(df, sha, "Remédio salvo!")
                st.session_state.show_form = False
                st.rerun()

st.divider()

# Busca com Label em Preto
busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...")

st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca: subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info(f"Nenhum remédio em {cat_name}.")
        else:
            # Cabeçalho
            h1, h2, h3, h4, h5 = st.columns([2, 1.5, 1, 1.5, 1.5])
            h1.markdown('<div class="label-col">Nome</div>', unsafe_allow_html=True)
            h2.markdown('<div class="label-col">Motivo</div>', unsafe_allow_html=True)
            h3.markdown('<div class="label-col">Qtde</div>', unsafe_allow_html=True)
            h4.markdown('<div class="label-col">Vencimento</div>', unsafe_allow_html=True)
            h5.markdown('<div class="label-col">Ações</div>', unsafe_allow_html=True)

            for i, r in subset.iterrows():
                row = st.columns([2, 1.5, 1, 1.5, 1.5])
                row[0].write(f"**{r['nome']}**")
                row[1].write(r['motivo'])
                row[2].write(f"{r['quantidade']} un")
                
                dt = datetime.strptime(r['validade'], '%Y-%m-%d').date()
                row[3].write(dt.strftime('%d/%m/%Y'))

                actions = row[4].columns(3)
                if actions[0].button("📓", key=f"bula_{i}"):
                    if model:
                        with st.spinner("Consultando..."):
                            res = model.generate_content(f"Resuma a bula de {r['nome']}: indicação e uso.")
                            st.info(res.text)
                
                if actions[1].button("✏️", key=f"edit_{i}"):
                    st.session_state.edit_item = i
                    st.session_state.show_form = True
                    st.rerun()
                
                if actions[2].button("🗑️", key=f"del_{i}"):
                    df = df.drop(i)
                    save_data(df, sha, "Excluído!")
                    st.rerun()
