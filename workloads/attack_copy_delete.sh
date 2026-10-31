
$lines = @(
'#!/system/bin/sh'
'TARGET=/sdcard/ranslab'
'for file in "$TARGET"/file_*.txt'
'do'
'    [ -f "$file" ] || continue'
'    encrypted="$file.encrypted"'
'    echo "SIMULATED ENCRYPTED DATA" > "$encrypted"'
'    rm "$file"'
'    sleep 0.1'
'done'
'echo "Copy-delete simulation completed."'
)

$content = ($lines -join "`n") + "`n"

[System.IO.File]::WriteAllText(
    "$PWD\workloads\attack_copy_delete.sh",
    $content,
    [System.Text.UTF8Encoding]::new($false)
)
