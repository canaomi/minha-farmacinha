import streamlit as st
import pandas as pd
from github import Github
import io
import google.generativeai as genai
from datetime import date, datetime

# --- 1. CONFIGURAÇÕES E IA ---
st.set_page_config(page_title="Farmacinha", layout="centered")

# Configuração do Gemini para a função Bula
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.warning("IA desativada: Adicione GEMINI_API_KEY aos Secrets.")

# --- 2. PALETA E ESTILO PREMIUM (iPhone 16 Pro Style) ---
PALETTE = {
    "fundo": "#FDE2E4",        # Rosa Pastel Suave
    "botao_fab": "#FB6F92",    # Rosa Vibrante
    "card": "#FFFFFF",         # Branco Puro
    "busca": "rgba(255, 255, 255, 0.5)", # Branco 50% Opacidade
    "texto": "#000000",        # Preto Puro
    "texto_sub": "#4A4A4A"     # Cinza para subtextos
}

st.markdown(f"""
    <style>
    /* Configuração Global */
    .stApp {{ background-color: {PALETTE['fundo']}; color: {PALETTE['texto']}; }}
    
    /* Barra de Busca Harmônica */
    .stTextInput > div > div > input {{
        background-color: {PALETTE['busca']} !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
        border-radius: 12px !important;
        color: {PALETTE['texto']} !important;
    }}

    /* Card Premium com Soft Shadows */
    .remedio-card {{
        background-color: {PALETTE['card']};
        padding: 20px;
        border-radius: 20px;
        margin-bottom: 16px;
        position: relative;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255,255,255,0.3);
    }}

    /* Título Seção (Peso Menor) */
    .sub-titulo {{
        font-weight: 400;
        font-size: 1.1rem;
        margin: 20px 0 10px 0;
        color: {PALETTE['texto']};
    }}

    /* Estilo Pills para Abas */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
        display: flex;
        overflow-x: auto;
        padding-bottom: 10px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: rgba(255,255,255,0.4) !important;
        border-radius: 50px !important;
        padding: 8px 20px !important;
        color: {PALETTE['texto']} !important;
        border: none !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PALETTE['botao_fab']} !important;
        color: white !important;
    }}

    /* Floating Action Button (FAB) */
    .fab-container {{
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 1000;
    }}
    
    /* Ícones e Textos */
    .nome-remedio {{ font-weight: 800; font-size: 1.1rem; margin-bottom: 4px; padding-right: 30px; }}
    .cat-label {{ color: {PALETTE['texto_sub']}; font-size: 0.75rem; text-transform: uppercase; font-weight: 600; }}
    
    /* Ajustes Mobile vs Web */
    @media (max-width: 768px) {{
        .web-only {{ display: none; }}
    }}
    @media (min-width: 769px) {{
        .mobile-only {{ display: none; }}
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. LÓGICA DE DADOS (GITHUB) ---
def load_data():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_NAME"])
        content = repo.get_contents("dados_remedios.csv")
        df = pd.read_csv(io.StringIO(content.decoded_content.decode()))
        return df, content.sha
    except:
        return pd.DataFrame(columns=["nome", "validade", "quantidade", "motivo"]), None

def save_data(df, sha):
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
    csv_data = df.to_csv(index=False)
    if sha: repo.update_file("dados_remedios.csv", "Update", csv_data, sha)
    else: repo.create_file("dados_remedios.csv", "Initial", csv_data)

# --- 4. INTERFACE ---
st.title("💊 Farmacinha de Bolso")

df, sha = load_data()

# Campo de Busca (Fundo harmônico)
busca = st.text_input("", placeholder="🔍 Qual remédio você procura?")

# Subtítulo com peso menor
st.markdown('<p class="sub-titulo">Lista de Remédios</p>', unsafe_allow_html=True)

# Categorias em Pills
categorias = ["Gases", "Diarréia", "Dor de cabeça", "Gripe", "Antiinflamatório", "Dor de estômago", "Outros"]
tabs = st.tabs(categorias)

for idx, cat_name in enumerate(categorias):
    with tabs[idx]:
        subset = df[df['motivo'] == cat_name] if not df.empty else pd.DataFrame()
        if busca: subset = subset[subset['nome'].str.contains(busca, case=False, na=False)]
        
        if subset.empty:
            st.info(f"Nenhum remédio em {cat_name}.")
        else:
            for i, r in subset.iterrows():
                # Lógica de Status
                val_dt = datetime.strptime(r['validade'], '%Y-%m-%d').date()
                dias = (val_dt - date.today()).days
                status_color = "#991B1B" if dias < 0 else ("#92400E" if dias <= 30 else "#166534")
                status_txt = "Vencido" if dias < 0 else ("Atenção" if dias <= 30 else "Em dia")

                # HTML do Card
                st.markdown(f"""
                    <div class="remedio-card">
                        <div class="nome-remedio">{r['nome']}</div>
                        <div class="cat-label">{r['motivo']}</div>
                        <div style="color: {PALETTE['texto_sub']}; font-size: 0.85rem; margin-top: 5px;">
                            📦 {r['quantidade']} un | 📅 {val_dt.strftime('%d/%m/%Y')}
                        </div>
                        <div style="color: {status_color}; font-size: 0.75rem; font-weight: 700; margin-top: 4px;">
                            {status_txt}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Botões de Ação dentro do Card (Grid para Mobile)
                col_b1, col_b2, col_b3 = st.columns([1, 1, 0.5])
                
                # Função Bula via AI
                with col_b1:
                    label_bula = "📖 Bula" # Fallback
                    if st.button(f"📖 Bula", key=f"bula_{i}", help="Consultar IA"):
                        with st.chat_message("assistant"):
                            with st.spinner("IA consultando bula..."):
                                prompt = f"Resuma a bula de {r['nome']} para um paciente. Use: 1. Para que serve, 2. Como tomar, 3. Alertas."
                                res = model.generate_content(prompt)
                                st.write(res.text)
                                st.caption("Informação gerada por IA. Não substitui consulta médica.")

                # Ícone Lixeira (Discreto)
                with col_b3:
                    if st.button("🗑️", key=f"del_{i}", help="Excluir"):
                        df = df.drop(i)
                        save_data(df, sha)
                        st.rerun()

# --- 5. FLOATING ACTION BUTTON (FAB) ---
# Em Streamlit, o FAB é injetado via CSS no botão fixo
st.markdown('<div class="fab-container">', unsafe_allow_html=True)
if st.button("＋", key="fab_incluir", help="Incluir novo remédio"):
    st.session_state.show_form = True
st.markdown('</div>', unsafe_allow_html=True)

# Estilo específico para o FAB (Botão Circular)
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div:last-child button {
        border-radius: 50% !important;
        width: 60px !important;
        height: 60px !important;
        background-color: #FB6F92 !important;
        color: white !important;
        font-size: 30px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        border: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# Formulário Suspenso (Modo Incluir)
if st.session_state.get("show_form"):
    with st.expander("📝 Cadastrar Medicamento", expanded=True):
        with st.form("form_add", clear_on_submit=True):
            nome = st.text_input("Nome")
            c1, c2 = st.columns(2)
            val = c1.date_input("Vencimento")
            qtd = c2.number_input("Qtd", min_value=1)
            cat = st.selectbox("Categoria", categorias)
            if st.form_submit_button("Salvar"):
                new_item = pd.DataFrame([{"nome": nome, "validade": str(val), "quantidade": int(qtd), "motivo": cat}])
                df = pd.concat([df, new_item], ignore_index=True)
                save_data(df, sha)
                st.session_state.show_form = False
                st.rerun()
