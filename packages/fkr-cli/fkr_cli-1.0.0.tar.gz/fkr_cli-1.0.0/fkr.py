import typer
from faker import Faker
import inspect
import json
import csv
from datetime import date, datetime
from decimal import Decimal
from typing import List, Dict, Any
from pathlib import Path

from providers.provider import PROVIDER_MAP
from providers.ERPProvider import ErpProvider
from parsers.parser_factory import ParserFactory

fake = Faker('pt_BR')
fake.add_provider(ErpProvider)

def smart_generate(field_name: str, field_type: type, hint: str = None):
    lowered_name = field_name.lower()
    
    if hint == 'uuid':
        return fake.uuid4()
    
    if hint == 'custom_class':
        return None
    
    if lowered_name.endswith('id'):
        if field_type == str:
            return fake.uuid4()
        elif field_type == int:
            return fake.random_int(min=1, max=99999)
    
    provider_name = None
    provider_kwargs = {}
    
    if lowered_name in PROVIDER_MAP:
        map_value = PROVIDER_MAP[lowered_name]
        
        if isinstance(map_value, tuple) and len(map_value) == 2:
            provider_name, provider_kwargs = map_value
        else:
            provider_name = map_value
    elif hasattr(fake, lowered_name):
        provider_name = lowered_name

    if provider_name:
        provider_method = getattr(fake, provider_name)
        
        result = provider_method(**provider_kwargs)

        if isinstance(result, (date, datetime)):
            return result.isoformat()
        
        if isinstance(result, Decimal):
            return float(result)
        
        return result

    if field_type == str:
        return fake.word()
    if field_type == int:
        return fake.random_int(min=1, max=100)
    if field_type == float:
        return fake.pyfloat()
    if field_type == bool:
        return fake.boolean()
    
    return None


def format_as_json(data: List[Dict[str, Any]]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_as_sql(data: List[Dict[str, Any]], table_name: str) -> str:
    if not data:
        return ""
    
    sql_statements = []
    columns = list(data[0].keys())
    columns_str = ", ".join(columns)
    
    for record in data:
        values = []
        for col in columns:
            value = record[col]
            if value is None:
                values.append("NULL")
            elif isinstance(value, (int, float)):
                values.append(str(value))
            elif isinstance(value, bool):
                values.append("1" if value else "0")
            else:
                escaped_value = str(value).replace("'", "''")
                values.append(f"'{escaped_value}'")
        
        values_str = ", ".join(values)
        sql_statements.append(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});")
    
    return "\n".join(sql_statements)


def format_as_csv(data: List[Dict[str, Any]]) -> str:
    if not data:
        return ""
    
    import io
    output = io.StringIO()
    
    columns = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=columns)
    
    writer.writeheader()
    writer.writerows(data)
    
    return output.getvalue()


def main(
    class_path: str = typer.Argument(..., help="Caminho para a classe no formato 'arquivo:NomeDaClasse'. Ex: 'pessoa.py:Pessoa' ou 'Pessoa.pas:TPessoa'"),
    count: int = typer.Option(1, "--count", "-c", help="Número de registros a serem gerados."),
    format: str = typer.Option("json", "--format", "-f", help="Formato de saída: json, sql, csv"),
    table: str = typer.Option(None, "--table", "-t", help="Nome da tabela para SQL (padrão: nome da classe em minúsculas)")
):
    try:
        file_path, class_name = class_path.rsplit(':', 1)
        
        if not Path(file_path).suffix:
            file_path += '.py'
        
        if not Path(file_path).exists():
            print(f"Erro: Arquivo '{file_path}' não encontrado")
            raise typer.Exit(code=1)
        
        parser_factory = ParserFactory()
        parser = parser_factory.get_parser(file_path)
        
        if not parser:
            extensions = ', '.join(parser_factory.get_supported_extensions())
            print(f"Erro: Extensão de arquivo não suportada. Extensões suportadas: {extensions}")
            raise typer.Exit(code=1)
        
        print(f"📖 Parseando {Path(file_path).suffix} - {file_path}")
        fields = parser.parse(file_path, class_name)
        
        if not fields:
            print(f"Erro: Nenhum campo encontrado na classe '{class_name}'")
            raise typer.Exit(code=1)
        
        print(f"✓ {len(fields)} campo(s) encontrado(s): {', '.join(fields.keys())}")

    except ValueError as e:
        if ':' not in class_path:
            print(f"Erro: Formato inválido. Use 'arquivo:NomeDaClasse'. Ex: 'pessoa.py:Pessoa' ou 'Pessoa.pas:TPessoa'")
        else:
            print(f"Erro: {e}")
        raise typer.Exit(code=1)
    except (FileNotFoundError, AttributeError) as e:
        print(f"Erro: {e}")
        raise typer.Exit(code=1)
    except Exception as e:
        print(f"Erro inesperado: {e}")
        raise typer.Exit(code=1)
    
    generated_data = []

    for _ in range(count):
        record = {}
        for field_name, field_type in fields.items():
            if field_name.startswith('__') and field_name.endswith('_hint'):
                continue
            
            hint_key = f'__{field_name}_hint'
            hint = fields.get(hint_key)
            
            record[field_name] = smart_generate(field_name, field_type, hint)
        generated_data.append(record)
    
    format = format.lower()
    if format not in ['json', 'sql', 'csv']:
        print(f"Erro: Formato '{format}' não suportado. Use: json, sql ou csv")
        raise typer.Exit(code=1)
    
    input_dir = Path(file_path).parent
    
    if format == 'json':
        output_content = format_as_json(generated_data)
        output_file = input_dir / f"{class_name}.json"
    elif format == 'sql':
        table_name = table if table else class_name.lower()
        output_content = format_as_sql(generated_data, table_name)
        output_file = input_dir / f"{class_name}.sql"
    elif format == 'csv':
        output_content = format_as_csv(generated_data)
        output_file = input_dir / f"{class_name}.csv"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"✓ {count} registro(s) gerado(s) no formato {format.upper()}")
    print(f"✓ Arquivo salvo: {output_file}")


def cli():
    typer.run(main)

if __name__ == "__main__":
    cli()