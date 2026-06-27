import sys
from neo4j import GraphDatabase
import neo4j.time

# Configurações de Conexão (Pode ser alterado para o AuraDB ou Local)
URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "123456789"

def format_value(value):
    """Formata valores Python para sintaxe Cypher."""
    if value is None:
        return "null"
    elif isinstance(value, str):
        # Escapa aspas simples
        escaped = value.replace("'", "\\'")
        return f"'{escaped}'"
    elif isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        items = [format_value(x) for x in value]
        return "[" + ", ".join(items) + "]"
    elif isinstance(value, (neo4j.time.DateTime, neo4j.time.Date)):
        return f"datetime('{value}')"
    else:
        return f"'{str(value)}'"

def exportar_para_cypher(uri, user, password, output_file):
    print(f"Conectando ao banco de dados em: {uri}")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver as d:
            d.verify_connectivity()
            
            with d.session() as session:
                # 1. Buscar todos os nós
                print("Buscando nos...")
                nodes_query = "MATCH (n) RETURN labels(n)[0] AS label, properties(n) AS props, elementId(n) AS id"
                nodes_records = session.run(nodes_query).data()
                
                # 2. Buscar todas as relações
                print("Buscando relacionamentos...")
                rels_query = """
                MATCH (n)-[r]->(m) 
                RETURN elementId(n) AS source, elementId(m) AS target, type(r) AS type, properties(r) AS props
                """
                rels_records = session.run(rels_query).data()
                
        # Gerar o conteúdo do arquivo Cypher
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("// ============================================================================\n")
            f.write(f"// BACKUP GERADO AUTOMATICAMENTE VIA SCRIPT DE EXPORTACAO\n")
            f.write(f"// Destino: {uri}\n")
            f.write("// ============================================================================\n\n")
            
            f.write("// Limpeza inicial do banco\n")
            f.write("MATCH (n) DETACH DELETE n;\n\n")
            
            # Escrever criação de nós
            f.write("// Criacao de nos\n")
            node_map = {} # Mapeia elementId do Neo4j para nome de variável no script
            for idx, record in enumerate(nodes_records):
                label = record['label']
                props = record['props']
                node_id = record['id']
                var_name = f"node_{idx}"
                node_map[node_id] = var_name
                
                # Formata propriedades
                props_list = []
                for k, v in props.items():
                    props_list.append(f"{k}: {format_value(v)}")
                
                props_str = " {" + ", ".join(props_list) + "}" if props_list else ""
                
                f.write(f"CREATE ({var_name}:{label}{props_str});\n")
                
            f.write("\n// Criacao de relacionamentos\n")
            # Escrever criação de relações
            for record in rels_records:
                source = record['source']
                target = record['target']
                rel_type = record['type']
                props = record['props']
                
                var_source = node_map.get(source)
                var_target = node_map.get(target)
                
                if var_source and var_target:
                    # Formata propriedades da relação
                    props_list = []
                    for k, v in props.items():
                        props_list.append(f"{k}: {format_value(v)}")
                    
                    props_str = " {" + ", ".join(props_list) + "}" if props_list else ""
                    
                    # Usa MATCH para localizar as variáveis criadas anteriormente e criar a relação
                    f.write(f"MATCH (s) WHERE id(s) = id({var_source}) MATCH (t) WHERE id(t) = id({var_target}) CREATE (s)-[:{rel_type}{props_str}]->(t);\n")
            
            # O MATCH com id() e id() funciona de forma simples no Cypher para vincular nos recem-criados em lote
            # Outra alternativa e usar CREATE direta unindo com WITH
            
        print(f"Exportacao concluida com sucesso! Arquivo salvo em: {output_file}")
        return True
        
    except Exception as e:
        print(f"Erro durante a exportacao: {e}")
        return False

if __name__ == "__main__":
    # Pode receber parametros via linha de comando
    # Exemplo: python exportar_banco.py "neo4j+s://xxxx.databases.neo4j.io" "neo4j" "senha" "backup.cypher"
    uri = sys.argv[1] if len(sys.argv) > 1 else URI
    user = sys.argv[2] if len(sys.argv) > 2 else USER
    password = sys.argv[3] if len(sys.argv) > 3 else PASSWORD
    output = sys.argv[4] if len(sys.argv) > 4 else "backup_exportado.cypher"
    
    exportar_para_cypher(uri, user, password, output)
