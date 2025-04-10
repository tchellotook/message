
import streamlit as st
import datetime

# Dados simulados
leads = {
    "João Silva": {
        "empresa": "ABC Ltda",
        "canal": "WhatsApp",
        "tag": "Lead Quente",
        "etapa": "Qualificação",
        "historico": [
            {"de": "João Silva", "mensagem": "Olá, gostaria de saber mais sobre o produto.", "hora": "10:15"},
            {"de": "Você", "mensagem": "Olá, tudo bem? Posso te ajudar com isso!", "hora": "10:17"},
            {"de": "João Silva", "mensagem": "Gostaria de informações sobre preços.", "hora": "10:18"}
        ],
        "notas": "Interessado em pricing"
    }
}

usuarios = ["Você", "Ana Souza", "Lucas Mendes"]

respostas_rapidas = [
    "Olá, tudo bem? Como posso te ajudar?",
    "Entendi! Estarei verificando isso para você.",
    "Perfeito! Podemos agendar uma demonstração?",
    "Obrigado pelo contato. Até mais!"
]

# Interface Streamlit
st.set_page_config(page_title="Message", layout="wide")

st.markdown(
    "<h1 style='color:#8838ff; font-size:40px;'>💬 Message</h1>",
    unsafe_allow_html=True
)

st.sidebar.title("Painel do Usuário")
usuario_atual = st.sidebar.selectbox("Logado como:", usuarios)

# Layout principal
col1, col2, col3 = st.columns([2, 4, 3])

# Coluna 1 – Lista de Leads
with col1:
    st.markdown("### Leads")
    for nome in leads:
        st.button(nome)

# Coluna 2 – Chat
lead_selecionado = list(leads.keys())[0]
chat = leads[lead_selecionado]["historico"]

with col2:
    st.markdown(f"### Conversa com {lead_selecionado}")
    for msg in chat:
        alinhamento = "➡️" if msg["de"] == "Você" else "⬅️"
        st.markdown(f"{alinhamento} **{msg['de']}** ({msg['hora']}): {msg['mensagem']}")

    with st.form("mensagem_form"):
        nova_mensagem = st.text_input("Digite sua mensagem")
        resposta_rapida = st.selectbox("Ou use uma resposta rápida:", [""] + respostas_rapidas)
        enviar = st.form_submit_button("Enviar")

        if enviar:
            texto = nova_mensagem if nova_mensagem else resposta_rapida
            if texto:
                chat.append({"de": "Você", "mensagem": texto, "hora": datetime.datetime.now().strftime("%H:%M")})
                st.experimental_rerun()

# Coluna 3 – Detalhes do Cliente
with col3:
    lead = leads[lead_selecionado]
    st.markdown("### Detalhes do Cliente")
    st.markdown(f"**Nome:** {lead_selecionado}")
    st.markdown(f"**Empresa:** {lead['empresa']}")
    st.markdown(f"**Canal:** {lead['canal']}")
    st.markdown(f"**Tag:** `{lead['tag']}`")
    st.markdown(f"**Etapa:** {lead['etapa']}")
    st.markdown(f"**Último contato:** Hoje")
    st.markdown("**Notas:**")
    st.write(lead["notas"])

    st.markdown("---")
    st.button("Transferir")
    st.button("Encerrar")
    st.button("Ver CRM")
