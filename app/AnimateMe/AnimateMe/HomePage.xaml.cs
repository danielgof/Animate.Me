using System.Diagnostics;
using System.Text;
using IronPython;
using IronPython.Runtime;
using Microsoft.Scripting.Hosting;

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

            ScriptEngine engine = IronPython.Hosting.Python.CreateEngine();

            var debugStream = new DebugStream();

            engine.Runtime.IO.SetOutput(debugStream, Encoding.UTF8);

            string pyScript = "import math\nresult = math.sqrt(25)\nprint(\"The result: \" + str(result))";

            ScriptSource scriptSource = engine.CreateScriptSourceFromString(pyScript);

            var pyResult = scriptSource.Execute();

            // send to api call here

        }
    }
}

public class DebugStream : Stream
{
    private readonly MemoryStream _buffer = new MemoryStream();

    public override bool CanRead => false;
    public override bool CanSeek => false;
    public override bool CanWrite => true;
    public override long Length => 0;
    public override long Position { get => 0; set { } }

    public override void Flush()
    {
        if (_buffer.Length > 0)
        {
            string text = Encoding.UTF8.GetString(_buffer.ToArray());
            System.Diagnostics.Debug.Write(text);
            _buffer.SetLength(0);
        }
    }

    public override int Read(byte[] buffer, int offset, int count) => 0;
    public override long Seek(long offset, SeekOrigin origin) => 0;
    public override void SetLength(long value) { }

    public override void Write(byte[] buffer, int offset, int count)
    {
        // Append to buffer
        _buffer.Write(buffer, offset, count);
        string utf8String = Encoding.UTF8.GetString(buffer);

        // If newline detected, flush
        if (buffer[offset + count - 1] == (byte)'\n')
        {
            Flush();
        }
    }
}