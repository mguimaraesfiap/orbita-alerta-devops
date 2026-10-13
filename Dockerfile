# syntax=docker/dockerfile:1

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj", "src/OrbitaAlerta.Api/"]
RUN dotnet restore "src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj"
COPY . .
RUN dotnet publish "src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj" \
    --configuration Release \
    --output /app/publish \
    --no-restore \
    /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ENV DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=false
COPY --from=build /app/publish .
USER app
ENTRYPOINT ["dotnet", "OrbitaAlerta.Api.dll"]

