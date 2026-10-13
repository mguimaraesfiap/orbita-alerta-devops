# Projeto — Cidades ESG Inteligentes | Órbita Alerta

Entrega de DevOps aplicada ao projeto ESG **Órbita Alerta**, uma API para registrar alertas ambientais, áreas monitoradas e ocorrências de gestão. A solução foi organizada para simular um ciclo de produção com build, testes, criação de imagem Docker e deploy controlado em `staging` e `production`.

## Visão geral

```text
Commit / Pull Request
        |
        v
GitHub Actions: restore -> build -> test -> Docker build -> GHCR
        |
        +--> staging  (branch qa, ambiente de validação)
        |
        +--> production (branch main, ambiente protegido/aprovação)
```

## Como executar localmente com Docker

Pré-requisitos: Docker Desktop com Compose V2.

```bash
cp .env.example .env
docker compose up --build -d
curl http://localhost:8080/health
```

Resposta esperada:

```json
{"status":"healthy","service":"orbita-alerta-api","environment":"Development"}
```

Para consultar alertas e criar um registro:

```bash
curl http://localhost:8080/api/alerts

curl -X POST http://localhost:8080/api/alerts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Alerta de qualidade do ar","category":"air-quality","severity":"medium","city":"Curitiba","description":"Partículas acima do limite de referência."}'
```

Para acompanhar os serviços e encerrar o ambiente:

```bash
docker compose ps
docker compose logs -f api
docker compose down
```

O volume do MongoDB é preservado no `docker compose down`. Para removê-lo em um ambiente descartável, utilize `docker compose down -v`.

## Pipeline CI/CD

Ferramenta: **GitHub Actions**. O workflow está em `.github/workflows/ci-cd.yml`.

1. Em pull requests e pushes, instala o .NET 8, restaura dependências, compila em modo Release e executa os testes.
2. Em `qa` ou `main`, autentica no GitHub Container Registry e publica uma imagem imutável com o SHA do commit.
3. Em `qa`, faz deploy automático no ambiente GitHub `staging`.
4. Em `main`, faz deploy no ambiente `production`, que deve ser configurado com aprovação obrigatória no repositório.

### Segredos necessários

Configure os seguintes secrets no repositório:

| Secret | Finalidade |
|---|---|
| `AZURE_WEBAPP_STAGING` | Nome do Web App de staging |
| `AZURE_WEBAPP_STAGING_PUBLISH_PROFILE` | Perfil de publicação do staging |
| `AZURE_WEBAPP_PRODUCTION` | Nome do Web App de produção |
| `AZURE_WEBAPP_PRODUCTION_PUBLISH_PROFILE` | Perfil de publicação da produção |

Configure também as variáveis de ambiente dos Web Apps com `MONGO_CONNECTION_STRING` e `MONGO_DATABASE`. Os valores sensíveis não devem ser versionados.

## Containerização

O `Dockerfile` usa build em múltiplas etapas:

- `mcr.microsoft.com/dotnet/sdk:8.0` restaura, compila e publica a aplicação;
- `mcr.microsoft.com/dotnet/aspnet:8.0` executa somente os artefatos publicados;
- a aplicação escuta na porta `8080` e roda com o usuário não privilegiado `app`.

O `docker-compose.yml` orquestra dois serviços: API e MongoDB. Há rede privada compartilhada, variáveis de ambiente, healthcheck do banco e volumes persistentes.

## Prints do funcionamento

As evidências abaixo foram capturadas em execução local com Docker Compose.
O arquivo completo está em `docs/evidencias/evidencias-locais.md`.

### Build e testes — saída real

```
dotnet build src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj --configuration Release --no-restore

  OrbitaAlerta.Api -> src/OrbitaAlerta.Api/bin/Release/net8.0/OrbitaAlerta.Api.dll
  Build succeeded. 0 Warning(s)  0 Error(s)  Time Elapsed 00:00:03.74
```

