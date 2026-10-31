
#!/system/bin/sh

TARGET=/sdcard/ranslab

for file in "$TARGET"/file_*.txt
do
    [ -f "$file" ] || continue

    echo "SIMULATED ENCRYPTED CONTENT" > "$file"

    mv "$file" "$file.locked"

    sleep 0.1
done

echo "Fast attack simulation completed."
