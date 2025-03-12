import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
#from google.cloud import storage

# Inicializa o cliente do Google Cloud Storage (GCS)
#storage_client = storage.Client()
#bucket = storage_client.bucket("seu-bucket-exames")  # Substitua por seu bucket

class MonitorCSV(FileSystemEventHandler):

    def __init__(self):
        # Conjunto para rastrear arquivos já processados
        self.processed_files = set()

    def on_modified(self, event):
        # Verifica se o arquivo modificado é um CSV
        if event.src_path.endswith(".csv"):

            # Normaliza o caminho para evitar duplicatas (ex.: diferenças de barra)
            file_path = os.path.normpath(event.src_path)

            # Verifica se o arquivo já foi processado
            if file_path not in self.processed_files:
                print(f"Novo CSV detectado: {file_path}, rodando main.py...")
                
                # Executa o script principal (main.py)
                subprocess.run(["python", "main.py"])
                
                # Após a execução, envia o arquivo processado para o GCS
                #self.upload_to_gcs(file_path)
                
                # Marca o arquivo como processado
                self.processed_files.add(file_path)

                # Reexibe a mensagem de monitoramento
                print(f"🛠️ Monitorando a pasta {os.path.join('data', 'raw')}...")
            
            # Após a execução, envia o arquivo processado para o GCS
            #self.upload_to_gcs(event.src_path)

    #def upload_to_gcs(self, file_path):
        # Envia o arquivo CSV original para o GCS (pasta raw/)
        #blob = bucket.blob(f"raw/{os.path.basename(file_path)}")
        #blob.upload_from_filename(file_path)
        #print(f"Arquivo {file_path} enviado para GCS na pasta raw/.")

        # Envia o arquivo processado (resultado_processado.csv) para o GCS (processed/)
        #processed_file = os.path.join("data", "processed", "resultado_processado.csv")
        #if os.path.exists(processed_file):
            #processed_blob = bucket.blob(f"processed/resultado_processado.csv")
            #processed_blob.upload_from_filename(processed_file)
            #print(f"Arquivo processado {processed_file} enviado para GCS na pasta processed/.")
        #else:
            #print(f"Arquivo processado {processed_file} não encontrado.")

if __name__ == "__main__":
    # Caminho da pasta a ser monitorada
    caminho_pasta = os.path.join("data", "raw")  # Ajustado para compatibilidade cruzada
    event_handler = MonitorCSV()
    observer = Observer()
    observer.schedule(event_handler, caminho_pasta, recursive=False)
    
    print(f"🛠️ Monitorando a pasta {caminho_pasta}...")
    observer.start()

    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()