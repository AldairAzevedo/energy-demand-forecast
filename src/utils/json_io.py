"""Módulo utilitário para serialização e desserialização robusta de JSON."""

import json
import os
from typing import Any, Dict

import numpy as np


class NumpyJSONEncoder(json.JSONEncoder):
    """Codificador JSON customizado com suporte a tipos nativos do NumPy."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, (np.bool_,)):
            return bool(obj)
        return super().default(obj)


def save_json(data: Dict[str, Any], file_path: str, indent: int = 2) -> None:
    """Salva um dicionário em formato JSON de maneira atômica e segura.

    Args:
        data: Dicionário contendo os dados a serem salvos.
        file_path: Caminho completo do arquivo de destino.
        indent: Nível de indentação do arquivo JSON gerado.

    Raises:
        ValueError: Caso o dicionário seja inválido.
        IOError: Em caso de erro de gravação em disco.
    """
    if not isinstance(data, dict):
        raise ValueError("Os dados a serem salvos em JSON devem ser um dicionário.")

    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    temp_path = f"{file_path}.tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, cls=NumpyJSONEncoder, ensure_ascii=False, indent=indent)
        # Substituição atômica para evitar corrupção em caso de parada abrupta
        os.replace(temp_path, file_path)
    except Exception as err:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise IOError(f"Falha ao salvar JSON em {file_path}: {err}") from err


def load_json(file_path: str) -> Dict[str, Any]:
    """Carrega dados estruturados de um arquivo JSON.

    Args:
        file_path: Caminho do arquivo a ser lido.

    Returns:
        Dicionário com o conteúdo carregado.

    Raises:
        FileNotFoundError: Se o arquivo especificado não existir.
        IOError: Se o arquivo estiver corrompido ou ilegível.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo JSON não encontrado no caminho: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as err:
        raise IOError(f"Conteúdo JSON inválido ou corrompido em {file_path}: {err}") from err
