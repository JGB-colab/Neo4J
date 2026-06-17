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
            resultado = session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
            
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
# TELA 3: GERENCIAMENTO DE RELACIONAMENTOS (CRUD COMPLETO)
# ==========================================
elif menu == "Gerenciamento de Relacionamentos":
    st.header("Central de Relacionamentos")
    st.markdown("Pesquise, crie, edite ou delete conexões do ecossistema.")

    # Função auxiliar para as listas (já existia)
    def obter_tabela_nos(label):
        if label == "User":
            query = "MATCH (n:User) RETURN n.nome AS Nome, n.username AS Username"
        elif label == "Post":
            query = "MATCH (n:Post) RETURN n.id AS ID, n.content AS Conteudo"
        elif label == "Community":
            query = "MATCH (n:Community) RETURN n.nome AS Nome"
        else:
            query = f"MATCH (n:{label}) RETURN n.id AS ID, n.nome AS Nome"
        try:
            return run_query(query)
        except Exception:
            return []

    lista_relacionamentos = [
        "FOLLOWS", "FRIEND_OF", "LIKES", "SHARES", "COMMENTS_ON", 
        "POSTED", "MEMBER_OF", "TAGGED_IN", "BLOCKED", "MUTED", 
        "VIEWED", "RECOMMENDED", "SIMILAR_TO"
    ]
    lista_labels = ["User", "Post", "Community", "Topic", "Hashtag", "Event", "Device", "Location", "Media", "Advertisement"]
    opcoes_busca = ["username", "id", "nome"]

    # Criação das 4 Abas de Operação
    tab_search, tab_create, tab_rename, tab_delete = st.tabs([
        "Pesquisar", "Criar", "Renomear", "Deletar"
    ])

    # ---------------------------------------------------------
    # ABA 1: PESQUISAR RELACIONAMENTOS (O que você pediu de visualização)
    # ---------------------------------------------------------
    with tab_search:
        st.subheader("Explorador de Conexões")
        st.write("Busque um nó específico para ver com quem/o que ele está conectado.")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            lbl_busca = st.selectbox("Buscar em qual tipo de Nó?", lista_labels, key="search_lbl")
        with col_s2:
            chave_busca = st.selectbox("Usando qual chave?", opcoes_busca, key="search_key")
            
        valor_busca = st.text_input("Digite o valor (ex: @carlos, id do post, etc):", key="search_val")
        
        if st.button("Buscar Conexões"):
            if valor_busca:
                # Query que busca o nó central e traz as setas que SAEM e ENTRAM nele
                q_search = f"""
                MATCH (centro:{lbl_busca} {{{chave_busca}: $valor}})-[r]-(vizinho)
                RETURN 
                    type(r) AS Tipo_Relacionamento, 
                    labels(vizinho)[0] AS Tipo_Vizinho, 
                    COALESCE(vizinho.username, vizinho.nome, vizinho.id, 'Desconhecido') AS Vizinho
                ORDER BY Tipo_Relacionamento
                """
                resultados_busca = run_query(q_search, {"valor": valor_busca})
                
                if resultados_busca:
                    st.success(f"Encontramos {len(resultados_busca)} conexões para '{valor_busca}':")
                    st.dataframe(resultados_busca, use_container_width=True)
                else:
                    st.warning(f"Nenhuma conexão encontrada para {lbl_busca} com {chave_busca} = '{valor_busca}'.")
            else:
                st.error("Digite um valor para buscar!")

    # ---------------------------------------------------------
    # ABA 2: CRIAR RELACIONAMENTO (Seu código original melhorado)
    # ---------------------------------------------------------
    with tab_create:
        st.subheader("Novo Relacionamento")
        
        tipo_relacao_c = st.selectbox("Qual o Tipo de Relacionamento a Criar?", lista_relacionamentos, key="create_rel")
        
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**Origem**")
            l_orig_c = st.selectbox("Nó Origem", lista_labels, index=0, key="c_l_orig")
            k_orig_c = st.selectbox("Buscar por", opcoes_busca, index=0, key="c_k_orig")
            v_orig_c = st.text_input("Valor da Origem:", key="c_v_orig")
            
        with cc2:
            st.markdown("**Destino**")
            l_dest_c = st.selectbox("Nó Destino", lista_labels, index=0, key="c_l_dest")
            k_dest_c = st.selectbox("Buscar por", opcoes_busca, index=0, key="c_k_dest")
            v_dest_c = st.text_input("Valor do Destino:", key="c_v_dest")

        if st.button("Criar Relacionamento", type="primary"):
            if v_orig_c and v_dest_c:
                q_create = f"""
                MATCH (a:{l_orig_c} {{{k_orig_c}: $orig_val}})
                MATCH (b:{l_dest_c} {{{k_dest_c}: $dest_val}})
                MERGE (a)-[r:{tipo_relacao_c}]->(b)
                ON CREATE SET r.timestamp = datetime()
                """
                try:
                    run_query(q_create, {"orig_val": v_orig_c, "dest_val": v_dest_c})
                    st.success(f"Relacionamento '{tipo_relacao_c}' criado!")
                    st.code(q_create.replace('$orig_val', f"'{v_orig_c}'").replace('$dest_val', f"'{v_dest_c}'"), language="cypher")
                except Exception as e:
                    st.error(f"Erro: {e}")
            else:
                st.error("Preencha origem e destino!")

    # ---------------------------------------------------------
    # ABA 3: RENOMEAR/ALTERAR RELACIONAMENTO
    # ---------------------------------------------------------
    with tab_rename:
        st.subheader("Renomear Tipo de Relacionamento")
        st.info("No Neo4j, nós 'renomeamos' criando uma nova conexão idêntica e deletando a antiga.")
        
        cr1, cr2 = st.columns(2)
        with cr1:
            rel_antigo = st.selectbox("De (Relacionamento Atual):", lista_relacionamentos, index=0)
            st.markdown("**Origem Atual**")
            k_orig_r = st.selectbox("Chave Origem", opcoes_busca, key="r_k_orig")
            v_orig_r = st.text_input("Valor Origem:", key="r_v_orig")
            
        with cr2:
            rel_novo = st.selectbox("Para (Novo Relacionamento):", lista_relacionamentos, index=1)
            st.markdown("**Destino Atual**")
            k_dest_r = st.selectbox("Chave Destino", opcoes_busca, key="r_k_dest")
            v_dest_r = st.text_input("Valor Destino:", key="r_v_dest")

        if st.button("Executar Renomeação"):
            if v_orig_r and v_dest_r:
                # O Cypher faz a cópia das propriedades e deleta o velho numa tacada só
                q_rename = f"""
                MATCH (a {{{k_orig_r}: $orig}})-[r_old:{rel_antigo}]->(b {{{k_dest_r}: $dest}})
                MERGE (a)-[r_new:{rel_novo}]->(b)
                SET r_new = r_old
                DELETE r_old
                """
                try:
                    run_query(q_rename, {"orig": v_orig_r, "dest": v_dest_r})
                    st.success(f"Sucesso! O relacionamento foi alterado de {rel_antigo} para {rel_novo}.")
                    st.code(q_rename.replace('$orig', f"'{v_orig_r}'").replace('$dest', f"'{v_dest_r}'"), language="cypher")
                except Exception as e:
                    st.error(f"Erro: Verifique se o relacionamento {rel_antigo} realmente existe entre os dois.")
            else:
                st.error("Preencha origem e destino!")

    # ---------------------------------------------------------
    # ABA 4: DELETAR RELACIONAMENTO
    # ---------------------------------------------------------
    with tab_delete:
        st.subheader("Deletar Relacionamento")
        st.warning("Atenção: Essa ação é irreversível!")
        
        rel_del = st.selectbox("Qual relação deseja apagar?", lista_relacionamentos, key="del_rel")
        
        cd1, cd2 = st.columns(2)
        with cd1:
            k_orig_d = st.selectbox("Chave Origem", opcoes_busca, key="d_k_orig")
            v_orig_d = st.text_input("Valor Origem:", key="d_v_orig")
        with cd2:
            k_dest_d = st.selectbox("Chave Destino", opcoes_busca, key="d_k_dest")
            v_dest_d = st.text_input("Valor Destino:", key="d_v_dest")
            
        if st.button("Deletar Definitivamente"):
            if v_orig_d and v_dest_d:
                q_delete = f"""
                MATCH (a {{{k_orig_d}: $orig}})-[r:{rel_del}]->(b {{{k_dest_d}: $dest}})
                DELETE r
                """
                try:
                    run_query(q_delete, {"orig": v_orig_d, "dest": v_dest_d})
                    st.success(f"Relacionamento '{rel_del}' deletado com sucesso!")
                    st.code(q_delete.replace('$orig', f"'{v_orig_d}'").replace('$dest', f"'{v_dest_d}'"), language="cypher")
                except Exception as e:
                    st.error(f"Erro na exclusão: {e}")
            else:
                st.error("Preencha origem e destino!")

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
                """
                registos = run_query(query_comunidades, {"username": usuario_alvo})
                if registos:
                    st.success("Comunidades que te podem interessar:")
                    st.table(registos)
                else:
                    st.warning("Não há comunidades sugeridas.")
                st.code(query_comunidades, language="cypher")