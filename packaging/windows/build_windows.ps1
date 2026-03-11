param(
    [ValidateSet("onedir", "onefile")]
    [string]$Mode = "onedir",
    [switch]$Clean,
    [switch]$Annotate
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$RepoRoot = Split-Path -Parent $Root

Set-Location $RepoRoot

$Python = if (Get-Command python -ErrorAction SilentlyContinue) {
    "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    "py"
} else {
    throw "Neither python nor py is available in PATH."
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Command
    )

    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $($Command -join ' ')"
    }
}

Invoke-Step -Command @($Python, "-m", "pip", "install", "--upgrade", "pip")
Invoke-Step -Command @($Python, "-m", "pip", "install", "cython", "pyinstaller")
Invoke-Step -Command @($Python, "-m", "pip", "install", ".")

$Args = @(
    (Join-Path $PSScriptRoot "build_windows.py"),
    "--mode", $Mode
)

if ($Clean) {
    $Args += "--clean"
}

if ($Annotate) {
    $Args += "--annotate"
}

Invoke-Step -Command (@($Python) + $Args)
