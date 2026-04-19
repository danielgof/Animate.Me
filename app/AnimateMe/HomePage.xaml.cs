using System.Diagnostics;
using System.Text;
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
        var result = await FilePicker.PickAsync(new PickOptions
        {
            PickerTitle = "pickerImage",
            FileTypes = FilePickerFileType.Images
        });

        if (result is not null)
        {
            var stream = await result.OpenReadAsync();

            byte[] imageData;

            // use stream, communicate with python here
            using (MemoryStream memoryStream = new MemoryStream())
            {
                await stream.CopyToAsync(memoryStream);
                imageData = memoryStream.ToArray();
            }

            imageDisplay.Source = ImageSource.FromStream(() => new MemoryStream(imageData));

            string imageString = Convert.ToBase64String(imageData);

            if (false)
            {
                #region IronPython method
                var engine = IronPython.Hosting.Python.CreateEngine();

                var outputStream = new MemoryStream();
                var writer = new StreamWriter(outputStream, Encoding.UTF8)
                {
                    AutoFlush = true
                };

                engine.Runtime.IO.SetOutput(outputStream, writer);

                string pyScript = @"
    import math
    result = math.sqrt(25)
    print('The result: ' + str(result))
    ";

                var source = engine.CreateScriptSourceFromString(pyScript);
                source.Execute();

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

                        sys.path.append(@"C:\Users\dg_os\Documents\Programming\Projects\Animate.Me\app\AnimateMe\Python");
                        sys.path.append(@"C:\Users\dg_os\Documents\Programming\Projects\Animate.Me\app\AnimateMe\engine\my_env\Lib\site-packages");

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
                #endregion
            }
        }
    }
}