from twilio.rest import Client
import sqlite3
from datetime import datetime
import os

# Configurações do Twilio (substitua pelos seus dados)
account_sid = "SUA_ACCOUNT_SID"
auth_token = "SEU_AUTH_TOKEN"
twilio_number = "SEU_NUMERO_TWILIO"
client = Client(account_sid, auth_token)

# Cria a pasta db/ se não existir
if not os.path.exists("db"):
    os.makedirs("db")

# Conecta ao banco de dados SQLite (cria o arquivo se não existir)
db_path = "db/envios.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Cria a tabela de envios se não existir
cursor.execute("""
    CREATE TABLE IF NOT EXISTS envios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_envio TEXT,
        telefone TEXT,
        mensagem TEXT,
        status TEXT
    )
""")
conn.commit()

def send_whatsapp_message(telefone, mensagem):
    """Envia uma mensagem via WhatsApp usando a API do Twilio e registra no SQLite."""
    try:
        message = client.messages.create(
            body=mensagem,
            from_=f"whatsapp:{twilio_number}",
            to=f"whatsapp:{telefone}"
        )
        status = "Sucesso"
        print(f"Mensagem para {telefone} enviada: Sim")
    except Exception as e:
        status = f"Falha - Erro: {str(e)}"
        print(f"Erro ao enviar para {telefone}: {e}")

    # Registra o envio no banco de dados
    data_envio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO envios (data_envio, telefone, mensagem, status) VALUES (?, ?, ?, ?)",
        (data_envio, telefone, mensagem, status)
    )
    conn.commit()
    return status.startswith("Sucesso")

def send_all_messages(messages): # Envia todas as mensagens geradas e registra cada envio.
    for idx, msg in enumerate(messages):
        success = send_whatsapp_message(msg["telefone"], msg["mensagem"])
        print(f"Mensagem {idx+1}/{len(messages)} - Enviada: {'Sim' if success else 'Não'}")

# Garante que o banco de dados será fechado quando o script terminar
import atexit
atexit.register(lambda: conn.close())