# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""Application launcher
~~~~~~~~~~~~~~~~~~~~~~~
"""

import wasp
import icons

class LauncherApp():
    """An application launcher application.

    .. figure:: res/LauncherApp.png
        :width: 179

        Screenshot of the application launcher
    """
    NAME = 'Launcher'
    ICON = icons.app

    def __init__(self):
        self._scroll = wasp.widgets.ScrollIndicator(y=6)

    def foreground(self):
        """Activate the application."""
        self._page = 0
        self._draw()
        wasp.system.request_event(wasp.EventMask.TOUCH |
                                  wasp.EventMask.SWIPE_UPDOWN)

    def swipe(self, event):
        i = self._page
        n = self._num_pages
        if event[0] == wasp.EventType.UP:
            i += 1
            if i >= n:
                i -= 1
                wasp.watch.vibrator.pulse()
                return
        else:
            i -= 1
            if i < 0:
                wasp.system.switch(wasp.system.quick_ring[0])
                return

        self._page = i
        wasp.watch.display.mute(True)
        self._draw()
        wasp.watch.display.mute(False)

    def touch(self, event):
        page = self._get_page(self._page)
        x = event[1]
        y = event[2]
        app = page[2 * (y // 120) + (x // 120)]
        if app:
            wasp.system.switch(app)
        else:
            wasp.watch.vibrator.pulse()

    @property
    def _num_pages(self):
        """Work out what the highest possible pages it."""
        num_apps = len(wasp.system.launcher_ring)
        return (num_apps + 3) // 4

    def _get_page(self, i):
        apps = wasp.system.launcher_ring
        page = apps[4*i: 4*(i+1)]
        while len(page) < 4:
            page.append(None)
        return page

    def _draw(self):
        """Redraw the display from scratch."""
        def string_wrapped(long_string, width):
            """String sliced within specified width"""
            chunks = draw.wrap(long_string, width)
            lines = len(chunks)-1
            s_wrapped = [x for x in range(lines)]
            for i in range(lines):
                s_wrapped[i] = long_string[chunks[i]:chunks[i+1]]
            return s_wrapped

        def draw_app(app, x, y):
            if not app:
                return
            draw.set_color(0xffff)
            draw.blit(app.ICON if 'ICON' in dir(app) else icons.app, x+13, y+12)
            draw.set_color(0xbdb6)
            name_wrapped = string_wrapped(app.NAME, 120)
            draw.string(name_wrapped[0], x, y + 120 - 30, 120)

        draw = wasp.watch.drawable
        page_num = self._page
        page = self._get_page(page_num)
        
        draw.fill()
        draw_app(page[0],   0,   0)
        draw_app(page[1], 120,   0)
        draw_app(page[2],   0, 120)
        draw_app(page[3], 120, 120)

        scroll = self._scroll
        scroll.up = page_num > 0
        scroll.down = page_num < (self._num_pages-1)
        scroll.draw()
