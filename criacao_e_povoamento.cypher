// ============================================================================
// SCRIPT DE CRIAÇÃO E POVOAMENTO DO BANCO DE DADOS - X4GOOD (NEO4J)
// Disciplina: Banco de Dados em Grafos
// ============================================================================

// 1. LIMPEZA DO BANCO DE DADOS (OPCIONAL - CUIDADO)
MATCH (n) DETACH DELETE n;

// ============================================================================
// 2. CRIAÇÃO DE NÓS DE CATEGORIA / ESTRUTURAIS
// ============================================================================

// Tópicos (Topic)
CREATE (t1:Topic {id: "tecnologia", nome: "Tecnologia"})
CREATE (t2:Topic {id: "jogos", nome: "Jogos"})
CREATE (t3:Topic {id: "cinema", nome: "Cinema"})
CREATE (t4:Topic {id: "educacao", nome: "Educacao"})
CREATE (t5:Topic {id: "esportes", nome: "Esportes"})
CREATE (t6:Topic {id: "financas", nome: "Financas"});

// Dispositivos (Device)
CREATE (d1:Device {id: "dev_iphone", nome: "iPhone 15 Pro", tipo: "Mobile"})
CREATE (d2:Device {id: "dev_galaxy", nome: "Samsung Galaxy S24", tipo: "Mobile"})
CREATE (d3:Device {id: "dev_macbook", nome: "MacBook Pro M3", tipo: "Desktop"})
CREATE (d4:Device {id: "dev_pc", nome: "Dell XPS Desktop", tipo: "Desktop"});

// Localizações (Location)
CREATE (l1:Location {id: "loc_ce", cidade: "Fortaleza", estado: "CE"})
CREATE (l2:Location {id: "loc_sp", cidade: "Sao Paulo", estado: "SP"})
CREATE (l3:Location {id: "loc_rj", cidade: "Rio de Janeiro", estado: "RJ"})
CREATE (l4:Location {id: "loc_ma", cidade: "Sao Luis", estado: "MA"});

// Comunidades (Community)
CREATE (c1:Community {id: "c_civil", nome: "Engenharia Civil", categoria: "Academico"})
CREATE (c2:Community {id: "c_gamer", nome: "Gamers Hardcore", categoria: "Entretenimento"})
CREATE (c3:Community {id: "c_devs", nome: "Desenvolvedores Python", categoria: "Tecnologia"})
CREATE (c4:Community {id: "c_invest", nome: "Investidores Iniciantes", categoria: "Financas"});

// Hashtags (Hashtag)
CREATE (h1:Hashtag {id: "tcema", nome: "#TCEMA"})
CREATE (h2:Hashtag {id: "eldenring", nome: "#EldenRing"})
CREATE (h3:Hashtag {id: "pythondev", nome: "#PythonDev"})
CREATE (h4:Hashtag {id: "investimentos", nome: "#Investimentos"});

// Eventos (Event)
CREATE (e1:Event {id: "evt_tce", nome: "Maratona de Questoes TCE-MA", data: "2026-07-20", plataforma: "YouTube"})
CREATE (e2:Event {id: "evt_elden", nome: "Torneio Elden Ring no Discord", data: "2026-06-30", plataforma: "Discord"})
CREATE (e3:Event {id: "evt_hack", nome: "Hackathon Python Brasil", data: "2026-08-15", plataforma: "Teams"});

// Anúncios (Advertisement)
CREATE (ad1:Advertisement {id: "ad_neo4j", titulo: "Curso de Neo4j - 50% OFF", anunciante: "Academy Tech"})
CREATE (ad2:Advertisement {id: "ad_teclado", titulo: "Novo Teclado Mecanico RGB", anunciante: "Gamer Store"});

// ============================================================================
// 3. CONEXÕES DE INFRAESTRUTURA / CATEGORIAS
// ============================================================================

// Comunidades hospedando Eventos (HOSTS)
MERGE (c1)-[r1:HOSTS]->(e1) ON CREATE SET r1.timestamp = datetime()
MERGE (c2)-[r2:HOSTS]->(e2) ON CREATE SET r2.timestamp = datetime()
MERGE (c3)-[r3:HOSTS]->(e3) ON CREATE SET r3.timestamp = datetime();

// ============================================================================
// 4. CRIAÇÃO DE USUÁRIOS E SEUS VÍNCULOS BÁSICOS
// ============================================================================

// Victor
CREATE (u_victor:User {id: "u_vic", nome: "Victor Silva", username: "victor_silva"})
// Carlos
CREATE (u_carlos:User {id: "u_car", nome: "Carlos Souza", username: "carlos_souza"})
// Ana
CREATE (u_ana:User {id: "u_ana", nome: "Ana Santos", username: "ana_santos"})
// Julia
CREATE (u_julia:User {id: "u_jul", nome: "Julia Lima", username: "julia_lima"});

