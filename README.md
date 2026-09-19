# Copa AI

Backend em Python + Flask + Groq para um chatbot especialista em Copa do Mundo.

## Requisitos

- Python 3.11+
- uv
- Chave da API Groq

## Instalação

```bash
uv sync
```

Se o projeto estiver sendo criado do zero:

```bash
uv init
uv add flask groq python-dotenv flask-cors
uv add --dev pytest
uv lock
```

## Configuração

Copie `.env.example` para `.env` e preencha:

```env
GROQ_API_KEY=sua_chave
GROQ_MODEL=llama-3.3-70b-versatile
FLASK_ENV=development
CORS_ORIGIN=http://localhost:3000
```

Nunca publique `.env`.

## Execução

```bash
uv run python app.py
```

API: `http://127.0.0.1:5000`

## Testes

```bash
uv run pytest
```

## Endpoints

### GET /

```json
{"status":"ok","message":"Copa do Mundo AI API is running"}
```

### GET /health

```json
{"status":"ok"}
```

### POST /api/chat

Entrada:

```json
{"message":"Quem ganhou a Copa de 2002?"}
```

Resposta:

```json
{
  "response":"O Brasil venceu a Copa do Mundo de 2002.",
  "conversation_id":"uuid"
}
```

Para continuar uma conversa:

```json
{
  "message":"E quem marcou os gols da final?",
  "conversation_id":"uuid"
}
```

### POST /api/chat/clear

Entrada:

```json
{"conversation_id":"uuid"}
```

## Frontend

```javascript
const response = await fetch("http://127.0.0.1:5000/api/chat", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    message: "Quem ganhou a Copa de 2002?"
  })
});

const data = await response.json();
console.log(data.response);
console.log(data.conversation_id);
```

O frontend envia JSON para Flask. O backend valida a entrada, recupera o histórico,
envia as mensagens ao Groq e devolve JSON.

## Produção

- Use `FLASK_ENV=production`.
- Configure `CORS_ORIGIN` para o domínio real do frontend.
- Nunca use `*` em CORS em produção.
- Nunca coloque a chave Groq no frontend.
- Use HTTPS.
- Para múltiplos workers/instâncias, substitua o histórico em memória por Redis
  ou banco de dados.
- Execute atrás de um servidor WSGI/reverse proxy apropriado em produção.
