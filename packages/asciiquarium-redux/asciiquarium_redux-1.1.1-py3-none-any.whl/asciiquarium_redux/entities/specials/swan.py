from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ...screen_compat import Screen

if TYPE_CHECKING:
    from ...protocols import ScreenProtocol, AsciiQuariumProtocol

from ...util import parse_sprite
from ..base import Actor


class Swan(Actor):
    def __init__(self, screen: "ScreenProtocol", app: "AsciiQuariumProtocol"):
        self.app = app
        self.dir = random.choice([-1, 1])
        self.speed = 10.0 * self.dir
        try:
            scene_w = int(getattr(getattr(app, "settings", None), "scene_width", screen.width))
        except Exception:
            scene_w = screen.width
        self.x = -10 if self.dir > 0 else scene_w
        self.y = 1
        swan_lr = [
            parse_sprite(
                r"""
       ___
,_    / _,\
| \???\(?\|
|  \_??\\
(_   \_) \
(\_   `   \
?\   -=~  /
"""
            ),
            parse_sprite(
                r"""
       ___
,_    / _,\
| \???\(?\|
|  \_??\\
(_   \_) \
(\_   `   \
?\   -=~  /
"""
            ),
        ]
        swan_rl = [
            parse_sprite(
                r"""
 ___
/,_ \    _,
|/?)/???/ |
??//??_/  |
?/ (?/   _)
/   `   _/)
\  ~=-   /
"""
            ),
            parse_sprite(
                r"""
 ___
/,_ \    _,
|/?)/???/ |
??//??_/  |
?/ (?/   _)
/   `   _/)
\   -=~  /
"""
            ),
        ]
        self.frames = swan_lr if self.dir > 0 else swan_rl
        # Build masks with full sprite height to preserve vertical alignment
        h = len(self.frames[0])
        ltr_mask = [''] * h
        rtl_mask = [''] * h
        # Match Perl: one blank line, then head 'g' and beak 'yy' alignment
        ltr_mask[1] = '         g'
        ltr_mask[2] = '         yy'
        rtl_mask[1] = ' g'
        rtl_mask[2] = 'yy'
        self.mask = ltr_mask if self.dir > 0 else rtl_mask
        self._frame_idx = 0
        self._frame_t = 0.0
        self._frame_dt = 0.25
        self._active = True

    @property
    def active(self) -> bool:
        return self._active

    def update(self, dt: float, screen: "ScreenProtocol", app: "AsciiQuariumProtocol") -> None:
        self.x += self.speed * dt
        self._frame_t += dt
        if self._frame_t >= self._frame_dt:
            self._frame_t = 0.0
            self._frame_idx = (self._frame_idx + 1) % len(self.frames)
        try:
            scene_w = int(getattr(getattr(app, "settings", None), "scene_width", screen.width))
        except Exception:
            scene_w = screen.width
        if (self.dir > 0 and self.x > scene_w) or (self.dir < 0 and self.x + 10 < 0):
            self._active = False

    def draw(self, screen: "ScreenProtocol", mono: bool = False) -> None:
        img = self.frames[self._frame_idx]
        self.draw_sprite(
            self.app,
            screen,
            img,
            self.mask,
            int(self.x),
            int(self.y),
            Screen.COLOUR_WHITE,
        )


def spawn_swan(screen: "ScreenProtocol", app: "AsciiQuariumProtocol"):
    return [Swan(screen, app)]
