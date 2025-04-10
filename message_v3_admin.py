
import streamlit as st
import datetime

# ========== DADOS SIMULADOS ==========

# Usuários
usuarios = {
    "duarte": {"senha": "mundo@123", "nome": "Marcelo Duarte", "cargo": "SDR"},
    "ana": {"senha": "1234", "nome": "Ana Souza", "cargo": "Inside Sales"},
    "lucas": {"senha": "abcd", "nome": "Lucas Mendes", "cargo": "Supervisor"}
}

# Leads
leads = {
    "João Silva": {
        "empresa": "ABC Ltda",
        "canal": "WhatsApp",
        "tag": "Lead Quente",
        "etapa": "Qualificação",
        "notas": "Interessado em pricing",
        "responsavel": "duarte",
        "ultimo_contato": "Hoje"
    },
    "Maria Oliveira": {
        "empresa": "XYZ Corp",
        "canal": "Telegram",
        "tag": "Aguardando Retorno",
        "etapa": "Proposta Enviada",
        "notas": "Ficou de responder até sexta",
        "responsavel": "ana",
        "ultimo_contato": "Ontem"
    }
}

# Configuração
st.set_page_config(page_title="Message V3", layout="wide")
st.markdown("<h1 style='color:#8838ff;'>💬 Message V3 – Admin Panel</h1>", unsafe_allow_html=True)

# ========== LOGIN ==========
if "logado" not in st.session_state:
    st.session_state.logado = False

if not st.session_state.logado:
    st.subheader("Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario_input in usuarios and usuarios[usuario_input]["senha"] == senha_input:
            st.session_state.logado = True
            st.session_state.usuario = usuario_input
            st.success(f"Bem-vindo, {usuarios[usuario_input]['nome']}!")
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# ========== ADMIN PANEL ==========
if st.session_state.logado:
    usuario_logado = st.session_state.usuario

    st.markdown("### 🎛️ Painel de Administração")

    # Filtros
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        filtro_canal = st.selectbox("Filtrar por Canal:", ["Todos", "WhatsApp", "Telegram"])
    with col_f2:
        filtro_etapa = st.selectbox("Filtrar por Etapa:", ["Todas"] + list(set(l["etapa"] for l in leads.values())))
    with col_f3:
        filtro_resp = st.selectbox("Filtrar por Responsável:", ["Todos"] + list(usuarios.keys()))

    st.markdown("---")

    # Lista de leads com filtros
    for nome, dados in leads.items():
        if (
            (filtro_canal == "Todos" or dados["canal"] == filtro_canal) and
            (filtro_etapa == "Todas" or dados["etapa"] == filtro_etapa) and
            (filtro_resp == "Todos" or dados["responsavel"] == filtro_resp)
        ):
            with st.expander(f"👤 {nome} – {dados['empresa']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    dados["tag"] = st.text_input(f"Tag – {nome}", value=dados["tag"], key=f"tag_{nome}")
                with col2:
                    dados["etapa"] = st.text_input(f"Etapa – {nome}", value=dados["etapa"], key=f"etapa_{nome}")
                with col3:
                    dados["responsavel"] = st.selectbox(
                        f"Responsável – {nome}",
                        options=list(usuarios.keys()),
                        index=list(usuarios.keys()).index(dados["responsavel"]),
                        key=f"resp_{nome}"
                    )
                dados["notas"] = st.text_area(f"Notas – {nome}", value=dados["notas"], key=f"notas_{nome}")
                st.markdown(f"📞 Último Contato: **{dados['ultimo_contato']}**")
                st.success("Alterações salvas automaticamente (modo simulado)")
