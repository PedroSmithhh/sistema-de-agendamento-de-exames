# Documentação do Sistema de Agendamento de Exames

Este documento fornece todas as informações necessárias para entender, executar e melhorar o sistema de agendamento de exames baseado em IA que desenvolvemos. Abaixo estão os obejtivos do projeto, instruções de execução, a arquitetura detalhada, justificativas de tecnologia, explicação do código e sugestões de melhorias com desafios, riscos e métricas.

---
## Objetivo do projeto

O objetivo deste case é desenvolver um sistema inteligente e proativo, que seja 
capaz de identificar automaticamente os pacientes com solicitações de 
exames de imagem pendentes. O sistema deverá incentivar esses pacientes, 
através do envio de mensagens personalizadas via WhatsApp, a agendar seus 
exames dentro da rede do grupo hospitalar.

## Instruções para Executar o Código

Para executar o sistema, siga os passos abaixo:

1. **Pré-requisitos**:
   - Instale o Python 3.8 ou superior.
   - Crie um ambiente virtual:
     ```bash
     python -m venv venv
     source venv/bin/activate  # No Windows: venv\Scripts\activate
     ```  
    - Instale as dependências listadas no requirements.txt:
      ```bash
      pip install -r requirements.txt
      ```
    - Configure as credenciais do Twilio no arquivo src/messaging/send_messages.py
        - Substitua "SUA_ACCOUNT_SID", "SEU_AUTH_TOKEN" e "SEU_NUMERO_TWILIO" pelos seus dados do Twilio
2. **Estrtura de arquivos**:
    - Certifique-se de ter os arquivos dataset_estruturado.csv e dataset_nao_estruturado.csv na pasta data/raw/
    - As pastas models/ e db/ serão criadas automaticamente
