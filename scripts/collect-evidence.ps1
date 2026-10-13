# Gera as evidências de execução: cada grupo de comandos roda ao vivo em uma janela real do
# Windows PowerShell; a janela é capturada em PNG (docs/evidencias/prints) e a saída é salva
# em texto (docs/evidencias/terminal).
# Uso (na raiz do projeto): powershell -ExecutionPolicy Bypass -File scripts/collect-evidence.ps1 [grupo...]
param([string[]]$Only)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$prints = Join-Path $root 'docs\evidencias\prints'
$texts = Join-Path $root 'docs\evidencias\terminal'
New-Item -ItemType Directory -Force $prints, $texts | Out-Null

$staging = 'https://orbita-alerta-staging-mg.azurewebsites.net'
$production = 'https://orbita-alerta-production-mg.azurewebsites.net'
$repo = 'mguimaraesfiap/orbita-alerta-devops'

function ApiChecks([string]$base, [string]$severity, [string]$city, [string]$envName) {
    @(
        "Invoke-WebRequest -UseBasicParsing $base/health | Select-Object StatusCode, Content | Format-List",
        "Invoke-RestMethod -Method Post -Uri $base/api/alerts -ContentType 'application/json' -Body (@{title='Alerta de qualidade do ar'; category='air-quality'; severity='$severity'; city='$city'; description='Evidencia $envName'} | ConvertTo-Json -Compress) | Format-List",
        "(Invoke-RestMethod $base/api/alerts) | ForEach-Object { `$_ } | Select-Object -First 3 title, severity, city, createdAt | Format-Table -AutoSize"
    )
}

$groups = [ordered]@{
    '01-dotnet-build'      = @('dotnet restore src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj',
                               'dotnet build src/OrbitaAlerta.Api/OrbitaAlerta.Api.csproj --configuration Release --no-restore')
    '02-dotnet-test'       = @('dotnet test tests/OrbitaAlerta.Api.Tests/OrbitaAlerta.Api.Tests.csproj --configuration Release --logger "console;verbosity=normal"')
    '03-docker-compose-up' = @('docker compose up --build -d 2>&1 | Select-Object -Last 14')
    '04-docker-compose-ps' = @('docker compose ps', 'docker images orbita-alerta-api',
                               'docker volume ls --filter name=orbita', 'docker network ls --filter name=orbita')
    '05-local-api'         = ApiChecks 'http://localhost:8080' 'medium' 'Curitiba' 'local'
    '06-local-logs'        = @('docker compose logs api --tail=12')
    '07-azure-recursos'    = @('az webapp list -g rg-orbita-alerta --query "[].{Nome:name,Estado:state,Host:defaultHostName}" -o table',
                               'az appservice plan list -g rg-orbita-alerta --query "[].{Plano:name,SKU:sku.name,Regiao:location}" -o table',
                               'az cosmosdb list --query "[].{Cosmos:name,Tipo:kind,FreeTier:enableFreeTier,Regiao:location}" -o table')
    '08-staging'           = ApiChecks $staging 'high' 'Sao Paulo' 'staging'
    '09-production'        = ApiChecks $production 'low' 'Recife' 'production'
    '10-github-actions'    = @("(Invoke-RestMethod 'https://api.github.com/repos/$repo/actions/runs?per_page=4').workflow_runs | Select-Object run_number, head_branch, event, conclusion, @{n='commit';e={`$_.head_sha.Substring(0,7)}}, created_at | Format-Table -AutoSize",
                               "& { foreach (`$b in 'qa','main') { `$run = (Invoke-RestMethod ('https://api.github.com/repos/$repo/actions/runs?per_page=1&branch=' + `$b)).workflow_runs[0]; if (`$run) { (Invoke-RestMethod `$run.jobs_url).jobs | Select-Object @{n='branch';e={`$b}}, @{n='run';e={`$run.run_number}}, @{n='job';e={`$_.name}}, conclusion, completed_at } } } | Format-Table -AutoSize")
}

Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
public static class Shot {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] static extern bool GetClientRect(IntPtr h, out RECT r);
    [DllImport("dwmapi.dll")] static extern int DwmGetWindowAttribute(IntPtr h, int attr, out RECT r, int size);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    public static void Front(IntPtr h) {
        SetWindowPos(h, new IntPtr(-1), 20, 20, 0, 0, 0x0001 | 0x0040);
        SetForegroundWindow(h);
    }
    public static void Release(IntPtr h) { SetWindowPos(h, new IntPtr(-2), 0, 0, 0, 0, 0x0001 | 0x0002); }
    // Captura a janela; rows/usedRows cortam as linhas vazias abaixo do conteúdo.
    public static void Save(IntPtr h, string path, int rows, int usedRows) {
        RECT w; DwmGetWindowAttribute(h, 9, out w, Marshal.SizeOf(typeof(RECT)));
        RECT c; GetClientRect(h, out c);
        int width = w.Right - w.Left, height = w.Bottom - w.Top;
        int chrome = height - (c.Bottom - c.Top);
        int keep = Math.Min(height, chrome + (int)Math.Ceiling((c.Bottom - c.Top) * (double)usedRows / rows) + 6);
        using (var bmp = new Bitmap(width, keep))
        using (var g = Graphics.FromImage(bmp)) {
            g.CopyFromScreen(w.Left, w.Top, 0, 0, new Size(width, keep));
            bmp.Save(path, ImageFormat.Png);
        }
    }
}
'@
[Shot]::SetProcessDPIAware() | Out-Null

