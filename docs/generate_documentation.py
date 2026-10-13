from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


OUT = "docs/Orbita-Alerta-DevOps-Documentacao.pdf"
PAGE_W, PAGE_H = A4
GREEN = colors.HexColor("#0B6B57")
DARK = colors.HexColor("#18323C")
LIGHT = colors.HexColor("#EAF4F1")
ORANGE = colors.HexColor("#D98528")
GRAY = colors.HexColor("#5B6870")

pdfmetrics.registerFont(TTFont("DejaVu", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Mono", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"))


class NumberedCanvasMixin:
    def on_page(self, canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#D8E2E0"))
        canvas.line(1.7 * cm, 1.35 * cm, PAGE_W - 1.7 * cm, 1.35 * cm)
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(GRAY)
        canvas.drawString(1.7 * cm, 0.85 * cm, "Órbita Alerta | DevOps | FIAP")
        canvas.drawRightString(PAGE_W - 1.7 * cm, 0.85 * cm, f"Página {doc.page}")
        canvas.restoreState()


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontName="DejaVu-Bold", fontSize=27, leading=32, textColor=DARK, alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontName="DejaVu", fontSize=13, leading=19, textColor=GREEN, alignment=TA_CENTER, spaceAfter=10))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], fontName="DejaVu-Bold", fontSize=18, leading=22, textColor=DARK, spaceBefore=8, spaceAfter=10))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], fontName="DejaVu-Bold", fontSize=12, leading=15, textColor=GREEN, spaceBefore=9, spaceAfter=6))
styles.add(ParagraphStyle(name="Bodyx", parent=styles["BodyText"], fontName="DejaVu", fontSize=9.5, leading=14, textColor=DARK, spaceAfter=7))
styles.add(ParagraphStyle(name="Smallx", parent=styles["BodyText"], fontName="DejaVu", fontSize=8, leading=11, textColor=GRAY, spaceAfter=5))
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], fontName="DejaVu-Bold", fontSize=10, leading=14, textColor=GREEN, backColor=LIGHT, borderPadding=8, spaceBefore=5, spaceAfter=10))
styles.add(ParagraphStyle(name="Codex", parent=styles["Code"], fontName="DejaVu-Mono", fontSize=7.5, leading=10, textColor=colors.HexColor("#233238"), backColor=colors.HexColor("#F3F6F5"), borderPadding=7, leftIndent=5, rightIndent=5, spaceBefore=4, spaceAfter=8))


def P(text, style="Bodyx"):
    return Paragraph(text, styles[style])


def bullet(text):
    return P(f"• {text}", "Bodyx")


def table(data, widths, header=True):
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C9D8D4")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    if header:
        commands += [("BACKGROUND", (0, 0), (-1, 0), GREEN), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold")]
        if len(data) > 1:
            commands.append(("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F8F7")]))
    t.setStyle(TableStyle(commands))
    return t


def flow_box(label, detail):
    return Table([[P(f"<b>{label}</b><br/><font size=8>{detail}</font>", "Bodyx")]], colWidths=[4.1 * cm], rowHeights=[1.25 * cm], style=TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.8, GREEN),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))


story = []

# Cover
story += [Spacer(1, 2.6 * cm), P("PROJETO ESG + DEVOPS", "CoverSub"), P("Cidades ESG Inteligentes", "CoverTitle"), P("Órbita Alerta", "CoverTitle"), P("Documentação técnica da entrega", "CoverSub"), Spacer(1, 1.2 * cm)]
story.append(table([[P("Objetivo", "Smallx"), P("Aplicar CI/CD, containerização e orquestração a uma API ESG executável.", "Bodyx")], [P("Integrante", "Smallx"), P("Micaela Guimarães — FIAP", "Bodyx")], [P("Stack", "Smallx"), P("C# / .NET 8, MongoDB, Docker Compose e GitHub Actions", "Bodyx")]], [3.2 * cm, 12.3 * cm], header=False))
story += [Spacer(1, 1.3 * cm), P("Versão preparada em 27/09/2026", "Smallx"), PageBreak()]

