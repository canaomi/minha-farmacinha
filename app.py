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
    except:
        return None

model = get_ai_model()

# --- 2. PALETA ZEN (MATCHA & CREAM) ---
COLORS = {
    "fundo":        "#F9F7F2",
    "matcha":       "#587058",
    "areia":        "#E8D5C4",
    "grafite":      "#2C2C2C",
    "branco":       "#FFFFFF",
    "matcha_claro": "#EAF0EA",
}

st.markdown(f"""
    <style>
    :root, html, body, .stApp {{
        color-scheme: light only !important;
        background-color: {COLORS['fundo']} !important;
        color: {COLORS['grafite']} !important;
    }}

    [data-testid="stHeader"] {{
        background-color: {COLORS['fundo']} !important;
    }}

    h1 {{ color: {COLORS['matcha']} !important; font-weight: 800 !important; }}
    label {{ color: {COLORS['grafite']} !important; font-weight: 600; }}

    .stButton > button,
    .stButton > button:hover,
    .stButton > button:focus,
    .stButton > button:active {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        outline: none !important;
        box-shadow: none !important;
    }}

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: 1.5px solid transparent !important;
        border-radius: 10px !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    .stTextInput input:focus,
    .stNumberInput input:focus {{
        border-color: {COLORS['matcha']} !important;
    }}
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {{
        color: {COLORS['grafite']} !important;
        opacity: 0.45;
    }}

    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div:focus-within {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: 1.5px solid transparent !important;
        border-radius: 10px !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    [data-baseweb="popover"] [data-baseweb="menu"] {{
        background-color: {COLORS['fundo']} !important;
        border: 1px solid {COLORS['areia']} !important;
        border-radius: 10px !important;
    }}
    [data-baseweb="popover"] [role="option"] {{
        color: {COLORS['grafite']} !important;
        background-color: {COLORS['fundo']} !important;
    }}
    [data-baseweb="popover"] [role="option"]:hover {{
        background-color: {COLORS['matcha_claro']} !important;
        color: {COLORS['matcha']} !important;
    }}

    .stNumberInput button,
    .stNumberInput button:hover {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 8px !important;
    }}
    .stNumberInput button:hover {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
    }}

    [data-testid="stExpander"] {{
        background-color: {COLORS['fundo']} !important;
        border: 1.5px solid {COLORS['areia']} !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }}
    [data-testid="stExpander"] > details > summary {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border-radius: 12px !important;
        outline: none !important;
    }}
    [data-testid="stExpanderDetails"] {{
        background-color: {COLORS['fundo']} !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        overflow-x: auto;
        flex-wrap: nowrap;
        scrollbar-width: none;
    }}
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display: none; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border-radius: 50px !important;
        border: none !important;
        font-weight: 600;
        white-space: nowrap;
        padding: 6px 16px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
    [data-testid="stIcon"] {{ display: none !important; }}

    hr {{ border-color: {COLORS['areia']} !important; opacity: 0.6; }}

    .empty-state {{
        opacity: 0.35;
        text-align: center;
        padding: 30px 0;
        font-size: 0.9rem;
    }}
    .col-header {{
        font-size: 0.68rem;
        font-weight: 700;
        opacity: 0.45;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"""
    <style>
    /* ── RESET GLOBAL ─────────────────────────────── */
    * {{ box-sizing: border-box; }}
    .stApp {{
        background-color: {COLORS['fundo']};
        color: {COLORS['grafite']};
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    /* ── TIPOGRAFIA ───────────────────────────────── */
    h1 {{ color: {COLORS['matcha']} !important; font-weight: 800 !important; }}
    label, .titulo-lista {{ color: {COLORS['grafite']} !important; font-weight: 600; }}

    /* ══════════════════════════════════════════════
       BOTÕES — TODOS OS ESTADOS (normal/hover/focus/active)
    ══════════════════════════════════════════════ */
    .stButton > button,
    .stButton > button:hover,
    .stButton > button:focus,
    .stButton > button:active,
    .stButton > button:focus-visible,
    .stButton > button:focus:not(:active) {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    .stButton > button:hover {{ opacity: 0.88 !important; }}
    .stButton > button:active {{ opacity: 0.75 !important; }}

    /* ── BOTÃO "INCLUIR REMÉDIO": SECUNDÁRIO ──────── */
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-secondary"]:hover,
    [data-testid="stBaseButton-secondary"]:focus,
    [data-testid="stBaseButton-secondary"]:active,
    [data-testid="stBaseButton-secondary"]:focus-visible {{
        background-color: {COLORS['fundo']} !important;
        color: {COLORS['matcha']} !important;
        border: 1.5px solid {COLORS['matcha']} !important;
        outline: none !important;
        box-shadow: none !important;
        opacity: 1 !important;
    }}
    [data-testid="stBaseButton-secondary"]:hover {{
        background-color: {COLORS['matcha_claro']} !important;
    }}

    /* ══════════════════════════════════════════════
       EXPANDER — MATA O PRETO NO HEADER
    ══════════════════════════════════════════════ */
    [data-testid="stExpander"] {{
        background-color: {COLORS['fundo']} !important;
        border: 1.5px solid {COLORS['areia']} !important;
        border-radius: 14px !important;
        box-shadow: none !important;
    }}
    [data-testid="stExpander"] > details {{
        background-color: {COLORS['fundo']} !important;
        border-radius: 14px !important;
    }}
    [data-testid="stExpander"] > details > summary {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        outline: none !important;          /* Remove foco preto no summary */
        box-shadow: none !important;
    }}
    [data-testid="stExpander"] > details > summary:hover {{
        background-color: {COLORS['matcha_claro']} !important;
    }}
    [data-testid="stExpander"] > details > summary svg {{
        fill: {COLORS['matcha']} !important;
    }}
    [data-testid="stExpanderDetails"] {{
        background-color: {COLORS['fundo']} !important;
        border-radius: 0 0 14px 14px !important;
    }}

    /* ══════════════════════════════════════════════
       CAMPOS DE ENTRADA — TODOS OS ESTADOS
       Remove outline/box-shadow preto do browser e Streamlit
    ══════════════════════════════════════════════ */
    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextInput input:hover,
    .stNumberInput input:hover,
    .stDateInput input:hover,
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus,
    .stTextInput input:active,
    .stNumberInput input:active,
    .stDateInput input:active,
    .stTextInput input:focus-visible,
    .stNumberInput input:focus-visible,
    .stDateInput input:focus-visible {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: 1.5px solid transparent !important;
        border-radius: 10px !important;
        outline: none !important;
        box-shadow: none !important;
        caret-color: {COLORS['matcha']};
    }}
    /* Focus ring suave só com a borda matcha */
    .stTextInput input:focus,
    .stNumberInput input:focus,
    .stDateInput input:focus {{
        border-color: {COLORS['matcha']} !important;
    }}
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stDateInput input::placeholder {{
        color: {COLORS['grafite']} !important;
        opacity: 0.45;
    }}

    /* ── WRAPPER DOS INPUTS (borda externa do Streamlit) */
    [data-testid="stTextInput"] > div,
    [data-testid="stNumberInput"] > div,
    [data-testid="stDateInput"] > div,
    [data-testid="stTextInput"] > div:focus-within,
    [data-testid="stNumberInput"] > div:focus-within,
    [data-testid="stDateInput"] > div:focus-within {{
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
    }}

    /* ══════════════════════════════════════════════
       SELECTBOX — TODOS OS ESTADOS
    ══════════════════════════════════════════════ */
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div:hover,
    .stSelectbox [data-baseweb="select"] > div:focus,
    .stSelectbox [data-baseweb="select"] > div:focus-within {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: 1.5px solid transparent !important;
        border-radius: 10px !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    /* Container pai do selectbox */
    [data-testid="stSelectbox"] > div:focus-within {{
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }}
    /* Dropdown aberto */
    [data-baseweb="popover"] [data-baseweb="menu"] {{
        background-color: {COLORS['fundo']} !important;
        border: 1px solid {COLORS['areia']} !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08) !important;
    }}
    [data-baseweb="popover"] [role="option"] {{
        color: {COLORS['grafite']} !important;
        background-color: {COLORS['fundo']} !important;
    }}
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {{
        background-color: {COLORS['matcha_claro']} !important;
        color: {COLORS['matcha']} !important;
        font-weight: 600;
    }}

    /* ── BOTÕES +/- DO NUMBER INPUT ───────────────── */
    .stNumberInput button,
    .stNumberInput button:hover,
    .stNumberInput button:focus,
    .stNumberInput button:active {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        border-radius: 8px !important;
    }}
    .stNumberInput button:hover {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
    }}

    /* ══════════════════════════════════════════════
       TABS / PILLS
    ══════════════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        overflow-x: auto;
        flex-wrap: nowrap;
        padding-bottom: 4px;
        scrollbar-width: none;
    }}
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {{ display: none; }}
    .stTabs [data-baseweb="tab"],
    .stTabs [data-baseweb="tab"]:focus,
    .stTabs [data-baseweb="tab"]:focus-visible {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border-radius: 50px !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        font-weight: 600;
        white-space: nowrap;
        padding: 6px 16px !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{ display: none !important; }}
    .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
    [data-testid="stIcon"] {{ display: none !important; }}

    /* ── DIVIDER ──────────────────────────────────── */
    hr {{ border-color: {COLORS['areia']} !important; opacity: 0.6; }}

    /* ── ESTADO VAZIO ─────────────────────────────── */
    .empty-state {{
        color: {COLORS['grafite']};
        opacity: 0.35;
        text-align: center;
        padding: 30px 0;
        font-size: 0.9rem;
    }}

    /* ── CABEÇALHO DA LISTA ───────────────────────── */
    .col-header {{
        font-size: 0.68rem;
        font-weight: 700;
        opacity: 0.45;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: {COLORS['grafite']};
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
    if sha:
        repo.update_file("dados_remedios.csv", "Sync", csv_data, sha)
    else:
        repo.create_file("dados_remedios.csv", "Init", csv_data)
    st.toast(msg)

# --- 4. HELPER: STATUS DE VALIDADE ---
def validade_badge(val_str):
    """Retorna texto de status baseado na data de validade."""
    try:
        dt = datetime.strptime(val_str, '%Y-%m-%d').date()
        hoje = date.today()
        diff = (dt - hoje).days
        if diff < 0:
            return "Vencido 🚨", "#E53E3E"   # Vermelho
        elif diff <= 30:
            return "Atenção ⚠️", "#D97706"   # Âmbar
        else:
            return "Em dia ✅", "#587058"     # Matcha
    except:
        return "—", COLORS['grafite']

# --- 5. INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

# Botão de entrada
if st.button("➕ Incluir remédio", use_container_width=True):
    st.session_state.show_form = not st.session_state.get("show_form", False)

# Formulário de cadastro
if st.session_state.get("show_form"):
    with st.expander("📝 Novo Cadastro", expanded=True):
        with st.form("form_cadastro", clear_on_submit=True):
            nome_f = st.text_input("Nome do medicamento", placeholder="Digite o nome do seu remédio")
            c1, c2 = st.columns(2)
            val_f  = c1.date_input("Vencimento")
            qtd_f  = c2.number_input("Quantidade", min_value=1, step=1)
            cat_f  = st.selectbox("Motivo (Categoria)", [
                "Gases", "Diarréia", "Dor de cabeça",
                "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"
            ])
            if st.form_submit_button("Salvar remédio"):
                new_row = {
                    "nome": nome_f,
                    "validade": str(val_f),
                    "quantidade": int(qtd_f),
                    "motivo": cat_f
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df, sha, "Remédio salvo! 💊")
                st.session_state.show_form = False
                st.rerun()

st.divider()

# Campo de busca
busca = st.text_input("🔍 Buscar remédio", placeholder="Digite o nome...")

st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

# Tabs por categoria
categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca:
            subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]

        if subset.empty:
            st.markdown(f'<div class="empty-state">Nenhum remédio em <strong>{cat_name}</strong>.</div>', unsafe_allow_html=True)
        else:
            # Cabeçalho da tabela invisível
            h_cols = st.columns([2.5, 1, 1.5, 1.5])
            for text in ["Medicamento", "Estoque", "Validade", "Ações"]:
                h_cols[["Medicamento", "Estoque", "Validade", "Ações"].index(text)].markdown(
                    f'<div class="col-header">{text}</div>', unsafe_allow_html=True
                )

            for i, r in subset.iterrows():
                row = st.columns([2.5, 1, 1.5, 1.5])

                row[0].write(f"**{r['nome']}**")
                row[1].write(f"{r['quantidade']} un")

                # Status de validade com cor semântica
                label, cor = validade_badge(r['validade'])
                row[2].markdown(
                    f'<span style="color:{cor}; font-weight:600; font-size:0.85rem;">{label}</span>',
                    unsafe_allow_html=True
                )

                # Ações
                acts = row[3].columns(3)

                if acts[0].button("📓", key=f"bula_{i}", help="Ver bula"):
                    if model:
                        with st.spinner("Consultando bula..."):
                            res = model.generate_content(f"Resuma a bula de {r['nome']} em tópicos curtos.")
                            st.info(res.text)
                    else:
                        st.warning("IA não disponível.")

                if acts[1].button("✏️", key=f"edit_{i}", help="Editar"):
                    st.session_state.edit_item = i
                    st.session_state.show_form = True
                    st.rerun()

                if acts[2].button("🗑️", key=f"del_{i}", help="Excluir"):
                    df = df.drop(i).reset_index(drop=True)
                    save_data(df, sha, "Remédio excluído.")
                    st.rerun()
