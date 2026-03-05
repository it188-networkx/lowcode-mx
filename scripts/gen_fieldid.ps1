# Sonyflake ID 分解与生成工具
# 位布局: [39 bits time | 8 bits sequence | 16 bits machineID]
# ID = (time * 16777216) + (sequence * 65536) + machineID

param(
    [string]$Action = "analyze",    # analyze | generate
    [string]$ModuleFile = "",       # 模块 JSON 文件路径
    [int]$Count = 1                 # 生成几个新 ID
)

function Decompose-SonyflakeID([long]$id) {
    $machineID = $id % 65536
    $sequence = [math]::Floor($id / 65536) % 256
    $time = [math]::Floor($id / 16777216)
    return @{ Time = $time; Sequence = $sequence; MachineID = $machineID }
}

function Compose-SonyflakeID([long]$time, [int]$sequence, [int]$machineID) {
    return [long]($time * 16777216 + $sequence * 65536 + $machineID)
}

# 分析已有的 fieldID
Write-Host "=== Sonyflake ID 分析 ===" -ForegroundColor Cyan

$testIDs = @(
    484224679364722689,
    484224679364788225,
    484224679364853761,
    484224679364919297
)

Write-Host "`nceshiAI 已有 fieldID 分解:"
foreach ($id in $testIDs) {
    $parts = Decompose-SonyflakeID $id
    Write-Host ("  ID={0}  time={1}  seq={2}  machineID={3}" -f $id, $parts.Time, $parts.Sequence, $parts.MachineID)
}

# 生成新 ID：基于当前时间
$epoch = [datetime]::Parse("2017-01-01T00:00:00Z").ToUniversalTime()
$now = [datetime]::UtcNow
$elapsed10ms = [long](($now - $epoch).TotalMilliseconds / 10)
$machineID = 1   # 从已有 ID 中提取的 machineID

Write-Host ("`n当前时间: {0}" -f $now.ToString("yyyy-MM-dd HH:mm:ss.fff"))
Write-Host ("Epoch: {0}" -f $epoch.ToString("yyyy-MM-dd"))
Write-Host ("Elapsed 10ms units: {0}" -f $elapsed10ms)
Write-Host ("MachineID: {0}" -f $machineID)

Write-Host "`n=== 生成新 fieldID ===" -ForegroundColor Green
for ($seq = 0; $seq -lt 4; $seq++) {
    $newID = Compose-SonyflakeID $elapsed10ms $seq $machineID
    Write-Host ("  seq={0}  newFieldID={1}" -f $seq, $newID)
    # 验证：反向分解
    $check = Decompose-SonyflakeID $newID
    Write-Host ("    验证: time={0}  seq={1}  machineID={2}" -f $check.Time, $check.Sequence, $check.MachineID)
}
