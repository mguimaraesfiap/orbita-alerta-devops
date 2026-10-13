# Evidências de execução local — Órbita Alerta

Data de captura: 13/10/2026

---

## 1. Restore de dependências

```
dotnet restore src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj
dotnet restore tests/OrbitaAlerta.Api.Tests/OrbitaAlerta.Api.Tests.csproj
```

**Saída:**
```
Determining projects to restore...
  Restored src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj (in 11,64 sec).
  Determining projects to restore...
  Restored tests/OrbitaAlerta.Api.Tests/OrbitaAlerta.Api.Tests.csproj (in 4,41 sec).
```

---

## 2. Build da aplicação

```
dotnet build src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj --configuration Release --no-restore
```

**Saída:**
```
  OrbitaAlerta.Api -> src/OrbitaAlerta.Api/bin/Release/net8.0/OrbitaAlerta.Api.dll

Build succeeded.
    0 Warning(s)
    0 Error(s)

Time Elapsed 00:00:03.74
```

---

## 3. Testes automatizados — 3/3 passando

```
dotnet test tests/OrbitaAlerta.Api.Tests/OrbitaAlerta.Api.Tests.csproj --configuration Release
```

**Saída:**
```
[xUnit.net 00:00:00.00] xUnit.net VSTest Adapter v2.8.1+ce9211e970 (64-bit .NET 8.0.31)
[xUnit.net 00:00:00.38]   Discovering: OrbitaAlerta.Api.Tests
[xUnit.net 00:00:00.41]   Discovered:  OrbitaAlerta.Api.Tests
[xUnit.net 00:00:00.42]   Starting:    OrbitaAlerta.Api.Tests
[xUnit.net 00:00:00.58]   Finished:    OrbitaAlerta.Api.Tests
  Passed OrbitaAlerta.Api.Tests.AlertValidatorTests.Should_reject_missing_required_fields [123 ms]
  Passed OrbitaAlerta.Api.Tests.AlertValidatorTests.Should_accept_a_valid_alert [1 ms]
  Passed OrbitaAlerta.Api.Tests.AlertValidatorTests.Should_reject_an_unknown_severity [1 ms]

Test Run Successful.
Total tests: 3
     Passed: 3
Total time: 1,4830 Seconds
```

---

## 4. Docker Compose — build e inicialização

```
cp .env.example .env
docker compose up --build -d
```

**Build Docker (multi-stage):**
```
#13 [build 4/6] RUN dotnet restore "src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj"  CACHED
#14 [build 5/6] COPY . .  DONE
#15 [build 6/6] RUN dotnet publish "src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj" \
      --configuration Release --output /app/publish --no-restore /p:UseAppHost=false
#15   OrbitaAlerta.Api -> /app/publish/  DONE 3.9s

Image orbita-alerta-api:local  Built
Container orbita-alerta-mongodb  Running
Container orbita-alerta-api  Running
Container orbita-alerta-mongodb  Healthy
```

---

## 5. Status dos containers

```
docker compose ps
```

**Saída:**
```
NAME                    IMAGE                    COMMAND               SERVICE   CREATED       STATUS                  PORTS
orbita-alerta-api       orbita-alerta-api:local  "dotnet OrbitaAlert…" api       14 min ago    Up 14 minutes           0.0.0.0:8080->8080/tcp
orbita-alerta-mongodb   mongo:7.0                "docker-entrypoint…"  mongodb   14 min ago    Up 14 minutes (healthy) 0.0.0.0:27017->27017/tcp
```

---

## 6. Endpoint /health

```
curl http://localhost:8080/health
```

**Resposta (HTTP 200):**
```json
{
  "status": "healthy",
  "service": "orbita-alerta-api",
  "environment": "Development"
}
```

---

## 7. POST /api/alerts — criação de alerta

```
curl -X POST http://localhost:8080/api/alerts \
  -H 'Content-Type: application/json' \
  -d '{"title":"Alerta de qualidade do ar","category":"air-quality","severity":"medium","city":"Curitiba","description":"Particulas acima do limite de referencia."}'
```

**Resposta (HTTP 201):**
```json
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

---

## 8. GET /api/alerts — listagem de alertas

```
curl http://localhost:8080/api/alerts
```

**Resposta (HTTP 200):**
```json
[
  {
    "id": "6acea524fb5214c1c0206c10",
    "title": "Alerta de qualidade do ar",
    "category": "air-quality",
    "severity": "medium",
    "city": "Curitiba",
    "description": "Particulas acima do limite de referencia.",
    "createdAt": "2026-10-13T21:39:48.515696+00:00"
  }
]
```

---

## 9. Logs do container API

```
docker compose logs api --tail=30
```

**Saída:**
```
orbita-alerta-api  | info: Microsoft.AspNetCore.Hosting.Diagnostics[2]
orbita-alerta-api  |       Request finished HTTP/1.1 GET http://localhost:8080/health - 200 - application/json; 1.2500ms
orbita-alerta-api  | info: Microsoft.AspNetCore.Hosting.Diagnostics[2]
orbita-alerta-api  |       Request finished HTTP/1.1 GET http://localhost:8080/api/alerts - 200 - application/json; 23.4647ms
orbita-alerta-api  | info: Microsoft.AspNetCore.Hosting.Diagnostics[2]
orbita-alerta-api  |       Request finished HTTP/1.1 POST http://localhost:8080/api/alerts - 201 - application/json; 71.5883ms
```

---

## Resumo

| Etapa                          | Resultado |
|-------------------------------|:---------:|
| Restore de dependências       | ✅ OK     |
| Build Release                 | ✅ OK     |
| Testes automatizados (3/3)    | ✅ PASSED |
| Docker image build            | ✅ OK     |
| MongoDB healthcheck           | ✅ HEALTHY|
| API /health                   | ✅ 200    |
| POST /api/alerts              | ✅ 201    |
| GET /api/alerts               | ✅ 200    |
