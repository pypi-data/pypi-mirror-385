import io
from typing import Any, Dict, Optional


class FilesController:
    """
    FilesController
    Handles file uploads, downloads, and file system operations
    in the VM associated with a Space.
    """

    def __init__(self, space):
        """
        Initialize with a Space instance.

        Args:
            space (Space): The Space instance representing the remote VM.
        """
        self.space = space

    async def upload(
        self,
        file: bytes,
        filename: str,
        destination_path: Optional[str] = None
    ) -> Dict[str, str]:
        
        files = { "file": (filename, io.BytesIO(file), "application/octet-stream")}
        
        data = {}
        if destination_path:
            data["destinationPath"] = destination_path
            
            
        return await self.space._request("POST", "/files/upload", files=files, data=data)
    
    

    async def download(self, file_path: str) -> bytes:
        """
        Downloads a file from the remote space to a buffer.

        Args:
            file_path (str): The full path to the file on the remote machine.

        Returns:
            bytes: The file content as bytes.

        Example:
            >>> file_bytes = await space.Files.download("C:\\Users\\Brian\\Desktop\\photo.jpg")
            >>> with open("photo.jpg", "wb") as f:
            ...     f.write(file_bytes)

        Raises:
            SpaceError: When the file doesn't exist or download fails.
        """
        response = await self.space._request(
            "POST",
            "/files/download",
            {"filePath": file_path},
            response_type="arraybuffer"
        )
        return response

    async def _action(self, action: str, body: Dict[str, Any]) -> Any:
        """
        Internal helper to perform file actions.
        """
        return await self.space._request("POST", "/files", {**{"action": action}, **body})

    async def move(self, target_path: str, new_path: str) -> Dict[str, Any]:
        """
        Move a file or folder to a new location.

        Args:
            target_path (str): Full path of the file/folder to move.
            new_path (str): Destination path.

        Returns:
            Dict[str, Any]: { success: bool, message: str }

        Example:
            >>> await space.Files.move("C:\\Temp\\example.txt", "C:\\Users\\Brian\\Documents\\example.txt")
        """
        return await self._action("move", {"targetPath": target_path, "newPath": new_path})

    async def copy(self, target_path: str, new_path: str) -> Dict[str, Any]:
        """
        Copy a file or folder to a new location.

        Args:
            target_path (str): Full path of the file/folder to copy.
            new_path (str): Destination path.

        Returns:
            Dict[str, Any]: { success: bool, message: str }

        Example:
            >>> await space.Files.copy("C:\\Temp\\example.txt", "C:\\Users\\Brian\\Documents\\example.txt")
        """
        return await self._action("copy", {"targetPath": target_path, "newPath": new_path})

    async def rename(self, target_path: str, new_name: str) -> Dict[str, Any]:
        """
        Rename a file or folder.

        Args:
            target_path (str): Full path of the file/folder to rename.
            new_name (str): The new name (without path).

        Returns:
            Dict[str, Any]: { success: bool, message: str }

        Example:
            >>> await space.Files.rename("C:\\Temp\\oldname.txt", "newname.txt")
        """
        return await self._action("rename", {"targetPath": target_path, "newName": new_name})

    async def delete(self, target_path: str) -> Dict[str, Any]:
        """
        Delete a file or folder and its contents.

        Args:
            target_path (str): Full path of the file/folder to delete.

        Returns:
            Dict[str, Any]: { success: bool, message: str }

        Example:
            >>> await space.Files.delete("C:\\Temp\\unused_folder")
            >>> await space.Files.delete("C:\\Users\\Brian\\Documents\\example.txt")
        """
        return await self._action("delete", {"targetPath": target_path})

    async def mkdir(self, target_path: str) -> Dict[str, Any]:
        """
        Create a new directory.

        Args:
            target_path (str): Full path of the directory to create.

        Returns:
            Dict[str, Any]: { success: bool, message: str }

        Example:
            >>> await space.Files.mkdir("C:\\Users\\Brian\\Projects\\NewFolder")
        """
        return await self._action("mkdir", {"targetPath": target_path})

    async def list(self, target_path: str) -> Dict[str, Any]:
        """
        List files and folders in a directory.

        Args:
            target_path (str): Directory path to list.

        Returns:
            Dict[str, Any]: { success: bool, message: [ { Name, FullName, Mode, Length, LastWriteTime } ] }

        Example:
            >>> files = await space.Files.list("C:\\Users\\Brian\\Documents")
            >>> print(files)
        """
        return await self._action("list", {"targetPath": target_path})

    async def info(self, target_path: str) -> Dict[str, Any]:
        """
        Get detailed info about a file or folder.

        Args:
            target_path (str): Full path of the file/folder.

        Returns:
            Dict[str, Any]: { success: bool, message: { Name, FullName, Mode, Length, LastWriteTime, CreationTime, Attributes } }

        Example:
            >>> info = await space.Files.info("C:\\Users\\Brian\\Documents\\report.docx")
            >>> print(info)
        """
        return await self._action("info", {"targetPath": target_path})
