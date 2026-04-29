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

# --- 2. PALETA E ESTILO MINIMALISTA (Pink & Black) ---
PALETTE = {
    "fundo": "#FDE2E4",
    "vibrante": "#FB6F92",
    "branco": "#FFFFFF",
    "preto": "#000000"
}

st.markdown(f"""
    <style>
    /* Reset Global */
    .stApp {{ background-color: {PALETTE['fundo']}; color: {PALETTE['preto']}; }}
    
    /* Título Principal */
    h1 {{ color: {PALETTE['vibrante']} !important; font-weight: 800 !important; }}

    /* Título: Lista de remédios (Ajuste de Peso e Tamanho) */
    .titulo-secao {{
        font-weight: 600;
        font-size: 1.6rem;
        color: {PALETTE['preto']};
        margin: 25px 0 15px 0;
    }}

    /* Campo de Busca (Clean) */
    .stTextInput > div > div > input {{
        background-color: {PALETTE['branco']} !important;
        border: none !important;
        outline: none !important;
        border-radius: 12px !important;
        color: {PALETTE['preto']} !important;
        box-shadow: none !important;
    }}

    /* Pills Sem Chevron e Sem Bordas */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.4) !important;
        border-radius: 50px !important;
        padding: 8px 18px !important;
        color: {PALETTE['preto']} !important;
        border: none !important;
    }}
    /* Remove o ícone de seta (chevron) das abas */
    [data-testid="stIcon"] {{ display: none !important; }}
    
    .stTabs [aria-selected="true"] {{
        background-color: {PALETTE['vibrante']} !important;
        color: white !important;
    }}

    /* Estilo do Cabeçalho da Tabela */
    .header-tabela {{
        font-weight: 700;
        font-size: 0.85rem;
        color: {PALETTE['preto']};
        text-transform: uppercase;
        letter-spacing: 1px;
        padding-bottom: 10px;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        margin-bottom: 10px;
    }}

    /* Linha da Listagem */
    .remedio-linha {{
        padding: 12px 0;
        font-size: 0.95rem;
        align-items: center;
    }}

    /* Botão Flutuante (FAB) */
    div[data-testid="stVerticalBlock"] > div:last-child button {{
        position: fixed !important;
        bottom: 30px !important;
        right: 25px !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        background-color: {PALETTE['vibrante']} !important;
        color: white !important;
        font-size: 30px !important;
        box-shadow: none !important;
        border: none !important;
        z-index: 999;
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

def save_data(df, sha):
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
    csv_data = df.to_csv(index=False)
    if sha: repo.update_file("dados_remedios.csv", "Sync", csv_data, sha)
    else: repo.create_file("dados_remedios.csv", "Init", csv_data)

# --- 4. INTERFACE ---
st.title("Farmacinha de Bolso")

df, sha = load_data()

# Busca Minimalista
busca = st.text_input("", placeholder="Procurar medicamento...")

st.markdown('<p class="titulo-secao">Lista de remédios</p>', unsafe_allow_html=True)

categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca: subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info(f"Nenhum item em {cat_name}.")
        else:
            # Cabeçalho da Tabela
            h1, h2, h3, h4, h5 = st.columns([2, 1.5, 1, 1.5, 1.5])
            h1.markdown('<div class="header-tabela">Nome</div>', unsafe_allow_html=True)
            h2.markdown('<div class="header-tabela">Motivo</div>', unsafe_allow_html=True)
            h3.markdown('<div class="header-tabela">Qtde</div>', unsafe_allow_html=True)
            h4.markdown('<div class="header-tabela">Vencimento</div>', unsafe_allow_html=True)
            h5.markdown('<div class="header-tabela">Ações</div>', unsafe_allow_html=True)

            for i, r in subset.iterrows():
                c1, c2, c3, c4, c5 = st.columns([2, 1.5, 1, 1.5, 1.5])
                
                c1.write(f"**{r['nome']}**")
                c2.write(f"{r['motivo']}")
                c3.write(f"{r['quantidade']} un")
                
                # Validação de data
                dt = datetime.strptime(r['validade'], '%Y-%m-%d')
                venc_txt = dt.strftime('%d/%m/%Y')
                venc_status = "🚨" if (dt.date() - date.today()).days < 0 else ""
                c4.write(f"{venc_txt} {venc_status}")

                # Coluna de Ações (Ícones)
                with c5:
                    sub_col1, sub_col2, sub_col3 = st.columns(3)
                    # Bula
                    if sub_col1.button("📓", key=f"bula_{i}", help="Bula IA"):
                        if model:
                            with st.spinner("Consultando IA..."):
                                res = model.generate_content(f"Resuma a bula de {r['nome']}: indicação e como tomar.")
                                st.info(res.text)
                    # Editar
                    if sub_col2.button("✏️", key=f"edit_{i}", help="Editar"):
                        st.session_state.edit_id = i
                        st.session_state.show_form = True
                    # Apagar
                    if sub_col3.button("🗑️", key=f"del_{i}", help="Apagar"):
                        df = df.drop(i)
                        save_data(df, sha)
                        st.rerun()

# --- 5. FAB E FORMULÁRIO (ADD/EDIT) ---
if st.button("＋", key="fab_main"):
    st.session_state.edit_id = None
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    title_form = "Editar Medicamento" if st.session_state.get("edit_id") is not None else "Novo Medicamento"
    with st.expander(f"📝 {title_form}", expanded=True):
        with st.form("form_entry", clear_on_submit=True):
            # Se for edição, preenche com os dados existentes
            curr_id = st.session_state.get("edit_id")
            default_nome = df.iloc[curr_id]['nome'] if curr_id is not None else ""
            default_qtd = int(df.iloc[curr_id]['quantidade']) if curr_id is not None else 1
            
            nome_f = st.text_input("Nome", value=default_nome)
            f1, f2 = st.columns(2)
            val_f = f1.date_input("Vencimento")
            qtd_f = f2.number_input("Quantidade", min_value=1, value=default_qtd)
            cat_f = st.selectbox("Categoria", categorias)
            
            if st.form_submit_button("Confirmar Salvamento"):
                new_row = {"nome": nome_f, "validade": str(val_f), "quantidade": int(qtd_f), "motivo": cat_f}
                if curr_id is not None:
                    df.iloc[curr_id] = new_row
                else:
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                
                save_data(df, sha)
                st.session_state.show_form = False
                st.session_state.edit_id = None
                st.rerun()
