import socket
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, ServiceUnavailable

URI = "neo4j+ssc://cb84c387.databases.neo4j.io"
# CERTIFIQUE-SE DE QUE O USUÁRIO É EXACTAMENTE "neo4j"
USER = "cb84c387"
PASSWORD = "1xe1FMi49ZrfSzUvfOfzK_j8GKGqqFblHkvsQrQZVjc"  # Substitua pela sua senha real do Aura

def testar_conexao():
    print("--- REALIZANDO DIAGNÓSTICO DE CONEXÃO ---")
    
    # ETAPA 1: Teste de Resolução de DNS e Rede Básica
    host = "cb84c387.databases.neo4j.io"
    print(f"[1/3] Testando conexão de rede com o servidor {host} na porta 7687...")
    try:
        # Tenta abrir uma conexão socket pura na porta do Bolt
        socket.create_connection((host, 7687), timeout=5)
        print("✅ Sucesso: Sua rede e firewall PERMITEM conexões com o Neo4j Aura!")
    except Exception as e:
        print(f"❌ Erro de Rede: Não foi possível alcançar o servidor. Motivo: {e}")
        print("👉 Isso confirma que sua rede local (Wi-Fi, Firewall, Provedor ou VPN) está bloqueando a porta 7687.")
        return

    # ETAPA 2: Teste de Inicialização do Driver e Autenticação
    print("\n[2/3] Tentando autenticar no banco de dados...")
    try:
        with GraphDatabase.driver(URI, auth=(USER, PASSWORD)) as driver:
            driver.verify_connectivity()
            print("✅ Sucesso: Usuário e Senha estão CORRETOS e o driver conectou!")
            
    except AuthError:
        print("❌ Erro de Autenticação: O usuário ou a senha inseridos estão incorretos.")
        print("👉 Verifique se você não trocou o usuário 'neo4j' ou se não há espaços em branco na senha.")
    except ServiceUnavailable as e:
        print(f"❌ Erro de Serviço Indisponível (Roteamento): {e}")
        print("👉 O driver não conseguiu obter a tabela de rotas. Isso geralmente acontece se você estiver usando uma versão muito antiga do Python/Driver ou atrás de um Proxy de rede.")
    except Exception as e:
        print(f"❌ Outro Erro Encontrado: {e}")

if __name__ == "__main__":
    testar_conexao()