// Vínculos de Localização (LOCATED_IN)
MATCH (u:User {id: "u_vic"}), (l:Location {id: "loc_ma"}) CREATE (u)-[:LOCATED_IN {timestamp: datetime()}]->(l);
MATCH (u:User {id: "u_car"}), (l:Location {id: "loc_ce"}) CREATE (u)-[:LOCATED_IN {timestamp: datetime()}]->(l);
MATCH (u:User {id: "u_ana"}), (l:Location {id: "loc_sp"}) CREATE (u)-[:LOCATED_IN {timestamp: datetime()}]->(l);
MATCH (u:User {id: "u_jul"}), (l:Location {id: "loc_rj"}) CREATE (u)-[:LOCATED_IN {timestamp: datetime()}]->(l);

// Vínculos de Dispositivos (USES_DEVICE)
MATCH (u:User {id: "u_vic"}), (d:Device {id: "dev_iphone"}) CREATE (u)-[:USES_DEVICE {timestamp: datetime(), frequencia: "diaria"}]->(d);
MATCH (u:User {id: "u_car"}), (d:Device {id: "dev_galaxy"}) CREATE (u)-[:USES_DEVICE {timestamp: datetime(), frequencia: "diaria"}]->(d);
MATCH (u:User {id: "u_car"}), (d:Device {id: "dev_pc"}) CREATE (u)-[:USES_DEVICE {timestamp: datetime(), frequencia: "semanal"}]->(d);
MATCH (u:User {id: "u_ana"}), (d:Device {id: "dev_macbook"}) CREATE (u)-[:USES_DEVICE {timestamp: datetime(), frequencia: "diaria"}]->(d);
MATCH (u:User {id: "u_jul"}), (d:Device {id: "dev_iphone"}) CREATE (u)-[:USES_DEVICE {timestamp: datetime(), frequencia: "diaria"}]->(d);

// Vínculos de Comunidades (MEMBER_OF)
MATCH (u:User {id: "u_vic"}), (c:Community {id: "c_civil"}) CREATE (u)-[:MEMBER_OF {timestamp: datetime(), role: "admin"}]->(c);
MATCH (u:User {id: "u_car"}), (c:Community {id: "c_gamer"}) CREATE (u)-[:MEMBER_OF {timestamp: datetime(), role: "member"}]->(c);
MATCH (u:User {id: "u_ana"}), (c:Community {id: "c_devs"}) CREATE (u)-[:MEMBER_OF {timestamp: datetime(), role: "member"}]->(c);
MATCH (u:User {id: "u_jul"}), (c:Community {id: "c_devs"}) CREATE (u)-[:MEMBER_OF {timestamp: datetime(), role: "member"}]->(c);
MATCH (u:User {id: "u_jul"}), (c:Community {id: "c_invest"}) CREATE (u)-[:MEMBER_OF {timestamp: datetime(), role: "member"}]->(c);

// Presença em Eventos (ATTENDS)
MATCH (u:User {id: "u_vic"}), (e:Event {id: "evt_tce"}) CREATE (u)-[:ATTENDS {timestamp: datetime(), status: "confirmado"}]->(e);
MATCH (u:User {id: "u_car"}), (e:Event {id: "evt_elden"}) CREATE (u)-[:ATTENDS {timestamp: datetime(), status: "confirmado"}]->(e);
MATCH (u:User {id: "u_ana"}), (e:Event {id: "evt_hack"}) CREATE (u)-[:ATTENDS {timestamp: datetime(), status: "confirmado"}]->(e);

// ============================================================================
// 5. CRIAÇÃO DE POSTS, COMENTÁRIOS E MÍDIAS
// ============================================================================

// Post 1 - Victor
CREATE (p1:Post {id: "post_v1", content: "Estudando para o concurso do TCE-MA com foco total!"});
MATCH (u:User {id: "u_vic"}), (p:Post {id: "post_v1"}) CREATE (u)-[:POSTED {timestamp: datetime()}]->(p);
MATCH (p:Post {id: "post_v1"}), (t:Topic {id: "educacao"}) CREATE (p)-[:HAS_TOPIC]->(t);
MATCH (p:Post {id: "post_v1"}), (h:Hashtag {id: "tcema"}) CREATE (p)-[:TAGGED_WITH {timestamp: datetime()}]->(h);

// Comentário no Post 1 - Carlos
CREATE (cmt1:Comment {id: "cmt_01", texto: "Muito bom, Victor! Foco na aprovação."});
MATCH (u:User {id: "u_car"}), (c:Comment {id: "cmt_01"}) CREATE (u)-[:POSTED {timestamp: datetime()}]->(c);
MATCH (c:Comment {id: "cmt_01"}), (p:Post {id: "post_v1"}) CREATE (c)-[:COMMENTS_ON {timestamp: datetime()}]->(p);

// Post 2 - Ana
CREATE (p2:Post {id: "post_a1", content: "Desenvolvendo automações com Python e Neo4j hoje."});
MATCH (u:User {id: "u_ana"}), (p:Post {id: "post_a1"}) CREATE (u)-[:POSTED {timestamp: datetime()}]->(p);
MATCH (p:Post {id: "post_a1"}), (t:Topic {id: "tecnologia"}) CREATE (p)-[:HAS_TOPIC]->(t);
MATCH (p:Post {id: "post_a1"}), (h:Hashtag {id: "pythondev"}) CREATE (p)-[:TAGGED_WITH {timestamp: datetime()}]->(h);

