import re
import sys
from pathlib import Path
from typing import Dict, Type

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.parser import Parser


class DelphiParser(Parser):
    """
    Parser para arquivos Delphi/Pascal.
    Extrai campos de classes e records Pascal.
    """
    
    # Mapeamento de tipos Delphi/Pascal para tipos Python
    TYPE_MAPPING = {
        'string': str,
        'ansistring': str,
        'widestring': str,
        'unicodestring': str,
        'shortstring': str,
        'integer': int,
        'int64': int,
        'cardinal': int,
        'word': int,
        'byte': int,
        'longint': int,
        'shortint': int,
        'longword': int,
        'smallint': int,
        'real': float,
        'single': float,
        'double': float,
        'extended': float,
        'currency': float,
        'boolean': bool,
        'bytebool': bool,
        'wordbool': bool,
        'longbool': bool,
        'tdatetime': str,  # Será formatado como ISO string
        'tdate': str,
        'ttime': str,
    }
    
    def parse(self, file_path: str, class_name: str) -> Dict[str, Type]:
        """
        Extrai campos de uma classe ou record Delphi/Pascal.
        
        Suporta:
        - Classes com properties
        - Records com campos
        - Campos privados (FNome: string)
        - Properties (property Nome: string)
        
        Args:
            file_path: Caminho para o arquivo .pas
            class_name: Nome da classe/record (com ou sem prefixo T)
            
        Returns:
            Dicionário com {nome_do_campo: tipo}
        """
        try:
            # Tenta múltiplos encodings (arquivos Delphi geralmente são Latin-1/Windows-1252)
            content = None
            encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise Exception(f"Não foi possível decodificar o arquivo com os encodings: {', '.join(encodings)}")
            
            # Remove comentários
            content = self._remove_comments(content)
            
            # Adiciona prefixo T se não tiver
            if not class_name.startswith('T'):
                class_name = f'T{class_name}'
            
            # Tenta parsear como class primeiro, depois como record
            fields = self._parse_class(content, class_name)
            if not fields:
                fields = self._parse_record(content, class_name)
            
            if not fields:
                raise ValueError(f"Classe/Record '{class_name}' não encontrada ou sem campos no arquivo {file_path}")
            
            return fields
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            raise Exception(f"Erro ao parsear arquivo Delphi: {e}")
    
    def _remove_comments(self, content: str) -> str:
        """Remove comentários Delphi/Pascal."""
        # Remove comentários de linha dupla //
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # Remove comentários de bloco { }
        content = re.sub(r'\{.*?\}', '', content, flags=re.DOTALL)
        # Remove comentários de bloco (* *)
        content = re.sub(r'\(\*.*?\*\)', '', content, flags=re.DOTALL)
        return content
    
    def _parse_class(self, content: str, class_name: str) -> Dict[str, Type]:
        """Parseia uma classe Delphi e extrai properties."""
        fields = {}
        
        # Padrão para encontrar a classe
        class_pattern = rf'{class_name}\s*=\s*class\s*.*?end\s*;'
        class_match = re.search(class_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not class_match:
            return fields
        
        class_content = class_match.group(0)
        
        # Extrai properties: property Nome: Tipo read ... write ...;
        property_pattern = r'property\s+(\w+)\s*:\s*(\w+)'
        
        for match in re.finditer(property_pattern, class_content, re.IGNORECASE):
            field_name = match.group(1)
            field_type_str = match.group(2).lower()
            
            # Mapeia tipo Delphi para Python
            field_type = self.TYPE_MAPPING.get(field_type_str, str)
            fields[field_name] = field_type
            
            # Se não está no TYPE_MAPPING, é provavelmente uma classe customizada
            if field_type_str not in self.TYPE_MAPPING:
                fields[f'__{field_name}_hint'] = 'custom_class'
        
        # Se não encontrou properties, tenta campos privados
        if not fields:
            # Extrai campos: FNome: string;
            field_pattern = r'F(\w+)\s*:\s*(\w+)\s*;'
            
            for match in re.finditer(field_pattern, class_content, re.IGNORECASE):
                field_name = match.group(1)  # Remove o F do prefixo
                field_type_str = match.group(2).lower()
                
                field_type = self.TYPE_MAPPING.get(field_type_str, str)
                fields[field_name] = field_type
                
                # Se não está no TYPE_MAPPING, é provavelmente uma classe customizada
                if field_type_str not in self.TYPE_MAPPING:
                    fields[f'__{field_name}_hint'] = 'custom_class'
        
        return fields
    
    def _parse_record(self, content: str, class_name: str) -> Dict[str, Type]:
        """Parseia um record Delphi e extrai campos."""
        fields = {}
        
        # Padrão para encontrar o record
        record_pattern = rf'{class_name}\s*=\s*record\s*.*?end\s*;'
        record_match = re.search(record_pattern, content, re.IGNORECASE | re.DOTALL)
        
        if not record_match:
            return fields
        
        record_content = record_match.group(0)
        
        # Extrai campos: Nome: Tipo;
        field_pattern = r'(\w+)\s*:\s*(\w+)\s*;'
        
        for match in re.finditer(field_pattern, record_content, re.IGNORECASE):
            field_name = match.group(1)
            # Ignora palavras-chave
            if field_name.lower() in ['record', 'end', 'type']:
                continue
                
            field_type_str = match.group(2).lower()
            
            # Mapeia tipo Delphi para Python
            field_type = self.TYPE_MAPPING.get(field_type_str, str)
            fields[field_name] = field_type
            
            # Se não está no TYPE_MAPPING, é provavelmente uma classe customizada
            if field_type_str not in self.TYPE_MAPPING:
                fields[f'__{field_name}_hint'] = 'custom_class'
        
        return fields
    
    def get_supported_extensions(self) -> list[str]:
        """Retorna extensões suportadas pelo parser Delphi."""
        return ['.pas', '.dpr', '.dpk']