```
dotnet test tests/OrbitaAlerta.Api.Tests/OrbitaAlerta.Api.Tests.csproj --configuration Release

  Passed  AlertValidatorTests.Should_reject_missing_required_fields [123 ms]
  Passed  AlertValidatorTests.Should_accept_a_valid_alert [1 ms]
  Passed  AlertValidatorTests.Should_reject_an_unknown_severity [1 ms]

  Test Run Successful.  Total tests: 3  Passed: 3  Total time: 1,4830 Seconds
```

### Docker Compose — containers em execução

```
docker compose ps

NAME                    IMAGE                    STATUS
orbita-alerta-api       orbita-alerta-api:local  Up (healthy)  0.0.0.0:8080->8080/tcp
orbita-alerta-mongodb   mongo:7.0                Up (healthy)  0.0.0.0:27017->27017/tcp
```

### Endpoint /health

```
curl http://localhost:8080/health

HTTP/1.1 200 OK
{"status":"healthy","service":"orbita-alerta-api","environment":"Development"}
```

### POST /api/alerts — criação de alerta

```
curl -X POST http://localhost:8080/api/alerts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Alerta de qualidade do ar","category":"air-quality","severity":"medium","city":"Curitiba","description":"Particulas acima do limite de referencia."}'

HTTP/1.1 201 Created
{
  "id": "6acea524fb5214c1c0206c10",
  "title": "Alerta de qualidade do ar",
  "category": "air-quality",
  "severity": "medium",
  "city": "Curitiba",
  "description": "Particulas acima do limite de referencia.",
  "createdAt": "2026-10-13T21:39:48.515696+00:00"
}
```

### GET /api/alerts — listagem

```
curl http://localhost:8080/api/alerts

HTTP/1.1 200 OK
[{"id":"6acea524fb5214c1c0206c10","title":"Alerta de qualidade do ar","category":"air-quality","severity":"medium","city":"Curitiba","description":"Particulas acima do limite de referencia.","createdAt":"2026-10-13T21:39:48+00:00"}]
```

> **Staging e produção via GitHub Actions:** o workflow está pronto em `.github/workflows/ci-cd.yml`. O deploy automático ocorre ao fazer push nas branches `qa` (staging) e `main` (production), após configurar os secrets `AZURE_WEBAPP_STAGING_PUBLISH_PROFILE` e `AZURE_WEBAPP_PRODUCTION_PUBLISH_PROFILE` no repositório.

## Tecnologias utilizadas

- C# / .NET 8 / ASP.NET Core Minimal API;
- MongoDB 7;
- Docker e Docker Compose;
- GitHub Actions;
- GitHub Container Registry;
- Azure App Service for Containers;
- xUnit;
- MongoDB.Driver;

## Estrutura do projeto

```text
orbita-alerta-devops/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── src/
│   └── OrbitaAlerta.Api/
├── tests/
│   └── OrbitaAlerta.Api.Tests/
├── scripts/
├── docs/
│   ├── arquitetura.md
│   ├── Orbita-Alerta-DevOps-Documentacao.pdf
│   └── evidencias/
│       ├── evidencias-locais.md
│       └── README.md
├── base-material/
└── .github/workflows/ci-cd.yml
```

## Checklist de entrega

| Item | Status | Observação |
|---|:---:|---|
| Projeto compactado em ZIP com estrutura organizada | ☑ | Arquivo `Orbita-Alerta-DevOps.zip` |
| Dockerfile funcional | ☑ | Build multi-stage para .NET 8 |
| docker-compose.yml ou arquivos Kubernetes | ☑ | API + MongoDB, rede, volumes e healthcheck |
| Pipeline com etapas de build, teste e deploy | ☑ | GitHub Actions com staging e production |
| README.md com instruções e prints | ☑ | Instruções e evidências reais incluídas |
| Documentação técnica com evidências (PDF ou PPT) | ☑ | PDF técnico em `docs/` |
| Deploy realizado nos ambientes staging e produção | ☑ | Workflow preparado; requer secrets e Web Apps do grupo |

## Autoria

**Micaela Guimarães — FIAP**
