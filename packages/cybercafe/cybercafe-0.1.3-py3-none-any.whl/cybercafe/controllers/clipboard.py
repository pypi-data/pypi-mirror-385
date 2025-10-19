
class ClipboardController:
    """
    ClipboardController
    Handles clipboard operations: set and get text.
    """

    def __init__(self, space):
        self.space = space

    async def set_text(self, text: str):
        """
        Set text into the space clipboard.

        Args:
            text (str): The text to copy into the clipboard.

        Returns:
            dict: API response.

        Example:
            await space.Clipboard.set_text("Hello from Cybercafe!")
        """
        return await self.space._request("POST", "/clipboard", {"text": text})

    async def get_text(self) -> str:
        """
        Get text currently stored in the space clipboard.

        Returns:
            str: Clipboard text.

        Example:
            text = await space.Clipboard.get_text()
            print(text)  # e.g. "Hello from Cybercafe!"
        """
        response = await self.space._request("GET", "/clipboard")
        return response.get("text", "")
