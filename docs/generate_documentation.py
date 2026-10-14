"""Gera docs/Orbita-Alerta-DevOps-Documentacao.pdf com os prints de docs/evidencias/prints.

Uso (na raiz do projeto): python docs/generate_documentation.py
Os prints são gerados antes por: powershell -ExecutionPolicy Bypass -File scripts/collect-evidence.ps1
"""
import os
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, PageTemplate, Paragraph,
    Preformatted, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/Orbita-Alerta-DevOps-Documentacao.pdf"
PRINTS = ROOT / "docs/evidencias/prints"
TERMINAL = ROOT / "docs/evidencias/terminal"
PAGE_W, PAGE_H = A4
GREEN = colors.HexColor("#0B6B57")
DARK = colors.HexColor("#18323C")
LIGHT = colors.HexColor("#EAF4F1")
GRAY = colors.HexColor("#5B6870")

WIN_FONTS = Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"
FONT_FILES = {
    "Body": [WIN_FONTS / "segoeui.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")],
    "Body-Bold": [WIN_FONTS / "segoeuib.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")],
    "Mono": [WIN_FONTS / "consola.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")],
    "Sym": [WIN_FONTS / "seguisym.ttf", Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")],
}
for name, candidates in FONT_FILES.items():
    pdfmetrics.registerFont(TTFont(name, str(next(p for p in candidates if p.exists()))))


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D8E2E0"))
    canvas.line(1.7 * cm, 1.35 * cm, PAGE_W - 1.7 * cm, 1.35 * cm)
    canvas.setFont("Body", 8)
    canvas.setFillColor(GRAY)
    canvas.drawString(1.7 * cm, 0.85 * cm, "Cidades ESG Inteligentes | Órbita Alerta | DevOps | FIAP")
    canvas.drawRightString(PAGE_W - 1.7 * cm, 0.85 * cm, f"Página {doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", fontName="Body-Bold", fontSize=27, leading=32, textColor=DARK, alignment=TA_CENTER, spaceAfter=14))
styles.add(ParagraphStyle(name="CoverSub", fontName="Body", fontSize=13, leading=19, textColor=GREEN, alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="H1x", fontName="Body-Bold", fontSize=17, leading=22, textColor=DARK, spaceBefore=6, spaceAfter=9))
styles.add(ParagraphStyle(name="H2x", fontName="Body-Bold", fontSize=12, leading=15, textColor=GREEN, spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="Bodyx", fontName="Body", fontSize=9.5, leading=14, textColor=DARK, spaceAfter=6))
styles.add(ParagraphStyle(name="Smallx", fontName="Body", fontSize=8, leading=11, textColor=GRAY, spaceAfter=4))
styles.add(ParagraphStyle(name="Caption", fontName="Body", fontSize=8, leading=11, textColor=GRAY, alignment=TA_CENTER, spaceBefore=3, spaceAfter=10))
styles.add(ParagraphStyle(name="Callout", fontName="Body-Bold", fontSize=9.5, leading=14, textColor=GREEN, backColor=LIGHT, borderPadding=8, spaceBefore=5, spaceAfter=10))
styles.add(ParagraphStyle(name="Codex", fontName="Mono", fontSize=7.5, leading=10, textColor=colors.HexColor("#233238"), backColor=colors.HexColor("#F3F6F5"), borderPadding=7, leftIndent=5, rightIndent=5, spaceBefore=4, spaceAfter=8))


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullet(text):
    return P(f"• {text}")


def table(data, widths, header=True):
    rows = [[P(c, "Smallx" if header and i == 0 else "Bodyx") if isinstance(c, str) else c for c in row] for i, row in enumerate(data)]
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    cmds = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D8D4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    if header:
        cmds += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAF9")])]
    t.setStyle(TableStyle(cmds))
    return t


def shot(name, caption):
    path = PRINTS / f"{name}.png"
    if not path.exists():
        return [P(f"[print ausente: {path.name}]", "Callout")]
    img = Image(str(path))
    max_w, max_h = PAGE_W - 3.4 * cm, PAGE_H - 6 * cm
    scale = min(max_w / img.imageWidth, max_h / img.imageHeight)
    img.drawWidth, img.drawHeight = img.imageWidth * scale, img.imageHeight * scale
    return [KeepTogether([img, P(caption, "Caption")])]


