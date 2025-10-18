# FKR CLI - Gerador de Dados Fake Multi-Linguagem

Gerador de dados fake inteligente que suporta Python, Delphi/Pascal e C#.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## 📝 Sobre o Projeto

FKR é um gerador de dados fake open source que facilita a criação de dados de teste para desenvolvimento. Com suporte a múltiplas linguagens e formatos, é ideal para popular bancos de dados, criar fixtures e testar aplicações.

## Instalação

```bash
pip install -e .
```

## Uso

```bash
# Gerar JSON (padrão)
fkr classes/pessoa.py:Pessoa -c 10

# Gerar SQL
fkr classes/Pessoa.pas:TPessoa -c 100 --format sql --table pessoas

# Gerar CSV
fkr classes/Usuario.cs:Usuario -c 50 --format csv
```

## Features

- ✅ Suporte a Python (.py), Delphi/Pascal (.pas), C# (.cs)
- ✅ Formatos de saída: JSON, SQL, CSV
- ✅ 100+ campos mapeados automaticamente
- ✅ IDs inteligentes (UUID para string, serial para int)
- ✅ Classes customizadas retornam null
- ✅ Providers personalizados para ERP

## Sintaxe

```bash
fkr <arquivo>:<classe> -c <count> --format <json|sql|csv> --table <nome>
```

**Opções:**
- `-c, --count`: Número de registros a gerar (padrão: 1)
- `-f, --format`: Formato de saída (json, sql, csv) (padrão: json)
- `-t, --table`: Nome da tabela SQL (padrão: nome da classe em minúsculas)

## Exemplos

```bash
# Python
fkr models/user.py:User -c 100 --format sql --table users

# Delphi
fkr units/Pessoa.pas:TPessoa -c 50 --format csv

# C#
fkr Entities/Product.cs:Product -c 200 --format json
```

O arquivo de saída será gerado no mesmo diretório do arquivo de entrada.

## 🤝 Contribuindo

Contribuições são bem-vindas! Este é um projeto open source e você pode:

- 🐛 Reportar bugs
- 💡 Sugerir novas features
- 🔧 Adicionar novos parsers (Java, Go, TypeScript, etc.)
- 📚 Melhorar a documentação
- ➕ Adicionar novos providers no `PROVIDER_MAP`

### Como Contribuir

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovoParser`)
3. Commit suas mudanças (`git commit -m 'Adiciona parser para Java'`)
4. Push para a branch (`git push origin feature/NovoParser`)
5. Abra um Pull Request

### Adicionando um Novo Parser

Para adicionar suporte a uma nova linguagem:

1. Crie um novo parser em `parsers/` implementando a interface `Parser`
2. Adicione o parser no `ParserFactory` em `parsers/parser_factory.py`
3. Teste com classes reais da linguagem

Exemplo:

```python
# parsers/java_parser.py
from interfaces.parser import Parser
from typing import Dict, Type

class JavaParser(Parser):
    def parse(self, file_path: str, class_name: str) -> Dict[str, Type]:
        # Implementação do parser
        pass
    
    def get_supported_extensions(self) -> list[str]:
        return ['.java']
```

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🌟 Autor

Desenvolvido com ❤️ pela comunidade open source.

---

**Gostou do projeto? Deixe uma ⭐ no repositório!**

