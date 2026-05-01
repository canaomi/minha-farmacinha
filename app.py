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

    .stButton > button,
    .stButton > button:hover,
    .stButton > button:focus,
    .stButton > button:active,
    .stButton > button:focus-visible {{
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

    /* ── CHIP ATIVO ── */
    .chip-ativo {{
        display: inline-block;
        background-color: {COLORS['matcha']};
        color: {COLORS['branco']};
        border-radius: 50px;
        padding: 5px 14px;
        font-size: 0.82rem;
        font-weight: 700;
        cursor: pointer;
        border: none;
        margin: 2px;
    }}
    .chip-inativo {{
        display: inline-block;
        background-color: {COLORS['areia']};
        color: {COLORS['grafite']};
        border-radius: 50px;
        padding: 5px 14px;
        font-size: 0.82rem;
        font-weight: 600;
        cursor: pointer;
        border: none;
        margin: 2px;
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
        padding: 10px 14px !important;
        outline: none !important;
        box-shadow: none !important;
    }}
    [data-testid="stExpanderDetails"] {{
        background-color: {COLORS['fundo']} !important;
    }}

    [data-testid="stDialog"] {{
        background-color: {COLORS['fundo']} !important;
        border-radius: 20px !important;
        border: 1.5px solid {COLORS['areia']} !important;
    }}
    [data-testid="stDialog"] h2 {{
        color: {COLORS['matcha']} !important;
        font-weight: 800 !important;
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
        caret-color: {COLORS['matcha']};
    }}
    .stTextInput input:focus,
    .stNumberInput input:focus {{ border-color: {COLORS['matcha']} !important; }}
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {{
        color: {COLORS['grafite']} !important; opacity: 0.45;
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

    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div:hover,
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
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [aria-selected="true"] {{
        background-color: {COLORS['matcha_claro']} !important;
        color: {COLORS['matcha']} !important;
        font-weight: 600;
    }}

    .stNumberInput button,
    .stNumberInput button:hover,
    .stNumberInput button:focus,
    .stNumberInput button:active {{
        background-color: {COLORS['areia']} !important;
        color: {COLORS['grafite']} !important;
        border: none !important; outline: none !important;
        box-shadow: none !important; border-radius: 8px !important;
    }}
    .stNumberInput button:hover {{
        background-color: {COLORS['matcha']} !important;
        color: {COLORS['branco']} !important;
    }}

    hr {{ border-color: {COLORS['areia']} !important; opacity: 0.6; }}

    .empty-state {{
        color: {COLORS['grafite']}; opacity: 0.35;
        text-align: center; padding: 30px 0; font-size: 0.9rem;
    }}
    .col-header {{
        font-size: 0.68rem; font-weight: 700; opacity: 0.45;
        text-transform: uppercase; letter-spacing: 0.05em;
        color: {COLORS['grafite']};
    }}

    /* ── BADGE DE USO ── */
    .badge-uso {{
        display: inline-block;
        background-color: {COLORS['matcha_claro']};
        color: {COLORS['matcha']};
        border-radius: 50px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
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
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "uso"]), None

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

# --- 5. CATEGORIAS ---
USOS = ["Todos", "Gases", "Diarréia", "Dor de cabeça", "Gripe",
        "Antiinflamatório", "Dor de estômago", "Outros"]

# --- 6. MODAL DE CADASTRO ---
@st.dialog("💊 Novo Remédio")
def modal_cadastro():
    with st.form("form_cadastro", clear_on_submit=True):
        nome_f = st.text_input("Nome do medicamento", placeholder="Digite o nome do seu remédio")
        c1, c2 = st.columns(2)
        val_f  = c1.date_input("Vencimento")
        qtd_f  = c2.number_input("Quantidade", min_value=1, step=1)
        uso_f  = st.selectbox("Uso", USOS[1:])  # sem "Todos"
        if st.form_submit_button("Salvar remédio", use_container_width=True):
            if not nome_f.strip():
                st.warning("Digite o nome do medicamento.")
                return
            df, sha = load_data()
            # Compatibilidade: renomeia coluna 'motivo' → 'uso' se necessário
            if "motivo" in df.columns:
                df = df.rename(columns={"motivo": "uso"})
            new_row = {
                "nome":      nome_f.strip(),
                "validade":  str(val_f),
                "quantidade": int(qtd_f),
                "uso":       uso_f
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            save_data(df, sha, "Remédio salvo! 💊")
            st.rerun()

# --- 7. INTERFACE ---
df, sha = load_data()

# Compatibilidade com dados antigos (coluna 'motivo' → 'uso')
if "motivo" in df.columns:
    df = df.rename(columns={"motivo": "uso"})

# ── Cabeçalho ──
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

# ── Filtros e Ordenação ──
st.markdown("#### Filtrar por Uso")

# Chips de filtro
if "filtro_uso" not in st.session_state:
    st.session_state.filtro_uso = "Todos"

chip_cols = st.columns(len(USOS))
for idx, uso in enumerate(USOS):
    with chip_cols[idx]:
        ativo = st.session_state.filtro_uso == uso
        if st.button(
            uso,
            key=f"chip_{uso}",
            type="primary" if ativo else "secondary",
            use_container_width=True
        ):
            st.session_state.filtro_uso = uso
            st.rerun()

# Ordenação
col_ord, _ = st.columns([2, 4])
with col_ord:
    ordenacao = st.selectbox(
        "Ordenar por",
        ["Validade (mais próxima)", "Nome (A-Z)", "Uso"],
        label_visibility="collapsed"
    )

st.divider()

# ── Aplicar filtros ──
subset = df.copy() if not df.empty else pd.DataFrame(columns=["nome", "validade", "quantidade", "uso"])

if busca:
    subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]

if st.session_state.filtro_uso != "Todos":
    subset = subset[subset['uso'] == st.session_state.filtro_uso]

# ── Aplicar ordenação ──
if not subset.empty:
    if ordenacao == "Nome (A-Z)":
        subset = subset.sort_values("nome", ignore_index=True)
    elif ordenacao == "Uso":
        subset = subset.sort_values("uso", ignore_index=True)
    elif ordenacao == "Validade (mais próxima)":
        subset["_val_date"] = pd.to_datetime(subset["validade"], errors="coerce")
        subset = subset.sort_values("_val_date", ignore_index=True)
        subset = subset.drop(columns=["_val_date"])

# ── Lista geral ──
st.markdown('<p class="titulo-lista">Lista de remédios</p>', unsafe_allow_html=True)

if subset.empty:
    st.markdown('<div class="empty-state">Nenhum remédio encontrado.</div>', unsafe_allow_html=True)
else:
    # Cabeçalho da tabela
    h_cols = st.columns([2.5, 1.2, 1.2, 1.5, 1.2])
    for col, text in zip(h_cols, ["Medicamento", "Uso", "Estoque", "Validade", "Ações"]):
        col.markdown(f'<div class="col-header">{text}</div>', unsafe_allow_html=True)

    for i, r in subset.iterrows():
        row = st.columns([2.5, 1.2, 1.2, 1.5, 1.2])

        row[0].write(f"**{r['nome']}**")
        row[1].markdown(f'<span class="badge-uso">{r["uso"]}</span>', unsafe_allow_html=True)
        row[2].write(f"{r['quantidade']} un")

        label, cor = validade_badge(r['validade'])
        row[3].markdown(
            f'<span style="color:{cor}; font-weight:600; font-size:0.85rem;">{label}</span>',
            unsafe_allow_html=True
        )

        acts = row[4].columns(3)

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
