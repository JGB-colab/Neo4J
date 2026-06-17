import streamlit as st
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config

# Configuração da Página para ficar mais larga e com título
st.set_page_config(page_title="Dashboard", layout="wide")

# Configuração do Banco
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "123456789")

def run_query(query, parameters=None):
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            return session.run(query, parameters).data()

# ==========================================
# BARRA DE NAVEGAÇÃO LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("Navegação")
menu = st.sidebar.radio(
    "Escolha a tela:",
    ["Home (Visão Geral)", "Gerenciamento de Usuários", "Gerenciamento de Relacionamentos", "Motor de Recomendação"]
)
st.sidebar.markdown("---")
st.sidebar.caption("Trabalho Prático - Banco de Dados em Grafos (Neo4j)")

# ==========================================
# TELA 1: HOME (VISUALIZADOR DE GRAFOS)
# ==========================================
if menu == "Home (Visão Geral)":
    st.header("Ecossistema")
    st.markdown("Visualização interativa da teia de relacionamentos do banco de dados.")
    
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            # Busca uma amostra de nós e relacionamentos para desenhar
            resultado = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100")
            
            nodes_set = set()
            nodes = []
            edges = []
            
            for record in resultado:
                n = record["n"]
                m = record["m"]
                r = record["r"]
                
                # Extraindo propriedades para o visual (Nome ou ID)
                n_id = str(n.element_id)
                n_label = list(n.labels)[0] if n.labels else "Nó"
                n_title = n.get("nome", n.get("username", n.get("id", "Desconhecido")))
                
                m_id = str(m.element_id)
                m_label = list(m.labels)[0] if m.labels else "Nó"
                m_title = m.get("nome", m.get("username", m.get("id", "Desconhecido")))
                
                # Cores baseadas no tipo de Nó
                cores = {"User": "#4C83FF", "Post": "#FF715B", "Community": "#34D399"}
                
                if n_id not in nodes_set:
                    nodes.append(Node(id=n_id, label=n_title, size=25, color=cores.get(n_label, "#A0AEC0")))
                    nodes_set.add(n_id)
                
                if m_id not in nodes_set:
                    nodes.append(Node(id=m_id, label=m_title, size=25, color=cores.get(m_label, "#A0AEC0")))
                    nodes_set.add(m_id)
                    
                edges.append(Edge(source=n_id, target=m_id, label=type(r).__name__))

    if nodes:
        # Configuração da física e layout do grafo
        config = Config(width=900, height=500, directed=True, physics=True, hierarchical=False)
        agraph(nodes=nodes, edges=edges, config=config)
    else:
        st.warning("O banco está vazio. Crie nós e relacionamentos para ver o grafo aqui.")
        
# ==========================================
# TELA 2: GERENCIAMENTO DE USUÁRIOS
# ==========================================
elif menu == "Gerenciamento de Usuários":
    st.header("Gerenciamento de Usuários")
    nome = st.text_input("Nome do Usuário")
    username = st.text_input("Username")

    if st.button("Criar Usuário"):
        query = "CREATE (u:User {nome: $nome, username: $username})"
        run_query(query, {"nome": nome, "username": username})
        
        st.success(f"Usuário {nome} criado com sucesso no banco!")
        st.code(f"CREATE (u:User {{nome: '{nome}', username: '{username}'}})", language="cypher")

