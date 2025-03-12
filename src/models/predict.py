from transformers import pipeline, AutoTokenizer

def predict_exam_batch(texts, batch_size=32): # Faz a previsão em lote para uma lista de textos usando os modelos binário e multiclasse.
    
    # Carrega o tokenizer e os modelos uma única vez
    tokenizer = AutoTokenizer.from_pretrained("./models/config")
    classifier_binario = pipeline(
        "text-classification",
        model="./models/binario/modelo_binario",
        tokenizer=tokenizer,
        truncation=True,
        max_length=128,
        padding="max_length",
        batch_size=batch_size  # Define o tamanho do lote
    )
    classifier_multiclasse = pipeline(
        "text-classification",
        model="./models/multiclasse/modelo_multiclasse",
        tokenizer=tokenizer,
        truncation=True,
        max_length=128,
        padding="max_length",
        batch_size=batch_size  # Define o tamanho do lote
    )
    
    # Limpa os textos e garante que sejam strings válidas
    texts_cleaned = [str(text) if isinstance(text, str) else "" for text in texts]
    
    # Faz a previsão binária em lote
    pred_binarias = classifier_binario(texts_cleaned)
    
    # Inicializa os resultados
    results = []
    # Filtra os textos que são exames (LABEL_1) para a previsão multiclasse
    textos_exames = []
    indices_exames = []
    for idx, pred in enumerate(pred_binarias):
        if pred["label"] == "LABEL_1":
            textos_exames.append(texts_cleaned[idx])
            indices_exames.append(idx)
        else:
            results.append("Não é exame de imagem")
    
    # Faz a previsão multiclasse em lote para os textos que são exames
    if textos_exames:
        pred_multiclasses = classifier_multiclasse(textos_exames)
        label_map = {0: "Tomografia", 1: "Ressonância Magnética", 2: "Ultrassonografia", 3: "Radiografia", 4: "Eletrocardiograma", 5: "Densiotometria"}
        for idx, pred in zip(indices_exames, pred_multiclasses):
            label_id = int(pred["label"].split("_")[1])
            results.insert(idx, label_map[label_id])
    
    # Preenche os resultados para os textos que não foram classificados como exames
    final_results = []
    result_idx = 0
    for idx in range(len(texts)):
        if idx in indices_exames:
            final_results.append(results[result_idx])
            result_idx += 1
        else:
            final_results.append("Não é exame de imagem")
    
    return final_results