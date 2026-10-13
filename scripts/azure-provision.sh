#!/usr/bin/env bash
# Provisiona os ambientes staging e production no Azure App Service (Linux, plano F1).
# Pré-requisitos: az login, Cosmos DB (API MongoDB) criado e plano plan-orbita-alerta existente.
set -euo pipefail

RG="${RG:-rg-orbita-alerta}"
PLAN="${PLAN:-plan-orbita-alerta}"
DB_RG="${DB_RG:-rg-orbita-alerta-db-southafricanorth}"
COSMOS="${COSMOS:-orbita-alerta-cosmos-mg}"
IMAGE="${IMAGE:-ghcr.io/mguimaraesfiap/orbita-alerta-api:main-latest}"
OUT_DIR="${OUT_DIR:-.azure-secrets}"

mkdir -p "$OUT_DIR"
MONGO_CONN=$(az cosmosdb keys list -g "$DB_RG" -n "$COSMOS" --type connection-strings \
  --query "connectionStrings[0].connectionString" -o tsv)

for env in staging production; do
  app="orbita-alerta-$env-mg"
  aspnet_env=$([ "$env" = "staging" ] && echo Staging || echo Production)

  az webapp create -g "$RG" -p "$PLAN" -n "$app" \
    --deployment-container-image-name "$IMAGE" -o none

  az webapp config appsettings set -g "$RG" -n "$app" -o none --settings \
    WEBSITES_PORT=8080 \
    ASPNETCORE_ENVIRONMENT="$aspnet_env" \
    MONGO_DATABASE="orbita_alerta_$env" \
    MONGO_CONNECTION_STRING="$MONGO_CONN"

  # O azure/webapps-deploy com publish profile exige credenciais básicas de publicação.
  az resource update -g "$RG" --namespace Microsoft.Web --resource-type basicPublishingCredentialsPolicies \
    --parent "sites/$app" -n scm --set properties.allow=true -o none

  az webapp deployment list-publishing-profiles -g "$RG" -n "$app" --xml > "$OUT_DIR/$app.PublishSettings"
  echo "$app -> https://$app.azurewebsites.net (publish profile em $OUT_DIR/$app.PublishSettings)"
done
