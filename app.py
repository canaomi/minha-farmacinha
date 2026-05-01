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
        return genai.GenerativeModel('gemini-2.0-flash')
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
    label, .titulo-lista {{ color: {COLORS['grafite']} !important; font-weight: 600; }}

    /* ── TODOS OS BOTÕES ── */
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

    /* ── MODAL / DIALOG ── */
    [data-testid="stDialog"] {{
        background-color: {COLORS['fundo']} !important;
        border-radius: 20px !important;
        border: 1.5px solid {COLORS['areia']} !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12) !important;
    }}
    [data-testid="stDialog"] h2 {{
        color: {COLORS['matcha']} !important;
        font-weight: 800 !important;
    }}

    /* ── EXPANDER ── */
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
        outline: none !important;
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

    /* ── CAMPOS DE ENTRADA ── */
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

    /* ── SELECTBOX ── */
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
    [data-testid="stSelectbox"] > div:focus-within {{
        outline: none !important;
        box-shadow: none !important;
        border: none !important;
    }}
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

    /* ── BOTÕES +/- ── */
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

    /* ── TABS / PILLS ── */
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
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {{ display: none !important; }}
    [data-testid="stIcon"] {{ display: none !important; }}

    hr {{ border-color: {COLORS['areia']} !important; opacity: 0.6; }}

    .empty-state {{
        color: {COLORS['grafite']};
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
    try:
        dt = datetime.strptime(val_str, '%Y-%m-%d').date()
        hoje = date.today()
        diff = (dt - hoje).days
        if diff < 0:
            return "Vencido 🚨", "#E53E3E"
        elif diff <= 30:
            return "Atenção ⚠️", "#D97706"
        else:
            return "Em dia ✅", "#587058"
    except:
        return "—", COLORS['grafite']

# --- 5. MODAL DE CADASTRO ---
@st.dialog("💊 Novo Remédio")
def modal_cadastro():
    with st.form("form_cadastro", clear_on_submit=True):
        nome_f = st.text_input("Nome do medicamento", placeholder="Digite o nome do seu remédio")
        c1, c2 = st.columns(2)
        val_f  = c1.date_input("Vencimento")
        qtd_f  = c2.number_input("Quantidade", min_value=1, step=1)
        cat_f  = st.selectbox("Motivo (Categoria)", [
            "Gases", "Diarréia", "Dor de cabeça",
            "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"
        ])
        if st.form_submit_button("Salvar remédio", use_container_width=True):
            if not nome_f.strip():
                st.warning("Digite o nome do medicamento.")
                return
            df, sha = load_data()
            new_row = {
                "nome": nome_f.strip(),
                "validade": str(val_f),
                "quantidade": int(qtd_f),
                "motivo": cat_f
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df, sha, "Remédio salvo! 💊")
            st.rerun()

# --- 6. INTERFACE ---
df, sha = load_data()

# ── Cabeçalho: título + botão alinhados ──
col_titulo, col_botao = st.columns([6, 1])
with col_titulo:
    st.title("💊 Farmacinha de Bolso")
with col_botao:
    st.markdown("<div style='padding-top:18px'>", unsafe_allow_html=True)
    if st.button("➕ Incluir", use_container_width=True):
        modal_cadastro()
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ── Busca ──
busca = st.text_input("🔍 Buscar remédio", placeholder="Digite o nome...")
st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

# ── Tabs por categoria ──
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
            h_cols = st.columns([2.5, 1, 1.5, 1.5])
            for text in ["Medicamento", "Estoque", "Validade", "Ações"]:
                h_cols[["Medicamento", "Estoque", "Validade", "Ações"].index(text)].markdown(
                    f'<div class="col-header">{text}</div>', unsafe_allow_html=True
                )

            for i, r in subset.iterrows():
                row = st.columns([2.5, 1, 1.5, 1.5])
                row[0].write(f"**{r['nome']}**")
                row[1].write(f"{r['quantidade']} un")

                label, cor = validade_badge(r['validade'])
                row[2].markdown(
                    f'<span style="color:{cor}; font-weight:600; font-size:0.85rem;">{label}</span>',
                    unsafe_allow_html=True
                )

                acts = row[3].columns(3)

                # 📓 BULA
                if acts[0].button("📓", key=f"bula_{i}", help="Ver bula"):
                    if model:
                        with st.spinner("Consultando bula..."):
                            try:
                                res = model.generate_content(f"Resuma a bula de {r['nome']} em tópicos curtos.")
                                st.info(res.text)
                            except Exception as e:
                                erro = str(e).lower()
                                if "resourceexhausted" in erro or "quota" in erro or "429" in erro:
                                    st.warning("⏳ Limite de consultas atingido. Tente novamente em alguns minutos.")
                                elif "notfound" in erro:
                                    st.warning("⚙️ Modelo de IA indisponível. Avise o administrador.")
                                else:
                                    st.warning("❌ Não foi possível consultar a bula agora. Tente mais tarde.")
                    else:
                        st.warning("⚙️ IA não configurada.")

                # ✏️ EDITAR
                if acts[1].button("✏️", key=f"edit_{i}", help="Editar"):
                    st.session_state.edit_item = i
                    st.rerun()

                # 🗑️ EXCLUIR
                if acts[2].button("🗑️", key=f"del_{i}", help="Excluir"):
                    df = df.drop(i).reset_index(drop=True)
                    save_data(df, sha, "Remédio excluído.")
                    st.rerun()
