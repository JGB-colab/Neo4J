# Tutorial de Backup e Dump do Banco de Dados - Neo4j

Este tutorial orienta como extrair o arquivo de backup/dump do banco de dados Neo4j do **X4Good** para entrega final ao professor, cobrindo tanto o ambiente local (Neo4j Desktop ou Server) quanto na nuvem (Neo4j AuraDB).

---

## Opção A: Se você estiver usando o Neo4j Desktop (Local) - Recomendado

O Neo4j Desktop possui uma interface gráfica muito simples para realizar dumps de banco de dados:

1. Abra o **Neo4j Desktop**.
2. Selecione o seu projeto e clique no banco de dados (que deve estar **parado** / **Offline**). 
   > **Nota:** Não é possível realizar um backup/dump de um banco de dados que esteja em execução. Clique em **Stop** primeiro!
3. Vá na aba **"Dumps"** (localizada ao lado de *Upgrade* ou na seção de gerenciamento da sua instância do banco).
4. Clique no botão **"Create dump"**.
5. O Neo4j Desktop irá gerar um arquivo com extensão `.dump` (ex: `neo4j-2026-06-26.dump`).
6. Clique no ícone de três pontinhos ao lado do dump criado e selecione **"Open folder"** para abrir a pasta no seu computador onde o arquivo foi salvo.
7. Copie esse arquivo `.dump` e renomeie-o para `x4good_backup.dump`. Este é o arquivo a ser entregue ao professor!

---

## Opção B: Se você estiver usando Neo4j AuraDB (Nuvem)

Se você fez o deploy do seu banco de dados na nuvem (AuraDB):

1. Acesse o console do **[Neo4j Aura Console](https://console.neo4j.io/)** e faça login.
2. Clique na sua instância de banco de dados ativa.
3. Clique na aba **"Backups"**.
4. Você verá uma lista de backups diários e snapshots gerados automaticamente.
5. Identifique o backup mais recente e clique no botão **Download** (ícone de download azul).
6. Um arquivo `.dump` será baixado para o seu computador. Renomeie-o para `x4good_backup.dump` e prepare-o para entrega.

---

## Opção C: Usando Linha de Comando (Via terminal)

Se você preferir rodar via terminal (em sistemas locais com o Neo4j instalado por pacotes):

1. Pare o serviço do Neo4j:
   - *Windows (PowerShell Administrador):*
     ```powershell
     net stop neo4j
     ```
   - *Linux / macOS:*
     ```bash
     sudo systemctl stop neo4j
     ```
2. Execute o comando `neo4j-admin` para exportar a base de dados padrão (`neo4j`):
   ```bash
   neo4j-admin database dump neo4j --to-path="C:\Caminho\Para\Salvar\x4good_backup.dump"
   ```
3. Reinicie o serviço do Neo4j após a conclusão:
   - *Windows:* `net start neo4j`
   - *Linux:* `sudo systemctl start neo4j`
