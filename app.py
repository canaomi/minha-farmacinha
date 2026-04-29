import streamlit as st
import pandas as pd
from github import Github
import io
from datetime import date, datetime

# --- CONFIGURAÇÕES VISUAIS E PALETA DE CORES ---
st.set_page_config(page_title="Minha Farmacinha", layout="centered")

# Definição da paleta Coolors
COLOR_PALETTE = {
    "azul_primario": "#2E98DD",  # Blue Bell (Ações principais)
    "roxo_fundo": "#392F5A",     # Space Indigo (Fundo do app)
    "rosa_destaque": "#F092DD",  # Plum (Destaques/Notificações)
    "rosa_fundo_card": "#EEC8E0", # Pastel Petal (Cards e Inputs)
    "texto_escuro": "#111111",   # Para contraste sobre rosa claro
    "texto_claro": "#FFFFFF"      # Para contraste sobre roxo escuro
}

MOTIVOS_ICONES = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

# CSS Customizado aplicando a paleta com foco em UX/UI e Contraste
st.markdown(f"""
    <style>
    /* Estilo do Fundo Principal */
    .stApp {{
        background-color: {COLOR_PALETTE['roxo_fundo']};
        color: {COLOR_PALETTE['texto_claro']};
    }}
    
    /* Estilo dos Títulos e Textos Principais */
    h1, h2, h3, p {{
        color: {COLOR_PALETTE['texto_claro']} !important;
    }}

    /* CSS para os Cards de Remédio (UX: Escaneabilidade) */
    .remedio-card {{
        background-color: {COLOR_PALETTE['rosa_fundo_card']};
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 15px;
        border: 2px solid {COLOR_PALETTE['rosa_destaque']}; /* Detalhe em Plum */
        color: {COLOR_PALETTE['texto_escuro']} !important; /* Contraste Máximo */
    }}
    .nome-remedio {{
        font-size: 1.3rem;
        font-weight: 800;
        margin-bottom: 8px;
        color: {COLOR_PALETTE['texto_escuro']} !important;
    }}
    .status-badge {{
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 700;
        display: inline-block;
        margin-top: 10px;
    }}
    .info-texto {{
        font-size: 0.95rem;
        color: {COLOR_PALETTE['texto_escuro']} !important;
        opacity: 0.9;
        line-height: 1.5;
    }}

    /* Estilo customizado para os inputs de busca e formulário (UI: Consistência) */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>select {{
        background-color: {COLOR_PALETTE['rosa_fundo_card']} !important;
        color: {COLOR_PALETTE['texto_escuro']} !important;
        border: 1px solid {COLOR_PALETTE['azul_primario']} !important;
        border-radius: 8px !important;
    }}
    /* Placeholder do input de busca */
    ::placeholder {{
        color: #666666 !important;
        opacity: 1;
    }}
    </style>
""", unsafe_allow_html=True)

# --- CONFIGURAÇÕES GITHUB (Sem alterações) ---
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
REPO_NAME = st.secrets["REPO_NAME"]
FILE_PATH = "dados_remedios.csv"

# --- FUNÇÕES DE DADOS (Sem alterações) ---
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
        repo.update_file(FILE_PATH, "Atualização de estoque via App", csv_buffer.getvalue(), sha)
    else:
        repo.create_file(FILE_PATH, "Criação do estoque inicial via App", csv_buffer.getvalue())

def get_status_info(validade_str):
    try:
        val = datetime.strptime(validade_str, '%Y-%m-%d').date()
        dias = (val - date.today()).days
        if dias < 0: return "Vencido 🚨", "#FEE2E2", "#991B1B"
        if dias <= 30: return "Vence logo ⚠️", "#FEF3C7", "#92400E"
        # Status normal usa o rosa de destaque da paleta
        return "Em dia", COLOR_PALETTE['rosa_destaque'], COLOR_PALETTE['texto_escuro']
    except:
        return "Data inválida", "#F3F4F6", "#374151"

# --- INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

# Fluxo de Inclusão (UX: Botão de ação clara com cor primária Blue Bell)
if st.button("➕ Incluir novo remédio", use_container_width=True, type="primary"):
    st.session_state.show_form = True

if st.session_state.get("show_form"):
    with st.form("add_form", clear_on_submit=True):
        st.subheader("Novo Cadastro")
        nome = st.text_input("Nome do medicamento", placeholder="Ex: Ibuprofeno 600mg")
        col1, col2 = st.columns(2)
        validade = col1.date_input("Data de validade")
        quantidade = col2.number_input("Qtd em estoque", min_value=1)
        motivo = st.selectbox("Para que serve? (Categoria)", list(MOTIVOS_ICONES.keys()))
        
        # Botão de confirmação dentro do formulário
        if st.form_submit_button("Confirmar e Salvar", use_container_width=True):
            new_data = pd.DataFrame([{"nome": nome, "validade": str(validade), "quantidade": int(quantidade), "motivo": motivo}])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df, sha)
            st.session_state.show_form = False
            st.toast("Remédio adicionado com sucesso!", icon="✅")
            st.rerun()

st.divider()

# Busca e Categorização (UX: Encontrar rápido)
busca = st.text_input("🔎 O que você está procurando?", placeholder="Digite o nome do remédio ou princípio ativo...")

# Abas com ícones (UX/UI: Organização visual)
tabs = st.tabs([f"{MOTIVOS_ICONES[m]} {m}" for m in MOTIVOS_ICONES.keys()])

for idx, motivo_nome in enumerate(MOTIVOS_ICONES.keys()):
    with tabs[idx]:
        # Filtra por categoria e busca
        itens = df[df['motivo'] == motivo_nome] if not df.empty else pd.DataFrame()
        if busca:
            itens = itens[itens['nome'].str.contains(busca, case=False, na=False)]
        
        if itens.empty:
            if busca:
                st.warning(f"Nenhum resultado para '{busca}' em {motivo_nome}.")
            else:
                st.info(f"Nenhum remédio cadastrado para '{motivo_nome}'.")
        else:
            for i, r in itens.iterrows():
                status_txt, bg_color, txt_color = get_status_info(r['validade'])
                
                st.markdown(f"""
                    <div class="remedio-card">
                        <div class="nome-remedio">{r['nome']}</div>
                        <div class="info-texto">
                            📦 Estoque: {r['quantidade']} unidades<br>
                            📅 Validade: {datetime.strptime(r['validade'], '%Y-%m-%d').strftime('%d/%m/%Y')}
                        </div>
                        <div class="status-badge" style="background-color: {bg_color}; color: {txt_color};">
                            {status_txt}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Botão de remover (UX Writing: Texto direto e claro)
                if st.button(f"🗑️ Remover do estoque: {r['nome']}", key=f"del_{i}", use_container_width=True):
                    df = df.drop(i)
                    save_data(df, sha)
                    st.toast("Estoque atualizado!", icon="🗑️")
                    st.rerun()
