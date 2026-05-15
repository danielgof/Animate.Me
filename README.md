# Animate.Me

Animate.Me is a cross-platform .NET MAUI application that converts video motion into 3D animation data.

The app uses an embedded Python runtime and `pythonnet` to run local Python scripts for pose estimation and BVH export. This makes it possible to process video files and generate motion capture data directly within the application.

## Key features

- Video upload and processing inside the app
- 3D pose estimation from video frames
- Motion data export to `motion_data_3d.json`
- BVH animation file generation
- Cross-platform support for Windows, Android, iOS, and MacCatalyst

## Architecture

- `app/AnimateMe` contains the .NET MAUI app and UI code
- `app/AnimateMe/HomePage.xaml` and `HomePage.xaml.cs` handle the video picker, Python initialization, and script execution
- `app/AnimateMe/engine` hosts the embedded Python runtime, helper scripts, and model assets
- `engine/requirements.txt` lists Python dependencies used by the motion processing scripts

## How it works

1. The user selects a video file from the app
2. The app initializes the embedded Python interpreter using `pythonnet`
3. The Python script `coords_to_json.py` processes the video and extracts pose/keypoint data
4. The app saves JSON motion data and then generates BVH animation using `bvhjoint.py`
5. The resulting `.bvh` file can be used in animation tools

## Setup

### Prerequisites

- .NET 9 SDK
- Visual Studio 2022 or later with MAUI workload, or `dotnet` CLI for MAUI development
- Windows, Android, iOS, or Mac build support depending on your target platform

### Build and run

From the `app/AnimateMe` folder:

```bash
cd app/AnimateMe
dotnet build
dotnet run
```

Or open `app/AnimateMe/AnimateMe.sln` in Visual Studio and run the MAUI app.

### Python environment

The project includes an embedded Python runtime in `app/AnimateMe/engine/python3.11` and a supporting environment in `app/AnimateMe/engine/venv`.

If you need to recreate the Python environment, use the embedded interpreter and install the dependencies from `engine/requirements.txt`.

```bash
cd app/AnimateMe/engine
python3.11/python.exe -m venv venv
venv/Scripts/python.exe -m pip install --upgrade pip setuptools wheel
venv/Scripts/python.exe -m pip install -r requirements.txt
```

> Important: The embedded Python runtime and the installed packages must match the same architecture (64-bit or 32-bit) to avoid import errors for compiled extensions like NumPy.

## Notes

- The app currently relies on `pythonnet` to bridge .NET and Python
- Model assets such as `pose_landmarker_heavy.task` are located in `app/AnimateMe/engine`
- Output files are written into the `engine` folder by default

## License

MIT



