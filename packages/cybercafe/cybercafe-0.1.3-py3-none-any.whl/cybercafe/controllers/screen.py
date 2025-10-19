
class ScreenController:
    """
    ScreenController
    Handles screen operations.
    """

    def __init__(self, space):
        self.space = space

    async def screenshot(self) -> str:
        """
        Take a screenshot of the current space.

        Returns:
            str: Base64 encoded screenshot.

        Example:
            image = await space.Screen.screenshot()
            print(image)  # "data:image/png;base64,..."
        """
        response = await self.space._request("GET", "/screenshot")
        return response.get("image")

    async def stream(self) -> str:
        """
        Generate a public interactive stream URL for the current space.

        This creates a temporary, publicly accessible URL that anyone can use to
        view or embed the live stream of this space. The URL can be safely shared
        or embedded on external websites (e.g., in an <iframe>).

        Returns:
            str: The public stream URL.

        Example:
            url = await space.Screen.stream()
            print(url)  # "https://cybercafe.space/stream?id=abc123"
        """
        response = await self.space._request("GET", "/stream_url")
        return response.get("stream_url")
