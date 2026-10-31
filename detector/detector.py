
import subprocess
import time
import os
import sys
from collections import deque

# -------------------------------
# CONFIGURATION
# -------------------------------

LAB_DIR = "/sdcard/ranslab"
WORKLOAD_DIR = "/data/local/tmp/workloads"

WINDOW_SECONDS = 10
POLL_INTERVAL = 0.2

MODIFIED_THRESHOLD = 15
RENAME_THRESHOLD = 10

WORKLOADS = [
    "benign_backup.sh",
    "benign_editor.sh",
    "attack_fast.sh",
    "attack_copy_delete.sh",
    "attack_slow.sh"
]

# -------------------------------
# ADB COMMAND
# -------------------------------

def adb(command):
    result = subprocess.run(
        ["adb", "shell", command],
        capture_output=True,
        text=True,
        timeout=10
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout


# -------------------------------
# TAKE FILE SNAPSHOT
# -------------------------------

def take_snapshot():

    command = (
        'for f in /sdcard/ranslab/*; do '
        '[ -f "$f" ] || continue; '
        'stat -c "%n|%s|%Y" "$f" 2>/dev/null; '
        'done'
    )

    output = adb(command)

    snapshot = {}

    for line in output.splitlines():

        parts = line.strip().split("|")

        if len(parts) != 3:
            continue

        name, size, modified = parts

        try:
            snapshot[name] = (
                int(size),
                int(modified)
            )
        except ValueError:
            continue

    return snapshot


# -------------------------------
# DETECT FILE CHANGES
# -------------------------------

def detect_changes(previous, current):

    events = []

    old_files = set(previous)
    new_files = set(current)

    removed = old_files - new_files
    created = new_files - old_files

    # Detect modifications
    for name in old_files & new_files:

        if previous[name] != current[name]:

            events.append(("MODIFY", name))

    # Infer renames by matching filename prefixes
    for old_name in list(removed):

        matches = [
            new_name for new_name in created
            if new_name.startswith(old_name + ".")
        ]

        if matches:

            new_name = matches[0]

            events.append(
                ("RENAME", old_name + " -> " + new_name)
            )

            removed.remove(old_name)
            created.remove(new_name)

    for name in created:
        events.append(("CREATE", name))

    for name in removed:
        events.append(("DELETE", name))

    return events


# -------------------------------
# SLIDING WINDOW
# -------------------------------

def update_window(window, events):

    now = time.time()

    for event_type, filename in events:

        window.append(
            (now, event_type, filename)
        )

    while window and now - window[0][0] > WINDOW_SECONDS:

        window.popleft()


# -------------------------------
# DETECTION
# -------------------------------

def calculate_detection(window):

    modified = set()
    renames = set()

    for timestamp, event_type, filename in window:

        if event_type == "MODIFY":
            modified.add(filename)

        elif event_type == "RENAME":

            renames.add(filename)

            # A renamed original also counts as changed
            modified.add(filename.split(" -> ")[0])

    suspicious_extensions = [
        ".locked",
        ".encrypted"
    ]

    suspicious = any(
        name.endswith(tuple(suspicious_extensions))
        for _, _, name in window
    )

    detected = (
        len(modified) > MODIFIED_THRESHOLD
        and len(renames) > RENAME_THRESHOLD
    )

    return detected, len(modified), len(renames), suspicious


# -------------------------------
# ALERT
# -------------------------------

def raise_alert(modified, renames, pid):

    print("\n" + "=" * 45)

    print("RANSOMWARE-LIKE ACTIVITY DETECTED")

    print("=" * 45)

    print("Modified files:", modified)
    print("Inferred renames:", renames)

    print("Workload PID:", pid)

    print("Action: stopping controlled test workload")

    print("=" * 45)


# -------------------------------
# START TEST WORKLOAD
# -------------------------------

def start_workload(workload):

    if workload not in WORKLOADS:
        raise ValueError("Unknown workload")

    command = (
        f"sh {WORKLOAD_DIR}/{workload} "
        "> /dev/null 2>&1 < /dev/null & echo $!"
    )

    output = adb(command).strip()

    pid = int(output.splitlines()[-1])

    return pid


# -------------------------------
# STOP TEST WORKLOAD
# -------------------------------

def stop_workload(pid):

    adb(f"kill -TERM {pid}")

    print("Test workload termination requested.")


# -------------------------------
# MAIN DETECTOR
# -------------------------------

def main():

    print("ANDROID RANSOMWARE EARLY WARNING")

    print("---------------------------------")

    print("Choose workload:")

    for index, workload in enumerate(WORKLOADS, 1):

        print(index, workload)

    choice = input("Enter number: ").strip()

    try:
        workload = WORKLOADS[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    print("\nTaking initial snapshot...")

    previous = take_snapshot()

    print("Initial files:", len(previous))

    input("Press ENTER to start workload monitoring...")

    pid = start_workload(workload)

    print("Monitoring workload:", workload)
    print("Workload PID:", pid)

    window = deque()

    start_time = time.time()

    try:

        while time.time() - start_time < 60:

            current = take_snapshot()

            events = detect_changes(previous, current)

            if events:

                for event_type, filename in events:

                    print(event_type, filename)

                update_window(window, events)

            detected, modified, renames, suspicious = (
                calculate_detection(window)
            )

            if detected:

                raise_alert(modified, renames, pid)

                stop_workload(pid)

                return

            previous = current

            time.sleep(POLL_INTERVAL)

        print("Monitoring time limit reached.")

    except KeyboardInterrupt:

        print("Monitoring interrupted.")

        stop_workload(pid)


if __name__ == "__main__":
    main()
