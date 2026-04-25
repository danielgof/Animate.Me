using System.Diagnostics;
using CommunityToolkit.Maui.Views;
using Python.Runtime;

namespace AnimateMe;

public partial class HomePage : ContentPage
{
    public HomePage()
    {
        InitializeComponent();
    }

    private async void OnUploadFile(object sender, EventArgs args)
    {
        var options = new MediaPickerOptions { Title = "Select video" };
        FileResult? fileResult = await MediaPicker.Default.PickVideoAsync(options);

        if (fileResult is null) return;

        // 1. Setup UI and Paths
        videoPlayer.Source = fileResult.FullPath;

        string baseDir = AppContext.BaseDirectory;
        string engineRoot = Path.Combine(baseDir, "engine");
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
                videoScript.process_video();

                Debug.WriteLine("Generating BVH...");
                dynamic bvhScript = Py.Import("bvhjoint");
                PyObject result = bvhScript.write_bvh_no_hierarchy("motion_data_3d.json");

                Debug.WriteLine($"Result: {result}");
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