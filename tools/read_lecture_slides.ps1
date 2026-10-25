$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$outDir = Join-Path $root 'tmp\lectures'
New-Item -ItemType Directory -Force $outDir | Out-Null
$pp = New-Object -ComObject PowerPoint.Application
$startedWithoutOpenDecks = ($pp.Presentations.Count -eq 0)
try {
    $result = @()
    foreach ($f in (Get-ChildItem -LiteralPath $root -Filter '*.ppt' | Sort-Object Name)) {
        $n = $f.Name.Substring(0,1)
        $dir = Join-Path $outDir $n
        New-Item -ItemType Directory -Force $dir | Out-Null
        $p = $pp.Presentations.Open($f.FullName,-1,0,0)
        try {
            $slides = @()
            foreach ($s in $p.Slides) {
                $txt = @()
                foreach ($sh in $s.Shapes) {
                    if ($sh.HasTextFrame -eq -1 -and $sh.TextFrame.HasText -eq -1) { $txt += $sh.TextFrame.TextRange.Text }
                    if ($sh.Type -eq 6) {
                        foreach ($g in $sh.GroupItems) {
                            if ($g.HasTextFrame -eq -1 -and $g.TextFrame.HasText -eq -1) { $txt += $g.TextFrame.TextRange.Text }
                        }
                    }
                }
                $slides += @{slide=$s.SlideIndex; text=($txt -join "`n")}
                $s.Export((Join-Path $dir ('slide-{0:D3}.png' -f $s.SlideIndex)),'PNG',1200,900)
            }
            $slides | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8 (Join-Path $dir 'slides.json')
            $result += @{file=$f.Name;slides=$p.Slides.Count}
        } finally { $p.Close() }
    }
    $result | ConvertTo-Json
} finally {
    if ($startedWithoutOpenDecks -and $pp.Presentations.Count -eq 0) { $pp.Quit() }
}
