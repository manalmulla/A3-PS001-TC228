# AIORI-3-HACKATHON-PROJECTS

**##Team Introduction Video**\
Youtube: https://youtu.be/WaHb90-Qao0

# Android Ransomware Early Warning System

## Team Kenshin — A3-PS001-TC228

### 1. Project Overview

The Android Ransomware Early Warning System is a laboratory prototype designed to identify suspicious file activity that resembles ransomware behavior on an Android emulator.

The project monitors a designated test directory, observes file changes, analyzes suspicious activity within a time window, and attempts to stop a controlled test workload when suspicious behavior is detected.

The system uses Python, Android Debug Bridge (ADB), shell scripts, and rule-based detection.

The primary objective is to demonstrate how ransomware-like file operations can be monitored and detected before a simulated attack processes all test files.

### 2. Project Objectives

- Create a controlled Android ransomware simulation environment.
- Generate approximately 100 dummy files for testing.
- Simulate normal file operations and ransomware-like behavior.
- Monitor file creation, modification, renaming, and deletion.
- Identify suspicious activity using a sliding time window.
- Generate alerts when detection thresholds are reached.
- Attempt to terminate the controlled test workload.
- Evaluate detection performance using precision, recall, and detection delay.

### 3. System Architecture

The project consists of five main components.

**1. Android Test Environment**

An Android Virtual Device (AVD) is used as the testing environment.

The designated laboratory directory is:

`/sdcard/ranslab/`

It contains approximately 100 dummy files.

**2. Workload Simulation**

Five shell scripts simulate different file-operation patterns:

- Benign Backup
- Benign Editor
- Fast Attack
- Copy-and-Delete Attack
- Slow Attack

**3. File Monitoring**

A Python-based detector communicates with Android through ADB.

It periodically collects file information, including:

- Filename
- File size
- Modification timestamp

The detector compares consecutive snapshots to identify changes.

**4. Detection and Response**

The detector analyzes observed file activity using a sliding time window and configurable thresholds.

When suspicious activity is identified, it generates an alert and requests termination of the controlled test workload.

**5. Evaluation**

The evaluator is designed to run repeated workload experiments and record:

- Detection status
- Detection delay
- Files changed before detection
- Process termination status
- Precision
- Recall

### 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python 3 | Detection and evaluation |
| Android Studio | Android development environment |
| Android Virtual Device | Simulation environment |
| ADB | Communication with Android |
| Shell scripting | Workload simulation |
| PowerShell | Windows automation |
| CSV | Experiment result storage |
| Git and GitHub | Version control and collaboration |

### 5. Project Directory Structure

```text
A3-PS001-TC228-temp/
│
├── README.md
├── .gitignore
│
├── workloads/
│   ├── benign_backup.sh
│   ├── benign_editor.sh
│   ├── attack_fast.sh
│   ├── attack_copy_delete.sh
│   └── attack_slow.sh
│
├── detector/
│   └── detector.py
│
├── evaluator/
│   └── evaluator.py
│
├── data/
│   └── results.csv
│
├── test_files/
│
├── create_test_files.ps1
└── reset_lab.ps1
```

### 6. Workload Description

The system includes five simulated workloads.

#### 6.1 Benign Backup

Simulates normal backup activity by creating multiple files in the laboratory directory.

Expected behavior:
- Multiple file creation events.
- No mass file renaming.
- No ransomware alert under the intended detection configuration.

#### 6.2 Benign Editor

Simulates normal document editing by repeatedly modifying a single file.

Expected behavior:
- Repeated modifications.
- Limited file activity.
- No ransomware alert under the intended detection configuration.

#### 6.3 Fast Attack

Simulates rapid ransomware-like behavior by modifying dummy files and renaming them with a `.locked` extension.

Expected behavior:
- Multiple modification events.
- Multiple inferred rename events.
- Suspicious activity alert.

#### 6.4 Copy-and-Delete Attack

Simulates ransomware-like replacement behavior by creating replacement files with an `.encrypted` extension and deleting the original dummy files.

Expected behavior:
- Multiple file creation events.
- Multiple deletion events.
- Suspicious activity alert.

#### 6.5 Slow Attack

Simulates slower ransomware-like file modifications and renaming.

Expected behavior:
- Repeated file modifications.
- Inferred renames over a longer period.
- Evaluation of detection performance against slower activity.

**Note:** These are controlled laboratory simulations. They do not implement real encryption or target personal files.

### 7. Installation and Requirements

Before running the project, install:

- Windows 10 or Windows 11
- Python 3.x
- Android Studio
- Android SDK Platform Tools
- Android Emulator
- Git

Verify Python:

```powershell
python --version
```

Verify ADB:

```powershell
adb version
```

Check connected Android devices:

```powershell
adb devices
```

The project uses an Android emulator with a Google APIs system image for laboratory testing.

### 8. Laboratory Setup

Create the test directory:

```powershell
adb shell "mkdir -p /sdcard/ranslab"
```

Generate the dummy files using:

```powershell
.\create_test_files.ps1
```

Push the generated files:

```powershell
adb push .\test_files\ /sdcard/ranslab/
```

Verify the files:

```powershell
adb shell "ls -l /sdcard/ranslab"
```

The laboratory should contain approximately 100 dummy files before an experiment.

### 9. Upload Workloads to Android

Push the workload directory:

```powershell
adb push workloads /data/local/tmp/
```

Set executable permissions:

