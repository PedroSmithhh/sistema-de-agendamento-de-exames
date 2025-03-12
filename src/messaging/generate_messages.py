import pandas as pd

def generate_messages(): # Gera mensagens personalizadas para os pacientes com exames de imagem.
    # Carrega o CSV processado
    df = pd.read_csv("data/processed/resultado_processado.csv")
    messages = []
    for _, row in df.iterrows():
        # Só gera mensagem se for exame de imagem
        if row["exame_resultado"] != "Não é exame de imagem":
            mensagem = f"Olá, temos uma boa notícia! Seu exame de {row['exame_resultado']} solicitado pelo Doutor(a) {row['SOLICITANTE']} já está agendado com a gente, e estamos muito felizes em cuidar de você com todo o carinho e a qualidade que você merece. Não deixe para depois, venha fazer seu exame com quem realmente se importa com a sua saúde! Qualquer dúvida, é só nos chamar!"
            messages.append({"telefone": row["TEL"], "mensagem": mensagem, "solicitante": row["SOLICITANTE"]})
    return messages