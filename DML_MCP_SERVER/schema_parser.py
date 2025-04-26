import sqlparse
import re
from collections import defaultdict


def parse_schema(schema_path):
    with open(schema_path, 'r') as file:
        schema_sql = file.read()

    # Parse SQL statements
    statements = sqlparse.parse(schema_sql)
    relationships = defaultdict(list)
    tables = set()

    for stmt in statements:
        if stmt.get_type() == 'CREATE':
            table_name = re.search(r'CREATE TABLE\s+(\w+)', str(stmt), re.IGNORECASE)
            if table_name:
                table = table_name.group(1)
                tables.add(table)

                # Find foreign key relationships
                foreign_keys = re.findall(
                    r'CONSTRAINT\s+\w+\s+FOREIGN KEY\s*\((\w+)\)\s+REFERENCES\s+(\w+)\s*\((\w+)\)', str(stmt),
                    re.IGNORECASE)
                for fk in foreign_keys:
                    child_col, parent_table, parent_col = fk
                    relationships[parent_table].append({
                        'child_table': table,
                        'child_col': child_col,
                        'parent_col': parent_col
                    })

    return tables, relationships
