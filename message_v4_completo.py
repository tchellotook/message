
import streamlit as st
import sqlite3
import pandas as pd
import datetime

DB_PATH = "message.db"

# ======= BANCO =======
def conectar_banco():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def iniciar_tabelas(conn):
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE,
        senha TEXT,
        nome TEXT,
        cargo TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        empresa TEXT,
        canal TEXT,
        tag TEXT,
        etapa TEXT,
        notas TEXT,
        responsavel TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensagens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lead_id INTEGER,
        autor TEXT,
        mensagem TEXT,
        hora TEXT
    )
    """)
    conn.commit()

def seed_usuarios(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO usuarios (usuario, senha, nome, cargo) VALUES (?, ?, ?, ?)", [
            ("duarte", "mundo@123", "Marcelo Duarte", "SDR"),
            ("ana", "1234", "Ana Souza", "Inside Sales"),
            ("lucas", "abcd", "Lucas Mendes", "Supervisor")
        ])
        conn.commit()

# ======= FUNÇÕES =======
def buscar_nome_usuario(conn, usuario):
    c = conn.cursor()
    c.execute("SELECT nome FROM usuarios WHERE usuario = ?", (usuario,))
    r = c.fetchone()
    return r[0] if r else usuario

def buscar_usuario(conn, usuario, senha):
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    return c.fetchone()

def buscar_leads(conn, responsavel=None):
    c = conn.cursor()
    if responsavel:
        c.execute("SELECT * FROM leads WHERE responsavel = ?", (responsavel,))
    else:
        c.execute("SELECT * FROM leads")
    return c.fetchall()

def buscar_mensagens(conn, lead_id):
    c = conn.cursor()
    c.execute("SELECT autor, mensagem, hora FROM mensagens WHERE lead_id = ?", (lead_id,))
    return c.fetchall()

def adicionar_mensagem(conn, lead_id, autor, mensagem):
    hora = datetime.datetime.now().strftime("%H:%M")
    c = conn.cursor()
    c.execute("INSERT INTO mensagens (lead_id, autor, mensagem, hora) VALUES (?, ?, ?, ?)", (lead_id, autor, mensagem, hora))
    conn.commit()

def buscar_usuarios_df(conn):
    return pd.read_sql("SELECT * FROM usuarios", conn)

def buscar_leads_df(conn):
    return pd.read_sql("SELECT * FROM leads", conn)

def atualizar_lead(conn, lead_id, campo, valor):
    c = conn.cursor()
    c.execute(f"UPDATE leads SET {campo} = ? WHERE id = ?", (valor, lead_id))
    conn.commit()

def inserir_lead(conn, nome, empresa, canal, etapa, tag, notas, responsavel):
    c = conn.cursor()
    c.execute(
        "INSERT INTO leads (nome, empresa, canal, etapa, tag, notas, responsavel) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (nome, empresa, canal, etapa, tag, notas, responsavel)
    )
    conn.commit()

def exportar_mensagens(conn, lead_id):
    df = pd.read_sql("SELECT autor, mensagem, hora FROM mensagens WHERE lead_id = ?", conn, params=(lead_id,))
    return df.to_csv(index=False).encode('utf-8')

# ======= INÍCIO DO APP =======
st.set_page_config(page_title="Message V4 Completa", layout="wide")
st.markdown("<h1 style='color:#8838ff;'>💬 Message V4 – Chat + Admin</h1>", unsafe_allow_html=True)

conn = conectar_banco()
iniciar_tabelas(conn)
seed_usuarios(conn)

if "logado" not in st.session_state:
    st.session_state.logado = False
if "pagina" not in st.session_state:
    st.session_state.pagina = "Chat"
if "lead_id" not in st.session_state:
    st.session_state.lead_id = None
if "mensagem_temp" not in st.session_state:
    st.session_state.mensagem_temp = ""

# ======= LOGIN =======
if not st.session_state.logado:
    st.subheader("Login")
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        user = buscar_usuario(conn, usuario_input, senha_input)
        if user:
            st.session_state.logado = True
            st.session_state.usuario = usuario_input
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
else:
    usuario_logado = st.session_state.usuario
    st.sidebar.markdown(f"👤 Logado como: **{buscar_nome_usuario(conn, usuario_logado)}**")
    st.sidebar.radio("Menu", ["Chat", "Admin", "Sair"], key="pagina")

    if st.session_state.pagina == "Sair":
        st.session_state.logado = False
        st.rerun()

    # ======= CHAT =======
    if st.session_state.pagina == "Chat":
        leads = buscar_leads(conn, responsavel=usuario_logado)
        col1, col2 = st.columns([2, 6])
        with col1:
            st.markdown("### Leads")
            for lead in leads:
                if st.button(f"{lead[1]} ({lead[2]})"):
                    st.session_state.lead_id = lead[0]
                    st.session_state.mensagem_temp = ""

        if st.session_state.lead_id:
            with col2:
                nome_lead = [l[1] for l in leads if l[0] == st.session_state.lead_id][0]
                st.markdown(f"### Conversa com {nome_lead}")
                historico = buscar_mensagens(conn, st.session_state.lead_id)
                for autor, mensagem, hora in historico:
                    alinhamento = "➡️" if autor == usuario_logado else "⬅️"
                    st.markdown(f"{alinhamento} **{buscar_nome_usuario(conn, autor)}** ({hora}): {mensagem}")

                def enviar_msg():
                    texto = st.session_state.mensagem_temp
                    if texto.strip():
                        adicionar_mensagem(conn, st.session_state.lead_id, usuario_logado, texto.strip())
                        st.session_state.mensagem_temp = ""
                        st.rerun()

                st.text_input("Digite sua mensagem", key="mensagem_temp", on_change=enviar_msg)
                if st.button("Enviar"):
                    enviar_msg()

    # ======= ADMIN =======
    if st.session_state.pagina == "Admin":
        st.markdown("## ➕ Cadastrar novo lead")
        with st.form("novo_lead"):
            col1, col2, col3 = st.columns(3)
            with col1:
                nome = st.text_input("Nome")
                empresa = st.text_input("Empresa")
                canal = st.selectbox("Canal", ["WhatsApp", "Telegram", "Email"])
            with col2:
                etapa = st.text_input("Etapa")
                tag = st.text_input("Tag")
                notas = st.text_area("Notas")
            with col3:
                usuarios_df = buscar_usuarios_df(conn)
                responsavel = st.selectbox("Responsável", usuarios_df["usuario"].tolist())
            enviar = st.form_submit_button("Cadastrar")
            if enviar:
                inserir_lead(conn, nome, empresa, canal, etapa, tag, notas, responsavel)
                st.success(f"Lead {nome} cadastrado com sucesso!")

        st.markdown("---")
        st.markdown("## 🗂️ Edição de Leads")
        leads_df = buscar_leads_df(conn)

        for _, lead in leads_df.iterrows():
            with st.expander(f"{lead['nome']} – {lead['empresa']}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    novo_tag = st.text_input(f"Tag ({lead['nome']})", value=lead['tag'], key=f"tag_{lead['id']}")
                    atualizar_lead(conn, lead['id'], "tag", novo_tag)
                with col2:
                    nova_etapa = st.text_input(f"Etapa ({lead['nome']})", value=lead['etapa'], key=f"etapa_{lead['id']}")
                    atualizar_lead(conn, lead['id'], "etapa", nova_etapa)
                with col3:
                    novo_resp = st.selectbox(
                        f"Responsável ({lead['nome']})",
                        options=usuarios_df["usuario"].tolist(),
                        index=usuarios_df["usuario"].tolist().index(lead["responsavel"]),
                        key=f"resp_{lead['id']}"
                    )
                    atualizar_lead(conn, lead['id'], "responsavel", novo_resp)
                novas_notas = st.text_area(f"Notas ({lead['nome']})", value=lead['notas'], key=f"notas_{lead['id']}")
                atualizar_lead(conn, lead['id'], "notas", novas_notas)
                st.download_button("⬇️ Exportar conversa", data=exportar_mensagens(conn, lead['id']),
                                   file_name=f"conversa_{lead['nome']}.csv", mime="text/csv")