3. **Execução**:
    - Treine os modelos (se necessário):
      ```bash
      python src/models/train_binario.py
      python src/models/train_multiclasse.py
      ```
    - Execute o script principal:
       ```bash
      python main.py
        ```
    - Se preferir, é possível automatizar o programa de tal forma que a cada vez que um arquivo .csv chegar no data/ram (simulando a chegada de csv's do banco de dados do cliente em tempo real) o módulo main.py seja executado. Para fazer isso basta deixar o módulo monitor.py rodando:
        ```bash
        python monitor.py
        ```
    - O sistema processará os dados, gerará o CSV em data/processed/resultado_processado.csv e enviará até 100 mensagens (limitado para teste), registrando os envios em db/envios.db
4. **Verificação**
    - Confira o arquivo db/envios.db para os registros de envio.
    - Monitore a saída no terminal para o tempo total de execução.

## Integração com Cloud (Simulação)

Atualmente, o sistema opera de forma local, mas já possui módulos preparados para migração para a nuvem utilizando Google Cloud Plataform (GCP) caso seja necessário escalar o processamento.
Abaixo estão os módulos e como funcionariam em uma implementação real na GCP.

1. **Armazenamento no Google Cloud Storage (GCS)**
    - Arquivos CSV brutos (data/raw/) seriam armazenados no GCS ao invés do sistema de arquivos local.
    - O módulo monitor.py já foi estruturado para enviar os arquivos para o GCS automaticamente (em comentários no código fonte para não inteferir no funcionamento local do sistema).
2. **Processamento Automático com Cloud Functions (cloud_function.py)**
    - Em uma versão escalável, sempre que um novo CSV fosse enviado ao GCS, uma Cloud Function seria ativada para:
        - Baixar o CSV para data/raw/
        - Executar main.py
        - Salvar o CSV processado em data/processed/ no GCS
        - Remover os arquivos locais para manter a organização

## Implementação do Streamlit

O sistema inclui um dashboard interativo desenvolvido com a biblioteca Streamlit, projetado para visualizar e analisar os dados processados pelos arquivos CSV (estruturado_processado.csv, nao_estruturado_processado.csv e resultado_processado.csv). O dashboard permite aos usuários explorar os dados de forma dinâmica, filtrando por intervalos de datas ou datas específicas, e oferece insights valiosos sobre as solicitações e classificações de exames.

1. **Como usar:**
    - Pré requisitos:
        - Certifique-se de que as dependências do Streamlit estão instaladas:
         ```bash
        pip install streamlit pandas
        ```
    - Execução do Dashboard:
        - Execute o script do dashboard:
        ```bash
        streamlit run dashboard.py
        ```
        - Acesse o dashboard em --- no seu navegador
2. **Como usar**
    - Filtros de Consulta: Use o sidebar para selecionar a visão ("Estruturado", "Não Estruturado", "Resultado Processado") e o tipo de filtro de data ("Intervalo de Datas" ou "Data Específica").
    - Visualização: Explore tabelas que mostram o total de exames, exames por solicitante e quantidades de exames.

3. **Tecnologias Utilizadas**
    - Streamlit: Biblioteca Python para criar interfaces web interativas de forma rápida e simples.
    - Pandas: Utilizado para manipulação e análise dos dados dos CSVs.

4. **Infomrações Valiosas Oferecidas**
    - Total de Exames Solicitados/Processados: Mostra o número de exames em um intervalo ou data específica, ajudando a monitorar o volume de trabalho.
    - Exames por Solicitante: Identifica quais médicos solicitam mais exames, permitindo um acompanhamento mais direcionado.
    - Tendências Temporais: Permite observar variações no volume de exames ao longo do tempo, facilitando a otimização do envio de mensagens.

    Esses insights ajudam a equipe a tomar decisões informadas, como priorizar campanhas para exames mais solicitados ou ajustar o cronograma de envios com base em picos de atividade.

## Descrição Detalhada da Arquitetura

A arquitetura do sistema é dividida em quatro camadas principais, projetadas para processar dados, classificar exames, enviar mensagens e (opcionalmente) oferecer uma interface de monitoramento.

1. **Componentes**
 - **Camada de dados**
   - Armazena os datasets brutos (dataset_estruturado.csv e dataset_nao_estruturado.csv) e o resultado processado (resultado_processado.csv), além de logs de envio em db/envios.db.
- **Camada de Processamento**
    - Realiza o treinamento dos modelos de IA (binário e multiclasse), a classificação dos exames e a geração de mensagens personalizadas.
- **Camada de mensageria**
   - Envia mensagens via API do Twilio e registra os envios.

2. **Tecnologias**
 - **Camada de Dados**: Sistema de arquivos local e SQLite.
 - **Camada de Processamento**: Python com transformers (DistilBERT), pandas, nlpaug.
 - **Camada de Mensageria**: API Twilio com biblioteca twilio em Python.

3. **Comunicação**
 - Dados brutos e processados são passados via arquivos CSV.
 - Módulos se comunicam por chamadas de função no main.py.
 - A Camada de Mensageria usa requisições HTTP para o Twilio.

4. **Diagrama**

![Descrição do Diagrama](images\diagrama_Arquitetura_Software.png)

## Justificativa para escolhas de tecnologias

- Python:
    - Vantagem: Versátil, com bibliotecas prontas (transformers, pandas, twilio) e grande comunidade.
    - Desvantagem: Pode ser mais lento que linguagens compiladas (ex.: C++) em larga escala.
    - Por quê?: Ideal para prototipagem rápida e integração com IA e APIs.
- Transformers (DistilBERT):
    - Vantagem: Leve (66M parâmetros), eficiente para classificação de texto em português, pré-treinado.
    - Desvantagem: Exige hardware decente (GPU ideal) e pode ter overhead em CPUs.
    - Por quê?: Equilíbrio entre performance e velocidade
- Twilio:
    - Vantagem: API confiável para WhatsApp, custo previsível (0,008/conversa + 0,005/mensagem).
    - Desvantagem: Dependência externa e custos crescentes.
    - Por quê?: Solução pronta e fácil de integrar.
- SQLite:
    - Vantagem: SQLite permite consultas e traz mais estrutura para o projeto
    - Desvantagem: SQLite adiciona complexidade.
    - Por quê?: SQLite é futuro se precisar de relatórios e permite escalbilidade para armazenar outros tipos de dados

## Explicação do código

- main.py:
    - Coordena a execução: chama process_data(), generate_messages() e send_all_messages().
    - Inclui um timer para medir o desempenho total.
    - Limita envios a 100 mensagens para teste, mas processa todo o CSV.
- src/data/process_data.py:
    - Carrega os CSVs, processa o dataset estruturado com mapeamento de CD_TUSS, e usa predict_exam_batch para classificar o dataset não estruturado em lotes.
    - Gera o resultado_processado.csv.
- src/models/predict.py:
    - Define predict_exam_batch, que usa pipelines do transformers para classificar textos em lotes (binário e multiclasse) com distilbert-base-multilingual-cased.
- src/messaging/generate_messages.py:
    - Gera mensagens personalizadas com base no CSV processado, usando um template apelativo.
- src/messaging/send_messages.py:
    - Envia mensagens via Twilio e registra cada envio em logs/envios.log (ou db/envios.db com SQLite).
    - Inclui tratamento de erros e logs detalhados.
- Treinamento (train_binario.py e train_multiclasse.py):
    - Usa transformers para treinar os modelos com DistilBERT, balanceando dados e salvando os modelos em models/.

O código é comentado internamente, mas a modularidade permite ajustes fáceis (ex.: trocar o modelo ou adicionar novas funções).

## Sugestões de Melhorias, Desafios, Riscos e Métricas

1. **Testes A/B para Otimizar o Conteúdo das Mensagens:**
    - Testar duas versões de mensagens (ex.: "Temos uma boa notícia!" vs. "Garanta sua vaga agora!") para ver qual aumenta a taxa de agendamento.
    - Implementar dividindo os pacientes em grupos e registrar resultados no log.
    - Benefício: Mensagens mais eficazes.
2. **Implementação de um canla de comunicação bidirecional**
    - Permitir que pacientes respondam no WhatsApp (ex.: "confirmar" ou "cancelar") usando webhooks do Twilio.
    - Benefício: Interatividade e confirmações diretas.
3. **Alimentar os modelos com mais dados**
    - Recolher mais informações a respeito dos dados de entrada, como tipos de abreviações de exames (us=Ultrassonografia) para alimentar o modelo binário e o de classificação.
    - Benefício: Maior acurácia de processamento

## Desafios e Riscos

- Qualidade dos Dados:
    - Risco: Dados imprecisos (ex.: telefones errados) causam falhas.
    - Mitigação: Validar telefones com regex e criar pipeline de limpeza.
- Limites e Custos do Twilio:
    - Risco: Atrasos ou custos altos com aumento de envios.
    - Mitigação: Usar filas (ex.: RabbitMQ) e monitorar custos com dashboard.
- Escalabilidade:
    - Risco: Lentidão com 10.000 solicitações/dia.
    - Mitigação: Usar AWS Lambda e escalar horizontalmente com Docker/Kubernetes.
- Conformidade com LGPD:
    - Risco: Vazamento de dados sensíveis (CPF/Telefone).
    - Mitigação: Criptografar CSVs/logs, limitar acesso e auditar.

## Métricas de sucesso

- Taxa de Conversão:
    - Percentual de solicitações que viram agendamentos (meta: 40%).
- Taxa de Abertura das Mensagens:
    - Percentual de mensagens lidas (meta: 75%).
- Tempo Médio entre Solicitação e Agendamento:
    - Tempo médio até confirmação (meta: <3 dias).
- Satisfação dos Pacientes:
    - Média de respostas a pesquisas (meta: 4.0/5).


