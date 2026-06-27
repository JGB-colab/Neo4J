# Diagrama do Grafo e Modelo de Dados - X4Good

Este documento descreve o modelo lógico de dados em grafo para a rede social **X4Good** e como gerar a visualização oficial para entrega ao professor.

---

## 1. Diagrama de Relacionamento Lógico (Mermaid)

Você pode visualizar o diagrama abaixo diretamente no VS Code, no GitHub ou colar o código no site [Mermaid Live Editor](https://mermaid.live/) para exportar como imagem (PNG/SVG/PDF).

```mermaid
classDiagram
    class User {
        +id: String
        +nome: String
        +username: String
    }
    class Post {
        +id: String
        +content: String
    }
    class Comment {
        +id: String
        +texto: String
    }
    class Community {
        +id: String
        +nome: String
        +categoria: String
    }
    class Topic {
        +id: String
        +nome: String
    }
    class Hashtag {
        +id: String
        +nome: String
    }
    class Event {
        +id: String
        +nome: String
        +data: String
        +plataforma: String
    }
    class Device {
        +id: String
        +nome: String
        +tipo: String
    }
    class Location {
        +id: String
        +cidade: String
        +estado: String
    }
    class Media {
        +id: String
        +url: String
        +tipo: String
    }
    class Advertisement {
        +id: String
        +titulo: String
        +anunciante: String
    }

    User --> Location : LOCATED_IN {timestamp}
    User --> Device : USES_DEVICE {timestamp, frequencia}
    User --> Community : MEMBER_OF {timestamp, role}
    User --> Event : ATTENDS {timestamp, status}
    User --> Post : POSTED {timestamp}
    User --> Comment : POSTED {timestamp}
    User --> Media : POSTED {timestamp}
    User --> User : FOLLOWS {timestamp}
    User --> User : FRIEND_OF {timestamp} (Mutuo)
    User --> User : BLOCKED {timestamp}
    User --> User : MUTED {timestamp}
    User --> User : SIMILAR_TO {score, timestamp}
    User --> Post : LIKES {timestamp, reaction}
    User --> Post : SHARES {timestamp}
    User --> Post : VIEWED {timestamp, cliques}
    User --> Post : TAGGED_IN {timestamp}
    
    Comment --> Post : COMMENTS_ON {timestamp}
    Post --> Topic : HAS_TOPIC
    Post --> Hashtag : TAGGED_WITH {timestamp}
    Post --> Media : CONTAINS_MEDIA
    Community --> Event : HOSTS {timestamp}
```

---

## 2. Como gerar e exportar o Diagrama do Neo4j (Recomendado para entrega)

O professor pediu o **diagrama do grafo referente ao banco criado**. A melhor forma é exportar diretamente a visualização do esquema do Neo4j.

Siga estes passos:

1. Abra o **Neo4j Browser** (local ou na nuvem AuraDB).
2. Na barra de comandos (topo), digite a seguinte consulta Cypher e clique em **Play/Executar**:
   ```cypher
   CALL db.schema.visualization()
   ```
3. O Neo4j gerará uma representação visual com todos os nós (User, Post, Location, etc.) conectados pelos seus respectivos relacionamentos.
4. No canto superior direito do painel de resultado do Neo4j Browser, clique no ícone **Export** (ícone de olho ou de seta/foto) e escolha **Export PNG** ou **SVG**.
5. Salve a imagem com o nome `diagrama_grafo_x4good.png` e adicione na pasta de entrega do seu trabalho.
