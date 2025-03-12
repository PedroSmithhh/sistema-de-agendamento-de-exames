from google.cloud import storage
import functions_framework
import subprocess
import os

# Inicializa o cliente do Google Cloud Storage
storage_client = storage.Client()

@functions_framework.cloud_event
def processar_csv(cloud_event):
    # Identificar o arquivo e o bucket de origem
    bucket_name = cloud_event.data["bucket"] # Nome do bucket
    file_name = cloud_event.data["name"]  # Nome do arquivo enviado

    print(f"Novo arquivo detectado: {file_name} no bucket {bucket_name}")

    # Criar diretórios temporários se não existirem
    raw_dir = "/tmp/data/raw/"
    processed_dir = "/tmp/data/processed/"
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(processed_dir, exist_ok=True)

    # Caminho local para salvar o arquivo
    raw_path = os.path.join(raw_dir, file_name)

    # Baixar o arquivo do GCS para a pasta temporária "data/raw/"
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    blob.download_to_filename(raw_path)

    print(f"Arquivo baixado para {raw_path}")

    # Executar `main.py` para processar o arquivo
    try:
        subprocess.run(["python", "main.py"], check=True)
        print("`main.py` executado com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar `main.py`: {e}")
        return

    # Verificar se o CSV processado foi gerado (busca resultado_processado.csv)
    processed_file_path = os.path.join(processed_dir, "resultado_processado.csv")

    if not os.path.exists(processed_file_path):
        print(f"O arquivo processado {processed_file_path} não foi encontrado.")
        return

    print(f"Arquivo processado encontrado: {processed_file_path}, enviando para GCS...")

    # Enviar o arquivo processado para "processed/" no GCS
    processed_blob = bucket.blob(f"processed/resultado_processado.csv")
    processed_blob.upload_from_filename(processed_file_path)

    print(f"Arquivo processado enviado para GCS: processed/resultado_processado.csv")

    # Limpeza: remover os arquivos locais para organização
    os.remove(raw_path)
    os.remove(processed_file_path)

    print("Arquivos locais removidos com sucesso.")