def pipeline_status():
    """Runs do GitHub Actions com deploy concluído (Figuras 3 e 4): #4 em qa (staging) e #5 em main (produção)."""
    ok = all((PRINTS / f"{n}.png").exists() for n in ("10-github-run-staging", "11-github-run-production"))
    return ok, ok


def check(ok):
    return f'<font name="Sym">{"☑" if ok else "☐"}</font>'


staging_ok, production_ok = pipeline_status()
deploy_ok = staging_ok and production_ok
story = []

# Capa
story += [Spacer(1, 2.4 * cm), P("PROJETO ESG + DEVOPS", "CoverSub"), P("Cidades ESG Inteligentes", "CoverTitle"),
          P("Órbita Alerta", "CoverTitle"), P("Documentação técnica da entrega — Navegando pelo mundo DevOps", "CoverSub"), Spacer(1, 1 * cm)]
story.append(table([
    ["Integrante", "Micaela Guimarães — FIAP"],
    ["Repositório", "github.com/mguimaraesfiap/orbita-alerta-devops"],
    ["Staging", "https://orbita-alerta-staging-mg.azurewebsites.net"],
    ["Produção", "https://orbita-alerta-production-mg.azurewebsites.net"],
    ["Stack", "C# / .NET 8, MongoDB, Docker, Docker Compose, GitHub Actions, GHCR, Azure App Service e Azure Cosmos DB (API MongoDB)"],
], [3.2 * cm, 14.4 * cm], header=False))
story.append(PageBreak())

# 1. Contexto
story += [P("1. Contexto e objetivo", "H1x"),
          P("O Órbita Alerta é uma API ESG para registro de alertas ambientais de cidades inteligentes. Nesta fase, o projeto C# foi adaptado para simular um ambiente de produção: build e testes automatizados, imagem Docker, orquestração com Docker Compose e deploy automatizado em dois ambientes na nuvem (staging e produção)."),
          P("Endpoints: <b>GET /health</b> (estado da aplicação e ambiente), <b>GET /api/alerts</b> (lista alertas ordenados por data) e <b>POST /api/alerts</b> (cria alerta com validação de título, categoria, severidade e cidade).")]

# 2. Pipeline
story += [P("2. Pipeline CI/CD", "H1x"),
          P("Ferramenta: <b>GitHub Actions</b>, arquivo <b>.github/workflows/ci-cd.yml</b>. O workflow é acionado em pull requests e pushes nas branches develop, qa e main. Os jobs são encadeados por <b>needs</b>: nada é publicado se o build ou os testes falharem, e o mesmo artefato (imagem identificada pelo SHA do commit) é promovido para os ambientes.")]
story.append(table([
    ["Job", "Quando executa", "O que faz"],
    ["Build e testes", "PR e push (develop, qa, main)", "Setup do .NET 8, restore, build Release, testes xUnit com cobertura e upload dos resultados (.trx) como artefato."],
    ["Build e publicação da imagem", "push em qa ou main", "Login no GHCR com GITHUB_TOKEN, docker build multi-stage e push com as tags &lt;sha&gt; e &lt;branch&gt;-latest."],
    ["Deploy staging", "push em qa", "azure/webapps-deploy atualiza o Web App de staging com a imagem do commit; em seguida, smoke test em /health e /api/alerts."],
    ["Deploy production", "push em main", "Mesmo processo no Web App de produção (GitHub Environment production), com smoke test ao final."],
], [3.6 * cm, 3.6 * cm, 10.4 * cm]))
story += [P("Fluxo de promoção", "H2x"),
          Preformatted("feature -> develop (build + testes)\n        -> qa      (build + testes -> imagem GHCR -> deploy staging    -> smoke test)\n        -> main    (build + testes -> imagem GHCR -> deploy production -> smoke test)", styles["Codex"]),
          P("Segredos usados pelo pipeline (GitHub → Settings → Secrets): AZURE_WEBAPP_STAGING, AZURE_WEBAPP_STAGING_PUBLISH_PROFILE, AZURE_WEBAPP_PRODUCTION e AZURE_WEBAPP_PRODUCTION_PUBLISH_PROFILE. A string de conexão do banco fica somente nas configurações de cada Web App (MONGO_CONNECTION_STRING e MONGO_DATABASE), fora do repositório.")]

