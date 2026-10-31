
import csv
import sys
import time
import subprocess
from pathlib import Path
from collections import deque

# Import functions from detector.py
PROJECT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from detector import detector as det


# --------------------------------
# CONFIGURATION
# --------------------------------

RESET_SCRIPT = PROJECT_DIR / "reset_lab.ps1"

RESULTS_FILE = PROJECT_DIR / "data" / "results.csv"

RUNS_PER_WORKLOAD = 5

MAX_TEST_SECONDS = 65

POLL_INTERVAL = 0.2

WORKLOADS = {
    "benign_backup.sh": "benign",
    "benign_editor.sh": "benign",
    "attack_fast.sh": "attack",
    "attack_copy_delete.sh": "attack",
    "attack_slow.sh": "attack"
}


# --------------------------------
# RESET LAB
# --------------------------------

def reset_lab():

    print("\nResetting Android laboratory...")

    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(RESET_SCRIPT)
        ],
        check=True
    )

    print("Lab reset successful.")


# --------------------------------
# CHECK PROCESS
# --------------------------------

def process_alive(pid):

    result = subprocess.run(
        ["adb", "shell", "kill", "-0", str(pid)],
        capture_output=True,
        text=True
    )

    return result.returncode == 0


# --------------------------------
# RUN ONE EXPERIMENT
# --------------------------------

def run_experiment(workload, run_number):

    expected = WORKLOADS[workload]

    print("\n" + "=" * 45)
    print("WORKLOAD:", workload)
    print("RUN:", run_number)
    print("=" * 45)

    reset_lab()

    # Take initial snapshot
    previous = det.take_snapshot()

    print("Initial files:", len(previous))

    # Start workload
    start_time = time.perf_counter()

    pid = det.start_workload(workload)

    print("Workload PID:", pid)

    window = deque()

    detected = False
    detection_delay = ""
    files_changed = ""
    termination_confirmed = 0

    changed_names = set()

    deadline = time.monotonic() + MAX_TEST_SECONDS

    try:

        while time.monotonic() < deadline:

            current = det.take_snapshot()

            events = det.detect_changes(
                previous,
                current
            )

            for event_type, filename in events:

                print(event_type, filename)

                if event_type == "MODIFY":
                    changed_names.add(filename)

                elif event_type == "RENAME":
                    old_name = filename.split(" -> ")[0]
                    changed_names.add(old_name)

                elif event_type == "DELETE":
                    changed_names.add(filename)

            det.update_window(window, events)

            is_suspicious, modified, renames, suspicious_extension = (
                det.calculate_detection(window)
            )

            if is_suspicious:

                detected = True

                detection_delay = round(
                    (time.perf_counter() - start_time) * 1000,
                    2
                )

                files_changed = len(changed_names)

                print("\nALERT DETECTED!")
                print("Modified:", modified)
                print("Renames:", renames)
                print("Detection delay:", detection_delay, "ms")

                det.stop_workload(pid)

                # Allow the process to exit
                time.sleep(0.5)

                termination_confirmed = int(
                    not process_alive(pid)
                )

                break

            previous = current

            # Stop monitoring when the workload finishes
            if not process_alive(pid):
                break

            time.sleep(POLL_INTERVAL)

    finally:

        # Ensure the controlled test process is not left running
        if process_alive(pid):

            det.stop_workload(pid)

            time.sleep(0.5)

        if not termination_confirmed:
            termination_confirmed = int(
                not process_alive(pid)
            )

    print("\nExperiment completed.")

    print("Expected:", expected)
    print("Detected:", detected)
    print("Detection delay:", detection_delay)
    print("Files changed:", files_changed)
    print("Termination confirmed:", termination_confirmed)

    return {
        "workload": workload,
        "run": run_number,
        "expected": expected,
        "detected": int(detected),
        "detection_delay_ms": detection_delay,
        "files_changed_before_alert": files_changed,
        "termination_confirmed": termination_confirmed
    }


# --------------------------------
# SAVE RESULTS
# --------------------------------

def save_results(results):

    RESULTS_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fields = [
        "workload",
        "run",
        "expected",
        "detected",
        "detection_delay_ms",
        "files_changed_before_alert",
        "termination_confirmed"
    ]

    with open(
        RESULTS_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()
        writer.writerows(results)

    print("\nResults saved to:")
    print(RESULTS_FILE)


# --------------------------------
# CALCULATE METRICS
# --------------------------------

def calculate_metrics(results):

    tp = 0
    fp = 0
    fn = 0
    tn = 0

    for result in results:

        expected_attack = result["expected"] == "attack"
        actually_detected = result["detected"] == 1

        if expected_attack and actually_detected:
            tp += 1

        elif not expected_attack and actually_detected:
            fp += 1

        elif expected_attack and not actually_detected:
            fn += 1

        else:
            tn += 1

    precision = (
        tp / (tp + fp) * 100
        if tp + fp else 0
    )

    recall = (
        tp / (tp + fn) * 100
        if tp + fn else 0
    )

    print("\n" + "=" * 45)
    print("EVALUATION SUMMARY")
    print("=" * 45)

    print("True positives:", tp)
    print("False positives:", fp)
    print("True negatives:", tn)
    print("False negatives:", fn)

    print("Precision:", round(precision, 2), "%")
    print("Recall:", round(recall, 2), "%")

    delays = [
        float(r["detection_delay_ms"])
        for r in results
        if r["detection_delay_ms"] != ""
    ]

    if delays:
        print(
            "Average detection delay:",
            round(sum(delays) / len(delays), 2),
            "ms"
        )

    print("=" * 45)


# --------------------------------
# MAIN
# --------------------------------

def main():

    print("ANDROID RANSOMWARE EVALUATOR")
    print("=" * 45)

    # Verify ADB
    subprocess.run(
        ["adb", "get-state"],
        check=True,
        capture_output=True
    )

    # Verify detector can read the lab
    snapshot = det.take_snapshot()

    if not snapshot:
        raise RuntimeError(
            "No files found. Check the Android lab folder."
        )

    print("ADB connected.")
    print("Lab files found:", len(snapshot))

    results = []

    for workload in WORKLOADS:

        for run_number in range(
            1,
            RUNS_PER_WORKLOAD + 1
        ):

            result = run_experiment(
                workload,
                run_number
            )

            results.append(result)

            # Save after every run so partial results survive
            save_results(results)

    calculate_metrics(results)

    print("\nALL EXPERIMENTS COMPLETED.")


if __name__ == "__main__":
    main()
