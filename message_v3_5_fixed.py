
import streamlit as st
import datetime

# ========== DADOS SIMULADOS ==========

usuarios = {
    "duarte": {"senha": "mundo@123", "nome": "Marcelo Duarte", "cargo": "SDR"},
    "ana": {"senha": "1234", "nome": "Ana Souza", "cargo": "Inside Sales"},
    "lucas": {"senha": "abcd", "nome": "Lucas Mendes", "cargo": "Supervisor"}
}

leads = {
    "João Silva": {
        "empresa": "ABC Ltda",
        "canal": "WhatsApp",
        "tag": "Lead Quente",
        "etapa": "Qualificação",
        "notas": "Interessado em pricing",
        "responsavel": "duarte",
        "ultimo_contato": "Hoje",
        "historico": [
            {"de": "João Silva", "mensagem": "Olá, gostaria de saber mais sobre o produto.", "hora": "10:15"},
            {"de": "duarte", "mensagem": "Olá, tudo bem? Posso te ajudar com isso!", "hora": "10:17"},
            {"de": "João Silva", "mensagem": "Gostaria de informações sobre preços.", "hora": "10:18"}
        ]
    },
    "Maria Oliveira": {
        "empresa": "XYZ Corp",
        "canal": "Telegram",
        "tag": "Aguardando Retorno",
        "etapa": "Proposta Enviada",
        "notas": "Ficou de responder até sexta",
        "responsavel": "ana",
        "ultimo_contato": "Ontem",
        "historico": [
            {"de": "ana", "mensagem": "Bom dia, Maria! Enviei a proposta por e-mail.", "hora": "11:00"},
            {"de": "Maria Oliveira", "mensagem": "Ok, vou olhar e te dou um retorno.", "hora": "11:02"}
        ]
    }
}

respostas_rapidas = [
    "Olá, tudo bem? Como posso te ajudar?",
    "Entendi! Estarei verificando isso para você.",
    "Perfeito! Podemos agendar uma demonstração?",
    "Obrigado pelo contato. Até mais!"
]

# ========== CONFIGURAÇÃO ==========
st.set_page_config(page_title="Message V3.5.1", layout="wide")
st.markdown("<h1 style='color:#8838ff;'>💬 Message V3.5.1</h1>", unsafe_allow_html=True)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "Chat"
if "lead_ativo" not in st.session_state:
    st.session_state.lead_ativo = list(leads.keys())[0]
if "mensagem_temp" not in st.session_state:
    st.session_state.mensagem_temp = ""

# ========== LOGIN ==========
if not st.session_state.logado:
    st.subheader("Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario_input in usuarios and usuarios[usuario_input]["senha"] == senha_input:
            st.session_state.logado = True
            st.session_state.usuario = usuario_input
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
else:
    usuario_logado = st.session_state.usuario
    st.sidebar.markdown(f"👤 Logado como: **{usuarios[usuario_logado]['nome']}**")
    st.sidebar.markdown("---")
    st.sidebar.radio("Menu", ["Chat", "Admin", "Sair"], key="pagina")

    if st.session_state.pagina == "Sair":
        st.session_state.logado = False
        st.rerun()

    # CHAT
    if st.session_state.pagina == "Chat":
        col1, col2, col3 = st.columns([2, 4, 3])

        with col1:
            st.markdown("### Leads")
            for nome, info in leads.items():
                if st.button(f"{nome} ({info['empresa']})"):
                    st.session_state.lead_ativo = nome
                    st.session_state.mensagem_temp = ""

        lead = leads[st.session_state.lead_ativo]
        chat = lead["historico"]

        with col2:
            st.markdown(f"### Conversa com {st.session_state.lead_ativo}")
            for msg in chat:
                autor = usuarios[msg["de"]]["nome"] if msg["de"] in usuarios else msg["de"]
                alinhamento = "➡️" if msg["de"] == usuario_logado else "⬅️"
                st.markdown(f"{alinhamento} **{autor}** ({msg['hora']}): {msg['mensagem']}")

            def enviar_mensagem():
                texto = st.session_state.mensagem_temp
                if texto.strip():
                    chat.append({
                        "de": usuario_logado,
                        "mensagem": texto.strip(),
                        "hora": datetime.datetime.now().strftime("%H:%M")
                    })
                    st.session_state.mensagem_temp = ""
                    st.rerun()

            st.text_input("Digite sua mensagem", key="mensagem_temp", on_change=enviar_mensagem)
            if st.button("Enviar"):
                enviar_mensagem()

            resposta_rapida = st.selectbox("Ou use uma resposta rápida:", [""] + respostas_rapidas)
            if st.button("Enviar resposta rápida"):
                if resposta_rapida:
                    chat.append({
                        "de": usuario_logado,
                        "mensagem": resposta_rapida,
                        "hora": datetime.datetime.now().strftime("%H:%M")
                    })
                    st.rerun()

        with col3:
            st.markdown("### Detalhes do Cliente")
            st.markdown(f"**Nome:** {st.session_state.lead_ativo}")
            st.markdown(f"**Empresa:** {lead['empresa']}")
            st.markdown(f"**Canal:** {lead['canal']}")
            st.markdown(f"**Tag:** `{lead['tag']}`")
            st.markdown(f"**Etapa:** {lead['etapa']}")
            st.markdown(f"**Responsável:** {usuarios[lead['responsavel']]['nome']}")
            st.markdown(f"**Último contato:** {lead['ultimo_contato']}")
            st.markdown("**Notas:**")
            st.write(lead["notas"])
            st.markdown("---")

    # ADMIN
    if st.session_state.pagina == "Admin":
        st.markdown("### 🎛️ Painel de Administração")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            filtro_canal = st.selectbox("Filtrar por Canal:", ["Todos", "WhatsApp", "Telegram"])
        with col_f2:
            filtro_etapa = st.selectbox("Filtrar por Etapa:", ["Todas"] + list(set(l["etapa"] for l in leads.values())))
        with col_f3:
            filtro_resp = st.selectbox("Filtrar por Responsável:", ["Todos"] + list(usuarios.keys()))

        st.markdown("---")

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
