"""Utilitários resilientes de leitura de arquivos bloqueados no Windows/Excel."""

import os
import shutil
import tempfile


def read_bytes_resilient(file_path: str) -> bytes:
    """Lê bytes de um arquivo mesmo se estiver bloqueado para leitura direta no Windows."""
    try:
        with open(file_path, "rb") as file:
            return file.read()
    except PermissionError:
        fd, tmp_path = tempfile.mkstemp()
        os.close(fd)
        try:
            shutil.copy2(file_path, tmp_path)
            with open(tmp_path, "rb") as tmp_file:
                return tmp_file.read()
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
