# Roteiro de evidências

As capturas abaixo devem ser obtidas depois que o repositório estiver conectado ao GitHub e os secrets do Azure estiverem configurados. O roteiro evita o uso de imagens ilustrativas como se fossem execuções reais.

1. **Build:** abrir o job `Build e testes` e capturar as etapas `Restore`, `Build` e `Testes automatizados` com status verde.
2. **Imagem:** abrir o job `Build e publicação da imagem` e capturar o `docker/build-push-action` concluído.
3. **Staging:** capturar o job `Deploy staging` e o endpoint `https://<app-staging>/health`.
4. **Produção:** capturar a aprovação do ambiente `production`, o job concluído e o endpoint `https://<app-production>/health`.
5. **Compose:** executar `docker compose ps` e `curl http://localhost:8080/health` localmente.

Sugestão de nomes:

```text
01-github-build-test.png
02-github-container.png
03-github-deploy-staging.png
04-github-deploy-production.png
05-local-compose-health.png
```

