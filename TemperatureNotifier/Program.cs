using System;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Toolkit.Uwp.Notifications; // NuGet package
using Newtonsoft.Json; // NuGet package

class Program
{
    static async Task Main(string[] args)
    {
        // Show toast notification
        ShowToastNotification();

        // Simulate a delay to wait for user input
        await Task.Delay(TimeSpan.FromSeconds(30)); // Adjust the time as needed
    }

    static void ShowToastNotification()
    {
        // Construct the content and show the toast
        new ToastContentBuilder()
            .AddArgument("action", "temperatureSurvey")
            .AddArgument("conversationId", 384928) // Example conversation ID
            .AddText("1129 (S) Temperature Survey")
            .AddText("Is the temperature warm, cold, or OK?")
            .AddButton(new ToastButton()
                .SetContent("Warm")
                .AddArgument("action", "warm")
                .SetBackgroundActivation())
            .AddButton(new ToastButton()
                .SetContent("Cold")
                .AddArgument("action", "cold")
                .SetBackgroundActivation())
            .AddButton(new ToastButton()
                .SetContent("OK")
                .AddArgument("action", "ok")
                .SetBackgroundActivation())
            .Show();
    }

    static async void HandleResponse(string argument)
    {
        // Determine the response based on the button clicked
        string response = argument switch
        {
            "action=warm" => "Warm",
            "action=cold" => "Cold",
            "action=ok" => "OK",
            _ => "Unknown"
        };

        Console.WriteLine($"User responded: {response}");

        // Send the response to the central server (placeholder URL)
        await SendResponseToServer(response);
    }

    static async Task SendResponseToServer(string response)
    {
        using (var httpClient = new HttpClient())
        {
            // This URL should point to your server endpoint
            string url = "http://localhost:5256/api/responses"; 

            var content = new StringContent(JsonConvert.SerializeObject(new { response }), Encoding.UTF8, "application/json");

            var result = await httpClient.PostAsync(url, content);
            if (result.IsSuccessStatusCode)
            {
                Console.WriteLine("Response sent successfully.");
            }
            else
            {
                Console.WriteLine("Failed to send response.");
            }
        }
    }
}