# 3. Docker
story += [P("3. Docker: arquitetura, comandos e imagem", "H1x"),
          P("O Dockerfile usa build multi-stage: a imagem do SDK compila e publica; a imagem final contém apenas o runtime ASP.NET Core e os binários publicados, roda na porta 8080 e com o usuário não privilegiado <b>app</b>.")]
story.append(Preformatted((ROOT / "Dockerfile").read_text(encoding="utf-8").strip(), styles["Codex"]))
story += [P("Orquestração com Docker Compose", "H2x"),
          bullet("<b>api</b>: build do Dockerfile, imagem orbita-alerta-api:local, porta ${API_PORT:-8080}, variáveis ASPNETCORE_ENVIRONMENT, MONGO_CONNECTION_STRING e MONGO_DATABASE, sobe somente após o MongoDB ficar saudável (depends_on + healthcheck)."),
          bullet("<b>mongodb</b>: mongo:7.0 com usuário root definido por variáveis do .env e healthcheck via mongosh."),
          bullet("<b>Volumes</b> nomeados orbita-alerta-mongodb-data e orbita-alerta-mongodb-config preservam os dados entre reinícios."),
          bullet("<b>Rede</b> bridge orbita-alerta-network isola a comunicação entre API e banco."),
          bullet("<b>.env.example</b> documenta as variáveis; o .env real não é versionado nem copiado para a imagem (.dockerignore).")]
story += [P("Comandos utilizados", "H2x"),
          Preformatted("Copy-Item .env.example .env\ndocker compose up --build -d\ndocker compose ps\nInvoke-RestMethod http://localhost:8080/health\ndocker compose logs -f api\ndocker compose down        # mantém o volume do MongoDB", styles["Codex"])]
story += [P("Ambientes em nuvem (Azure for Students, capacidade mínima)", "H2x")]
story.append(table([
    ["Recurso", "Configuração"],
    ["App Service Plan plan-orbita-alerta", "Linux, SKU F1 (gratuito), North Central US"],
    ["Web App orbita-alerta-staging-mg", "Container da imagem GHCR, ASPNETCORE_ENVIRONMENT=Staging, banco orbita_alerta_staging"],
    ["Web App orbita-alerta-production-mg", "Container da imagem GHCR, ASPNETCORE_ENVIRONMENT=Production, banco orbita_alerta_production"],
    ["Cosmos DB orbita-alerta-cosmos-mg", "API MongoDB, free tier (1000 RU/s gratuitos), 400 RU/s por banco, South Africa North"],
], [6 * cm, 11.6 * cm]))
story.append(PageBreak())

# 4. Prints do pipeline
story += [P("4. Evidências: pipeline (build, testes e deploy)", "H1x")]
story += shot("01-dotnet-build", "Figura 1 — Restore e build Release da API.")
story += shot("02-dotnet-test", "Figura 2 — Testes automatizados xUnit: 3 de 3 aprovados.")
story += shot("10-github-run-staging", "Figura 3 — GitHub Actions, run #4 (branch qa): build e testes, publicação da imagem e Deploy staging concluídos com sucesso.")
story += shot("11-github-run-production", "Figura 4 — GitHub Actions, run #5 (branch main): build e testes, publicação da imagem e Deploy production concluídos com sucesso.")
story += shot("12-github-secrets", "Figura 5 — Secrets do Azure cadastrados no repositório GitHub (valores criptografados, não exibidos).")
story += shot("03-docker-compose-up", "Figura 6 — Build da imagem multi-stage e subida dos containers com Docker Compose.")
story += shot("04-docker-compose-ps", "Figura 7 — Containers em execução, imagem criada, volumes e rede.")
story += shot("05-local-api", "Figura 8 — API local: healthcheck, criação e listagem de alertas.")
story += shot("06-local-logs", "Figura 9 — Logs do container da API.")

