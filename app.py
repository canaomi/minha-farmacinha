import streamlit as st
import pandas as pd
from github import Github
import io
import google.generativeai as genai
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES E IA ---
st.set_page_config(page_title="Farmacinha de Bolso", layout="centered")

def get_ai_model():
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        return None

model = get_ai_model()

# --- 2. PALETA E ESTILO FLAT (Sem Sombras) ---
PALETTE = {
    "fundo": "#FDE2E4",        # Rosa Pastel
    "vibrante": "#FB6F92",     # Rosa das Pills e Título
    "branco": "#FFFFFF",
    "preto": "#000000",
    "cinza_linha": "rgba(0,0,0,0.05)"
}

st.markdown(f"""
    <style>
    /* Reset Global e Fundo */
    .stApp {{ background-color: {PALETTE['fundo']}; color: {PALETTE['preto']}; }}
    
    /* Título Principal no tom das Pills */
    h1 {{ color: {PALETTE['vibrante']} !important; font-weight: 800 !important; }}

    /* Título: Lista de remédios (Aumentado e Bold) */
    .titulo-secao {{
        font-weight: 800 !important;
        font-size: 2.2rem !important; /* +3 tamanhos do anterior */
        color: {PALETTE['preto']};
        margin-top: 30px;
        margin-bottom: 10px;
    }}

    /* Campo de Busca (Branco, Fonte Preta, Sem Sombra) */
    .stTextInput > div > div > input {{
        background-color: {PALETTE['branco']} !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        color: {PALETTE['preto']} !important;
        box-shadow: none !important; /* Remove sombra */
    }}

    /* Pills Roláveis (Sem Sombras e Sem Chevron) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        display: flex;
        overflow-x: auto;
        padding: 5px 0;
    }}
    /* Esconde o Chevron/Setas das abas */
    [data-testid="stTabs"] button [data-testid="stIcon"] {{ display: none !important; }}
    
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.6) !important;
        border-radius: 25px !important;
        padding: 8px 18px !important;
        color: {PALETTE['preto']} !important;
        border: none !important;
        box-shadow: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PALETTE['vibrante']} !important;
        color: white !important;
    }}

    /* Listagem Simples Horizontal (Substituindo o Card) */
    .remedio-item {{
        background-color: transparent;
        padding: 12px 0;
        border-bottom: 1px solid {PALETTE['cinza_linha']};
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    
    .info-principal {{ flex: 2; }}
    .info-dados {{ flex: 1; text-align: right; }}

    .nome-texto {{ font-weight: 700; font-size: 1.1rem; color: {PALETTE['preto']}; margin: 0; }}
    .meta-texto {{ font-size: 0.85rem; color: #555; }}
    
    /* Botões Flat (Sem Sombra) */
    button {{
        box-shadow: none !important;
        border: none !important;
    }}

    /* FAB Customizado (Sem Sombra) */
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
        z-index: 1000 !important;
        box-shadow: none !important;
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
    repo = g.get_repo(repo_name := st.secrets["REPO_NAME"])
    csv_data = df.to_csv(index=False)
    if sha: g.get_repo(repo_name).update_file("dados_remedios.csv", "Update", csv_data, sha)
    else: g.get_repo(repo_name).create_file("dados_remedios.csv", "Initial", csv_data)

# --- 4. INTERFACE ---
st.title("Farmacinha de Bolso")

df, sha = load_data()

# Busca Flat
busca = st.text_input("", placeholder="🔍 O que você está procurando?")

# Subtítulo (Grande e Bold)
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
            for i, r in subset.iterrows():
                val_dt = datetime.strptime(r['validade'], '%Y-%m-%d').date()
                dias = (val_dt - date.today()).days
                status_icon = "🚨" if dias < 0 else ("⚠️" if dias <= 30 else "✅")
                
                # Layout Horizontal de Listagem
                st.markdown(f"""
                    <div class="remedio-item">
                        <div class="info-principal">
                            <p class="nome-texto">{r['nome']}</p>
                            <span class="meta-texto">{r['motivo']}</span>
                        </div>
                        <div class="info-dados">
                            <div class="nome-texto">{r['quantidade']} un</div>
                            <div class="meta-texto">{val_dt.strftime('%d/%m/%Y')} {status_icon}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Ações em linha (UX: Limpeza)
                col_bula, col_del = st.columns([1, 0.2])
                with col_bula:
                    if st.button(f"📖 Bula", key=f"bula_{i}", use_container_width=False):
                        if model:
                            with st.spinner("Consultando IA..."):
                                res = model.generate_content(f"Resuma a bula de {r['nome']}: Indicação, Uso e Alerta.")
                                st.success(res.text)
                        else:
                            st.error("IA não configurada.")
                with col_del:
                    if st.button("🗑️", key=f"del_{i}"):
                        df = df.drop(i)
                        save_data(df, sha)
                        st.rerun()

# --- 5. FAB E FORMULÁRIO ---
if st.button("＋", key="fab_main"):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.expander("📝 Adicionar Novo", expanded=True):
        with st.form("add_form", clear_on_submit=True):
            nome = st.text_input("Nome do medicamento")
            c1, c2 = st.columns(2)
            val = c1.date_input("Vencimento")
            qtd = c2.number_input("Qtd", min_value=1)
            cat = st.selectbox("Categoria", categorias)
            if st.form_submit_button("Salvar na Lista"):
                new_item = pd.DataFrame([{"nome": nome, "validade": str(val), "quantidade": int(qtd), "motivo": cat}])
                df = pd.concat([df, new_item], ignore_index=True)
                save_data(df, sha)
                st.session_state.show_form = False
                st.rerun()
