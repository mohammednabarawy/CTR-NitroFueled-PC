param(
    [Parameter(Mandatory = $true)]
    [string] $Command
)

# Use the workspace-local MSYS2 install without changing the machine's PATH.
$ErrorActionPreference = 'Stop'
$taskRepoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$taskMsysRoot = Join-Path $taskRepoRoot 'out\toolchains\msys64'
$taskBash = Join-Path $taskMsysRoot 'usr\bin\bash.exe'
if (-not (Test-Path -LiteralPath $taskBash)) {
    throw "Workspace-local MSYS2 not found: $taskMsysRoot"
}
$taskPreviousEnvironment = @{}
foreach ($taskName in @('MSYSTEM', 'CHERE_INVOKING', 'MSYS2_PATH_TYPE', 'MSYS2_ROOT')) {
    $taskPreviousEnvironment[$taskName] = [Environment]::GetEnvironmentVariable($taskName, 'Process')
}
try {
    $env:MSYSTEM = 'CLANG64'
    $env:CHERE_INVOKING = '1'
    $env:MSYS2_PATH_TYPE = 'minimal'
    $env:MSYS2_ROOT = '/' + $taskMsysRoot.Substring(0, 1).ToLowerInvariant() +
        '/' + $taskMsysRoot.Substring(3).Replace('\', '/')
    Push-Location -LiteralPath $taskRepoRoot
    try {
        & $taskBash -lc $Command
        $taskCommandExit = $LASTEXITCODE
    } finally {
        Pop-Location
    }
} finally {
    foreach ($taskName in $taskPreviousEnvironment.Keys) {
        [Environment]::SetEnvironmentVariable($taskName, $taskPreviousEnvironment[$taskName], 'Process')
    }
}
exit $taskCommandExit
