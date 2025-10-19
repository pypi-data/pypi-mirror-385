
class PowerShellController:
    """
    PowerShellController
    Handles sending PowerShell commands to a space/VM.
    """

    def __init__(self, space):
        self.space = space

    async def send_command(self, command: str) -> str:
        """
        Send a PowerShell command to the space/VM.

        Args:
            command (str): The PowerShell command to execute.

        Returns:
            str: Message from the command execution.

        Example:
            result = await space.PowerShell.send_command("Get-Process | Select-Object -First 5")
            print(result)
        """
        if not isinstance(command, str) or not command.strip():
            raise ValueError("Command must be a non-empty string")

        response = await self.space._request(
            "POST",
            "/powershell",
            {"command": command}
        )

        return response.get("message", "")
