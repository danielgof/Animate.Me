using System.Diagnostics;
using Python.Runtime;
using CommunityToolkit.Maui.Storage;

namespace AnimateMe;

public partial class HomePage : ContentPage
{

    string outputBvhPath;


    public HomePage()
    {
        InitializeComponent();
    }

    //private async void OnDownloadClicked(object sender, EventArgs e)
    //{
    //    try
    //    {
    //        if (!File.Exists(outputBvhPath))
    //            return;

    //        string fileName = Path.GetFileName(outputBvhPath);

    //        // Example: Downloads folder
    //        string downloadsPath = Path.Combine(
    //            Environment.GetFolderPath(Environment.SpecialFolder.UserProfile),
    //            "Downloads",
    //            fileName);

    //        File.Copy(outputBvhPath, downloadsPath, overwrite: true);

    //        await DisplayAlert("Saved", $"File saved to:\n{downloadsPath}", "OK");
    //    }
    //    catch (Exception ex)
    //    {
    //        await DisplayAlert("Error", ex.Message, "OK");
    //    }
    //}

    

    private async void OnDownloadClicked(object sender, EventArgs e)
    {
        try
        {
            if (!File.Exists(outputBvhPath))
                return;

            using var stream = File.OpenRead(outputBvhPath);

            var result = await FileSaver.Default.SaveAsync("animation_result.bvh", stream);

            if (result.IsSuccessful)
            {
                await DisplayAlert("Saved", $"File saved to:\n{result.FilePath}", "OK");
            }
            else
            {
                await DisplayAlert("Error", result.Exception?.Message ?? "Unknown error", "OK");
            }
        }
        catch (Exception ex)
        {
            await DisplayAlert("Error", ex.Message, "OK");
        }
    }

private async void OnUploadFile(object sender, EventArgs args)
    {
        var options = new MediaPickerOptions { Title = "Select video" };
        loadingSpinner.IsRunning = true;
        FileResult? fileResult = await MediaPicker.Default.PickVideoAsync(options);


        if (fileResult is null) return;

        // 1. Setup UI and Paths
        videoPlayer.Source = fileResult.FullPath;

        // string baseDir = AppContext.BaseDirectory;
        string engineRoot = Path.Combine(AppContext.BaseDirectory, "engine");
        string modelPath = Path.Combine(engineRoot, "pose_landmarker_heavy.task");
        string envRoot = Path.Combine(engineRoot, "python3.11");

        // Path to the Python DLL in your localized engine folder
        string pythonDllPath = Path.Combine(engineRoot, "python3.11", "python311.dll");
        string sitePackages = Path.Combine(envRoot, "Lib", "site-packages");

        Debug.WriteLine($"sitePackages Directory: {sitePackages}");

        try
        {
            // 2. Initialize Python Engine
            if (!PythonEngine.IsInitialized)
            {
                Runtime.PythonDLL = pythonDllPath;
                PythonEngine.Initialize();
            }

            using (Py.GIL())
            {
                dynamic sys = Py.Import("sys");
                // Add local engine and site-packages to sys.path dynamically
                sys.path.append(engineRoot);
                sys.path.append(sitePackages);

                // 3. Execute Python Scripts
                //dynamic script = Py.Import("pythonscript");
                //PyObject result = script.say_hello();
                //Debug.WriteLine($"Python Script Result: {result}");


                Debug.WriteLine("Processing video...");
                dynamic videoScript = Py.Import("coords_to_json");
                string videoPath = fileResult.FullPath;
                PyObject coordinatesFrames = videoScript.process_video(videoPath, modelPath);
                Debug.WriteLine($"Result: {coordinatesFrames}");

                dynamic jsonMod = Py.Import("json");
                string jsonString = jsonMod.dumps(coordinatesFrames).ToString();

                // 3. Define the output path
                string outputPath = Path.Combine(engineRoot, "motion_data_3d.json");

                // 4. Write to disk using standard C#
                File.WriteAllText(outputPath, jsonString);

                Debug.WriteLine($"Result saved successfully to: {outputPath}");

                //Debug.WriteLine("Generating BVH...");
                dynamic bvhScript = Py.Import("bvhjoint");
                PyObject result = bvhScript.write_bvh_no_hierarchy("motion_data_3d.json");

                Debug.WriteLine($"Result: {result}");

                string outputBvhPath = Path.Combine(engineRoot, "animation_result.bvh");

                try
                {
                    // 3. Write the file using C# I/O
                    File.WriteAllText(outputBvhPath, result.ToString());
                    loadingSpinner.IsRunning = false;
                    downloadButton.IsVisible = true;
                    this.outputBvhPath = Path.Combine(engineRoot, "animation_result.bvh");
                    Debug.WriteLine($"Successfully wrote BVH to: {outputBvhPath}");
                }
                catch (Exception ex)
                {
                    Debug.WriteLine($"C# File Error: {ex.Message}");
                }
            }
        }
        catch (PythonException ex)
        {
            Debug.WriteLine("PYTHON ERROR: " + ex.Message);
            Debug.WriteLine(ex.StackTrace);
            await DisplayAlert("Python Error", ex.Message, "OK");
        }
        catch (Exception ex)
        {
            Debug.WriteLine("GENERAL ERROR: " + ex.Message);
            await DisplayAlert("Error", ex.Message, "OK");
        }
    }
}