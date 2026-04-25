using System.Diagnostics;
using System.Text;
using CommunityToolkit.Maui.Views;
using IronPython;
using IronPython.Runtime;
using Microsoft.Scripting.Hosting;
using Python.Runtime;

namespace AnimateMe;

public partial class HomePage : ContentPage
{
    public HomePage()
    {
        InitializeComponent();
    }

    async void OnUploadFile(object sender, EventArgs args)
    {

        var options = new MediaPickerOptions
        {
            Title = "Select video"
        };
        FileResult? fileResult = await MediaPicker.Default.PickVideoAsync(options);


        if (fileResult is not null)
        {
            var videoPath = fileResult.FullPath;

            videoPlayer.Source = videoPath;

            //Runtime.PythonDLL = @"C:\Users\dg_os\Documents\Programming\Projects\Animate.Me\app\AnimateMe\Python\DLL\python313.dll";

            string baseDir = AppContext.BaseDirectory;

            string pythonDllPath = Path.Combine(
                baseDir,
                "Python",
                "DLL",
                "python313.dll"
            );

            Debug.WriteLine("Python DLL Path: " + pythonDllPath);

            Runtime.PythonDLL = pythonDllPath;

            PythonEngine.Initialize();
            using (Py.GIL())
            {
                try
                {
                    dynamic sys = Py.Import("sys");

                    sys.path.append(@"C:\Users\quint\Documents\GitHub\Animate.Me\app\AnimateMe\Python\");
                    sys.path.append(@"C:\Users\quint\AppData\Local\Programs\Python\Python313\Lib\site-packages");

                    dynamic script = Py.Import("bvhjoint");
                    PyObject r = script.write_bvh_no_hierarchy(
                        "motion_data_3d.json"
                    );

                    string bvhText = r.ToString();

                // IMPORTANT: rewind stream
                writer.Flush();
                outputStream.Position = 0;

                string outputText = new StreamReader(outputStream).ReadToEnd();
                outputText = outputText.Replace("\0", "");

                Debug.WriteLine(outputText);
                #endregion
            }
            else
            {
                #region Python.NET method

                string baseDir = AppContext.BaseDirectory;

                string pythonDllPath = Path.Combine(
                    baseDir,
                    "engine",
                    "DLL",
                    "python313.dll"
                );

                Debug.WriteLine("Python DLL Path: " + pythonDllPath);

                Runtime.PythonDLL = pythonDllPath;

                PythonEngine.Initialize();
                using (Py.GIL())
                {
                    try
                    {
                        dynamic sys = Py.Import("sys");

                        sys.path.append(@"C:\Users\dg_os\Documents\Programming\Projects\Animate.Me\app\AnimateMe\engine");
                        sys.path.append(@"C:\Users\dg_os\Documents\Programming\Projects\Animate.Me\app\AnimateMe\engine\my_env\Lib\site-packages");

                        dynamic videoScript = Py.Import("coords_to_json");
                        videoScript.process_video();

                        dynamic script = Py.Import("bvhjoint");
                        PyObject r = script.write_bvh_no_hierarchy(
                            "motion_data_3d.json"
                        );

                        Debug.WriteLine(r.ToString());
                    }
                    catch (Python.Runtime.PythonException ex)
                    {
                        Debug.WriteLine("PYTHON ERROR:");
                        Debug.WriteLine(ex.Message);
                        Debug.WriteLine(ex.StackTrace);
                    }
                }
            }
        }
    }
}