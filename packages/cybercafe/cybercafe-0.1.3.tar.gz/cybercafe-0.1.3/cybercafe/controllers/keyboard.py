
class KeyboardController:
    """
    KeyboardController
    Handles keyboard input, key presses, and text typing.
    """

    def __init__(self, space):
        self.space = space

    async def type(self, text: str):
        """
        Type text into the current space.

        Args:
            text (str): Text to type.

        Returns:
            dict: API response.

        Example:
            await space.Keyboard.type("Hello, world!")
        """
        return await self.space._request("POST", "/keyboard", {"text": text})

    async def press(self, keys):
        """
        Press one or more keys.

        Args:
            keys (str | list[str]): Key or array of keys to press.

        Returns:
            dict: API response.

        Example:
            await space.Keyboard.press("Windows")
            await space.Keyboard.press(["Control", "C"])
        """
        key_array = keys if isinstance(keys, list) else [keys]
        return await self.space._request("POST", "/keyboard", {"keys": key_array})
