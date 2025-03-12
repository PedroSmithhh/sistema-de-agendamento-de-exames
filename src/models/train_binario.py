from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.utils import resample
from collections import Counter
import pandas as pd

def is_exame_imagem(texto):
    # Palavras chaves de exames de imagem
    exames_imagem = ["tomografia ", "tc ", "ct ", "ressonância magnética ", "rnm ", "rm ", "mri ", "ultrassom ", "us ", "ecografia ", "usg ", "radiografia ", "rx ", "raio x ", "eletrocardiograma ", "ecg ", "densitometria ", "mamografia "]
    texto_lower = texto.lower()
    # Verifica se o texto obedece as regras para ser um exame de imagem
    for exame in exames_imagem:
        if exame in texto_lower and not any(med in texto_lower for med in ["furosemida ", "uso oral ", "uso ", "uso interno ", "obstipante ", "hemograma ", "uso nasal ", "uso inalatorio "]):
            return 1 # Sim
    return 0 # Não

def balance_data(dados):
    # Filtra dados com texto válido e converte para string
    dados_validos = []
    for d in dados:
        texto = str(d["texto"]) if pd.notna(d["texto"]) else ""  # Converte para string e substitui NaN por ""
        if texto:  # Só adiciona se o texto não for vazio
            dados_validos.append({"texto": texto, "label": is_exame_imagem(texto)})
    
    dados_binarios = dados_validos
    print(f"Total de entradas válidas após filtragem: {len(dados_binarios)}")
    
    dados_sim = [d for d in dados_binarios if d["label"] == 1]
    dados_nao = [d for d in dados_binarios if d["label"] == 0]
    if len(dados_nao) >= len(dados_sim):
        dados_nao_reduzidos = resample(dados_nao, replace=False, n_samples=len(dados_sim), random_state=42)
        return dados_sim + dados_nao_reduzidos
    else:
        dados_sim_aumentados = resample(dados_sim, replace=True, n_samples=len(dados_nao), random_state=42)
        return dados_sim_aumentados + dados_nao

def train_binario(dados, output_dir="./models/binario"):
    # Carrega o tokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")
    
    # Balanceia os dados
    dados_balanceados = balance_data(dados)
    print(f"Total de dados binários balanceados: {len(dados_balanceados)}")

    # Pré-processa os dados
    def preprocess_function(examples):
        return tokenizer(examples["texto"], truncation=True, padding=True, max_length=128)

    dataset = Dataset.from_list(dados_balanceados).map(preprocess_function, batched=True)
    dataset = dataset.rename_column("label", "labels")
    dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    # Divide os dados (treino, validação, teste)
    dataset_split = dataset.train_test_split(test_size=0.3)
    dataset_test_val = dataset_split["test"].train_test_split(test_size=0.5)
    train_dataset = dataset_split["train"]
    val_dataset = dataset_test_val["train"]
    test_dataset = dataset_test_val["test"]

    # Define métricas
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        acc = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds, average="weighted")
        return {"accuracy": acc, "f1": f1}

    # Configura os argumentos de treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=2, # Escolhido por uma questão de tempo de processamento
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=50,
        weight_decay=0.01,
        learning_rate=2e-5,
        logging_dir="./logs_binario",
        logging_steps=10,
        evaluation_strategy="no",
        save_strategy="no",
    )

    # Inicializa o modelo
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-multilingual-cased", num_labels=2)
    
    # Inicializa o trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    
    # Treina o modelo
    trainer.train()
    
    # Avalia no conjunto de teste
    results = trainer.evaluate(test_dataset)
    print("Resultados no teste (binário):", results)
    
    # Salva o modelo e o tokenizer
    model.save_pretrained(output_dir + "/modelo_binario")
    tokenizer.save_pretrained(output_dir + "/../config")
    return model

if __name__ == "__main__":
    # Carrega os dados do CSV
    df = pd.read_csv("data/raw/sample_nao_estruturados.csv")
    # Filtra entradas válidas (remove NaN ou vazias)
    df = df.dropna(subset=["DS_RECEITA"])
    df = df[df["DS_RECEITA"].str.strip() != ""]
    print(f"Total de entradas válidas após filtragem: {len(df)}")
    dados = [{"texto": row["DS_RECEITA"]} for _, row in df.iterrows()]
    train_binario(dados)