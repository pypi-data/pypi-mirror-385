from abc import ABC, abstractmethod
from typing import Dict, Type, Any
from pathlib import Path


class Parser(ABC):
    """
    Interface abstrata para parsers de diferentes linguagens.
    Cada parser deve implementar a lógica para extrair campos e tipos de uma classe.
    """
    
    @abstractmethod
    def parse(self, file_path: str, class_name: str) -> Dict[str, Type]:
        """
        Extrai os campos e seus tipos de uma classe em um arquivo.
        
        Args:
            file_path: Caminho para o arquivo fonte
            class_name: Nome da classe a ser parseada
            
        Returns:
            Dicionário com {nome_do_campo: tipo}
        """
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """
        Retorna lista de extensões de arquivo suportadas por este parser.
        
        Returns:
            Lista de extensões (ex: ['.py', '.pyw'])
        """
        pass
    
    def supports_file(self, file_path: str) -> bool:
        """
        Verifica se este parser suporta o arquivo dado.
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            True se o parser suporta o arquivo
        """
        extension = Path(file_path).suffix.lower()
        return extension in self.get_supported_extensions()

