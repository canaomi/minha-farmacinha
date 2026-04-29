import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES VISUAIS E PALETA PINK ---
st.set_page_config(page_title="Farmacinha", layout="centered")

# Paleta Rosa Profissional
PINK_PALETTE = {
    "fundo_tela": "#FDE2E4",      # Rosa Pastel Suave (Fundo)
    "botao_cor": "#FB6F92",       # Rosa Vibrante (Botões)
    "card_branco": "#FFFFFF",     # Branco (Para os itens saltarem)
    "texto_preto": "#000000",     # Preto (Contraste máximo)
    "texto_cinza": "#4A4A4A",     # Cinza escuro (Apoio)
    "borda": "#FFC2D1"            # Rosa médio (Divisores)
}

MOTIVOS = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# CSS Responsivo e Tematizado
st.markdown(f"""
    <style>
    /* Fundo do App */
    .stApp {{
        background-color: {PINK_PALETTE['fundo_tela']};
        color: {PINK_PALETTE['texto_preto']};
    }}
    
    /* Títulos e Labels */
    h1, h2, label, .stMarkdown p {{
        color: {PINK_PALETTE['texto_preto']} !important;
    }}

    /* Estilo das Linhas (Cards) */
    .remedio-row {{
        background-color: {PINK_PALETTE['card_branco']};
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid {PINK_PALETTE['borda']};
    }}
    
    .left-content {{ display: flex; align-items: center; }}

    /* Ícone Mobile (Emoji no círculo) */
    .mobile-icon {{
        width: 42px; height: 42px;
        background-color: {PINK_PALETTE['fundo_tela']};
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 20px; margin-right: 12px;
    }}

    .nome-texto {{ font-weight: 700; font-size: 1rem; margin: 0; }}
    .cat-texto {{ color: {PINK_PALETTE['texto_cinza']}; font-size: 0.75rem; text-transform: uppercase; }}
    .right-content {{ text-align: right; }}
    .qtd-texto {{ font-weight: 800; font-size: 1rem; }}
    .data-texto {{ color: {PINK_PALETTE['texto_cinza']}; font-size: 0.8rem; }}

    /* Responsividade: Esconde o ícone no Desktop */
    @media (min-width: 768px) {{
        .mobile-icon {{ display: none !important; }}
        .remedio-row {{ padding: 12px 20px; }}
    }}

    /* Botões Customizados */
    div.stButton > button {{
        background-color: {PINK_PALETTE['botao_cor']} !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
    }}

    /* Estilo das Abas (Tabs) */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [data-baseweb="tab"] {{
        color: {PINK_PALETTE['texto_cinza']};
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        color: {PINK_PALETTE['texto_preto']} !important;
        border-bottom: 3px solid {PINK_PALETTE['botao_cor']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 2. LÓGICA DE DADOS ---
def get_github_repo():
    return Github(st.secrets["GITHUB_TOKEN"]).get_repo(st.secrets["REPO_NAME"])

def load_data():
    repo = get_github_repo()
    try:
        content = repo.get_contents("dados_remedios.csv")
        df = pd.read_csv(io.StringIO(content.decoded_content.decode()))
        return df, content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha):
    repo = get_github_repo()
    csv_data = df.to_csv(index=False)
    if sha:
        repo.update_file("dados_remedios.csv", "Update", csv_data, sha)
    else:
        repo.create_file("dados_remedios.csv", "Initial", csv_data)

# --- 3. INTERFACE ---
st.title("Minha Farmacinha")

df, sha = load_data()

# Botão de inclusão
if st.button("＋ Adicionar Novo Item", use_container_width=True):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("form_add", clear_on_submit=True):
        nome = st.text_input("Nome do Remédio")
        c1, c2 = st.columns(2)
        val = c1.date_input("Validade")
        qtd = c2.number_input("Quantidade", min_value=1)
        cat = st.selectbox("Categoria", list(MOTIVOS.keys()))
        if st.form_submit_button("Salvar na Lista"):
            new_item = pd.DataFrame([{"nome": nome, "validade": str(val), "quantidade": int(qtd), "motivo": cat}])
            df = pd.concat([df, new_item], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.rerun()

st.divider()

# Busca e Navegação (Minimalista)
busca = st.text_input("Procurar", placeholder="Ex: Dorflex...")
tabs = st.tabs(list(MOTIVOS.keys()))

for idx, cat_name in enumerate(MOTIVOS.keys()):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca:
            subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info("Nada por aqui ainda.")
        else:
            for i, r in subset.iterrows():
                emoji = MOTIVOS.get(r['motivo'], "💊")
                try:
                    dt_str = datetime.strptime(r['validade'], '%Y-%m-%d').strftime('%d/%m/%y')
                except:
                    dt_str = r['validade']

                st.markdown(f"""
                    <div class="remedio-row">
                        <div class="left-content">
                            <div class="mobile-icon">{emoji}</div>
                            <div>
                                <p class="nome-texto">{r['nome']}</p>
                                <span class="cat-texto">{r['motivo']}</span>
                            </div>
                        </div>
                        <div class="right-content">
                            <div class="qtd-texto">{r['quantidade']} un</div>
                            <div class="data-texto">{dt_str}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Excluir {r['nome']}", key=f"del_{i}", use_container_width=True):
                    df = df.drop(i)
                    save_data(df, sha)
                    st.rerun()

# --- FIM DO ARQUIVO ---
