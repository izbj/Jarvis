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

& $Python -m pip install --upgrade pip
& $Python -m pip install cython pyinstaller
& $Python -m pip install .

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

& $Python @Args
