from typing import List, Optional, Tuple


class MouseController:
    """
    MouseController
    Provides methods for simulating mouse interactions in a Space.
    """

    def __init__(self, space) -> None:
        self.space = space

    async def move(self, point: Tuple[int, int]):
        """
        Move the mouse cursor to the given coordinates.

        Args:
            point (Tuple[int, int]): Target coordinates [x, y].

        Example:
            await space.Mouse.move((100, 200))
        """
        return await self.space._request("POST", "/mouse", {
            "action": "move",
            "point": point,
        })

    async def click(
        self,
        button: str = "left",
        point: Optional[Tuple[int, int]] = None,
        count: int = 1,
    ):
        """
        Click at the given coordinates, or at the current cursor position if `point` is omitted.

        Args:
            button (str): Mouse button to click. One of "left", "middle", "right". Defaults to "left".
            point (Tuple[int, int], optional): Coordinates [x, y]. Defaults to None (current cursor).
            count (int): Number of times to click (1–10). Defaults to 1.

        Example:
            await space.Mouse.click(point=(150, 200))
            await space.Mouse.click(button="right")
            await space.Mouse.click(point=(300, 400), count=2)
        """
        clicks = min(max(count, 1), 10)
        return await self.space._request("POST", "/mouse", {
            "action": "click",
            "point": point,
            "button": button,
            "count": clicks,
        })

    async def scroll(self, direction: str, point: Optional[Tuple[int, int]] = None):
        """
        Scroll in the specified direction.

        Args:
            direction (str): "up" or "down".
            point (Tuple[int, int], optional): Coordinates [x, y]. Defaults to current cursor.

        Example:
            await space.Mouse.scroll(direction="down")
            await space.Mouse.scroll(direction="up", point=(100, 200))
        """
        if direction not in ("up", "down"):
            raise ValueError("direction must be 'up' or 'down'")

        return await self.space._request("POST", "/mouse", {
            "action": "scroll",
            "direction": direction,
            "point": point,
        })

    async def drag(self, path: List[Tuple[int, int]]):
        """
        Drag the mouse along a series of points.

        Args:
            path (List[Tuple[int, int]]): List of [x, y] coordinate pairs.

        Example:
            await space.Mouse.drag([(10, 10), (50, 50), (200, 200)])
        """
        if not isinstance(path, list) or len(path) == 0:
            raise ValueError("'path' must be a non-empty list of (x, y) pairs")

        for point in path:
            if not isinstance(point, (list, tuple)) or len(point) != 2:
                raise ValueError("Each point in 'path' must be (x, y)")

        return await self.space._request("POST", "/mouse", {
            "action": "drag",
            "path": path,
        })

    async def position(self) -> Tuple[int, int]:
        """
        Get the current mouse position.

        Returns:
            Tuple[int, int]: Current mouse coordinates.

        Example:
            point = await space.Mouse.position()
            x, y = point
            print(f"Mouse is at {x}, {y}")
        """
        response = await self.space._request("GET", "/mouse")
        return response["point"]
