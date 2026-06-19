import random
from neo4j import GraphDatabase
from faker import Faker

# Configuração do Neo4j (Usando o usuário e senha exatos do teste.py)
URI = "neo4j+ssc://cb84c387.databases.neo4j.io"
AUTH = ("cb84c387", "1xe1FMi49ZrfSzUvfOfzK_j8GKGqqFblHkvsQrQZVjc")
with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()


# Inicializando o Faker para português do Brasil
fake = Faker('pt_BR')

def povoar_banco(driver, num_users=12, num_posts_max=3):
    print("Iniciando o povoamento do banco de dados Neo4j")
    
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
            ("loc_ce", "Fortaleza", "CE"),
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

        # Conectar Eventos as Comunidades correspondentes (HOSTS) usando ON CREATE SET
        session.run("MATCH (c:Community {id: 'c_civil'}), (e:Event {id: 'evt_tce'}) MERGE (c)-[r:HOSTS]->(e) ON CREATE SET r.timestamp = datetime()")
        session.run("MATCH (c:Community {id: 'c_gamer'}), (e:Event {id: 'evt_elden'}) MERGE (c)-[r:HOSTS]->(e) ON CREATE SET r.timestamp = datetime()")
        session.run("MATCH (c:Community {id: 'c_devs'}), (e:Event {id: 'evt_hack'}) MERGE (c)-[r:HOSTS]->(e) ON CREATE SET r.timestamp = datetime()")
        session.run("MATCH (c:Community {id: 'c_invest'}), (e:Event {id: 'evt_webinar'}) MERGE (c)-[r:HOSTS]->(e) ON CREATE SET r.timestamp = datetime()")

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
            
            # Relacionamento: LOCATED_IN
            loc = random.choice(locations)
            session.run(
                """
                MATCH (u:User {id: $uid}), (l:Location {id: $lid})
                MERGE (u)-[r:LOCATED_IN]->(l)
                ON CREATE SET r.timestamp = datetime()
                """,
                uid=user_id, lid=loc[0]
            )

            # Relacionamento: USES_DEVICE
            devs = random.sample(devices, random.randint(1, 2))
            for dev in devs:
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (d:Device {id: $did})
                    MERGE (u)-[r:USES_DEVICE]->(d)
                    ON CREATE SET r.timestamp = datetime(), r.frequencia = 'diaria'
                    """,
                    uid=user_id, did=dev[0]
                )

            # Relacionamento: MEMBER_OF
            comm_selection = random.sample(communities, random.randint(1, 3))
            for comm in comm_selection:
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (c:Community {id: $cid})
                    MERGE (u)-[r:MEMBER_OF]->(c)
                    ON CREATE SET r.timestamp = datetime(), r.role = 'member'
                    """,
                    uid=user_id, cid=comm[0]
                )

            # Relacionamento: ATTENDS
            for comm in comm_selection:
                if random.choice([True, False]):
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (c:Community {id: $cid})-[:HOSTS]->(e:Event)
                        MERGE (u)-[r:ATTENDS]->(e)
                        ON CREATE SET r.timestamp = datetime(), r.status = 'confirmado'
                        """,
                        uid=user_id, cid=comm[0]
                    )

        # 9. CRIANDO POSTS
        print("[10/11] Gerando posts e conectando a Topicos, Hashtags e Midias...")
        posts_ids = []
        for uid in users_ids:
            for _ in range(random.randint(1, num_posts_max)):
                post_id = fake.uuid4()
                content = fake.sentence(nb_words=10)
                
                session.run(
                    """
                    MATCH (u:User {id: $uid})
                    CREATE (p:Post {id: $pid, content: $content})
                    CREATE (u)-[:POSTED {timestamp: datetime()}]->(p)
                    """,
                    uid=uid, pid=post_id, content=content
                )
                posts_ids.append(post_id)

                # Relacionamento: HAS_TOPIC
                top = random.choice(topics).lower()
                session.run(
                    """
                    MATCH (p:Post {id: $pid}), (t:Topic {id: $tid})
                    MERGE (p)-[:HAS_TOPIC]->(t)
                    """,
                    pid=post_id, tid=top
                )

                # Relacionamento: TAGGED_WITH
                post_tags = random.sample(hashtags, random.randint(0, 2))
                for t in post_tags:
                    session.run(
                        """
                        MATCH (p:Post {id: $pid}), (h:Hashtag {id: $hid})
                        MERGE (p)-[r:TAGGED_WITH]->(h)
                        ON CREATE SET r.timestamp = datetime()
                        """,
                        pid=post_id, hid=t.lower()
                    )

                # Criar Media associada ao post
                if random.choice([True, False]):
                    media_id = fake.uuid4()
                    m_type = random.choice(["imagem", "video"])
                    m_url = f"https://media.x4good.com/files/{media_id}.{'png' if m_type == 'imagem' else 'mp4'}"
                    
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
            for _ in range(random.randint(0, 2)):
                comentador_id = random.choice(users_ids)
                comment_id = fake.uuid4()
                texto = fake.sentence(nb_words=8)
                
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
            # FOLLOWS
            seguindo = random.sample(users_ids, random.randint(1, min(4, len(users_ids))))
            for seg_id in seguindo:
                if uid != seg_id:
                    session.run(
                        """
                        MATCH (u1:User {id: $uid}), (u2:User {id: $seg_id})
                        MERGE (u1)-[r:FOLLOWS]->(u2)
                        ON CREATE SET r.timestamp = datetime()
                        """,
                        uid=uid, seg_id=seg_id
                    )

            # FRIEND_OF
            amigos = random.sample(users_ids, random.randint(1, min(2, len(users_ids))))
            for amigo_id in amigos:
                if uid != amigo_id:
                    session.run(
                        """
                        MATCH (u1:User {id: $uid}), (u2:User {id: $amigo_id})
                        MERGE (u1)-[r1:FRIEND_OF]->(u2)
                        ON CREATE SET r1.timestamp = datetime()
                        MERGE (u2)-[r2:FRIEND_OF]->(u1)
                        ON CREATE SET r2.timestamp = datetime()
                        """,
                        uid=uid, amigo_id=amigo_id
                    )

            # LIKES (Este já estava correto no código original)
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

            # SHARES
            if posts_ids:
                compartilhados = random.sample(posts_ids, random.randint(0, min(2, len(posts_ids))))
                for pid in compartilhados:
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        MERGE (u)-[r:SHARES]->(p)
                        ON CREATE SET r.timestamp = datetime()
                        """,
                        uid=uid, pid=pid
                    )

            # VIEWED
            if posts_ids:
                visualizados = random.sample(posts_ids, random.randint(1, min(6, len(posts_ids))))
                for pid in visualizados:
                    session.run(
                        """
                        MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                        MERGE (u)-[r:VIEWED]->(p)
                        ON CREATE SET r.timestamp = datetime(), r.cliques = 3
                        """,
                        uid=uid, pid=pid
                    )

            # TAGGED_IN
            if posts_ids and random.random() < 0.15:
                pid = random.choice(posts_ids)
                session.run(
                    """
                    MATCH (u:User {id: $uid}), (p:Post {id: $pid})
                    MERGE (u)-[r:TAGGED_IN]->(p)
                    ON CREATE SET r.timestamp = datetime()
                    """,
                    uid=uid, pid=pid
                )

            # BLOCKED / MUTED
            if random.random() < 0.15:
                alvo = random.choice(users_ids)
                if uid != alvo:
                    rel_type = random.choice(["BLOCKED", "MUTED"])
                    session.run(
                        f"""
                        MATCH (u1:User {{id: $uid}}), (u2:User {{id: $alvo}})
                        MERGE (u1)-[r:{rel_type}]->(u2)
                        ON CREATE SET r.timestamp = datetime()
                        """,
                        uid=uid, alvo=alvo
                    )

            # SIMILAR_TO
            alvo_sim = random.choice(users_ids)
            if uid != alvo_sim:
                session.run(
                    """
                    MATCH (u1:User {id: $uid}), (u2:User {id: $alvo})
                    MERGE (u1)-[r:SIMILAR_TO]->(u2)
                    ON CREATE SET r.score = 0.85, r.timestamp = datetime()
                    """,
                    uid=uid, alvo=alvo_sim
                )

    print("Povoamento concluido com sucesso!")

# Execucao principal
if __name__ == "__main__":
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        povoar_banco(driver, num_users=12)