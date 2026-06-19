import streamlit as st
from neo4j import GraphDatabase
from streamlit_agraph import agraph, Node, Edge, Config
import uuid
import datetime

# Configuração da Página
st.set_page_config(page_title="X4Good - Dashboard de Grafos", layout="wide", page_icon="🕸️")

# Estilização CSS customizada (Aesthetics & Typography)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;800&display=swap');

/* Fonte Principal */
* {
    font-family: 'Outfit', sans-serif;
}

/* Título com Degradê */
.main-title {
    background: linear-gradient(135deg, #4C83FF 0%, #EC4899 50%, #FF715B 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.8rem;
    margin-bottom: 0.1rem;
    text-align: left;
}

.subtitle {
    color: #8A8F98;
    font-size: 1.1rem;
    font-weight: 400;
    margin-bottom: 1.5rem;
}

/* Estilo Glassmorphism para os cards */
.glass-card {
    background: rgba(128, 128, 128, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Badge de Cores para Legenda */
.legend-badge {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 50%;
    margin-right: 6px;
    vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR - CONFIGURAÇÃO E NAVEGAÇÃO
# ==========================================
st.sidebar.markdown("<h2 style='text-align: center; color: #4C83FF;'>🕸️ X4Good System</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

# Valores padrão de conexão (com suporte a Streamlit Secrets na nuvem)
default_uri = "bolt://localhost:7687"
default_user = "neo4j"
default_pass = "123456789"

try:
    if "NEO4J_URI" in st.secrets:
        default_uri = st.secrets["NEO4J_URI"]
    if "NEO4J_USER" in st.secrets:
        default_user = st.secrets["NEO4J_USER"]
    if "NEO4J_PASSWORD" in st.secrets:
        default_pass = st.secrets["NEO4J_PASSWORD"]
except Exception:
    pass

st.sidebar.subheader("🔌 Conexão Neo4j")
neo4j_uri = st.sidebar.text_input("URI do Banco", value=default_uri, key="neo4j_uri")
neo4j_user = st.sidebar.text_input("Usuário", value=default_user, key="neo4j_user")
neo4j_password = st.sidebar.text_input("Senha", value=default_pass, type="password", key="neo4j_pwd")

def get_driver():
    return GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def run_query(query, parameters=None):
    with get_driver() as driver:
        with driver.session() as session:
            return session.run(query, parameters).data()

# Testar conexão de forma elegante na barra lateral
try:
    with get_driver() as d:
        d.verify_connectivity()
    st.sidebar.success("🟢 Conectado ao Neo4j!")
except Exception as e:
    st.sidebar.error(f"🔴 Erro de Conexão: {e}")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Navegação")
menu = st.sidebar.radio(
    "Selecione uma tela:",
    [
        "Home (Visão Geral)", 
        "Gerenciamento de Entidades (CRUD)", 
        "Central de Relacionamentos", 
        "Ações & Simulação de Usuário",
        "Motor de Recomendação"
    ]
)
st.sidebar.markdown("---")
st.sidebar.caption("Trabalho Prático - Banco de Dados em Grafos (Neo4j)")

# Título Principal do Dashboard
st.markdown("<div class='main-title'>X4Good Graph Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Ecosystem Explorer, CRUD Manager, and Recommendation Engine</div>", unsafe_allow_html=True)

# Cores de design para os diferentes nós do ecossistema
CORES_NOS = {
    "User": "#4C83FF",          # Sleek blue
    "Post": "#FF715B",          # Coral red
    "Comment": "#F59E0B",       # Orange/Amber
    "Community": "#10B981",     # Emerald green
    "Topic": "#8B5CF6",         # Violet
    "Hashtag": "#EC4899",       # Pink
    "Event": "#3B82F6",         # Light Blue
    "Device": "#6B7280",        # Gray
    "Location": "#06B6D4",      # Cyan
    "Media": "#F43F5E",         # Rose
    "Advertisement": "#14B8A6"  # Teal
}

# ==========================================
# TELA 1: HOME (VISUALIZADOR DE GRAFOS)
# ==========================================
if menu == "Home (Visão Geral)":
    st.header("🌐 O Ecossistema em Rede")
    st.markdown("Visualização interativa em tempo real de todas as entidades e interações do X4Good.")
    
    # Exibir a legenda dos nós com cores bonitas
    st.markdown("<div class='glass-card'><strong>Legenda dos Nós:</strong><br>" + 
                " ".join([f"<span style='margin-right: 15px;'><span class='legend-badge' style='background-color: {color};'></span>{lbl}</span>" 
                          for lbl, color in CORES_NOS.items()]) + 
                "</div>", unsafe_allow_html=True)
    
    try:
        with get_driver() as driver:
            with driver.session() as session:
                # Busca nós e relacionamentos para plotar
                resultado = session.run("MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 80")
                
                nodes_set = set()
                nodes = []
                edges = []
                
                for record in resultado:
                    n = record["n"]
                    m = record["m"]
                    r = record["r"]
                    
                    n_id = str(n.element_id)
                    n_label = list(n.labels)[0] if n.labels else "Nó"
                    n_title = n.get("nome", n.get("username", n.get("titulo", n.get("texto", n.get("id", "Desconhecido")))))
                    if len(n_title) > 20: n_title = n_title[:17] + "..."
                    
                    m_id = str(m.element_id)
                    m_label = list(m.labels)[0] if m.labels else "Nó"
                    m_title = m.get("nome", m.get("username", m.get("titulo", m.get("texto", m.get("id", "Desconhecido")))))
                    if len(m_title) > 20: m_title = m_title[:17] + "..."
                    
                    if n_id not in nodes_set:
                        nodes.append(Node(id=n_id, label=f"({n_label}) {n_title}", size=22, color=CORES_NOS.get(n_label, "#A0AEC0")))
                        nodes_set.add(n_id)
                    
                    if m_id not in nodes_set:
                        nodes.append(Node(id=m_id, label=f"({m_label}) {m_title}", size=22, color=CORES_NOS.get(m_label, "#A0AEC0")))
                        nodes_set.add(m_id)
                        
                    edges.append(Edge(source=n_id, target=m_id, label=type(r).__name__))

        if nodes:
            config = Config(width=1000, height=600, directed=True, physics=True, hierarchical=False)
            agraph(nodes=nodes, edges=edges, config=config)
        else:
            st.warning("O banco de dados parece vazio. Vá em 'Gerenciamento de Entidades' ou execute o script de povoamento.")
    except Exception as e:
        st.error(f"Erro ao gerar a visualização: {e}")

# ==========================================
# TELA 2: GERENCIAMENTO DE ENTIDADES (CRUD COMPLETO)
# ==========================================
elif menu == "Gerenciamento de Entidades (CRUD)":
    st.header("🗂️ Central de Cadastro de Entidades")
    st.markdown("Crie, edite ou remova qualquer tipo de nó do sistema.")
    
    lista_entidades = list(CORES_NOS.keys())
    tipo_entidade = st.selectbox("Selecione o tipo de nó a gerenciar:", lista_entidades)
    
    tab_create, tab_read, tab_update, tab_delete = st.tabs(["Criar Nó", "Listar Nós", "Editar Nó", "Deletar Nó"])
    
    # --- ABA 1: CRIAR ---
    with tab_create:
        st.subheader(f"Novo Nó do tipo {tipo_entidade}")
        
        with st.form("form_criar_entidade"):
            dados_novos = {}
            if tipo_entidade == "User":
                dados_novos["nome"] = st.text_input("Nome Completo")
                dados_novos["username"] = st.text_input("Username (sem @)")
            elif tipo_entidade == "Post":
                dados_novos["content"] = st.text_area("Conteúdo da Publicação")
                # Permitir vincular a um criador existente na hora
                lista_users = [u["username"] for u in run_query("MATCH (u:User) RETURN u.username AS username ORDER BY username")]
                dados_novos["_creator"] = st.selectbox("Autor (User)", lista_users) if lista_users else None
            elif tipo_entidade == "Comment":
                dados_novos["texto"] = st.text_area("Texto do Comentário")
                lista_users = [u["username"] for u in run_query("MATCH (u:User) RETURN u.username AS username ORDER BY username")]
                lista_posts = [p["id"] for p in run_query("MATCH (p:Post) RETURN p.id AS id LIMIT 30")]
                dados_novos["_creator"] = st.selectbox("Comentador (User)", lista_users) if lista_users else None
                dados_novos["_post_target"] = st.selectbox("Destino (ID do Post)", lista_posts) if lista_posts else None
            elif tipo_entidade == "Community":
                dados_novos["nome"] = st.text_input("Nome da Comunidade")
                dados_novos["categoria"] = st.text_input("Categoria (ex: Entretenimento, Acadêmico)")
            elif tipo_entidade == "Topic":
                dados_novos["nome"] = st.text_input("Nome do Tópico (Ex: Finanças)")
            elif tipo_entidade == "Hashtag":
                dados_novos["nome"] = st.text_input("Nome da Hashtag (sem #)")
            elif tipo_entidade == "Event":
                dados_novos["nome"] = st.text_input("Nome do Evento")
                dados_novos["data"] = st.date_input("Data do Evento").strftime("%Y-%m-%d")
                dados_novos["plataforma"] = st.text_input("Plataforma (ex: YouTube, Discord)")
            elif tipo_entidade == "Device":
                dados_novos["nome"] = st.text_input("Nome do Dispositivo (ex: iPhone 15)")
                dados_novos["tipo"] = st.selectbox("Tipo", ["Mobile", "Desktop", "Tablet"])
            elif tipo_entidade == "Location":
                dados_novos["cidade"] = st.text_input("Cidade")
                dados_novos["estado"] = st.text_input("Estado (UF)")
            elif tipo_entidade == "Media":
                dados_novos["url"] = st.text_input("URL do arquivo de mídia")
                dados_novos["tipo"] = st.selectbox("Tipo de Mídia", ["imagem", "video", "audio", "documento"])
            elif tipo_entidade == "Advertisement":
                dados_novos["titulo"] = st.text_input("Título do Anúncio")
                dados_novos["anunciante"] = st.text_input("Nome do Anunciante")
                
            submitted = st.form_submit_button("Salvar no Banco", type="primary")
            
            if submitted:
                # Gerar ID único
                id_node = str(uuid.uuid4())
                if tipo_entidade == "Topic": id_node = dados_novos["nome"].lower()
                elif tipo_entidade == "Hashtag": id_node = dados_novos["nome"].lower()
                
                if tipo_entidade == "User":
                    if not dados_novos["nome"] or not dados_novos["username"]:
                        st.error("Preencha todos os campos!")
                    else:
                        run_query("CREATE (u:User {id: $id, nome: $nome, username: $username})", 
                                  {"id": id_node, "nome": dados_novos["nome"], "username": dados_novos["username"]})
                        st.success(f"Usuário {dados_novos['nome']} criado com sucesso!")
                elif tipo_entidade == "Post":
                    if not dados_novos["content"] or not dados_novos["_creator"]:
                        st.error("Preencha o conteúdo e defina um autor!")
                    else:
                        q = """
                        MATCH (u:User {username: $username})
                        CREATE (p:Post {id: $id, content: $content})
                        CREATE (u)-[:POSTED {timestamp: datetime()}]->(p)
                        """
                        run_query(q, {"id": id_node, "content": dados_novos["content"], "username": dados_novos["_creator"]})
                        st.success("Publicação inserida com sucesso!")
                elif tipo_entidade == "Comment":
                    if not dados_novos["texto"] or not dados_novos["_creator"] or not dados_novos["_post_target"]:
                        st.error("Campos incompletos!")
                    else:
                        q = """
                        MATCH (u:User {username: $username})
                        MATCH (p:Post {id: $post_id})
                        CREATE (c:Comment {id: $id, texto: $texto})
                        CREATE (u)-[:POSTED {timestamp: datetime()}]->(c)
                        CREATE (c)-[:COMMENTS_ON {timestamp: datetime()}]->(p)
                        """
                        run_query(q, {"id": id_node, "texto": dados_novos["texto"], "username": dados_novos["_creator"], "post_id": dados_novos["_post_target"]})
                        st.success("Comentário inserido!")
                elif tipo_entidade == "Community":
                    run_query("CREATE (:Community {id: $id, nome: $nome, categoria: $categoria})", 
                              {"id": id_node, "nome": dados_novos["nome"], "categoria": dados_novos["categoria"]})
                    st.success("Comunidade cadastrada!")
                elif tipo_entidade == "Topic":
                    run_query("CREATE (:Topic {id: $id, nome: $nome})", {"id": id_node, "nome": dados_novos["nome"]})
                    st.success("Tópico cadastrado!")
                elif tipo_entidade == "Hashtag":
                    run_query("CREATE (:Hashtag {id: $id, nome: $nome})", {"id": id_node, "nome": f"#{dados_novos['nome']}"})
                    st.success("Hashtag cadastrada!")
                elif tipo_entidade == "Event":
                    run_query("CREATE (:Event {id: $id, nome: $nome, data: $data, plataforma: $plataforma})", 
                              {"id": id_node, "nome": dados_novos["nome"], "data": dados_novos["data"], "plataforma": dados_novos["plataforma"]})
                    st.success("Evento cadastrado!")
                elif tipo_entidade == "Device":
                    run_query("CREATE (:Device {id: $id, nome: $nome, tipo: $tipo})", 
                              {"id": id_node, "nome": dados_novos["nome"], "tipo": dados_novos["tipo"]})
                    st.success("Dispositivo cadastrado!")
                elif tipo_entidade == "Location":
                    run_query("CREATE (:Location {id: $id, cidade: $cidade, estado: $estado})", 
                              {"id": id_node, "cidade": dados_novos["cidade"], "estado": dados_novos["estado"]})
                    st.success("Localização cadastrada!")
                elif tipo_entidade == "Media":
                    run_query("CREATE (:Media {id: $id, url: $url, tipo: $tipo})", 
                              {"id": id_node, "url": dados_novos["url"], "tipo": dados_novos["tipo"]})
                    st.success("Mídia cadastrada!")
                elif tipo_entidade == "Advertisement":
                    run_query("CREATE (:Advertisement {id: $id, titulo: $titulo, anunciante: $anunciante})", 
                              {"id": id_node, "titulo": dados_novos["titulo"], "anunciante": dados_novos["anunciante"]})
                    st.success("Campanha de Anúncio cadastrada!")
                    
    # --- ABA 2: LEITURA (Listar) ---
    with tab_read:
        st.subheader(f"Nós existentes de {tipo_entidade}")
        dados_tabela = run_query(f"MATCH (n:{tipo_entidade}) RETURN n")
        if dados_tabela:
            # Flatten dict para tabela amigável
            registros = [dict(r["n"]) for r in dados_tabela]
            st.dataframe(registros, use_container_width=True)
        else:
            st.info("Nenhum nó desta categoria encontrado.")
            
    # --- ABA 3: EDITAR ---
    with tab_update:
        st.subheader(f"Atualizar Atributos de {tipo_entidade}")
        dados_lista = run_query(f"MATCH (n:{tipo_entidade}) RETURN n")
        
        if dados_lista:
            opcoes_nodes = {}
            for r in dados_lista:
                n = r["n"]
                label_show = n.get("nome", n.get("username", n.get("titulo", n.get("texto", n.get("id")))))
                opcoes_nodes[label_show] = n
                
            selected_label = st.selectbox("Escolha o nó para editar:", list(opcoes_nodes.keys()), key="edit_select")
            node_atual = opcoes_nodes[selected_label]
            
            with st.form("form_edit_entidade"):
                st.info(f"Editando nó ID: {node_atual['id']}")
                novas_propriedades = {}
                for key, val in node_atual.items():
                    if key == "id": continue # ID não deve ser editado
                    if type(val) == int:
                        novas_propriedades[key] = st.number_input(key, value=val)
                    else:
                        novas_propriedades[key] = st.text_input(key, value=str(val))
                        
                sub_edit = st.form_submit_button("Salvar Alterações")
                if sub_edit:
                    sets = ", ".join([f"n.{k} = ${k}" for k in novas_propriedades.keys()])
                    query_update = f"MATCH (n:{tipo_entidade} {{id: $id}}) SET {sets} RETURN n"
                    params = {"id": node_atual["id"], **novas_propriedades}
                    run_query(query_update, params)
                    st.success("Nó atualizado com sucesso!")
        else:
            st.info("Nenhum nó disponível para edição.")
            
    # --- ABA 4: DELETAR ---
    with tab_delete:
        st.subheader(f"Remover Nó ({tipo_entidade})")
        dados_lista_del = run_query(f"MATCH (n:{tipo_entidade}) RETURN n")
        
        if dados_lista_del:
            opcoes_nodes_del = {}
            for r in dados_lista_del:
                n = r["n"]
                label_show = n.get("nome", n.get("username", n.get("titulo", n.get("texto", n.get("id")))))
                opcoes_nodes_del[label_show] = n
                
            selected_label_del = st.selectbox("Escolha o nó para deletar:", list(opcoes_nodes_del.keys()), key="del_select")
            node_del = opcoes_nodes_del[selected_label_del]
            
            st.warning(f"Isso irá apagar permanentemente o nó '{selected_label_del}' e todas as suas relações correspondentes!")
            confirm_del = st.checkbox("Confirmo que quero excluir definitivamente.")
            
            if st.button("Remover do Banco", type="primary"):
                if confirm_del:
                    run_query(f"MATCH (n:{tipo_entidade} {{id: $id}}) DETACH DELETE n", {"id": node_del["id"]})
                    st.success(f"Nó '{selected_label_del}' removido com sucesso!")
                else:
                    st.error("Marque a caixa de confirmação para poder excluir.")
        else:
            st.info("Nenhum nó disponível para exclusão.")

# ==========================================
# TELA 3: CENTRAL DE RELACIONAMENTOS (INTEGRANDO CARDINALIDADE)
# ==========================================
elif menu == "Central de Relacionamentos":
    st.header("🔗 Gestão de Conexões e Relacionamentos")
    st.markdown("Pesquise, crie, renomeie ou delete relacionamentos usando regras estruturadas de cardinalidade.")

    lista_relacionamentos = [
        "FOLLOWS", "FRIEND_OF", "LIKES", "SHARES", "COMMENTS_ON", 
        "POSTED", "MEMBER_OF", "TAGGED_IN", "BLOCKED", "MUTED", 
        "VIEWED", "RECOMMENDED", "SIMILAR_TO", "HAS_TOPIC", "USES_DEVICE", "LOCATED_IN"
    ]
    lista_labels = list(CORES_NOS.keys())
    opcoes_busca = ["id", "username", "nome"]

    tab_search, tab_create, tab_rename, tab_delete = st.tabs(["Pesquisar", "Criar", "Renomear", "Deletar"])

    # 1. PESQUISAR
    with tab_search:
        st.subheader("Explorador de Relações")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            lbl_busca = st.selectbox("Tipo de Nó", lista_labels, key="search_lbl")
        with col_s2:
            chave_busca = st.selectbox("Chave de Busca", opcoes_busca, key="search_key")
        valor_busca = st.text_input("Valor buscado (ex: teixeiraerick, c_gamer):")
        
        if st.button("Buscar Conexões"):
            if valor_busca:
                q_search = f"""
                MATCH (centro:{lbl_busca} {{{chave_busca}: $valor}})-[r]-(vizinho)
                RETURN 
                    type(r) AS Tipo_Relacionamento, 
                    labels(vizinho)[0] AS Tipo_Vizinho, 
                    COALESCE(vizinho.nome, vizinho.username, vizinho.id, 'Desconhecido') AS Vizinho
                ORDER BY Tipo_Relacionamento
                """
                resultados = run_query(q_search, {"valor": valor_busca})
                if resultados:
                    st.dataframe(resultados, use_container_width=True)
                else:
                    st.warning("Nenhum relacionamento encontrado para este nó.")
            else:
                st.error("Digite o valor para buscar.")

    # 2. CRIAR (COM VALIDAÇÃO DE CARDINALIDADE DO RPA_CARDINALIDADE.PY)
    with tab_create:
        st.subheader("Novo Relacionamento Estruturado")
        st.info("Aqui a criação obedece às regras de cardinalidade que impedem inserções inválidas.")
        
        tipo_relacao = st.selectbox("Escolha o relacionamento:", lista_relacionamentos, key="rel_create")
        
        col_orig, col_dest = st.columns(2)
        with col_orig:
            st.markdown("**Origem**")
            l_orig = st.selectbox("Tipo de Nó Origem", lista_labels, key="l_orig")
            k_orig = st.selectbox("Chave de Busca Origem", opcoes_busca, key="k_orig")
            v_orig = st.text_input("Valor Origem (ex: id, username):", key="v_orig")
            
        with col_dest:
            st.markdown("**Destino**")
            l_dest = st.selectbox("Tipo de Nó Destino", lista_labels, key="l_dest")
            k_dest = st.selectbox("Chave de Busca Destino", opcoes_busca, key="k_dest")
            v_dest = st.text_input("Valor Destino (ex: id, username):", key="v_dest")
            
        st.markdown("**Regra de Restrição de Grafo**")
        cardinalidade = st.radio(
            "Selecione a Cardinalidade a aplicar:",
            ["N:N (Livre)", "1:N (Origem pode apontar para no máximo 1 Destino)", "1:1 (Origem e Destino são exclusivos)"],
            index=0
        )
        
        card_code = "N:N"
        if "1:N" in cardinalidade: card_code = "1:N"
        elif "1:1" in cardinalidade: card_code = "1:1"

        if st.button("Executar Criação de Relação", type="primary"):
            if v_orig and v_dest:
                # Obter IDs reais de origem e destino primeiro se as chaves forem nome/username
                q_get_ids = f"""
                MATCH (o:{l_orig} {{{k_orig}: $v_orig}})
                MATCH (d:{l_dest} {{{k_dest}: $v_dest}})
                RETURN o.id AS id_orig, d.id AS id_dest
                """
                res_ids = run_query(q_get_ids, {"v_orig": v_orig, "v_dest": v_dest})
                
                if res_ids:
                    id_orig_real = res_ids[0]["id_orig"]
                    id_dest_real = res_ids[0]["id_dest"]
                    
                    # Importa a validação dinâmica de cardinalidade
                    from RPA_cardinalidade import criar_relacionamento_cardinalidade
                    
                    with get_driver() as driver:
                        sucesso, msg = criar_relacionamento_cardinalidade(
                            driver, l_orig, id_orig_real, l_dest, id_dest_real, tipo_relacao, card_code
                        )
                        if sucesso:
                            st.success(msg)
                        else:
                            st.warning(msg)
                else:
                    st.error("Nós de Origem ou Destino não foram localizados com os critérios informados.")
            else:
                st.error("Preencha os dados de busca de origem e destino.")

    # 3. RENOMEAR
    with tab_rename:
        st.subheader("Renomear Relacionamento")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rel_antigo = st.selectbox("Relação Atual", lista_relacionamentos, key="rename_old")
            k_orig_r = st.selectbox("Chave Origem", opcoes_busca, key="r_k_orig")
            v_orig_r = st.text_input("Valor Origem:", key="r_v_orig")
        with col_r2:
            rel_novo = st.selectbox("Nova Relação", lista_relacionamentos, key="rename_new")
            k_dest_r = st.selectbox("Chave Destino", opcoes_busca, key="r_k_dest")
            v_dest_r = st.text_input("Valor Destino:", key="r_v_dest")
            
        if st.button("Executar Renomeação"):
            if v_orig_r and v_dest_r:
                q_rename = f"""
                MATCH (a {{{k_orig_r}: $orig}})-[r_old:{rel_antigo}]->(b {{{k_dest_r}: $dest}})
                MERGE (a)-[r_new:{rel_novo}]->(b)
                SET r_new = r_old
                DELETE r_old
                """
                try:
                    run_query(q_rename, {"orig": v_orig_r, "dest": v_dest_r})
                    st.success("Relacionamento atualizado com sucesso!")
                except Exception as e:
                    st.error(f"Erro: {e}")

    # 4. DELETAR
    with tab_delete:
        st.subheader("Deletar Relacionamento")
        rel_del = st.selectbox("Qual relação deseja apagar?", lista_relacionamentos, key="del_rel")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            k_orig_d = st.selectbox("Chave Origem", opcoes_busca, key="d_k_orig")
            v_orig_d = st.text_input("Valor Origem:", key="d_v_orig")
        with col_d2:
            k_dest_d = st.selectbox("Chave Destino", opcoes_busca, key="d_k_dest")
            v_dest_d = st.text_input("Valor Destino:", key="d_v_dest")
            
        if st.button("Deletar Definitivamente"):
            if v_orig_d and v_dest_d:
                q_delete = f"""
                MATCH (a {{{k_orig_d}: $orig}})-[r:{rel_del}]->(b {{{k_dest_d}: $dest}})
                DELETE r
                """
                run_query(q_delete, {"orig": v_orig_d, "dest": v_dest_d})
                st.success("Conexão deletada com sucesso.")

# ==========================================
# TELA 4: AÇÕES & SIMULAÇÃO DE USUÁRIO (NOVA!)
# ==========================================
elif menu == "Ações & Simulação de Usuário":
    st.header("🎭 Simulação de Interação Social")
    st.markdown("Entre na pele de um usuário da rede e interaja de forma visual e realista.")
    
    lista_users = run_query("MATCH (u:User) RETURN u.nome AS nome, u.username AS username ORDER BY nome")
    if lista_users:
        opcoes_usuarios = {f"{u['nome']} (@{u['username']})": u['username'] for u in lista_users}
        usuario_atual = st.selectbox("Entrar na rede como:", list(opcoes_usuarios.keys()))
        username_atual = opcoes_usuarios[usuario_atual]
        
        st.markdown(f"---")
        
        col_actions, col_preview = st.columns([1, 1])
        
        with col_actions:
            st.subheader("O que você deseja fazer?")
            opcao_acao = st.selectbox(
                "Ação:", 
                [
                    "Fazer uma publicação (Post)", 
                    "Comentar em uma publicação", 
                    "Curtir / Compartilhar / Visualizar", 
                    "Seguir / Desfazer Amizade", 
                    "Bloquear / Silenciar Usuário", 
                    "Comunidades & Eventos"
                ]
            )
            
            # 1. Novo Post
            if opcao_acao == "Fazer uma publicação (Post)":
                conteudo_post = st.text_area("Texto do Post")
                lista_topics = [t["nome"] for t in run_query("MATCH (t:Topic) RETURN t.nome AS nome ORDER BY nome")]
                topico_selecionado = st.selectbox("Tópico do Post", lista_topics) if lista_topics else None
                
                if st.button("Publicar Post", type="primary"):
                    if conteudo_post:
                        pid = str(uuid.uuid4())
                        # Criar post
                        q = """
                        MATCH (u:User {username: $username})
                        CREATE (p:Post {id: $pid, content: $content})
                        CREATE (u)-[:POSTED {timestamp: datetime()}]->(p)
                        """
                        run_query(q, {"username": username_atual, "pid": pid, "content": conteudo_post})
                        
                        # Link topic
                        if topico_selecionado:
                            run_query(
                                "MATCH (p:Post {id: $pid}), (t:Topic {nome: $t_nome}) MERGE (p)-[:HAS_TOPIC]->(t)",
                                {"pid": pid, "t_nome": topico_selecionado}
                            )
                        st.success("Post publicado com sucesso!")
                    else:
                        st.error("Escreva algo antes de postar!")
                        
            # 2. Comentar
            elif opcao_acao == "Comentar em uma publicação":
                todos_posts = run_query("MATCH (u:User)-[:POSTED]->(p:Post) RETURN p.id AS id, p.content AS content, u.username AS autor LIMIT 30")
                if todos_posts:
                    opcoes_posts = {f"@{p['autor']}: {p['content'][:40]}...": p['id'] for p in todos_posts}
                    post_alvo = st.selectbox("Selecione o post:", list(opcoes_posts.keys()))
                    post_id = opcoes_posts[post_alvo]
                    
                    texto_coment = st.text_area("Seu comentário")
                    if st.button("Enviar Comentário"):
                        if texto_coment:
                            cid = str(uuid.uuid4())
                            q = """
                            MATCH (u:User {username: $username})
                            MATCH (p:Post {id: $post_id})
                            CREATE (c:Comment {id: $cid, texto: $texto})
                            CREATE (u)-[:POSTED {timestamp: datetime()}]->(c)
                            CREATE (c)-[:COMMENTS_ON {timestamp: datetime()}]->(p)
                            """
                            run_query(q, {"username": username_atual, "post_id": post_id, "cid": cid, "texto": texto_coment})
                            st.success("Comentário publicado!")
                else:
                    st.info("Nenhuma publicação encontrada no banco.")
                    
            # 3. Likes, Shares, Views
            elif opcao_acao == "Curtir / Compartilhar / Visualizar":
                todos_posts = run_query("MATCH (u:User)-[:POSTED]->(p:Post) RETURN p.id AS id, p.content AS content, u.username AS autor LIMIT 30")
                if todos_posts:
                    opcoes_posts = {f"@{p['autor']}: {p['content'][:40]}...": p['id'] for p in todos_posts}
                    post_alvo = st.selectbox("Selecione o post:", list(opcoes_posts.keys()))
                    post_id = opcoes_posts[post_alvo]
                    
                    tipo_interacao = st.selectbox("Tipo de Interação", ["Curtir (LIKE)", "Compartilhar (SHARE)", "Visualizar (VIEW)"])
                    
                    if st.button("Registrar Interação"):
                        if tipo_interacao == "Curtir (LIKE)":
                            q = """
                            MATCH (u:User {username: $username}), (p:Post {id: $post_id})
                            MERGE (u)-[r:LIKES]->(p)
                            SET r.timestamp = datetime(), r.reaction = 'like'
                            """
                            run_query(q, {"username": username_atual, "post_id": post_id})
                            st.success("Você curtiu esta publicação!")
                        elif tipo_interacao == "Compartilhar (SHARE)":
                            q = """
                            MATCH (u:User {username: $username}), (p:Post {id: $post_id})
                            MERGE (u)-[r:SHARES]->(p)
                            SET r.timestamp = datetime()
                            """
                            run_query(q, {"username": username_atual, "post_id": post_id})
                            st.success("Publicação compartilhada com sucesso!")
                        elif tipo_interacao == "Visualizar (VIEW)":
                            q = """
                            MATCH (u:User {username: $username}), (p:Post {id: $post_id})
                            MERGE (u)-[r:VIEWED]->(p)
                            SET r.timestamp = datetime()
                            """
                            run_query(q, {"username": username_atual, "post_id": post_id})
                            st.success("Visualização registrada!")
                else:
                    st.info("Nenhum post disponível.")
                    
            # 4. Seguir/Amizade
            elif opcao_acao == "Seguir / Desfazer Amizade":
                outros_usuarios = run_query("MATCH (u:User) WHERE u.username <> $username RETURN u.nome AS nome, u.username AS username ORDER BY nome", {"username": username_atual})
                if outros_usuarios:
                    opcoes_amigos = {f"{o['nome']} (@{o['username']})": o['username'] for o in outros_usuarios}
                    amigo_selecionado = st.selectbox("Selecione o usuário:", list(opcoes_amigos.keys()))
                    amigo_username = opcoes_amigos[amigo_selecionado]
                    
                    tipo_conexao = st.selectbox("Tipo de Relação", ["Seguir (FOLLOWS)", "Amigo Mútuo (FRIEND_OF)"])
                    
                    if st.button("Conectar"):
                        if tipo_conexao == "Seguir (FOLLOWS)":
                            run_query(
                                "MATCH (u1:User {username: $u1}), (u2:User {username: $u2}) MERGE (u1)-[:FOLLOWS {timestamp: datetime()}]->(u2)",
                                {"u1": username_atual, "u2": amigo_username}
                            )
                            st.success(f"Você agora segue @{amigo_username}!")
                        else:
                            run_query(
                                """
                                MATCH (u1:User {username: $u1}), (u2:User {username: $u2})
                                MERGE (u1)-[:FRIEND_OF {timestamp: datetime()}]->(u2)
                                MERGE (u2)-[:FRIEND_OF {timestamp: datetime()}]->(u1)
                                """,
                                {"u1": username_atual, "u2": amigo_username}
                            )
                            st.success(f"Conexão de amizade estabelecida com @{amigo_username}!")
                else:
                    st.info("Nenhum outro usuário cadastrado.")

            # 5. Bloquear/Mute
            elif opcao_acao == "Bloquear / Silenciar Usuário":
                outros_usuarios = run_query("MATCH (u:User) WHERE u.username <> $username RETURN u.nome AS nome, u.username AS username ORDER BY nome", {"username": username_atual})
                if outros_usuarios:
                    opcoes_bloq = {f"{o['nome']} (@{o['username']})": o['username'] for o in outros_usuarios}
                    bloq_username = opcoes_bloq[st.selectbox("Usuário:", list(opcoes_bloq.keys()))]
                    tipo_b = st.selectbox("Ação", ["Bloquear (BLOCKED)", "Silenciar (MUTED)"])
                    
                    if st.button("Confirmar Ação"):
                        run_query(
                            f"MATCH (u1:User {{username: $u1}}), (u2:User {{username: $u2}}) MERGE (u1)-[:{tipo_b} {{timestamp: datetime()}}]->(u2)",
                            {"u1": username_atual, "u2": bloq_username}
                        )
                        st.success(f"Ação {tipo_b} aplicada para @{bloq_username}!")

            # 6. Comunidades e Eventos
            elif opcao_acao == "Comunidades & Eventos":
                comunidades = run_query("MATCH (c:Community) RETURN c.id AS id, c.nome AS nome")
                eventos = run_query("MATCH (e:Event) RETURN e.id AS id, e.nome AS nome")
                
                acao_ce = st.radio("Deseja interagir com:", ["Comunidades (MEMBER_OF)", "Eventos (ATTENDS)"])
                
                if acao_ce == "Comunidades (MEMBER_OF)" and comunidades:
                    opcoes_comm = {c["nome"]: c["id"] for c in comunidades}
                    comm_id = opcoes_comm[st.selectbox("Selecione a Comunidade:", list(opcoes_comm.keys()))]
                    if st.button("Participar da Comunidade"):
                        run_query(
                            "MATCH (u:User {username: $username}), (c:Community {id: $cid}) MERGE (u)-[:MEMBER_OF {timestamp: datetime()}]->(c)",
                            {"username": username_atual, "cid": comm_id}
                        )
                        st.success("Você agora é membro da comunidade!")
                elif acao_ce == "Eventos (ATTENDS)" and eventos:
                    opcoes_evt = {e["nome"]: e["id"] for e in eventos}
                    evt_id = opcoes_evt[st.selectbox("Selecione o Evento:", list(opcoes_evt.keys()))]
                    if st.button("Confirmar Presença"):
                        run_query(
                            "MATCH (u:User {username: $username}), (e:Event {id: $eid}) MERGE (u)-[:ATTENDS {timestamp: datetime(), status: 'confirmado'}]->(e)",
                            {"username": username_atual, "eid": evt_id}
                        )
                        st.success("Presença confirmada no evento!")
                        
        with col_preview:
            st.subheader("Atividades Recentes na Rede")
            st.markdown("Veja o que está acontecendo na linha do tempo do ecossistema:")
            
            # Buscar posts recentes geral
            posts_recentes = run_query(
                """
                MATCH (u:User)-[:POSTED]->(p:Post)
                OPTIONAL MATCH (p)-[:HAS_TOPIC]->(t:Topic)
                RETURN u.nome AS autor, u.username AS username, p.content AS texto, COALESCE(t.nome, 'Geral') AS topico
                LIMIT 5
                """
            )
            for p in posts_recentes:
                st.markdown(f"""
                <div class='glass-card'>
                    <strong>{p['autor']}</strong> <span style='color: #8A8F98;'>@{p['username']}</span> 
                    <span style='float: right; font-size: 0.8rem; background: #4C83FF; color: white; padding: 2px 8px; border-radius: 10px;'>{p['topico']}</span>
                    <p style='margin-top: 10px;'>{p['texto']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Cadastre usuários primeiro na aba 'Gerenciamento de Entidades'.")

# ==========================================
# TELA 5: MOTOR DE RECOMENDAÇÃO (MELHORADO)
# ==========================================
elif menu == "Motor de Recomendação":
    st.header("🧠 Inteligência de Grafos & Recomendações")
    st.markdown("Consulte sugestões personalizadas de relacionamentos, conteúdos e propagandas.")
    
    st.subheader("Usuários Ativos no Banco:")
    lista_usuarios = run_query("MATCH (u:User) RETURN u.nome AS Nome, u.username AS Username ORDER BY Nome")
    if lista_usuarios:
        st.dataframe(lista_usuarios, use_container_width=True)
        usuario_alvo = st.selectbox("Selecione o usuário para ver recomendações:", [u["Username"] for u in lista_usuarios])
        
        tab1, tab2, tab3, tab4 = st.tabs(["Amizades Sugeridas", "Posts Recomendados", "Comunidades Recomendadas", "Anúncios Personalizados"])
        
        # 1. Amizades
        with tab1:
            st.info("Lógica: Pessoas que curtiram as mesmas publicações que você, mas que você ainda não segue.")
            query_amigos = """
            MATCH (u:User {username: $username})-[:LIKES]->(p:Post)<-[:LIKES]-(sugerido:User)
            WHERE u <> sugerido AND NOT (u)-[:FOLLOWS]->(sugerido)
            RETURN sugerido.nome AS SugestaoAmigo, sugerido.username AS Username, count(p) AS InteressesEmComum
            ORDER BY InteressesEmComum DESC
            """
            if st.button("Gerar Recomendações de Amigos"):
                registos = run_query(query_amigos, {"username": usuario_alvo})
                if registos:
                    st.table(registos)
                else:
                    st.warning("Não há novas sugestões com interesses em comum no momento.")
                st.code(query_amigos, language="cypher")
                
        # 2. Conteúdo
        with tab2:
            st.info("Lógica: Publicações que seus amigos/seguidos curtiram, mas que você ainda não curtiu.")
            query_conteudo = """
            MATCH (u:User {username: $username})-[:FOLLOWS]->(amigo:User)-[:LIKES]->(p:Post)
            WHERE NOT (u)-[:LIKES]->(p)
            RETURN p.content AS PostRecomendado, amigo.nome AS QuemGostou
            """
            if st.button("Gerar Recomendações de Conteúdo"):
                registos = run_query(query_conteudo, {"username": usuario_alvo})
                if registos:
                    st.table(registos)
                else:
                    st.warning("Você já viu ou curtiu todo o conteúdo sugerido pelos seus amigos.")
                st.code(query_conteudo, language="cypher")
                
        # 3. Comunidades
        with tab3:
            st.info("Lógica: Comunidades em que as pessoas que você segue são membros, mas você ainda não é.")
            query_comunidades = """
            MATCH (u:User {username: $username})-[:FOLLOWS]->(amigo:User)-[:MEMBER_OF]->(c:Community)
            WHERE NOT (u)-[:MEMBER_OF]->(c)
            RETURN c.nome AS ComunidadeSugerida, count(amigo) AS AmigosNaComunidade
            ORDER BY AmigosNaComunidade DESC
            """
            if st.button("Gerar Recomendações de Comunidades"):
                registos = run_query(query_comunidades, {"username": usuario_alvo})
                if registos:
                    st.table(registos)
                else:
                    st.warning("Sem sugestões de novas comunidades baseadas nas suas conexões.")
                st.code(query_comunidades, language="cypher")

        # 4. Anúncios
        with tab4:
            st.info("Lógica: Campanhas de anunciantes direcionadas pelo seu tópico de posts favorito.")
            query_ads = """
            MATCH (u:User {username: $username})-[:LIKES]->(p:Post)-[:HAS_TOPIC]->(t:Topic)
            WITH u, t, count(p) AS curtidas_topico
            ORDER BY curtidas_topico DESC LIMIT 1
            MATCH (ad:Advertisement)
            RETURN ad.titulo AS CampanhaAnuncio, ad.anunciante AS Anunciante, t.nome AS BaseadoNoTopico
            LIMIT 3
            """
            if st.button("Gerar Anúncios Recomendados"):
                registos = run_query(query_ads, {"username": usuario_alvo})
                if registos:
                    st.success("Anúncios personalizados direcionados para o seu perfil:")
                    st.table(registos)
                else:
                    st.warning("Curta alguns posts vinculados a tópicos para receber anúncios segmentados.")
                st.code(query_ads, language="cypher")
    else:
        st.warning("Não há usuários cadastrados no sistema.")