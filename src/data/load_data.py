import pandas as pd
import os

def load_data(data_dir="data/raw/"):
    estruturado = pd.read_csv(os.path.join(data_dir, "sample_estruturados.csv"))
    nao_estruturado = pd.read_csv(os.path.join(data_dir, "sample_nao_estruturados.csv"))
    return estruturado, nao_estruturado