import importlib.util
import sys
from pathlib import Path
from typing import Dict, Type

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.parser import Parser


class PyParser(Parser):
    """
    Parser para arquivos Python.
    Extrai campos de classes Python usando type annotations.
    """
    
    def parse(self, file_path: str, class_name: str) -> Dict[str, Type]:
        """
        Extrai campos e tipos de uma classe Python usando __annotations__.
        
        Args:
            file_path: Caminho para o arquivo .py
            class_name: Nome da classe
            
        Returns:
            Dicionário com {nome_do_campo: tipo}
        """
        try:
            # Carrega o módulo dinamicamente
            spec = importlib.util.spec_from_file_location(class_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Obtém a classe
            target_class = getattr(module, class_name)
            
            # Retorna as annotations (type hints)
            if hasattr(target_class, '__annotations__'):
                return target_class.__annotations__
            else:
                raise ValueError(f"Classe '{class_name}' não possui type annotations")
                
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except AttributeError:
            raise AttributeError(f"Classe '{class_name}' não encontrada no arquivo {file_path}")
        except Exception as e:
            raise Exception(f"Erro ao parsear arquivo Python: {e}")
    
    def get_supported_extensions(self) -> list[str]:
        """Retorna extensões suportadas pelo parser Python."""
        return ['.py', '.pyw']

