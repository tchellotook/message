
import streamlit as st
import datetime

# ========== DADOS SIMULADOS ==========

# Usuários com login
usuarios = {
    "duarte": {"senha": "mundo@123", "nome": "Marcelo Duarte", "cargo": "SDR"},
    "ana": {"senha": "1234", "nome": "Ana Souza", "cargo": "Inside Sales"},
    "lucas": {"senha": "abcd", "nome": "Lucas Mendes", "cargo": "Supervisor"}
}

# Leads com histórico de mensagens
leads = {
    "João Silva": {
        "empresa": "ABC Ltda",
        "canal": "WhatsApp",
        "tag": "Lead Quente",
        "etapa": "Qualificação",
        "notas": "Interessado em pricing",
        "responsavel": "duarte",
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

# ========== CONFIGURAÇÃO STREAMLIT ==========
st.set_page_config(page_title="Message V2", layout="wide")
st.markdown("<h1 style='color:#8838ff;'>💬 Message</h1>", unsafe_allow_html=True)

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
            st.session_state.lead_ativo = list(leads.keys())[0]
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")
else:
    usuario_logado = st.session_state.usuario
    st.success(f"Bem-vindo, {usuarios[usuario_logado]['nome']}!")

    # ========== LAYOUT ==========
    col1, col2, col3 = st.columns([2, 4, 3])

    # --- COLUNA 1: Lista de Leads ---
    with col1:
        st.markdown("### Leads")
        for nome, info in leads.items():
            if st.button(f"{nome} ({info['empresa']})"):
                st.session_state.lead_ativo = nome

    # --- COLUNA 2: Chat ---
    lead = leads[st.session_state.lead_ativo]
    chat = lead["historico"]

    with col2:
        st.markdown(f"### Conversa com {st.session_state.lead_ativo}")
        for msg in chat:
            autor = usuarios[msg["de"]]["nome"] if msg["de"] in usuarios else msg["de"]
            alinhamento = "➡️" if msg["de"] == usuario_logado else "⬅️"
            st.markdown(f"{alinhamento} **{autor}** ({msg['hora']}): {msg['mensagem']}")

        with st.form("mensagem_form"):
            nova_mensagem = st.text_input("Digite sua mensagem")
            resposta_rapida = st.selectbox("Ou use uma resposta rápida:", [""] + respostas_rapidas)
            enviar = st.form_submit_button("Enviar")
            if enviar:
                texto = nova_mensagem if nova_mensagem else resposta_rapida
                if texto:
                    chat.append({
                        "de": usuario_logado,
                        "mensagem": texto,
                        "hora": datetime.datetime.now().strftime("%H:%M")
                    })
                    st.experimental_rerun()

    # --- COLUNA 3: Detalhes do Cliente ---
    with col3:
        st.markdown("### Detalhes do Cliente")
        st.markdown(f"**Nome:** {st.session_state.lead_ativo}")
        st.markdown(f"**Empresa:** {lead['empresa']}")
        st.markdown(f"**Canal:** {lead['canal']}")
        st.markdown(f"**Tag:** `{lead['tag']}`")
        st.markdown(f"**Etapa:** {lead['etapa']}")
        st.markdown(f"**Responsável:** {usuarios[lead['responsavel']]['nome']}")
        st.markdown(f"**Último contato:** Hoje")
        st.markdown("**Notas:**")
        st.write(lead["notas"])

        st.markdown("---")
        novo_responsavel = st.selectbox("Transferir para:", [u for u in usuarios if u != lead["responsavel"]])
        if st.button("Transferir"):
            lead["responsavel"] = novo_responsavel
            st.success(f"Transferido para {usuarios[novo_responsavel]['nome']}")
        if st.button("Exportar conversa (.txt)"):
            texto = ""
            for msg in chat:
                autor = usuarios[msg["de"]]["nome"] if msg["de"] in usuarios else msg["de"]
                texto += f"{autor} ({msg['hora']}): {msg['mensagem']}\n"
            st.download_button("Clique para baixar", texto, file_name=f"{st.session_state.lead_ativo}_conversa.txt")
