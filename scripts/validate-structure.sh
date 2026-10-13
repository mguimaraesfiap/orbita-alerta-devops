#!/usr/bin/env bash
set -euo pipefail

required=(
  "Dockerfile"
  "docker-compose.yml"
  ".env.example"
  "README.md"
  "src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj"
  "tests/OrbitaAlerta.Api.Tests/OrbitaAlerta.Api.Tests.csproj"
  ".github/workflows/ci-cd.yml"
)

for file in "${required[@]}"; do
  test -f "$file" || { echo "Arquivo ausente: $file"; exit 1; }
done

echo "Estrutura mínima validada com sucesso."

