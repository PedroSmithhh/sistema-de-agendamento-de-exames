import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, pipeline
from datasets import Dataset
from sklearn.metrics import accuracy_score, f1_score
from sklearn.utils import resample
from collections import Counter
from nlpaug.augmenter.word import SynonymAug
import warnings

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

def classificar_exame(texto): # Classifica o tipo de exame de imagem com base no texto.
    texto_lower = texto.lower()
    if "tomografia" in texto_lower or "tc" in texto_lower or "ct" in texto_lower:
        return "Tomografia"
    elif "ressonância magnética" in texto_lower or "rnm" in texto_lower or "rm" in texto_lower or "mri" in texto_lower:
        return "Ressonância Magnética"
    elif "ultrassom" in texto_lower or "us" in texto_lower or "ecografia" in texto_lower or "usg" in texto_lower:
        return "Ultrassonografia"
    elif "radiografia" in texto_lower or "rx" in texto_lower or "raio x" in texto_lower:
        return "Radiografia"
    elif "eletrocardiograma" in texto_lower or "ecg" in texto_lower:
        return "Eletrocardiograma"
    elif "densitometria" in texto_lower:
        return "Densiotometria"
    return None

def filter_exames(dados): # Filtra os dados usando o modelo binário treinado, retornando apenas os textos classificados como exames (label=1).
    # Carrega o modelo binário treinado
    tokenizer = AutoTokenizer.from_pretrained("./models/config")
    classifier_binario = pipeline(
        "text-classification",
        model="./models/binario/modelo_binario",
        tokenizer=tokenizer,
        truncation=True,
        max_length=128,
        padding="max_length"
    )

    # Filtra os dados
    dados_filtrados = []
    for d in dados:
        # Usa "DS_RECEITA" ou "texto" como chave, com fallback para string vazia
        texto = d.get("DS_RECEITA", d.get("texto", ""))
        if pd.isna(texto):
            texto = ""
        texto = str(texto)
        
        # Faz a previsão com o modelo binário
        pred_binaria = classifier_binario(texto)[0]
        if pred_binaria["label"] == "LABEL_1":  # Apenas exames de imagem
            dados_filtrados.append({"texto": texto})
    
    print(f"Total de textos classificados como exames de imagem: {len(dados_filtrados)}")
    return dados_filtrados

def balance_multiclasse(dados): # Faz o balanceamento dos dados multiclasse para evitar viés no modelo.  
    # Classifica os textos filtrados
    dados_multiclasse = [
        {"texto": d["texto"], "label": classificar_exame(d["texto"])}
        for d in dados if classificar_exame(d["texto"]) is not None
    ]
    
    # Verifica a distribuição das classes
    contagem = Counter([d["label"] for d in dados_multiclasse])
    print("Distribuição das classes antes do balanceamento:", contagem)
    
    # Aumenta dados se necessário
    min_samples = 75
    aug = SynonymAug(aug_p=0.3)
    for d in dados_multiclasse.copy():
        if contagem[d["label"]] < min_samples:
            texto_aumentado = aug.augment(d["texto"])[0]
            dados_multiclasse.append({"texto": texto_aumentado, "label": d["label"]})
    
    # Balanceia as classes usando oversampling
    balanced = []
    for label in set([d["label"] for d in dados_multiclasse]):
        dados_classe = [d for d in dados_multiclasse if d["label"] == label]
        if len(dados_classe) < min_samples:
            dados_classe = resample(dados_classe, replace=True, n_samples=min_samples, random_state=42)
        balanced.extend(dados_classe)
    
    # Mapeia os labels para números
    label_map = {
        "Tomografia": 0,
        "Ressonância Magnética": 1,
        "Ultrassonografia": 2,
        "Radiografia": 3,
        "Eletrocardiograma": 4,
        "Densiotometria": 5
    }
    dados_balanceados = [{"texto": d["texto"], "label": label_map[d["label"]]} for d in balanced]
    
    print("Distribuição das classes após balanceamento:", Counter([d["label"] for d in dados_balanceados]))
    return dados_balanceados

def train_multiclasse(dados, output_dir="./models/multiclasse"): # Treina o modelo multiclasse para classificar tipos de exames de imagem.
    # Filtra os dados usando o modelo binário
    dados_filtrados = filter_exames(dados)
    if not dados_filtrados:
        raise ValueError("Nenhum texto foi classificado como exame de imagem pelo modelo binário.")

    # Carrega o tokenizer
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-multilingual-cased")
    
    # Balanceia os dados
    dados_balanceados = balance_multiclasse(dados_filtrados)

    # Prepara o dataset
    def preprocess_function(examples):
        return tokenizer(examples["texto"], truncation=True, padding=True, max_length=128)

    dataset = Dataset.from_list(dados_balanceados).map(preprocess_function, batched=True)
    dataset = dataset.rename_column("label", "labels")
    dataset.set_format("torch", columns=["input_ids", "attention_mask", "labels"])

    # Divide em treino, validação e teste
    dataset_split = dataset.train_test_split(test_size=0.3)
    dataset_test_val = dataset_split["test"].train_test_split(test_size=0.5)
    train_dataset = dataset_split["train"]
    val_dataset = dataset_test_val["train"]
    test_dataset = dataset_test_val["test"]

    # Define métricas de avaliação
    def compute_metrics(pred):
        labels = pred.label_ids
        preds = pred.predictions.argmax(-1)
        acc = accuracy_score(labels, preds)
        f1 = f1_score(labels, preds, average="weighted")
        return {"accuracy": acc, "f1": f1}

    # Configura os parâmetros de treinamento
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=2, # Escolhido por uma questão de tempo de processamento
        per_device_train_batch_size=16,
        per_device_eval_batch_size=16,
        warmup_steps=50,
        weight_decay=0.01,
        learning_rate=2e-5,
        logging_dir="./logs_multiclasse",
        logging_steps=10,
        evaluation_strategy="no",
        save_strategy="no",
    )

    # Carrega e treina o modelo
    model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-multilingual-cased", num_labels=6)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        compute_metrics=compute_metrics
    )
    trainer.train()
    results = trainer.evaluate(test_dataset)
    print("Resultados no teste (multiclasse):", results)
    
    # Salva o modelo e o tokenizer
    model.save_pretrained(output_dir + "/modelo_multiclasse")
    tokenizer.save_pretrained(output_dir + "/../config")
    return model

if __name__ == "__main__":
    # Carrega os dados
    df = pd.read_csv("data/raw/sample_nao_estruturados.csv")
    dados = df.to_dict("records")
    train_multiclasse(dados)