```powershell
adb shell "chmod +x /data/local/tmp/workloads/*.sh"
```

The workload scripts can be executed individually using:

```powershell
adb shell "sh /data/local/tmp/workloads/benign_backup.sh"
```

Other workload scripts can be launched by replacing the filename.

### 10. Running the Detector

From the project root directory, run:

```powershell
python .\detector\detector.py
```

The detector presents five workload options.

```text
1. benign_backup.sh
2. benign_editor.sh
3. attack_fast.sh
4. attack_copy_delete.sh
5. attack_slow.sh
```

Select the required workload and press Enter to begin monitoring.

The detector takes an initial snapshot and compares subsequent snapshots to identify file changes.

### 11. Detection Methodology

The prototype uses snapshot-based file monitoring.

The main monitoring operations are:

1. Collect the current file snapshot.
2. Compare it with the previous snapshot.
3. Identify newly created files.
4. Identify modified files.
5. Infer possible renames from disappeared and newly appearing filenames.
6. Identify deleted files.
7. Maintain recent events within a configurable sliding window.
8. Calculate suspicious activity statistics.
9. Generate an alert when configured detection conditions are met.

Initial experimental configuration:

| Parameter | Initial Value |
|---|---:|
| Polling interval | 200 ms |
| Sliding window | 3 seconds |
| Modified file threshold | More than 15 |
| Inferred rename threshold | More than 10 |

Thresholds may be adjusted during experiments to evaluate detection performance.

### 12. Response Mechanism

When suspicious activity is detected, the prototype:

- Generates a ransomware-like activity alert.
- Displays the number of modified files and inferred renames.
- Identifies the controlled workload PID.
- Requests termination of the test workload.

Process termination must be verified during testing rather than assumed from the termination request.

### 13. Evaluation Methodology

The evaluator is designed to test all five workloads repeatedly.

Initial proposed experiment plan:

| Workload | Planned Runs |
|---|---:|
| Benign Backup | 5 |
| Benign Editor | 5 |
| Fast Attack | 5 |
| Copy-and-Delete Attack | 5 |
| Slow Attack | 5 |
| **Total** | **25** |

The evaluator records experiment results in:

`data/results.csv`

The following metrics are used.

**Detection Delay**

Time between the beginning of a simulated attack and the generated alert.

**Files Changed Before Alert**

Number of files observed as changed before the detector generates an alert.

**Precision**

TP / (TP + FP)

Measures how many generated alerts correspond to actual attack workloads.

**Recall**

TP / (TP + FN)

Measures how many attack workloads are successfully detected.

**Termination Rate**

Percentage of controlled test workloads successfully terminated after detection.

Actual performance values will be reported after completing and validating the experiments.

### 14. Expected Results

The intended system behavior is:

| Workload | Expected Classification |
|---|---|
| Benign Backup | Benign |
| Benign Editor | Benign |
| Fast Attack | Suspicious |
| Copy-and-Delete Attack | Suspicious |
| Slow Attack | Suspicious |

These are expected outcomes, not measured results. Actual detection performance depends on emulator performance, polling behavior, workload execution, and detection thresholds.

### 15. Current Development Status

The project is being developed and tested in stages.

| Component | Status |
|---|---|
| Android emulator setup | Completed |
| ADB communication | Working |
| Dummy file generation | Working |
| Benign backup workload | Created and tested |
| Benign editor workload | Created and monitored |
| Fast attack workload | Created and independently tested |
| Copy-and-delete workload | Requires final script correction and testing |
| Slow attack workload | Requires validation |
| Python snapshot monitoring | Implemented |
| Sliding-window detection | Implemented; requires validation |
| Automatic process termination | Requires validation |
| Evaluation framework | Implemented; requires validation |
| Final performance measurements | Pending |

### 16. Limitations

- The prototype monitors a designated laboratory directory rather than the entire Android device.
- Snapshot polling can miss file operations occurring between observations.
- Rename events are inferred from file disappearance and appearance; they are not direct filesystem rename notifications.
- ADB polling introduces communication overhead and may affect detection timing.
- Detection thresholds require experimental tuning.
- The prototype does not provide complete device-wide ransomware protection.
- Process termination is designed for controlled laboratory workloads.

### 17. Future Improvements

Possible future enhancements include:

- Implementing Android FileObserver-based monitoring.
- Improving detection of rapid file operations.
- Adding entropy-based analysis as an additional detection signal.
- Improving detection of copy-and-delete behavior.
- Implementing more advanced risk scoring.
- Building a graphical monitoring dashboard.
- Expanding the evaluation dataset.
- Comparing different detection thresholds and configurations.

### 18. Safety and Ethical Considerations

All experiments are conducted in a controlled Android emulator environment.

The test scripts operate exclusively on dummy files inside:

`/sdcard/ranslab/`

The project does not target personal documents, real user data, or production Android devices.

The simulated workloads are intended only for academic research, security education, and controlled testing.


### Conclusion

The Android Ransomware Early Warning System demonstrates a laboratory-based approach to identifying suspicious file activity using snapshot monitoring and rule-based detection.

By combining controlled workload simulations, file activity analysis, sliding-window detection, and process response, the project provides a foundation for studying ransomware-like behavior on Android.

Further testing and improvements are required to validate detection accuracy, response speed, and reliability across different workload patterns.

### Images
<img width="865" height="935" alt="image" src="https://github.com/user-attachments/assets/3bb8d550-10ef-4c25-b71d-a75e0e097a4d" />
