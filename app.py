import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- CONFIGURAÇÕES VISUAIS (Inspirado na referência de Listagem) ---
st.set_page_config(page_title="Minha Farmacinha", layout="centered")

# Paleta baseada na nova referência: Limpo, contraste alto e profissional
COLOR_PALETTE = {
    "azul_primario": "#2E98DD",  # Blue Bell
    "fundo_app": "#F0F2EF",      # White Smoke (Fundo da referência)
    "cinza_texto": "#65655E",    # Dim Grey (Texto secundário)
    "branco_card": "#FFFFFF",    # Cards brancos limpos
    "texto_titulo": "#1A1A1A",   # Quase preto para títulos
    "borda_leve": "#E0E0E0"      # Bordas sutis
}

MOTIVOS_EMOJIS = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# CSS para UI estilo "Explore Tokens"
st.markdown(f"""
    <style>
    /* Reset de fundo */
    .stApp {{
        background-color: {COLOR_PALETTE['fundo_app']};
    }}
    
    /* Card estilo Listagem Profissional */
    .remedio-row {{
        background-color: {COLOR_PALETTE['branco_card']};
        padding: 16px;
        border-bottom: 1px solid {COLOR_PALETTE['borda_leve']};
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    
    .remedio-info {{
        display: flex;
        align-items: center;
    }}

    /* Ícone circular para Mobile (com Emoji) */
    .icon-circle {{
        width: 40px;
        height: 40px;
        background-color: #F8F9FA;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        margin-right: 12px;
    }}

    .nome-texto {{
        color: {COLOR_PALETTE['texto_titulo']};
        font-weight: 600;
        font-size: 1rem;
        margin-bottom: 2px;
    }}

    .sub-texto {{
        color: {COLOR_PALETTE['cinza_texto']};
        font-size: 0.85rem;
    }}

    .valor-estoque {{
        text-align: right;
        color: {COLOR_PALETTE['texto_titulo']};
        font-weight: 600;
    }}

    /* Esconder ícones em telas grandes (Desktop) conforme solicitado */
    @media (min-width: 768px) {{
        .icon-circle {{ display: none; }}
    }}

    /* Estilização das Tabs e Inputs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: transparent;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent;
        border: none;
        color: {COLOR_PALETTE['cinza_texto']};
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        color: {COLOR_PALETTE['texto_titulo']} !important;
        border-bottom: 2px solid {COLOR_PALETTE['texto_titulo']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES GITHUB ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "dados_remedios.csv"

def load_data():
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    try:
        file_content = repo.get_contents(FILE_PATH)
        return pd.read_csv(io.StringIO(file_content.decoded_content.decode())), file_content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha):
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    if sha:
        repo.update_file(FILE_PATH, "Update inventory", csv_buffer.getvalue(), sha)
    else:
        repo.create_file(FILE_PATH, "Initial inventory", csv_buffer.getvalue())

# --- INTERFACE ---
st.title("Farmacinha")

df, sha = load_data()

# Botão de ação com cor Blue Bell da paleta
if st.button("＋ Incluir remédio", use_container_width=True):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("add_form", clear_on_submit=True):
        nome = st.text_input("Nome")
        c1, c2 = st.columns(2)
        validade = c1.date_input("Validade")
        quantidade = c2.number_input("Qtd", min_value=1)
        motivo = st.selectbox("Categoria", list(MOTIVOS_EMOJIS.keys()))
        if st.form_submit_button("Confirmar"):
            new_data = pd.DataFrame([{"nome": nome, "validade": str(validade), "quantidade": int(quantidade), "motivo": motivo}])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.rerun()

# Busca (Sem emoji na label para ficar clean)
busca = st.text_input("Buscar remédio", placeholder="Ex: Paracetamol...")

# Categorias em Tabs (Apenas texto, conforme solicitado)
tabs = st.tabs(list(MOTIVOS_EMOJIS.keys()))

for idx, motivo_nome in enumerate(MOTIVOS_EMOJIS.keys()):
    with tabs[idx]:
        itens = df[df['motivo'] == motivo_nome] if not df.empty else pd.DataFrame()
        if busca:
            itens = itens[itens['nome'].str.contains(busca, case=False, na=False)]
        
        if itens.empty:
            st.info("Nenhum item encontrado.")
        else:
            # Cabeçalho da Lista (Estilo referência)
            st.markdown(f"""
                <div style="display: flex; justify-content: space-between; padding: 10px 16px; color: {COLOR_PALETTE['cinza_texto']}; font-size: 0.8rem; text-transform: uppercase;">
                    <span>Nome / Categoria</span>
                    <span>Qtd / Validade</span>
                </div>
            """, unsafe_allow_html=True)
            
            for i, r in itens.iterrows():
                emoji = MOTIVOS_EMOJIS.get(r['motivo'], "💊")
                val_formatada = datetime.strptime(r['validade'], '%Y-%m-%d').strftime('%d/%m/%Y')
                
                # Card no estilo "Explore Tokens"
                st.markdown(f"""
                    <div class="remedio-row">
                        <div class="remedio-info">
                            <div class="icon-circle">{emoji}</div>
                            <div>
                                <div class="nome-texto">{r['nome']}</div>
                                <div class="sub-texto">{r['motivo']}</div>
                            </div>
                        </div>
                        <div class="valor-estoque">
                            <div>{r['quantidade']} un</div>
                            <div class="sub-texto" style="font-weight: 400;">{val_formatada}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botão de deletar discreto abaixo do card
                if st.button(f"Remover {r['nome']}", key=f"del_{i}", use_container_width=True):
                    df = df.drop(i)
                    save_data(df, sha)
                    st.rerun()
