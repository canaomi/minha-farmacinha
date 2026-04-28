import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date, datetime

# --- CONFIGURAÇÕES E ESTILO ---
st.set_page_config(page_title="Farmacinha de Bolso", layout="centered")

MOTIVOS_ICONES = {
    "Gases": "🎈", "Diarréia": "🚽", "Dor de cabeça": "🤕", 
    "Gripe": "🤧", "Antiinflamatório": "🩹", "Dor de estômago": "🤢", "Outros": "➕"
}

st.markdown("""
    <style>
    .remedio-card { background: #F9FAFB; padding: 18px; border-radius: 16px; border: 1px solid #F3F4F6; margin-bottom: 12px; }
    .nome-remedio { font-size: 1.3rem; font-weight: 800; color: #111827; }
    .status-badge { padding: 4px 10px; border-radius: 8px; font-size: 0.75rem; font-weight: 600; display: inline-block; }
    .mobile-icon { font-size: 1.8rem; margin-right: 12px; }
    @media (min-width: 600px) { .mobile-icon { display: none; } }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS ---
# Certifique-se de configurar a URL nas 'Secrets' do Streamlit Cloud
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="0s")

def get_status_info(validade_str):
    try:
        val = pd.to_datetime(validade_str).date()
        dias = (val - date.today()).days
        if dias < 0: return "Vencido 🚨", "#FEE2E2", "#991B1B"
        if dias <= 30: return "Atenção ⚠️", "#FEF3C7", "#92400E"
        return "Em dia", "#DCFCE7", "#166534"
    except:
        return "Sem data", "#F3F4F6", "#374151"

# --- INTERFACE ---
st.title("💊 Farmacinha de Bolso")

if "show_form" not in st.session_state: st.session_state.show_form = False

if st.button("➕ Incluir remédio", use_container_width=True, type="primary"):
    st.session_state.show_form = True

df = get_data()

# Formulário de Cadastro
if st.session_state.show_form:
    with st.form("form_remedio"):
        nome = st.text_input("Nome do medicamento")
        c1, c2 = st.columns(2)
        validade = c1.date_input("Vencimento", value=date.today())
        quantidade = c2.number_input("Quantidade", min_value=1)
        motivo = st.selectbox("Motivo (Categoria)", list(MOTIVOS_ICONES.keys()))
        
        if st.form_submit_button("Salvar remédio", use_container_width=True):
            new_row = pd.DataFrame([{
                "nome": nome, "validade": validade.isoformat(),
                "quantidade": quantidade, "motivo": motivo,
                "criado_em": datetime.now().isoformat()
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=updated_df, worksheet="Página1")
            st.session_state.show_form = False
            st.toast("Remédio salvo!", icon="✅")
            st.rerun()

# Busca e Listagem
st.divider()
busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...")
tabs = st.tabs(list(MOTIVOS_ICONES.keys()))

for idx, motivo_nome in enumerate(MOTIVOS_ICONES.keys()):
    with tabs[idx]:
        itens = df[df['motivo'] == motivo_nome] if not df.empty else pd.DataFrame()
        if busca:
            itens = itens[itens['nome'].str.contains(busca, case=False, na=False)]
        
        if itens.empty:
            st.info(f"Nenhum remédio em {motivo_nome}.")
        else:
            for i, r in itens.iterrows():
                status_txt, bg_color, txt_color = get_status_info(r['validade'])
                st.markdown(f"""
                    <div class="remedio-card">
                        <div style="display: flex; align-items: center; justify-content: space-between;">
                            <div style="display: flex; align-items: center;">
                                <div class="mobile-icon">{MOTIVOS_ICONES[r['motivo']]}</div>
                                <div>
                                    <div class="nome-remedio">{r['nome']}</div>
                                    <div class="status-badge" style="background-color: {bg_color}; color: {txt_color};">{status_txt}</div>
                                </div>
                            </div>
                            <div style="font-weight: 600;">{r['quantidade']} un</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Excluir", key=f"del_{i}", use_container_width=True):
                    updated_df = df.drop(i)
                    conn.update(data=updated_df)
                    st.toast("Excluído!")
                    st.rerun()
