
import streamlit as st
import sqlite3
import datetime
import random

DB_PATH = "message.db"

# ========== BANCO DE DADOS ==========
def conectar():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def buscar_nome_usuario(conn, usuario):
    cur = conn.cursor()
    cur.execute("SELECT nome FROM usuarios WHERE usuario = ?", (usuario,))
    res = cur.fetchone()
    return res[0] if res else usuario

def buscar_usuario(conn, usuario, senha):
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    return cur.fetchone()

def buscar_leads(conn, responsavel):
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads WHERE responsavel = ?", (responsavel,))
    return cur.fetchall()

def buscar_mensagens(conn, lead_id):
    cur = conn.cursor()
    cur.execute("SELECT autor, mensagem, hora FROM mensagens WHERE lead_id = ?", (lead_id,))
    return cur.fetchall()

def adicionar_mensagem(conn, lead_id, autor, mensagem):
    cur = conn.cursor()
    hora = datetime.datetime.now().strftime("%H:%M")
    cur.execute("INSERT INTO mensagens (lead_id, autor, mensagem, hora) VALUES (?, ?, ?, ?)",
                (lead_id, autor, mensagem, hora))
    conn.commit()

def buscar_dados_lead(conn, lead_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
    return cur.fetchone()

# ========== IA SIMULADA ==========
def gerar_resposta_ia():
    respostas = [
        "Obrigado pela explicação, vou analisar com calma.",
        "Poderia me mandar um resumo por e-mail?",
        "Interessante! Como funciona o suporte de vocês?",
        "Vou discutir com meu time e volto em breve.",
        "Qual seria o próximo passo para avançarmos?"
    ]
    return random.choice(respostas)

# ========== INTERFACE ==========
st.set_page_config("Message V4", layout="wide")
st.markdown("<h1 style='color:#8838ff;'>💬 Message V4 Corrigida</h1>", unsafe_allow_html=True)

conn = conectar()

# ========== SESSION STATE ==========
if "logado" not in st.session_state:
    st.session_state.logado = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "Chat"
if "lead_id" not in st.session_state:
    st.session_state.lead_id = None
if "mensagem_temp" not in st.session_state:
    st.session_state.mensagem_temp = ""

# ========== LOGIN ==========
if not st.session_state.logado:
    st.subheader("Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        usuario = buscar_usuario(conn, usuario_input, senha_input)
        if usuario:
            st.session_state.logado = True
            st.session_state.usuario = usuario_input
            st.rerun()
        else:
            st.error("Credenciais incorretas.")
else:
    usuario = st.session_state.usuario
    st.sidebar.markdown(f"👤 Logado como: **{buscar_nome_usuario(conn, usuario)}**")
    st.sidebar.radio("Menu", ["Chat", "Sair"], key="pagina")

    if st.session_state.pagina == "Sair":
        st.session_state.logado = False
        st.rerun()

    # ========== CHAT ==========
    if st.session_state.pagina == "Chat":
        col1, col2, col3 = st.columns([2, 5, 3])

        # Lista de leads
        with col1:
            st.markdown("### Leads")
            leads = buscar_leads(conn, usuario)
            for lead in leads:
                if st.button(f"{lead[1]} ({lead[2]})"):
                    st.session_state.lead_id = lead[0]
                    st.session_state.mensagem_temp = ""

        # Conversa com lead
        if st.session_state.lead_id:
            lead_id = st.session_state.lead_id
            mensagens = buscar_mensagens(conn, lead_id)
            with col2:
                st.markdown("### Conversa")
                for autor, mensagem, hora in mensagens:
                    alinhamento = "➡️" if autor == usuario else "⬅️"
                    nome_autor = buscar_nome_usuario(conn, autor) if autor != "ia" else "Cliente"
                    st.markdown(f"{alinhamento} **{nome_autor}** ({hora}): {mensagem}")

                def enviar_msg():
                    texto = st.session_state.mensagem_temp.strip()
                    if texto:
                        adicionar_mensagem(conn, lead_id, usuario, texto)
                        st.session_state.mensagem_temp = ""
                        st.rerun()

                        # Simular resposta do cliente após 1 segundo
                        resposta = gerar_resposta_ia()
                        adicionar_mensagem(conn, lead_id, "ia", resposta)

                st.text_input("Digite sua mensagem e pressione Enter", key="mensagem_temp", on_change=enviar_msg)

            # Dados do lead
            with col3:
                dados = buscar_dados_lead(conn, lead_id)
                if dados:
                    st.markdown("### Detalhes do Lead")
                    st.markdown(f"**Nome:** {dados[1]}")
                    st.markdown(f"**Empresa:** {dados[2]}")
                    st.markdown(f"**Canal:** {dados[3]}")
                    st.markdown(f"**Tag:** {dados[4]}")
                    st.markdown(f"**Etapa:** {dados[5]}")
                    st.markdown(f"**Responsável:** {dados[7]}")
                    st.markdown("**Notas:**")
                    st.write(dados[6])
