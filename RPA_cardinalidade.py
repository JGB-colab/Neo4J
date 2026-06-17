from neo4j import GraphDatabase

def criar_relacionamento_cardinalidade(driver, origin_lbl, origin_val, dest_lbl, dest_val, rel_type, card):
    """
    Gera e executa a query Cypher correta baseada na regra de cardinalidade.
    card: 'N:N', '1:N' ou '1:1'
    """
    
    # Parâmetros de base
    query_base = f"""
    MATCH (origem:{origin_lbl} {{id: $orig_val}})
    MATCH (destino:{dest_lbl} {{id: $dest_val}})
    """
    
    # N:N - Usa MERGE para evitar duplicatas exatas
    if card == 'N:N':
        query = query_base + f"MERGE (origem)-[:{rel_type}]->(destino)"
        
    # 1:N - Bloqueia se a origem já tiver esse relacionamento com qualquer destino
    elif card == '1:N':
        query = query_base + f"""
        WHERE NOT EXISTS {{
            MATCH (origem)-[:{rel_type}]->(:{dest_lbl})
        }}
        CREATE (origem)-[:{rel_type}]->(destino)
        """
        
    # 1:1 - Bloqueia se a origem já apontar para alguém OU se o destino já receber de alguém[cite: 2]
    elif card == '1:1':
        query = query_base + f"""
        WHERE NOT EXISTS {{
            MATCH (origem)-[:{rel_type}]->(:{dest_lbl})
        }}
        AND NOT EXISTS {{
            MATCH (:{origin_lbl})-[:{rel_type}]->(destino)
        }}
        CREATE (origem)-[:{rel_type}]->(destino)
        """
    else:
        return "Cardinalidade não suportada."

    # Execução
    try:
        with driver.session() as session:
            result = session.run(query, orig_val=origin_val, dest_val=dest_val)
            res_summary = result.consume()
            if res_summary.counters.relationships_created > 0:
                print(f"✅ Relacionamento {rel_type} criado com sucesso ({card}).")
            else:
                print(f"⚠️ Relacionamento bloqueado pela regra de cardinalidade {card} ou nós não encontrados.")
    except Exception as e:
        print(f"❌ Erro na execução: {e}")

# Exemplo de uso
if __name__ == "__main__":
    URI = "bolt://localhost:7687"
    AUTH = ("neo4j", "sua_senha_aqui")
    
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Exemplo X4Good: LIKES (N:N)
        criar_relacionamento_cardinalidade(driver, "User", "amir123", "Post", "post99", "LIKES", "N:N")