# Context
story += [P("1. Contexto e objetivo", "H1x"), P("O Órbita Alerta é uma solução ESG voltada ao registro de alertas ambientais, áreas monitoradas e ocorrências de gestão. Nesta etapa, o projeto foi adaptado para representar um ciclo de entrega mais próximo de um ambiente produtivo: o código possui API executável, persistência em MongoDB, testes automatizados, imagem Docker e fluxo de promoção entre staging e produção.")]
story.append(P("A implementação foi preparada para execução real. As evidências de pipeline e de deploy externo não foram simuladas no documento: dependem da conexão do repositório às contas GitHub/Azure e da configuração dos secrets descritos no README.", "Callout"))
story += [P("2. Arquitetura da solução", "H1x"), P("A arquitetura separa a aplicação da persistência e utiliza o mesmo artefato de imagem no processo de promoção. No ambiente local, Docker Compose cria a API e o MongoDB em uma rede dedicada, com volumes nomeados para preservar os dados.")]
arch = [[flow_box("Desenvolvedor", "commit / pull request"), P("→", "CoverTitle"), flow_box("GitHub Actions", "build + testes"), P("→", "CoverTitle"), flow_box("GHCR", "imagem por SHA")], [P("", "Bodyx"), P("", "Bodyx"), P("↓", "CoverTitle"), P("", "Bodyx"), P("", "Bodyx")], [P("", "Bodyx"), P("", "Bodyx"), flow_box("staging", "Azure App Service"), P("→", "CoverTitle"), flow_box("production", "ambiente protegido")]]
story.append(Table(arch, colWidths=[4.1 * cm, 1.0 * cm, 4.1 * cm, 1.0 * cm, 4.1 * cm], style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"), ("SPAN", (2, 1), (2, 1))])))
story += [Spacer(1, 8), P("Componentes principais", "H2x"), bullet("ASP.NET Core Minimal API em .NET 8, com endpoint de healthcheck e operações de consulta/criação de alertas."), bullet("MongoDB 7, collection alerts e conexão configurável por variável de ambiente."), bullet("Docker Compose com rede, volumes e healthcheck do banco."), bullet("GitHub Actions para integração contínua, publicação no GHCR e deploy em dois ambientes.")]

# Pipeline
story += [P("3. Pipeline CI/CD", "H1x"), P("O workflow .github/workflows/ci-cd.yml é acionado em pull requests e pushes nas branches develop, qa e main. O pipeline foi dividido em jobs para deixar explícita a dependência entre qualidade, empacotamento e promoção.")]
pipeline_rows = [[P("Job", "Smallx"), P("Quando", "Smallx"), P("Responsabilidade", "Smallx")], [P("build-test", "Bodyx"), P("PR e push", "Bodyx"), P("Restore, build Release, testes xUnit e upload dos resultados.", "Bodyx")], [P("container", "Bodyx"), P("push em qa/main", "Bodyx"), P("Login no GHCR, build da imagem e tags por SHA/branch.", "Bodyx")], [P("deploy-staging", "Bodyx"), P("push em qa", "Bodyx"), P("Deploy automático no ambiente staging.", "Bodyx")], [P("deploy-production", "Bodyx"), P("push em main", "Bodyx"), P("Deploy no ambiente production, sujeito à aprovação configurada no GitHub.", "Bodyx")]]
story.append(table(pipeline_rows, [3.1 * cm, 3.5 * cm, 8.9 * cm]))
story += [P("Secrets previstos", "H2x"), P("Os nomes dos Web Apps e os publish profiles são mantidos fora do código. O pipeline espera AZURE_WEBAPP_STAGING, AZURE_WEBAPP_STAGING_PUBLISH_PROFILE, AZURE_WEBAPP_PRODUCTION e AZURE_WEBAPP_PRODUCTION_PUBLISH_PROFILE. As credenciais do MongoDB devem ser configuradas como variáveis do App Service ou secret manager equivalente.")]

# Docker
story += [P("4. Containerização e orquestração", "H1x"), P("O Dockerfile utiliza uma estratégia multi-stage. A etapa de build contém o SDK completo apenas durante a compilação; a etapa final utiliza a imagem menor de runtime do ASP.NET Core. O processo reduz a superfície da imagem e evita transportar artefatos de desenvolvimento para execução.")]
story.append(Preformatted("FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build\nRUN dotnet restore ...\nRUN dotnet publish ... --configuration Release\n\nFROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime\nEXPOSE 8080\nUSER app\nENTRYPOINT [\"dotnet\", \"OrbitaAlerta.Api.dll\"]", styles["Codex"]))
story += [P("O Compose define API e MongoDB, configura a dependência pelo healthcheck e monta os volumes mongodb-data e mongodb-config. A rede orbita-alerta-network mantém a comunicação dos serviços isolada do restante do host.")]
story.append(Preformatted("cp .env.example .env\ndocker compose up --build -d\ncurl http://localhost:8080/health\ndocker compose down", styles["Codex"]))

# Evidence
story += [P("5. Evidências de execução", "H1x"), P("A entrega inclui o roteiro docs/evidencias/README.md. Ele orienta a captura de cinco evidências reais: build/testes, publicação no GHCR, deploy em staging, aprovação/deploy em produção e healthcheck do Compose.")]
evidence_rows = [[P("Evidência", "Smallx"), P("Fonte", "Smallx"), P("Situação desta versão", "Smallx")], [P("Build e testes", "Bodyx"), P("GitHub Actions", "Bodyx"), P("Workflow configurado; capturar após execução.", "Bodyx")], [P("Imagem Docker", "Bodyx"), P("GHCR", "Bodyx"), P("Job configurado; capturar após publicação.", "Bodyx")], [P("Staging", "Bodyx"), P("Azure App Service", "Bodyx"), P("Deploy automatizado; requer Web App e secrets.", "Bodyx")], [P("Produção", "Bodyx"), P("Azure App Service", "Bodyx"), P("Deploy automatizado e protegido; requer aprovação.", "Bodyx")], [P("Execução local", "Bodyx"), P("Docker Compose", "Bodyx"), P("Comandos documentados; executar no host com Docker.", "Bodyx")]]
story.append(table(evidence_rows, [4.1 * cm, 4.0 * cm, 7.4 * cm]))
story.append(P("Importante: não foram incluídos prints falsos. O material entregue contém a implementação e o roteiro para anexar os prints após a execução no ambiente do grupo.", "Callout"))

# Challenges
story += [P("6. Desafios encontrados e soluções", "H1x"), bullet("Ausência de infraestrutura externa no momento da preparação: a solução foi parametrizada para receber nomes de Web Apps, publish profiles e conexão MongoDB por secrets/variáveis, sem expor credenciais."), bullet("Necessidade de separar qualidade de promoção: o pipeline usa jobs dependentes e só publica imagem/deploy em branches de ambiente."), bullet("Persistência em ambiente local: o Compose utiliza volumes nomeados, enquanto a aplicação recebe a conexão por variável de ambiente."), bullet("Segurança mínima do container: a imagem de runtime utiliza o usuário não privilegiado app e não incorpora o arquivo .env.")]

# Checklist
story += [P("7. Checklist de entrega", "H1x")]
check_rows = [[P("Item", "Smallx"), P("OK", "Smallx"), P("Observação", "Smallx")], [P("Projeto compactado em ZIP", "Bodyx"), P("☑", "Bodyx"), P("Pacote com estrutura organizada.", "Bodyx")], [P("Dockerfile funcional", "Bodyx"), P("☑", "Bodyx"), P("Build multi-stage para .NET 8.", "Bodyx")], [P("docker-compose.yml", "Bodyx"), P("☑", "Bodyx"), P("API + MongoDB, volumes, rede e healthcheck.", "Bodyx")], [P("Pipeline build/test/deploy", "Bodyx"), P("☑", "Bodyx"), P("GitHub Actions para staging e produção.", "Bodyx")], [P("README com instruções", "Bodyx"), P("☑", "Bodyx"), P("Inclui comandos, tecnologias e checklist.", "Bodyx")], [P("Documentação técnica", "Bodyx"), P("☑", "Bodyx"), P("Este PDF.", "Bodyx")], [P("Deploy realizado em staging e produção", "Bodyx"), P("☐", "Bodyx"), P("Pendente de execução nas contas externas; automação está pronta.", "Bodyx")]]
story.append(table(check_rows, [7.0 * cm, 1.5 * cm, 7.0 * cm]))
story += [Spacer(1, 10), P("Conclusão", "H2x"), P("A entrega consolida os principais conceitos da fase DevOps: integração contínua, testes automatizados, empacotamento reproduzível, containerização, orquestração local e promoção controlada entre ambientes. Para concluir a última linha do checklist, basta conectar o repositório aos recursos Azure, cadastrar os secrets e executar o workflow nas branches qa e main.")]


doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=1.7 * cm, rightMargin=1.7 * cm, topMargin=1.6 * cm, bottomMargin=1.8 * cm, title="Órbita Alerta - Documentação DevOps", author="Micaela Guimarães")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
doc.addPageTemplates([PageTemplate(id="main", frames=frame, onPage=NumberedCanvasMixin().on_page)])
doc.build(story)
print(OUT)
