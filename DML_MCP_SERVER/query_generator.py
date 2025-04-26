from collections import defaultdict


def build_dependency_graph(relationships):
    graph = defaultdict(list)
    for parent, children in relationships.items():
        for child in children:
            graph[parent].append(child['child_table'])
    return graph


def get_child_tables(table, relationships, visited=None):
    if visited is None:
        visited = set()

    children = []
    for child in relationships.get(table, []):
        child_table = child['child_table']
        if child_table not in visited:
            visited.add(child_table)
            children.append(child_table)
            children.extend(get_child_tables(child_table, relationships, visited))
    return children


def generate_delete_queries(table, condition, relationships):
    queries = []
    child_tables = get_child_tables(table, relationships)

    # Delete from child tables first (reverse order to ensure proper cascade)
    for child in reversed(child_tables):
        queries.append(f"DELETE FROM {child} WHERE {child} IN (SELECT {child} FROM {table} WHERE {condition});\n")

    # Delete from parent table
    queries.append(f"DELETE FROM {table} WHERE {condition};\n")

    return "\n".join(queries)


def generate_update_query(table, set_clause, condition):
    return f"UPDATE {table} SET {set_clause} WHERE {condition};"
