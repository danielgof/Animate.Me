namespace AnimateMe;

public partial class NewPage1 : ContentPage
{
	public NewPage1()
	{
		InitializeComponent();
	}

	async void OnTakePicture(object sender, EventArgs args)
	{
        var cameraPermissionsRequest = await Permissions.RequestAsync<Permissions.Camera>();

    }
}