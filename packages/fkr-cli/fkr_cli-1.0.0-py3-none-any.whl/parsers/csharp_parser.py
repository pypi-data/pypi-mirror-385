import re
import sys
from pathlib import Path
from typing import Dict, Type

# Adiciona o diretório raiz ao path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from interfaces.parser import Parser


class CsharpParser(Parser):
    """
    Parser para arquivos C#.
    Extrai campos e propriedades de classes C#.
    """
    
    # Mapeamento de tipos C# para tipos Python
    TYPE_MAPPING = {
        'string': str,
        'int': int,
        'int32': int,
        'int64': int,
        'long': int,
        'short': int,
        'byte': int,
        'sbyte': int,
        'uint': int,
        'uint32': int,
        'uint64': int,
        'ulong': int,
        'ushort': int,
        'float': float,
        'double': float,
        'decimal': float,
        'bool': bool,
        'boolean': bool,
        'datetime': str,  # Será formatado como ISO string
        'date': str,
        'time': str,
        'timespan': str,
        'guid': str,
        'char': str,
    }
    
    def parse(self, file_path: str, class_name: str) -> Dict[str, Type]:
        """
        Extrai campos e propriedades de uma classe C#.
        
        Suporta:
        - Properties com get/set (public string Nome { get; set; })
        - Campos públicos (public string Nome;)
        - Auto-properties
        
        Args:
            file_path: Caminho para o arquivo .cs
            class_name: Nome da classe
            
        Returns:
            Dicionário com {nome_do_campo: tipo}
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove comentários
            content = self._remove_comments(content)
            
            # Parseia a classe
            fields = self._parse_class(content, class_name)
            
            if not fields:
                raise ValueError(f"Classe '{class_name}' não encontrada ou sem campos no arquivo {file_path}")
            
            return fields
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        except Exception as e:
            raise Exception(f"Erro ao parsear arquivo C#: {e}")
    
    def _remove_comments(self, content: str) -> str:
        """Remove comentários C#."""
        # Remove comentários de linha dupla //
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        # Remove comentários de bloco /* */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        return content
    
    def _parse_class(self, content: str, class_name: str) -> Dict[str, Type]:
        """Parseia uma classe C# e extrai properties e campos."""
        fields = {}
        
        # Padrão simplificado para encontrar a classe
        # Busca por "class NomeClasse" e captura tudo até o fechamento do bloco
        class_pattern = rf'class\s+{class_name}\s*(?:<[^>]+>)?\s*(?::\s*[\w\s,<>]+)?\s*\{{'
        class_match = re.search(class_pattern, content, re.IGNORECASE)
        
        if not class_match:
            return fields
        
        # Encontra o início da classe e extrai o conteúdo
        start_pos = class_match.end()
        brace_count = 1
        end_pos = start_pos
        
        # Conta chaves para encontrar o fim da classe
        for i in range(start_pos, len(content)):
            if content[i] == '{':
                brace_count += 1
            elif content[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_pos = i
                    break
        
        class_content = content[start_pos:end_pos]
        
        # Extrai auto-properties com possíveis atributos
        # Captura atributos opcionais antes da property
        # Suporta: { get; set; }, { get; private set; }, { get; init; }, etc.
        property_pattern = r'((?:\[[^\]]+\]\s*)*)\s*(public|private|protected|internal)?\s*(\w+(?:<[^>]+>)?)\??\s+(\w+)\s*\{\s*get\s*;(?:\s*(?:private|protected|internal|init))?\s*set\s*;\s*\}'
        
        for match in re.finditer(property_pattern, class_content, re.IGNORECASE):
            attributes = match.group(1)  # Atributos como [BsonId], etc
            # group(2) é o modificador de acesso (public, private, etc) - ignoramos
            field_type_str = match.group(3).lower()
            field_name = match.group(4)
            
            # Remove generics para mapeamento simples (ex: List<string> -> list)
            base_type = re.sub(r'<.*?>', '', field_type_str)
            
            # Verifica se tem atributos que indicam tipo especial
            if attributes and 'bsonrepresentation' in attributes.lower() and 'objectid' in attributes.lower():
                # É um ObjectId do MongoDB - gera UUID
                field_type = str  # Será mapeado para uuid no smart_generate
                fields[field_name] = field_type
                # Marca como UUID para o gerador saber
                fields[f'__{field_name}_hint'] = 'uuid'
            else:
                # Mapeia tipo C# para Python
                field_type = self.TYPE_MAPPING.get(base_type, str)
                fields[field_name] = field_type
                
                # Se não está no TYPE_MAPPING, é provavelmente uma classe customizada
                if base_type not in self.TYPE_MAPPING:
                    fields[f'__{field_name}_hint'] = 'custom_class'
        
        # Extrai campos públicos: public Tipo Nome;
        field_pattern = r'(?:public|internal)\s+(\w+(?:<[^>]+>)?)\s+(\w+)\s*;'
        
        for match in re.finditer(field_pattern, class_content, re.IGNORECASE):
            field_type_str = match.group(1).lower()
            field_name = match.group(2)
            
            # Ignora se já foi capturado como property
            if field_name in fields:
                continue
            
            # Remove generics
            base_type = re.sub(r'<.*?>', '', field_type_str)
            
            # Mapeia tipo C# para Python
            field_type = self.TYPE_MAPPING.get(base_type, str)
            fields[field_name] = field_type
        
        return fields
    
    def get_supported_extensions(self) -> list[str]:
        """Retorna extensões suportadas pelo parser C#."""
        return ['.cs']