// Mídia no Post 2
CREATE (m1:Media {id: "media_a1", url: "https://media.x4good.com/files/print_code.png", tipo: "imagem"});
MATCH (u:User {id: "u_ana"}), (m:Media {id: "media_a1"}) CREATE (u)-[:POSTED {timestamp: datetime()}]->(m);
MATCH (p:Post {id: "post_a1"}), (m:Media {id: "media_a1"}) CREATE (p)-[:CONTAINS_MEDIA]->(m);

// Post 3 - Julia
CREATE (p3:Post {id: "post_j1", content: "Dicas de fundos imobiliários para começar a investir."});
MATCH (u:User {id: "u_jul"}), (p:Post {id: "post_j1"}) CREATE (u)-[:POSTED {timestamp: datetime()}]->(p);
MATCH (p:Post {id: "post_j1"}), (t:Topic {id: "financas"}) CREATE (p)-[:HAS_TOPIC]->(t);
MATCH (p:Post {id: "post_j1"}), (h:Hashtag {id: "investimentos"}) CREATE (p)-[:TAGGED_WITH {timestamp: datetime()}]->(h);

// ============================================================================
// 6. CONEXÕES SOCIAIS E INTERAÇÕES
// ============================================================================

// Seguidores (FOLLOWS)
MATCH (u1:User {id: "u_vic"}), (u2:User {id: "u_car"}) CREATE (u1)-[:FOLLOWS {timestamp: datetime()}]->(u2);
MATCH (u1:User {id: "u_car"}), (u2:User {id: "u_vic"}) CREATE (u1)-[:FOLLOWS {timestamp: datetime()}]->(u2);
MATCH (u1:User {id: "u_ana"}), (u2:User {id: "u_jul"}) CREATE (u1)-[:FOLLOWS {timestamp: datetime()}]->(u2);
MATCH (u1:User {id: "u_jul"}), (u2:User {id: "u_ana"}) CREATE (u1)-[:FOLLOWS {timestamp: datetime()}]->(u2);

// Amizades (FRIEND_OF)
MATCH (u1:User {id: "u_vic"}), (u2:User {id: "u_car"}) CREATE (u1)-[:FRIEND_OF {timestamp: datetime()}]->(u2), (u2)-[:FRIEND_OF {timestamp: datetime()}]->(u1);
MATCH (u1:User {id: "u_ana"}), (u2:User {id: "u_jul"}) CREATE (u1)-[:FRIEND_OF {timestamp: datetime()}]->(u2), (u2)-[:FRIEND_OF {timestamp: datetime()}]->(u1);

// Curtidas (LIKES)
MATCH (u:User {id: "u_car"}), (p:Post {id: "post_v1"}) CREATE (u)-[:LIKES {timestamp: datetime(), reaction: "love"}]->(p);
MATCH (u:User {id: "u_jul"}), (p:Post {id: "post_a1"}) CREATE (u)-[:LIKES {timestamp: datetime(), reaction: "like"}]->(p);
MATCH (u:User {id: "u_ana"}), (p:Post {id: "post_j1"}) CREATE (u)-[:LIKES {timestamp: datetime(), reaction: "wow"}]->(p);

// Compartilhamentos (SHARES)
MATCH (u:User {id: "u_car"}), (p:Post {id: "post_v1"}) CREATE (u)-[:SHARES {timestamp: datetime()}]->(p);
MATCH (u:User {id: "u_jul"}), (p:Post {id: "post_a1"}) CREATE (u)-[:SHARES {timestamp: datetime()}]->(p);

// Visualizações (VIEWED)
MATCH (u:User {id: "u_vic"}), (p:Post {id: "post_a1"}) CREATE (u)-[:VIEWED {timestamp: datetime(), cliques: 2}]->(p);
MATCH (u:User {id: "u_car"}), (p:Post {id: "post_a1"}) CREATE (u)-[:VIEWED {timestamp: datetime(), cliques: 1}]->(p);
MATCH (u:User {id: "u_jul"}), (p:Post {id: "post_v1"}) CREATE (u)-[:VIEWED {timestamp: datetime(), cliques: 4}]->(p);

// Marcações em posts (TAGGED_IN)
MATCH (u:User {id: "u_car"}), (p:Post {id: "post_v1"}) CREATE (u)-[:TAGGED_IN {timestamp: datetime()}]->(p);

// Silenciamentos e Bloqueios (MUTED / BLOCKED)
MATCH (u1:User {id: "u_vic"}), (u2:User {id: "u_jul"}) CREATE (u1)-[:MUTED {timestamp: datetime()}]->(u2);

// Relações de Similaridade (SIMILAR_TO)
MATCH (u1:User {id: "u_ana"}), (u2:User {id: "u_jul"}) CREATE (u1)-[:SIMILAR_TO {score: 0.90, timestamp: datetime()}]->(u2);
