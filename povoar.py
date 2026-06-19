import random
from neo4j import GraphDatabase
from faker import Faker

# Configuração do Neo4j (Ajuste a senha para a sua)
URI = "neo4j+ssc://cb84c387.databases.neo4j.io"
AUTH = ("...", "...")
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()


# Inicializando o Faker para português do Brasil
fake = Faker('pt_BR')

def povoar_banco(driver, num_users=12, num_posts_max=3):
    print("Iniciando o povoamento da rede X4Good...")
    
    with driver.session() as session:
        # Limpa o banco antes de popular
        print("[1/11] Limpando banco de dados para o novo povoamento...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # 1. CRIANDO TOPICOS (Topic)
        print("[2/11] Criando Topicos...")
        topics = ["Tecnologia", "Jogos", "Cinema", "Educacao", "Esportes", "Saude", "Moda", "Financas", "Musica"]
        for topic in topics:
            session.run("CREATE (:Topic {id: $id, nome: $nome})", id=topic.lower(), nome=topic)

        # 2. CRIANDO DISPOSITIVOS (Device)
        print("[3/11] Criando Dispositivos...")
        devices = [
            ("dev_iphone", "iPhone 15 Pro", "Mobile"),
            ("dev_galaxy", "Samsung Galaxy S24", "Mobile"),
            ("dev_macbook", "MacBook Pro M3", "Desktop"),
            ("dev_pc", "Dell XPS Desktop", "Desktop"),
            ("dev_ipad", "iPad Air", "Tablet")
        ]
        for dev_id, name, dev_type in devices:
            session.run("CREATE (:Device {id: $id, nome: $nome, tipo: $tipo})", id=dev_id, nome=name, tipo=dev_type)

        # 3. CRIANDO LOCALIZACOES (Location)
        print("[4/11] Criando Localizacoes...")
        locations = [
            ("loc_sp", "Sao Paulo", "SP"),
            ("loc_rj", "Rio de Janeiro", "RJ"),
            ("loc_mg", "Belo Horizonte", "MG"),
            ("loc_ma", "Sao Luis", "MA"),
            ("loc_ba", "Salvador", "BA"),
            ("loc_rs", "Porto Alegre", "RS")
        ]
        for loc_id, city, state in locations:
            session.run("CREATE (:Location {id: $id, cidade: $cidade, estado: $estado})", id=loc_id, cidade=city, estado=state)

        # 4. CRIANDO COMUNIDADES (Community)
        print("[5/11] Criando Comunidades...")
        communities = [
            ("c_civil", "Engenharia Civil", "Academico"),
            ("c_gamer", "Gamers Hardcore", "Entretenimento"),
            ("c_devs", "Desenvolvedores Python", "Tecnologia"),
            ("c_invest", "Investidores Iniciantes", "Financas")
        ]
        for c_id, name, cat in communities:
            session.run("CREATE (:Community {id: $id, nome: $nome, categoria: $categoria})", id=c_id, nome=name, categoria=cat)

        # 5. CRIANDO HASHTAGS (Hashtag)
        print("[6/11] Criando Hashtags...")
        hashtags = ["TCEMA", "EldenRing", "PythonDev", "Investimentos", "IA", "Tech2026", "VagasDev"]
        for h in hashtags:
            session.run("CREATE (:Hashtag {id: $id, nome: $nome})", id=h.lower(), nome=f"#{h}")

        # 6. CRIANDO EVENTOS (Event)
        print("[7/11] Criando Eventos...")
        events = [
            ("evt_tce", "Maratona de Questoes TCE-MA", "2026-07-20", "YouTube"),
            ("evt_elden", "Torneio Elden Ring no Discord", "2026-06-30", "Discord"),
            ("evt_hack", "Hackathon Python Brasil", "2026-08-15", "Teams"),
            ("evt_webinar", "Webinar: Como investir em FIIs", "2026-07-05", "Zoom")
        ]
        for evt_id, name, date, platform in events:
            session.run(
                "CREATE (:Event {id: $id, nome: $nome, data: $data, plataforma: $plataforma})",
                id=evt_id, nome=name, data=date, plataforma=platform
            )

        # Conectar Eventos as Comunidades correspondentes (HOSTS)
        session.run("MATCH (c:Community {id: 'c_civil'}), (e:Event {id: 'evt_tce'}) MERGE (c)-[:HOSTS {timestamp: datetime()}]->(e)")
        session.run("MATCH (c:Community {id: 'c_gamer'}), (e:Event {id: 'evt_elden'}) MERGE (c)-[:HOSTS {timestamp: datetime()}]->(e)")
        session.run("MATCH (c:Community {id: 'c_devs'}), (e:Event {id: 'evt_hack'}) MERGE (c)-[:HOSTS {timestamp: datetime()}]->(e)")
        session.run("MATCH (c:Community {id: 'c_invest'}), (e:Event {id: 'evt_webinar'}) MERGE (c)-[:HOSTS {timestamp: datetime()}]->(e)")

        # 7. CRIANDO ANUNCIOS (Advertisement)
        print("[8/11] Criando Anuncios...")
        ads = [
            ("ad_neo4j", "Curso Completo de Neo4j - 50% OFF", "Academy Tech"),
            ("ad_teclado", "Novo Teclado Mecanico RGB Sem Fio", "Gamer Store"),
            ("ad_corretora", "Abra sua conta e ganhe 10 fundos imobiliarios", "Invest Facil")
        ]
        for ad_id, title, advertiser in ads:
            session.run("CREATE (:Advertisement {id: $id, titulo: $titulo, anunciante: $anunciante})", id=ad_id, titulo=title, anunciante=advertiser)

        # 8. CRIANDO USUARIOS
        print(f"[9/11] Criando {num_users} usuarios e atribuindo Local, Dispositivos e Comunidades...")
        users_ids = []
        user_usernames = []
        for i in range(num_users):
            user_id = fake.uuid4()
            name = fake.name()
            username = fake.user_name() + str(random.randint(10, 99))
            
            session.run(
                "CREATE (u:User {id: $id, nome: $nome, username: $username})",
                id=user_id, nome=name, username=username
            )
            users_ids.append(user_id)
            user_usernames.append(username)
            
            # Relacionamento: LOCATED_IN (1:N - Usuario esta em uma localizacao)
            loc = random.choice(locations)
            session.run(
                """
                MATCH (u:User {id: $uid}), (l:Location {id: $lid})
                MERGE (u)-[:LOCATED_IN {timestamp: datetime()}]->(l)
                """,
                uid=user_id, lid=loc[0]
            )

            # Relacionamento: USES_DEVICE (N:N - Usuario usa um ou mais dispositivos)
            devs = random.sample(devices, random.randint(1, 2))
            for dev in devs:
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (d:Device {id: $did})
                    MERGE (u)-[:USES_DEVICE {timestamp: datetime(), frequencia: 'diaria'}]->(d)
                    """,
                    uid=user_id, did=dev[0]
                )

            # Relacionamento: MEMBER_OF (N:N - Usuario entra em 1 a 3 comunidades)
            comm_selection = random.sample(communities, random.randint(1, 3))
            for comm in comm_selection:
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (c:Community {id: $cid})
                    MERGE (u)-[:MEMBER_OF {timestamp: datetime(), role: 'member'}]->(c)
                    """,
                    uid=user_id, cid=comm[0]
                )

            # Relacionamento: ATTENDS (N:N - Usuario participa de eventos vinculados as suas comunidades)
            for comm in comm_selection:
                # Se a comunidade tiver evento, ha 50% de chance de participar
                if random.choice([True, False]):
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (c:Community {id: $cid})-[:HOSTS]->(e:Event)
                        MERGE (u)-[:ATTENDS {timestamp: datetime(), status: 'confirmado'}]->(e)
                        """,
                        uid=user_id, cid=comm[0]
                    )

        # 9. CRIANDO POSTS
        print("[10/11] Gerando posts e conectando a Topicos, Hashtags e Midias...")
        posts_ids = []
        for uid in users_ids:
            # Cada usuario faz de 0 a max posts
            for _ in range(random.randint(1, num_posts_max)):
                post_id = fake.uuid4()
                content = fake.sentence(nb_words=10)
                
                # Cria post e conecta via POSTED
                session.run(
                    """
                    MATCH (u:User {id: $uid})
                    CREATE (p:Post {id: $pid, content: $content})
                    CREATE (u)-[:POSTED {timestamp: datetime()}]->(p)
                    """,
                    uid=uid, pid=post_id, content=content
                )
                posts_ids.append(post_id)

                # Relacionamento: HAS_TOPIC (Cada post tem um topico aleatorio)
                top = random.choice(topics).lower()
                session.run(
                    """
                    MATCH (p:Post {id: $pid}), (t:Topic {id: $tid})
                    MERGE (p)-[:HAS_TOPIC]->(t)
                    """,
                    pid=post_id, tid=top
                )

                # Relacionamento: TAGGED_WITH (Post tem hashtags aleatorias)
                post_tags = random.sample(hashtags, random.randint(0, 2))
                for t in post_tags:
                    session.run(
                        """
                        MATCH (p:Post {id: $pid}), (h:Hashtag {id: $hid})
                        MERGE (p)-[:TAGGED_WITH {timestamp: datetime()}]->(h)
                        """,
                        pid=post_id, hid=t.lower()
                    )

                # Criar Media associada ao post (50% de chance)
                if random.choice([True, False]):
                    media_id = fake.uuid4()
                    m_type = random.choice(["imagem", "video"])
                    m_url = f"https://media.x4good.com/files/{media_id}.{'png' if m_type == 'imagem' else 'mp4'}"
                    
                    # Usuario posta a midia e a midia e associada ao post
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        CREATE (m:Media {id: $mid, url: $url, tipo: $tipo})
                        CREATE (u)-[:POSTED {timestamp: datetime()}]->(m)
                        CREATE (p)-[:CONTAINS_MEDIA]->(m)
                        """,
                        uid=uid, pid=post_id, mid=media_id, url=m_url, tipo=m_type
                    )

        # 10. CRIANDO COMENTARIOS (Comment)
        print("[10.5/11] Gerando comentarios...")
        for pid in posts_ids:
            # Cada post recebe de 0 a 2 comentarios de usuarios aleatorios
            for _ in range(random.randint(0, 2)):
                comentador_id = random.choice(users_ids)
                comment_id = fake.uuid4()
                texto = fake.sentence(nb_words=8)
                
                # Usuario posta o comentario e comentario esta associado ao post via COMMENTS_ON
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                    CREATE (c:Comment {id: $cid, texto: $texto})
                    CREATE (u)-[:POSTED {timestamp: datetime()}]->(c)
                    CREATE (c)-[:COMMENTS_ON {timestamp: datetime()}]->(p)
                    """,
                    uid=comentador_id, pid=pid, cid=comment_id, texto=texto
                )

        # 11. CRIANDO INTERACOES DA REDE SOCIAL
        print("[11/11] Construindo conexoes sociais...")
        for uid in users_ids:
            # FOLLOWS: Segue 1 a 4 pessoas aleatorias
            seguindo = random.sample(users_ids, random.randint(1, min(4, len(users_ids))))
            for seg_id in seguindo:
                if uid != seg_id:
                    session.run(
                        "MATCH (u1:User {id: $uid}), (u2:User {id: $seg_id}) MERGE (u1)-[:FOLLOWS {timestamp: datetime()}]->(u2)",
                        uid=uid, seg_id=seg_id
                    )

            # FRIEND_OF: Amizade com 1 a 2 pessoas (mutuo)
            amigos = random.sample(users_ids, random.randint(1, min(2, len(users_ids))))
            for amigo_id in amigos:
                if uid != amigo_id:
                    session.run(
                        """
                        MATCH (u1:User {id: $uid}), (u2:User {id: $amigo_id})
                        MERGE (u1)-[:FRIEND_OF {timestamp: datetime()}]->(u2)
                        MERGE (u2)-[:FRIEND_OF {timestamp: datetime()}]->(u1)
                        """,
                        uid=uid, amigo_id=amigo_id
                    )

            # LIKES: Curte 1 a 5 posts aleatorios
            if posts_ids:
                curtidos = random.sample(posts_ids, random.randint(1, min(5, len(posts_ids))))
                for pid in curtidos:
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        MERGE (u)-[r:LIKES]->(p)
                        ON CREATE SET r.reaction = $reaction, r.timestamp = datetime()
                        """,
                        uid=uid, pid=pid, reaction=random.choice(["love", "like", "haha", "wow"])
                    )

            # SHARES: Compartilha 0 a 2 posts aleatorios
            if posts_ids:
                compartilhados = random.sample(posts_ids, random.randint(0, min(2, len(posts_ids))))
                for pid in compartilhados:
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        MERGE (u)-[:SHARES {timestamp: datetime()}]->(p)
                        """,
                        uid=uid, pid=pid
                    )

            # VIEWED: Visualiza 1 a 6 posts aleatorios
            if posts_ids:
                visualizados = random.sample(posts_ids, random.randint(1, min(6, len(posts_ids))))
                for pid in visualizados:
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        MERGE (u)-[:VIEWED {timestamp: datetime(), cliques: 3}]->(p)
                        """,
                        uid=uid, pid=pid
                    )

            # TAGGED_IN: Marcado em posts (15% de chance)
            if posts_ids and random.random() < 0.15:
                pid = random.choice(posts_ids)
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                    MERGE (u)-[:TAGGED_IN {timestamp: datetime()}]->(p)
                    """,
                    uid=uid, pid=pid
                )

            # BLOCKED / MUTED (15% de chance de bloquear ou silenciar alguem aleatorio)
            if random.random() < 0.15:
                alvo = random.choice(users_ids)
                if uid != alvo:
                    rel_type = random.choice(["BLOCKED", "MUTED"])
                    session.run(
                        f"MATCH (u1:User {{id: $uid}}), (u2:User {{id: $alvo}}) MERGE (u1)-[:{rel_type} {{timestamp: datetime()}}]->(u2)",
                        uid=uid, alvo=alvo
                    )

            # SIMILAR_TO (Simular relacoes de similaridade calculadas pelo sistema)
            alvo_sim = random.choice(users_ids)
            if uid != alvo_sim:
                session.run(
                    """
                    MATCH (u1:User {id: $uid}), (u2:User {id: $alvo})
                    MERGE (u1)-[:SIMILAR_TO {score: 0.85, timestamp: datetime()}]->(u2)
                    """,
                    uid=uid, alvo=alvo_sim
                )

    print("Povoamento concluido com sucesso!")

# Execucao principal
if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        povoar_banco(driver, num_users=12)