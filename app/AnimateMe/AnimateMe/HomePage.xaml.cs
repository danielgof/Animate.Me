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

			imageDisplay.Source = ImageSource.FromStream(() => stream);

			// use stream, communicate with python here
			using (MemoryStream memoryStream = new MemoryStream())
			{
				stream.CopyTo(memoryStream);
				byte[] imageData = memoryStream.ToArray();
				string imageString = Convert.ToBase64String(imageData);

				// send to api call here
			}
		}
    }
}