# 5. Staging e produção
story += [PageBreak(), P("5. Evidências: ambientes staging e produção", "H1x")]
story += shot("07-azure-recursos", "Figura 10 — Recursos Azure: Web Apps de staging e produção em execução, plano F1 e Cosmos DB free tier.")
story += shot("08-staging", "Figura 11 — Staging (orbita-alerta-staging-mg.azurewebsites.net): /health com environment=Staging, POST e GET de alertas.")
story += shot("09-production", "Figura 12 — Produção (orbita-alerta-production-mg.azurewebsites.net): /health com environment=Production, POST e GET de alertas.")

# 6. Desafios
story += [PageBreak(), P("6. Desafios encontrados e soluções", "H1x")]
story.append(table([
    ["Desafio", "Solução"],
    ["Primeiro deploy de produção falhou com “No credentials found”: o workflow dependia de secrets ainda não cadastrados e a branch qa não existia.", "Criação dos Web Apps, habilitação das credenciais de publicação (basic auth do SCM), cadastro dos publish profiles como secrets e criação da branch qa para o fluxo de staging."],
    ["A assinatura Azure for Students só permite 5 regiões; o Cosmos DB herdava a região do resource group (eastus) e era bloqueado pela política.", "Resource group dedicado ao banco, criado em uma região permitida."],
    ["North Central US sem capacidade para novas contas Cosmos DB no momento da criação.", "Banco criado em South Africa North; a API acessa o banco pela string de conexão, independente da região."],
    ["O MongoDB local (Docker Desktop) não é acessível pelos ambientes em nuvem.", "Cosmos DB com API MongoDB no free tier, um banco por ambiente (orbita_alerta_staging e orbita_alerta_production)."],
    ["GET /api/alerts retornava HTTP 500 no Azure: o Cosmos DB só ordena por campos indexados (no MongoDB local o índice é opcional).", "A aplicação passou a criar o índice CreatedAt na inicialização (MongoAlertRepository) e o índice foi criado nas collections existentes."],
    ["Manter custo zero e não expor credenciais.", "Plano F1 gratuito, Cosmos free tier, segredos somente em GitHub Secrets e nas configurações do App Service; .env e publish profiles no .gitignore."],
], [8.3 * cm, 9.3 * cm]))

# 7. Checklist
story += [Spacer(1, 10), P("7. Checklist de entrega", "H1x")]
story.append(table([
    ["Item", "OK", "Observação"],
    ["Projeto compactado em .ZIP com estrutura organizada", check(True), "Dockerfile, docker-compose.yml, src/, tests/, scripts/, docs/, README.md, .env.example e .github/workflows/."],
    ["Dockerfile funcional", check(True), "Multi-stage .NET 8, usuário não privilegiado (Figura 6)."],
    ["docker-compose.yml ou arquivos Kubernetes", check(True), "API + MongoDB com volumes, variáveis de ambiente, rede e healthcheck (Figura 7)."],
    ["Pipeline com etapas de build, teste e deploy", check(True), "GitHub Actions: build, testes, imagem GHCR e deploy (Figuras 3 a 5)."],
    ["README.md com instruções e prints", check(True), "Execução local, pipeline, containerização, prints e tecnologias."],
    ["Documentação técnica com evidências (PDF ou PPT)", check(True), "Este PDF."],
    ["Deploy realizado nos ambientes staging e produção", check(deploy_ok),
     "Deploy pelo pipeline concluído em staging (run #4) e produção (run #5), com smoke test (Figuras 3, 4, 11 e 12)." if deploy_ok else
     "Ambientes no ar e respondendo (Figuras 10 a 12); job de deploy do pipeline aguardando o cadastro dos secrets do Azure."],
], [6.4 * cm, 1.2 * cm, 10 * cm]))

doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.6 * cm, bottomMargin=1.8 * cm,
                      title="Órbita Alerta - Documentação DevOps", author="Micaela Guimarães")
doc.addPageTemplates([PageTemplate(id="main", frames=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal"), onPage=on_page)])
doc.build(story)
print(OUT)