# ==========================================
# TELA 3: GERENCIAMENTO DE RELACIONAMENTOS
# ==========================================
elif menu == "Gerenciamento de Relacionamentos":
    st.header("Gerenciamento de Relacionamentos")

    def obter_tabela_nos(label):
        if label == "User":
            query = "MATCH (n:User) RETURN n.nome AS Nome, n.username AS Username LIMIT 50"
        elif label == "Post":
            query = "MATCH (n:Post) RETURN n.id AS ID, n.content AS Conteudo LIMIT 50"
        elif label == "Community":
            query = "MATCH (n:Community) RETURN n.nome AS Nome LIMIT 50"
        else:
            query = f"MATCH (n:{label}) RETURN n.id AS ID, n.nome AS Nome LIMIT 50"
        try:
            return run_query(query)
        except Exception:
            return []

    mapeamento_relacoes = {
        "FOLLOWS": {"orig": "User", "dest": "User", "busca_orig": "username", "busca_dest": "username"},
        "FRIEND_OF": {"orig": "User", "dest": "User", "busca_orig": "username", "busca_dest": "username"},
        "LIKES": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "SHARES": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "COMMENTS_ON": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "POSTED": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "MEMBER_OF": {"orig": "User", "dest": "Community", "busca_orig": "username", "busca_dest": "nome"},
        "TAGGED_IN": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "BLOCKED": {"orig": "User", "dest": "User", "busca_orig": "username", "busca_dest": "username"},
        "MUTED": {"orig": "User", "dest": "User", "busca_orig": "username", "busca_dest": "username"},
        "VIEWED": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "RECOMMENDED": {"orig": "User", "dest": "Post", "busca_orig": "username", "busca_dest": "id"},
        "SIMILAR_TO": {"orig": "User", "dest": "User", "busca_orig": "username", "busca_dest": "username"}
    }

    lista_relacionamentos = list(mapeamento_relacoes.keys())
    lista_labels = ["User", "Post", "Comment", "Community", "Topic", "Hashtag", "Event", "Device", "Location", "Media", "Advertisement"]
    opcoes_busca = ["username", "id", "nome"]

    tipo_relacao = st.selectbox("Qual o Tipo de Relacionamento?", lista_relacionamentos)
    config = mapeamento_relacoes[tipo_relacao]

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Nó de Origem")
        idx_orig = lista_labels.index(config["orig"]) if config["orig"] in lista_labels else 0
        idx_busca_orig = opcoes_busca.index(config["busca_orig"])
        
        label_origem = st.selectbox("Tipo de Nó (Origem)", lista_labels, index=idx_orig)
        chave_origem = st.selectbox("Buscar origem por:", opcoes_busca, index=idx_busca_orig, key="chave_orig")
        
        dados_origem = obter_tabela_nos(label_origem)
        if dados_origem:
            st.dataframe(dados_origem, use_container_width=True, height=150)
        else:
            st.caption(f"Nenhum {label_origem} encontrado.")
            
        valor_origem = st.text_input(f"Valor da Origem ({chave_origem}):")

    with col2:
        st.subheader("Nó de Destino")
        idx_dest = lista_labels.index(config["dest"]) if config["dest"] in lista_labels else 0
        idx_busca_dest = opcoes_busca.index(config["busca_dest"])
        
        label_destino = st.selectbox("Tipo de Nó (Destino)", lista_labels, index=idx_dest)
        chave_destino = st.selectbox("Buscar destino por:", opcoes_busca, index=idx_busca_dest, key="chave_dest")
        
        dados_destino = obter_tabela_nos(label_destino)
        if dados_destino:
            st.dataframe(dados_destino, use_container_width=True, height=150)
        else:
            st.caption(f"Nenhum {label_destino} encontrado.")
            
        valor_destino = st.text_input(f"Valor do Destino ({chave_destino}):")

    if st.button("Criar Relacionamento"):
        if valor_origem and valor_destino:
            query_relacionamento = f"""
            MATCH (a:{label_origem} {{{chave_origem}: $orig_val}})
            MATCH (b:{label_destino} {{{chave_destino}: $dest_val}})
            MERGE (a)-[r:{tipo_relacao}]->(b)
            ON CREATE SET r.timestamp = datetime()
            """
            try:
                with GraphDatabase.driver(URI, auth=AUTH) as driver:
                    with driver.session() as session:
                        resultado = session.run(query_relacionamento, orig_val=valor_origem, dest_val=valor_destino)
                        res_summary = resultado.consume()
                        
                        if res_summary.counters.relationships_created > 0:
                            st.success(f"✅ Sucesso! Relacionamento '{tipo_relacao}' criado.")
                        else:
                            st.warning("⚠️ Relacionamento não criado (já existia ou nós não encontrados).")
                st.code(query_relacionamento.replace('$orig_val', f"'{valor_origem}'").replace('$dest_val', f"'{valor_destino}'"), language="cypher")
            except Exception as e:
                st.error(f"❌ Erro de execução: {e}")
        else:
            st.error("Preencha os valores de origem e destino!")

