import sqlite3
from datetime import date, datetime
import streamlit as st

# --- CONFIGURAÇÕES E DICIONÁRIOS ---
DB_PATH = "estoque_remedios.db"
MOTIVOS_ICONES = {
    "Gases": "🎈",
    "Diarréia": "🚽",
    "Dor de cabeça": "🤕",
    "Gripe": "🤧",
    "Antiinflamatório": "🩹",
    "Dor de estômago": "🤢",
    "Outros": "➕"
}

# --- BACKEND: FUNÇÕES DE BANCO DE DADOS ---
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS remedios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            validade TEXT NOT NULL,
            quantidade INTEGER NOT NULL DEFAULT 1,
            motivo TEXT NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def salvar_remedio(id_remedio, nome, validade, quantidade, motivo):
    conn = get_connection()
    if id_remedio: # Update
        conn.execute("UPDATE remedios SET nome=?, validade=?, quantidade=?, motivo=? WHERE id=?",
                     (nome.strip(), validade.isoformat(), quantidade, motivo, id_remedio))
    else: # Insert
        conn.execute("INSERT INTO remedios (nome, validade, quantidade, motivo, criado_em) VALUES (?, ?, ?, ?, ?)",
                     (nome.strip(), validade.isoformat(), quantidade, motivo, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def delete_remedio(remedio_id):
    conn = get_connection()
    conn.execute("DELETE FROM remedios WHERE id = ?", (remedio_id,))
    conn.commit()
    conn.close()

def list_remedios():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM remedios ORDER BY validade ASC").fetchall()
    conn.close()
    return rows

# --- UI: ESTILIZAÇÃO CSS CUSTOMIZADA ---
def apply_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
        .stApp { background: #FFFFFF; }
        .remedio-card {
            background: #F9FAFB;
            padding: 18px;
            border-radius: 16px;
            border: 1px solid #F3F4F6;
            margin-bottom: 12px;
        }
        .nome-remedio { font-size: 1.3rem; font-weight: 800; color: #111827; margin-bottom: 4px; }
        .vencimento-texto { font-size: 0.9rem; color: #6B7280; margin-bottom: 8px; }
        .status-badge {
            padding: 4px 10px;
            border-radius: 8px;
            font-size: 0.75rem;
            font-weight: 600;
            display: inline-block;
        }
        .qtd-texto { font-size: 1rem; font-weight: 600; color: #374151; }
        .mobile-icon { font-size: 1.8rem; margin-right: 12px; }
        /* Esconde ícone em telas grandes, mostra em mobile */
        @media (min-width: 600px) { .mobile-icon { display: none; } }
        </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE STATUS ---
def get_status_info(validade_iso):
    try:
        val = datetime.strptime(validade_iso, "%Y-%m-%d").date()
        dias = (val - date.today()).days
        if dias < 0: return "Vencido 🚨", "#FEE2E2", "#991B1B"
        if dias <= 30: return "Atenção ⚠️", "#FEF3C7", "#92400E"
        return "Em dia", "#DCFCE7", "#166534"
    except:
        return "Sem data", "#F3F4F6", "#374151"

# --- MAIN APP ---
def main():
    apply_custom_css()
    init_db()

    if "edit_id" not in st.session_state: st.session_state.edit_id = None
    if "show_form" not in st.session_state: st.session_state.show_form = False

    st.title("💊 Farmacinha de Bolso")

    # Botão Incluir
    if not st.session_state.show_form:
        if st.button("➕ Incluir remédio", use_container_width=True, type="primary"):
            st.session_state.show_form = True
            st.session_state.edit_id = None
            st.rerun()

    # Formulário de Cadastro/Edição
    if st.session_state.show_form:
        titulo_form = "Editar medicamento" if st.session_state.edit_id else "Incluir remédio"
        st.subheader(titulo_form)
        
        # Se for edição, busca dados atuais
        default_nome, default_val, default_qtd, default_mot = "", date.today(), 1, "Gases"
        if st.session_state.edit_id:
            conn = get_connection()
            r = conn.execute("SELECT * FROM remedios WHERE id=?", (st.session_state.edit_id,)).fetchone()
            default_nome, default_val, default_qtd, default_mot = r['nome'], datetime.strptime(r['validade'], "%Y-%m-%d").date(), r['quantidade'], r['motivo']
            conn.close()

        with st.form("form_remedio"):
            nome = st.text_input("Nome do medicamento", value=default_nome)
            c1, c2 = st.columns(2)
            validade = c1.date_input("Vencimento", value=default_val, format="DD/MM/YYYY")
            quantidade = c2.number_input("Quantidade", min_value=1, value=default_qtd)
            motivo = st.selectbox("Motivo (Categoria)", list(MOTIVOS_ICONES.keys()), index=list(MOTIVOS_ICONES.keys()).index(default_mot))
            
            col_b1, col_b2 = st.columns(2)
            if col_b1.form_submit_button("Salvar remédio", use_container_width=True):
                if nome:
                    salvar_remedio(st.session_state.edit_id, nome, validade, quantidade, motivo)
                    st.session_state.show_form = False
                    st.toast("Remédio salvo!", icon="✅")
                    st.rerun()
            if col_b2.form_submit_button("Cancelar", use_container_width=True):
                st.session_state.show_form = False
                st.rerun()

    # Busca e Filtros
    st.divider()
    busca = st.text_input("Qual remédio você procura?", placeholder="Digite o nome...", label_visibility="visible")
    
    tabs = st.tabs(list(MOTIVOS_ICONES.keys()))
    
    remedios = list_remedios()

    for idx, motivo_nome in enumerate(MOTIVOS_ICONES.keys()):
        with tabs[idx]:
            itens = [r for r in remedios if r['motivo'] == motivo_nome]
            if busca:
                itens = [r for r in itens if busca.lower() in r['nome'].lower()]
            
            if not itens:
                st.info(f"Nenhum remédio em {motivo_nome}.")
            else:
                for r in itens:
                    status_txt, bg_color, txt_color = get_status_info(r['validade'])
                    data_pt = datetime.strptime(r['validade'], "%Y-%m-%d").strftime("%d/%m/%Y")
                    
                    # Card UI
                    st.markdown(f"""
                        <div class="remedio-card">
                            <div style="display: flex; align-items: center; justify-content: space-between;">
                                <div style="display: flex; align-items: center;">
                                    <div class="mobile-icon">{MOTIVOS_ICONES[r['motivo']]}</div>
                                    <div>
                                        <div class="nome-remedio">{r['nome']}</div>
                                        <div class="vencimento-texto">Vence em: {data_pt}</div>
                                        <div class="status-badge" style="background-color: {bg_color}; color: {txt_color};">{status_txt}</div>
                                    </div>
                                </div>
                                <div class="qtd-texto">{r['quantidade']} un</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Ações (Alinhamento Horizontal Corrigido)
                    btn_col1, btn_col2, btn_col3 = st.columns([1, 0.5, 0.5])
                    with btn_col1:
                        if st.button("Bula", key=f"bula_{r['id']}", use_container_width=True):
                            st.toast(f"Consultando bula de {r['nome']}...", icon="📖")
                    with btn_col2:
                        if st.button("✏️", key=f"edit_{r['id']}", use_container_width=True, help="Editar"):
                            st.session_state.edit_id = r['id']
                            st.session_state.show_form = True
                            st.rerun()
                    with btn_col3:
                        if st.button("🗑️", key=f"del_{r['id']}", use_container_width=True, help="Excluir"):
                            delete_remedio(r['id'])
                            st.toast("Remédio excluído com sucesso.", icon="🗑️")
                            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()