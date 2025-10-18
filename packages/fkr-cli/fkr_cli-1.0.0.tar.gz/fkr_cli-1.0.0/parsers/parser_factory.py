import sys
from pathlib import Path
from typing import Optional

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.parser import Parser
from parsers.py_parser import PyParser
from parsers.delphi_parser import DelphiParser
from parsers.csharp_parser import CsharpParser


class ParserFactory:
    """
    Factory para criar parsers baseado na extensão do arquivo.
    """
    
    def __init__(self):
        """Inicializa a factory com todos os parsers disponíveis."""
        self.parsers = [
            PyParser(),
            DelphiParser(),
            CsharpParser(),
        ]
    
    def get_parser(self, file_path: str) -> Optional[Parser]:
        """
        Retorna o parser adequado para o arquivo.
        
        Args:
            file_path: Caminho para o arquivo fonte
            
        Returns:
            Instância do parser adequado ou None se não houver suporte
        """
        extension = Path(file_path).suffix.lower()
        
        for parser in self.parsers:
            if extension in parser.get_supported_extensions():
                return parser
        
        return None
    
    def get_supported_extensions(self) -> list[str]:
        """
        Retorna todas as extensões suportadas por todos os parsers.
        
        Returns:
            Lista de extensões suportadas
        """
        extensions = []
        for parser in self.parsers:
            extensions.extend(parser.get_supported_extensions())
        return extensions

