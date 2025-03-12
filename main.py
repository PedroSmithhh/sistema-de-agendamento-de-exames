from src.data.process_data import process_data
from src.messaging.generate_messages import generate_messages
from src.messaging.send_messages import send_all_messages
import time

if __name__ == "__main__":
    # Marca o início do tempo
    start_time = time.time()
    
    # Processa todos os dados e gera o CSV completo
    print("Processando todos os dados...")
    df_processed = process_data()
    print(f"Processamento concluído. Total de linhas no CSV: {len(df_processed)}")
    df_processed.to_csv("data/processed/resultado_processado.csv", index=False)
    
    # Gera as mensagens personalizadas
    print("Gerando mensagens...")
    messages = generate_messages()
    print(f"Total de mensagens geradas: {len(messages)}")
    
    # Limita os disparos a 100 mensagens para teste
    max_messages = 100
    if len(messages) > max_messages:
        messages = messages[:max_messages]
        print(f"Limitando envio a {max_messages} mensagens.")
    else:
        print(f"Enviando todas as {len(messages)} mensagens.")
    
    # Dispara as mensagens
    print("Enviando mensagens...")
    send_all_messages(messages)
    
    # Marca o fim do tempo e exibe o total
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Tempo total de execução: {total_time:.2f} segundos ({total_time/60:.2f} minutos)")