foreach ($name in $groups.Keys) {
    if ($Only -and $name -notin $Only) { continue }
    $marker = Join-Path $env:TEMP "evid-$name.done"
    $runner = Join-Path $env:TEMP "evid-$name.ps1"
    Remove-Item $marker -ErrorAction SilentlyContinue
    $cmds = ($groups[$name] | ForEach-Object { "'" + ($_ -replace "'", "''") + "'" }) -join ",`r`n    "
    @"
`$Host.UI.RawUI.WindowTitle = 'Windows PowerShell'
`$raw = `$Host.UI.RawUI
`$max = `$raw.MaxPhysicalWindowSize
`$w = [Math]::Min(150, `$max.Width); `$h = [Math]::Min(60, `$max.Height - 2)
`$raw.BufferSize = New-Object Management.Automation.Host.Size(`$w, 3000)
`$raw.WindowSize = New-Object Management.Automation.Host.Size(`$w, `$h)
Set-Location '$root'
Clear-Host
`$log = "# `$((Get-Date).ToUniversalTime().AddHours(-3).ToString('dd/MM/yyyy HH:mm:ss')) (horario de Brasilia)``r``n"
Write-Host "# Evidencia $name - `$((Get-Date).ToUniversalTime().AddHours(-3).ToString('dd/MM/yyyy HH:mm:ss')) (horario de Brasilia)" -ForegroundColor DarkGray
foreach (`$cmd in @(
    $cmds
)) {
    Write-Host "PS `$(Get-Location)> " -NoNewline
    Write-Host `$cmd -ForegroundColor Yellow
    `$text = (Invoke-Expression `$cmd 2>&1 | Out-String -Width (`$w - 2)).Trim("``r``n")
    Write-Host `$text
    Write-Host ''
    `$log += "PS `$(Get-Location)> `$cmd``r``n`$text``r``n``r``n"
}
Write-Host "PS `$(Get-Location)> " -NoNewline
`$log | Out-File -Encoding utf8 '$texts\$name.txt'
"`$(`$raw.CursorPosition.Y + 1) `$(`$raw.WindowSize.Height) `$(`$raw.WindowTop)" | Out-File -Encoding ascii '$marker'
Start-Sleep -Seconds 600
"@ | Out-File -Encoding utf8 $runner

    $proc = Start-Process conhost.exe -ArgumentList "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$runner`"" -PassThru
    $deadline = (Get-Date).AddMinutes(8)
    while (-not (Test-Path $marker) -and (Get-Date) -lt $deadline) { Start-Sleep -Milliseconds 500 }
    $child = Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like "*evid-$name.ps1*" } | Select-Object -First 1
    $hwnd = (Get-Process -Id $child.ProcessId).MainWindowHandle
    $used, $rows, $top = (Get-Content $marker -Raw).Trim() -split ' ' | ForEach-Object { [int]$_ }
    [Shot]::Front($hwnd); Start-Sleep -Milliseconds 800
    [Shot]::Save($hwnd, (Join-Path $prints "$name.png"), $rows, [Math]::Min($rows, $used - $top))
    [Shot]::Release($hwnd)
    Stop-Process -Id $proc.Id -Force
    Get-CimInstance Win32_Process -Filter "Name='powershell.exe'" | Where-Object { $_.CommandLine -like "*evid-$name.ps1*" } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
    Remove-Item $runner, $marker -ErrorAction SilentlyContinue
    Write-Host "capturado: $name.png"
}

# Print da página pública do GitHub Actions (último run), capturado com o Edge em modo headless.
if (-not $Only -or '11-github-actions-web' -in $Only) {
    $run = (Invoke-RestMethod "https://api.github.com/repos/$repo/actions/runs?per_page=1").workflow_runs[0]
    $edge = "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"
    $png = Join-Path $prints '11-github-actions-web.png'
    Start-Process -FilePath $edge -Wait -NoNewWindow -ArgumentList '--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run',
        "--user-data-dir=$env:TEMP\edge-evid", '--window-size=1400,1000', "--screenshot=$png", $run.html_url
    Write-Host "capturado: 11-github-actions-web.png ($($run.html_url))"
}