# ==========================================
# TELA 4: MOTOR DE RECOMENDAÇÃO
# ==========================================
elif menu == "Motor de Recomendação":
    st.header("Motor de Recomendação")

    st.subheader("Usuários Disponíveis no Banco")
    query_todos_usuarios = "MATCH (u:User) RETURN u.nome AS Nome, u.username AS Username ORDER BY Nome"
    lista_usuarios = run_query(query_todos_usuarios)
            
    if lista_usuarios:
        st.dataframe(lista_usuarios, use_container_width=True)
    else:
        st.warning("O banco de dados está vazio. Crie usuários primeiro.")

    st.markdown("---")
    usuario_alvo = st.text_input("Ver recomendações para o Username (ex: teixeiraerick):")

    if usuario_alvo:
        tab1, tab2, tab3 = st.tabs(["Sugestão de Amigos", "Conteúdo Recomendado", "Comunidades Recomendadas"])
        
        with tab1:
            st.info("Lógica: Pessoas que gostaram das mesmas publicações que tu, mas que ainda não segues.")
            if st.button("Gerar Recomendações de Amigos"):
                query_amigos = """
                MATCH (u:User {username: $username})-[:LIKES]->(p:Post)<-[:LIKES]->(sugerido:User)
                WHERE u <> sugerido AND NOT (u)-[:FOLLOWS]->(sugerido)
                RETURN sugerido.nome AS SugestaoAmigo, sugerido.username AS Username, count(p) AS InteressesEmComum
                ORDER BY InteressesEmComum DESC
                LIMIT 5
                """
                registos = run_query(query_amigos, {"username": usuario_alvo})
                if registos:
                    st.success("Sugestões de novas amizades encontradas:")
                    st.table(registos)
                else:
                    st.warning("Não há sugestões no momento.")
                st.code(query_amigos, language="cypher")

        with tab2:
            st.info("Lógica: Publicações que os teus amigos gostaram, mas que tu ainda não viste/curtiste.")
            if st.button("Gerar Recomendações de Conteúdo"):
                query_conteudo = """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(amigo:User)-[:LIKES]->(p:Post)
                WHERE NOT (u)-[:LIKES]->(p)
                RETURN p.content AS PostRecomendado, amigo.nome AS QuemGostou
                LIMIT 5
                """
                registos = run_query(query_conteudo, {"username": usuario_alvo})
                if registos:
                    st.success("Publicações recomendadas para ti:")
                    st.table(registos)
                else:
                    st.warning("Não há novos conteúdos recomendados no momento.")
                st.code(query_conteudo, language="cypher")

        with tab3:
            st.info("Lógica: Comunidades onde os teus amigos estão inscritos, mas tu ainda não és membro.")
            if st.button("Gerar Recomendações de Comunidades"):
                query_comunidades = """
                MATCH (u:User {username: $username})-[:FOLLOWS]->(amigo:User)-[:MEMBER_OF]->(c:Community)
                WHERE NOT (u)-[:MEMBER_OF]->(c)
                RETURN c.nome AS ComunidadeSugerida, count(amigo) AS AmigosNaComunidade
                ORDER BY AmigosNaComunidade DESC
                LIMIT 5
                """
                registos = run_query(query_comunidades, {"username": usuario_alvo})
                if registos:
                    st.success("Comunidades que te podem interessar:")
                    st.table(registos)
                else:
                    st.warning("Não há comunidades sugeridas.")
                st.code(query_comunidades, language="cypher")