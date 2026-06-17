import random
from neo4j import GraphDatabase
from faker import Faker

# Configuração do Neo4j (Ajuste a senha para a sua)
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "123456789")

# Inicializando o Faker para português do Brasil
fake = Faker('pt_BR')

def povoar_banco(driver, num_users=10, num_posts_max=3):
    print("Iniciando o povoamento da rede X4Good...")
    
    users_ids = []
    posts_ids = []
    
    with driver.session() as session:
        # 1. CRIANDO USUÁRIOS
        print(f"👥 Criando {num_users} usuários...")
        for _ in range(num_users):
            user_id = fake.uuid4()
            name = fake.name()
            username = fake.user_name()
            
            session.run(
                "CREATE (u:User {id: $id, nome: $nome, username: $username})",
                id=user_id, nome=name, username=username
            )
            users_ids.append(user_id)
            
        # 2. CRIANDO POSTS (Ligados aos usuários com a relação POSTED)
        print("Gerando posts aleatórios...")
        for uid in users_ids:
            # Cada usuário faz de 0 a max posts
            for _ in range(random.randint(0, num_posts_max)):
                post_id = fake.uuid4()
                content = fake.sentence(nb_words=10)
                
                # Cria o post e já conecta ao usuário criador
                session.run(
                    """
                    MATCH (u:User {id: $uid})
                    CREATE (p:Post {id: $pid, content: $content})
                    CREATE (u)-[:POSTED]->(p)
                    """,
                    uid=uid, pid=post_id, content=content
                )
                posts_ids.append(post_id)

        # 3. GERANDO INTERAÇÕES (FOLLOWS e LIKES)
        print("Construindo a teia social (Seguidores e Curtidas)...")
        for uid in users_ids:
            # Usuário segue de 1 a 5 pessoas aleatórias
            amigos = random.sample(users_ids, random.randint(1, 5))
            for amigo_id in amigos:
                if uid != amigo_id: # Não seguir a si mesmo
                    session.run(
                        """
                        MATCH (u1:User {id: $uid}), (u2:User {id: $amigo_id})
                        MERGE (u1)-[:FOLLOWS]->(u2)
                        """,
                        uid=uid, amigo_id=amigo_id
                    )
            
            # Usuário curte de 1 a 8 posts aleatórios
            if posts_ids:
                posts_curtidos = random.sample(posts_ids, random.randint(1, min(8, len(posts_ids))))
                for pid in posts_curtidos:
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        MERGE (u)-[r:LIKES]->(p)
                        ON CREATE SET r.reaction = 'love', r.timestamp = datetime()
                        """,
                        uid=uid, pid=pid
                    )

    print("Povoamento concluído com sucesso!")

# Execução principal
if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        # Limpa o banco antes de popular (Opcional, mas recomendado para testes)
        # with driver.session() as session:
        #     session.run("MATCH (n) DETACH DELETE n")
        #     print("Banco de dados limpo para receber os novos dados.")
            
        povoar_banco(driver, num_users=10)