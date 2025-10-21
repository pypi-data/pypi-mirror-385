from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ...protocols import AsciiQuariumProtocol
    from ...screen_compat import Screen
else:
    from ...screen_compat import Screen

from ...util import parse_sprite, draw_sprite


@dataclass
class Splat:
    x: int
    y: int
    age_frames: int = 0
    max_frames: int = 15
    # Coordinate space for x,y: "scene" (pans with scene) or "screen" (fixed to current view)
    coord_space: str = "scene"

    FRAMES: List[List[str]] = field(
        default_factory=lambda: [
            parse_sprite(
                r"""

   .
  ***
   '

"""
            ),
            parse_sprite(
                r"""

 ",*;`
 "*,**
 *"'~'

"""
            ),
            parse_sprite(
                r"""
  , ,
 " ","'
 *" *'"
  " ; .

"""
            ),
            parse_sprite(
                r"""
* ' , ' `
' ` * . '
 ' `' ",'
* ' " * .
" * ', '
"""
            ),
        ]
    )

    def update(self, dt: float, screen: "Screen", app: "AsciiQuariumProtocol") -> None:
        self.age_frames += 1

    @property
    def active(self) -> bool:
        return self.age_frames < self.max_frames

    def draw(self, screen: Screen, mono: bool = False):
        idx = min(len(self.FRAMES) - 1, self.age_frames // 4)
        lines = self.FRAMES[idx]
        draw_sprite(screen, lines, self.x - 4, self.y - 2, Screen.COLOUR_WHITE if mono else Screen.COLOUR_RED)
