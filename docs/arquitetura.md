# Arquitetura técnica

## Componentes

- **API:** ASP.NET Core Minimal API em .NET 8.
- **Persistência:** MongoDB 7, collection `alerts`.
- **Execução local:** Docker Compose, rede `orbita-alerta-network` e volumes nomeados.
- **CI:** GitHub Actions com restore, build e testes xUnit.
- **CD:** imagem publicada no GHCR e promoção para Azure App Service em `staging` e `production`.

## Fluxo de promoção

```text
Pull Request -> build/test -> merge em qa -> imagem GHCR -> staging
                                              |
                         validação/aprovação -+
                                              v
                                           main -> production
```

## Decisões de segurança

- Segredos ficam em GitHub Actions Secrets e nas configurações do App Service.
- O arquivo `.env.example` possui somente valores de exemplo.
- A imagem de runtime usa o usuário não privilegiado `app`.
- A produção é um GitHub Environment protegido por aprovação.
- O deploy usa a imagem identificada pelo SHA do commit, evitando dependência exclusiva de `latest`.

