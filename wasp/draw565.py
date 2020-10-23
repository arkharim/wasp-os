# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2020 Daniel Thompson

"""RGB565 drawing library
~~~~~~~~~~~~~~~~~~~~~~~~~
"""

import array
import fonts.sans24
import math
import micropython

from micropython import const

R = const(0b11111_000000_00000)
G = const(0b00000_111111_00000)
B = const(0b00000_000000_11111)

@micropython.viper
def _bitblit(bitbuf, pixels, bgfg: int, count: int):
    mv = ptr16(bitbuf) #Points to a 16 bit half-word.
    px = ptr8(pixels) #Points to a byte

    # Extract and byte-swap
    bg = ((bgfg >> 24) & 0xff) + ((bgfg >> 8) & 0xff00)
    fg = ((bgfg >>  8) & 0xff) + ((bgfg & 0xff) << 8)

    bitselect = 0x80
    pxp = 0
    mvp = 0

    for bit in range(count):
        # Draw the pixel
        active = px[pxp] & bitselect
        mv[mvp] = fg if active else bg
        mvp += 1

        # Advance to the next bit
        bitselect >>= 1
        if not bitselect:
            bitselect = 0x80
            pxp += 1

@micropython.viper
def _clut8_rgb565(i: int) -> int:
    if i < 216:
        rgb565  = (( i  % 6) * 0x33) >> 3
        rg = i // 6
        rgb565 += ((rg  % 6) * (0x33 << 3)) & 0x07e0
        rgb565 += ((rg // 6) * (0x33 << 8)) & 0xf800
    elif i < 252:
        i -= 216
        rgb565  = (0x7f + (( i  % 3) * 0x33)) >> 3
        rg = i // 3
        rgb565 += ((0x4c << 3) + ((rg  % 4) * (0x33 << 3))) & 0x07e0
        rgb565 += ((0x7f << 8) + ((rg // 4) * (0x33 << 8))) & 0xf800
    else:
        i -= 252
        gr6 = (0x2c + (0x10 * i)) >> 2
        gr5 = gr6 >> 1
        rgb565 = (gr5 << 11) + (gr6 << 5) + gr5

    return rgb565

@micropython.viper
def _fill(mv, color: int, count: int, offset: int):
#llena el buffer que despues escribira en pantalla con el color que quiere. dentro del rango seleccionado.
    p = ptr16(mv) #Points to a 16 bit half-word.
    color = (color >> 8) + ((color & 0xff) << 8)

    for x in range(offset, offset+count):
        p[x] = color

def _bounding_box(s, font):
    if not s:
        return (0, font.height())

    get_ch = font.get_ch
    w = len(s) - 1
    for ch in s:
        (_, h, wc) = get_ch(ch)
        w += wc

    return (w, h)

@micropython.native
def _draw_glyph(display, glyph, x, y, bgfg):
    (px, h, w) = glyph #el glyph es una tira de bytes + altura+ancho

    buf = display.linebuffer[0:2*(w+1)]
    buf[2*w] = bgfg >> 24
    buf[2*w + 1] = (bgfg >> 16) & 0xff
    bytes_per_row = (w + 7) // 8

    display.set_window(x, y, w+1, h)
    quick_write = display.quick_write

    display.quick_start()
    for row in range(h):
        _bitblit(buf, px[row*bytes_per_row:], bgfg, w)
        quick_write(buf)
    display.quick_end()

class Draw565(object):
    """Drawing library for RGB565 displays.

    A full framebufer is not required although the library will
    'borrow' a line buffer from the underlying display driver.

    .. automethod:: __init__
    """

    def __init__(self, display):
        """Initialise the library.

        Defaults to white-on-black for monochrome drawing operations
        and 24pt Sans Serif text.
        """
        self._display = display
        self.reset()

    def reset(self):
        """Restore the default colours and font.

        Default colours are white-on-block (white foreground, black
        background) and the default font is 24pt Sans Serif."""
        self.set_color(0xffff)
        self.set_font(fonts.sans24)

    def fill(self, bg=None, x=0, y=0, w=None, h=None):
        """Draw a solid colour rectangle.

        If no arguments a provided the whole display will be filled with
        the background colour (typically black).

        :param bg: Background colour (in RGB565 format)
        :param x:  X coordinate of the left-most pixels of the rectangle
        :param y:  Y coordinate of the top-most pixels of the rectangle
        :param w:  Width of the rectangle, defaults to None (which means select
                   the right-most pixel of the display)
        :param h:  Height of the rectangle, defaults to None (which means select
                   the bottom-most pixel of the display)
        """
        display = self._display
        quick_write = display.quick_write

        if bg is None:
            bg = self._bgfg >> 16
        if w is None:
            w = display.width - x
        if h is None:
            h = display.height - y

        display.set_window(x, y, w, h)

        remaining = w * h #pixeles que hay en el cuadrado. y los que quedan por rellenar. no es toda la pantalla

        # Populate the line buffer
        buf = display.linebuffer
        sz = len(buf) // 2 # tamaño de los pixles. el buff es x2.
        _fill(buf, bg, min(sz, remaining), 0) #aqui prepara el buff con el color (bg) pixel a pixel hasta que se acabe el area arellenar..

        display.quick_start() #"enciende la pantalla" para el llenar el nuevo color.
        while remaining >= sz: #pinta linea a linea.
            quick_write(buf)
            remaining -= sz
        if remaining:#no se que hace.
            quick_write(buf[0:2*remaining])
        display.quick_end()

    @micropython.native
    def blit(self, image, x, y, fg=0xffff, c1=0x4a69, c2=0x7bef):
        """Decode and draw an encoded image.

        :param image: Image data in either 1-bit RLE or 2-bit RLE formats. The
                      format will be autodetected
        :param x: X coordinate for the left-most pixels in the image
        :param y: Y coordinate for the top-most pixels in the image
        """
        if len(image) == 3:
            # Legacy 1-bit image
            self.rleblit(image, (x, y), fg)
        else: #elif image[0] == 2:
            # 2-bit RLE image, (255x255, v1)
            self._rle2bit(image, x, y, fg, c1, c2)

    @micropython.native
    def rleblit(self, image, pos=(0, 0), fg=0xffff, bg=0):
        """Decode and draw a 1-bit RLE image.

        .. deprecated:: M2
            Use :py:meth:`~.blit` instead.
        """
        display = self._display
        write_data = display.write_data
        (sx, sy, rle) = image

        display.set_window(pos[0], pos[1], sx, sy)

        buf = display.linebuffer[0:2*sx]
        bp = 0
        color = bg

        for rl in rle:
            while rl:
                count = min(sx - bp, rl)
                _fill(buf, color, count, bp)
                bp += count
                rl -= count

                if bp >= sx:
                    write_data(buf)
                    bp = 0

            if color == bg:
                color = fg
            else:
                color = bg

    @micropython.native
    def _rle2bit(self, image, x, y, fg, c1, c2):
        """Decode and draw a 2-bit RLE image."""
        display = self._display
        quick_write = display.quick_write
        sx = image[1] #ancho imagen
        sy = image[2] #alto imagen
        rle = memoryview(image)[3:] #informacion codificada de la imagen

        display.set_window(x, y, sx, sy) #prepara el area de pintar.

        if sx <= (len(display.linebuffer) // 4) and not bool(sy & 1):
            sx *= 2
            sy //= 2

        palette = array.array('H', (0, c1, c2, fg)) #Array de unsigned shrot (int) Con los 4 valores que le pasa. No se que es c1 y c2.
        next_color = 1
        rl = 0
        buf = display.linebuffer[0:2*sx] #prepara la lnea del buffer a llenar.
        bp = 0

        display.quick_start()
        for op in rle:
            #aqui creo que calcula la longutid de losa bits con el mismo color.
            if rl == 0:
                px = op >> 6
                rl = op & 0x3f
                if 0 == rl:
                    rl = -1
                    continue
                if rl >= 63:
                    continue
            elif rl > 0:
                rl += op
                if op >= 255:
                    continue
            else:
                palette[next_color] = _clut8_rgb565(op)
                if next_color < 3:
                    next_color += 1
                else:
                    next_color = 1
                rl = 0
                continue

            while rl:
                count = min(sx - bp, rl)
                _fill(buf, palette[px], count, bp) #preapra el buffer con los colores. el bp es el offset.
                bp += count
                rl -= count

                if bp >= sx: #compreba que no se salte de ancho y si no lo pinta.
                    quick_write(buf)
                    bp = 0
        display.quick_end()

    def set_color(self, color, bg=0):
        """Set the foreground and background colours.

        The supplied colour will be used for all monochrome drawing operations.
        If no background colour is provided then the background will be set
        to black.

        :param color: Foreground colour
        :param bg:    Background colour, defaults to black
        """
        self._bgfg = (bg << 16) + color

    def set_font(self, font):
        """Set the font used for rendering text.

        :param font:  A font module generated using ``font_to_py.py``.
        """
        self._font = font

    def string(self, s, x, y, width=None, right=False):
        """Draw a string at the supplied position.

        :param s:     String to render
        :param x:     X coordinate for the left-most pixels in the image
        :param y:     Y coordinate for the top-most pixels in the image
        :param width: If no width is provided then the text will be left
                      justified, otherwise the text will be centred within the
                      provided width and, importantly, the remaining width will
                      be filled with the background colour (to ensure that if
                      we update one string with a narrower one there is no
                      need to "undraw" it)
        :param right: If True (and width is set) then right justify rather than
                      centre the text
        """
        display = self._display
        bgfg = self._bgfg
        font = self._font
        bg = self._bgfg >> 16

        if width:
            (w, h) = _bounding_box(s, font)
            if right:
                leftpad = width - w
                rightpad = 0
            else:
                leftpad = (width - w) // 2
                rightpad = width - w - leftpad
            leftpad = (width - w) // 2
            rightpad = width - w - leftpad
            #TODO aqui es donde pinta toda la linea de negro antes del string.
            self.fill(bg, x, y, leftpad, h)
            x += leftpad

        for ch in s:
            glyph = font.get_ch(ch)
            _draw_glyph(display, glyph, x, y, bgfg)
            #TODO aqui es donde creo que rellena el fondo del texto.
            self.fill(bg, x+glyph[2], y, 1, glyph[1]) #glyph[2] = ancho, glyph[1] = altura
            x += glyph[2] + 1

        if width:
            #TODO aqui es donde pinta toda la linea de negro despues del string.
            self.fill(bg, x, y, rightpad, h)

    def bounding_box(self, s):
        """Return the bounding box of a string.

        :param s: A string
        :returns: Tuple of (width, height)
        """
        return _bounding_box(s, self._font)

    def wrap(self, s, width):
        """Chunk a string so it can rendered within a specified width.

        Example:

        .. code-block:: python

            draw = wasp.watch.drawable
            chunks = draw.wrap(long_string, 240)

            # line(1) will provide the first line
            # line(len(chunks)-1) will provide the last line
            def line(n):
                return long_string[chunks[n-1]:chunks[n]]

        :param s:     String to be chunked
        :param width: Width to wrap the text into
        :returns:     List of chunk boundaries
        """
        font = self._font
        max = len(s)
        chunks = [ 0, ]
        end = 0

        while end < max:
            start = end
            l = 0

            for i in range(start, max+1):
                if i >= len(s):
                    break
                ch = s[i]
                (_, h, w) = font.get_ch(ch)
                l += w + 1
                if l > width:
                    break

                # Break the line immediately if requested
                if ch == '\n':
                    end = i+1
                    break

                # Remember the right-most place we can cleanly break the line
                if ch == ' ':
                    end = i+1
            if end <= start:
                end = i
            chunks.append(end)

        return chunks

    def line(self, x0, y0, x1, y1, width=1, color=None):
        """Draw a line between points (x0, y0) and (x1, y1).

        Example:

        .. code-block:: python

            draw = wasp.watch.drawable
            draw.line(0, 120, 240, 240, 0xf800)

        :param x0: X coordinate of the start of the line
        :param y0: Y coordinate of the start of the line
        :param x1: X coordinate of the end of the line
        :param y1: Y coordinate of the end of the line
        :param width: Width of the line in pixels
        :param color: Colour to draw line, defaults to the foreground colour
        """
        if color is None:
            color = self._bgfg & 0xffff
        px = bytes(((color >> 8) & 0xFF, color & 0xFF)) * (width * width)
        write_data = self._display.write_data
        set_window = self._display.set_window

        dw = (width - 1) // 2
        x0 -= dw
        y0 -= dw
        x1 -= dw
        y1 -= dw

        dx =  abs(x1 - x0)
        sx = 1 if x0 < x1 else -1
        dy = -abs(y1 - y0)
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        if dx == 0 or dy == 0:
            if x1 < x0 or y1 < y0:
                x0, x1 = x1, x0
                y0, y1 = y1, y0
            w = width if dx == 0 else (dx + width)
            h = width if dy == 0 else (-dy + width)
            self.fill(color, x0, y0, w, h)
            return
        while True:
            set_window(x0, y0, width, width)
            write_data(px)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx;
                y0 += sy;
        
    def polar(self, x, y, theta, r0, r1, width=1, color=None):
        """Draw a line using polar coordinates.

        The coordinate system is tuned for clock applications so it
        adopts navigational conventions rather than mathematical ones.
        Specifically the reference direction is drawn vertically
        upwards and the angle is measures clockwise in degrees.

        Example:

        .. code-block:: python

            draw = wasp.watch.drawable
            draw.line(360 / 12, 16, 64)

        :param theta: Angle, in degrees
        :param r0: Radius of the start of the line
        :param y0: Radius of the end of the line
        :param x: X coordinate of the origin
        :param y: Y coordinate of the origin
        :param width: Width of the line in pixels
        :param color: Colour to draw line in, defaults to the foreground colour
        """
        to_radians = math.pi / 180
        xdelta = math.sin(theta * to_radians)
        ydelta = math.cos(theta * to_radians)

        x0 = x + int(xdelta * r0)
        x1 = x + int(xdelta * r1)
        y0 = y - int(ydelta * r0)
        y1 = y - int(ydelta * r1)

        self.line(x0, y0, x1, y1, width, color)

    def lighten(self, color, step=1):
        """Get a lighter shade from the same palette.

        The approach is somewhat unsophisticated. It is essentially just a
        saturating add for each of the RGB fields.

        :param color: Shade to lighten
        :returns:     New colour
        """
        r = (color & R) + (step << 11)
        if r > R:
            r = R

        g = (color & G) + (step <<  6)
        if g > G:
            g = G

        b = (color & B) + step
        if b > B:
            b = B

        return (r | g | b)

    def darken(self, color, step=1):
        """Get a darker shade from the same palette.

        The approach is somewhat unsophisticated. It is essentially just a
        desaturating subtract for each of the RGB fields.

        :param color: Shade to darken
        :returns:     New colour
        """
        rm = color & R
        rs = step << 11
        r = rm - rs if rm > rs else 0

        gm = color & G
        gs = step << 6
        g = gm - gs if gm > gs else 0

        bm = color & B
        b = bm - step if bm > step else 0

        return (r | g | b)

    @micropython.native
    def get_blit_color(self, image, x, y, fg=0xffff, c1=0x4a69, c2=0x7bef):
        """Decode and return the pixel color.

        :param image: Image data in either 1-bit RLE or 2-bit RLE formats. The
                      format will be autodetected
        :param x: X coordinate for the pixel in the image
        :param y: Y coordinate for the pixel in the image
        """
        if len(image) == 3:
            # Legacy 1-bit image
            return self._get_rle1blit_color(image, x, y, fg)
        else:
            # 2-bit RLE image, (255x255, v1)
            return self._get_rle2bit_color(image, x, y, fg, c1, c2)

    @micropython.native
    def _get_rle1blit_color(self, image, x, y, fg=0xffff, bg=0):
        """Decode a 1-bit RLE image and return the pixel color.

        :param image: Image data in either 1-bit RLE formats
        :param x: X coordinate for the pixel in the image
        :param y: Y coordinate for the pixel in the image
        """
        #display = self._display
        #write_data = display.write_data
        (sx, sy, rle) = image

        #display.set_window(x, y, sx, sy)

        #buf = memoryview(display.linebuffer)[0:2*sx]
        bp = 0
        sy_count = 0
        color = bg

        for rl in rle:
            while rl:
                count = min(sx - bp, rl)
                #_fill(buf, color, count, bp)
                if bp <= x < (bp + count) and sy_count == y:
                    return color
                bp += count
                rl -= count

                if bp >= sx:
                    #write_data(buf)
                    sy_count += 1
                    bp = 0

            if color == bg:
                color = fg
            else:
                color = bg

    @micropython.native
    def _get_rle2bit_color(self, image, x, y, fg=0xffff, c1=0x4a69, c2=0x7bef):
        """Decode a 2-bit RLE image and return the pixel color.

        :param image: Image data in either 2-bit RLE formats
        :param x: X coordinate for the pixel in the image
        :param y: Y coordinate for the pixel in the image
        """
        display = self._display
        sx = image[1]
        sy = image[2]
        rle = memoryview(image)[3:]

        if sx <= (len(display.linebuffer) // 4) and not bool(sy & 1):
            sx *= 2
            sy //= 2
            y //= 2

        palette = array.array('H', (0, c1, c2, fg))
        next_color = 1
        rl = 0
        bp = 0
        sy_count = 0

        for op in rle:
            if rl == 0:
                px = op >> 6
                rl = op & 0x3f
                if 0 == rl:
                    rl = -1
                    continue
                if rl >= 63:
                    continue
            elif rl > 0:
                rl += op
                if op >= 255:
                    continue
            else:
                palette[next_color] = _clut8_rgb565(op)
                if next_color < 3:
                    next_color += 1
                else:
                    next_color = 1
                rl = 0
                continue

            while rl:
                count = min(sx - bp, rl)
                if bp <= x < (bp + count) and sy_count == y:
                    return palette[px]
                bp += count
                rl -= count

                if bp >= sx:
                    sy_count += 1
                    bp = 0

    @micropython.native
    def redraw_blit(self, image, pixels, fg=0xffff, c1=0x4a69, c2=0x7bef):
        """Decode and drawn the pixels.

        :param image: Image data in either 1-bit RLE or 2-bit RLE formats. The
                      format will be autodetected
        :param pixels: [(Y1,X1),(Y2,X2),...] list of coordinate for the pixel in the image
        """
        if len(image) == 3:
            # Legacy 1-bit image
            return self._redraw_rle1bit(image, pixels, fg)
        else:
            # 2-bit RLE image, (255x255, v1)
            return self._redraw_rle2bit(image, pixels, fg, c1, c2)

    @micropython.native
    def _redraw_rle1bit(self, image, pixels, fg=0xffff, bg=0):
        """Decode a 1-bit RLE image and drawn the pixels.

        :param image: Image data in either 2-bit RLE formats
        :param pixels: [(Y1,X1),(Y2,X2),...] list of coordinate for the pixel in the image
        """
        display = self._display
        quick_write = display.quick_write
        set_window = display.set_window
        (sx, sy, rle) = image

        pixels = sorted(pixels)
        i = 0
        x = pixels[i][1]
        y = pixels[i][0]

        buf = memoryview(display.linebuffer)[0:2]  # pixel a pixel. tamaño de 1 pixel.
        bp = 0
        sy_count = 0
        color = bg

        for rl in rle:
            while rl:
                count = min(sx - bp, rl)
                if bp <= x < (bp + count) and sy_count == y:
                    set_window(x, y, 1, 0)
                    _fill(buf, color, 1, 0)
                    quick_write(buf)
                    i += 1
                    while i < len(pixels):
                        x = pixels[i][1]
                        y = pixels[i][0]
                        if bp <= x < (bp + count) and sy_count == y:
                            set_window(x, y, 1, 1)
                            _fill(buf, color, 1, 0)
                            quick_write(buf)
                            i += 1
                        else:
                            break
                    if i >= len(pixels):
                        #TODO revisar como salir elegantemente de ambos for y while.
                        display.quick_end()
                        return

                bp += count
                rl -= count

                if bp >= sx:
                    sy_count += 1
                    bp = 0

            if color == bg:
                color = fg
            else:
                color = bg
        display.quick_end()

    @micropython.native
    def _redraw_rle2bit(self, image, pixels, fg=0xffff, c1=0x4a69, c2=0x7bef):
        """Decode a 2-bit RLE image and drawn the pixels.

        :param image: Image data in either 2-bit RLE formats
        :param pixels: [(Y1,X1),(Y2,X2),...] list of coordinate for the pixel in the image
        """
        display = self._display
        #rawblit = display.rawblit
        set_window = display.set_window
        quick_write = display.quick_write
        sx = image[1]
        sy = image[2]

        rle = memoryview(image)[3:]

        pixels = sorted(pixels)
        i = 0
        x = pixels[i][1]
        y = pixels[i][0]

        if sx <= (len(display.linebuffer) // 4) and not bool(sy & 1):
            sx *= 2
            sy //= 2
            y //= 2

        palette = array.array('H', (0, c1, c2, fg))
        next_color = 1
        rl = 0
        buf = memoryview(display.linebuffer)[0:2] # Drawn pixel by pixel
        bp = 0
        sy_count = 0

        display.quick_start()
        for op in rle:
            if rl == 0:
                px = op >> 6
                rl = op & 0x3f
                if 0 == rl:
                    rl = -1
                    continue
                if rl >= 63:
                    continue
            elif rl > 0:
                rl += op
                if op >= 255:
                    continue
            else:
                palette[next_color] = _clut8_rgb565(op)
                if next_color < 3:
                    next_color += 1
                else:
                    next_color = 1
                rl = 0
                continue

            while rl:
                count = min(sx - bp, rl)
                if bp <= x < (bp + count) and sy_count == y:
                    # self.fill(palette[px], x, y, 1, 1)
                    set_window(x, y, 1, 1)
                    _fill(buf, palette[px], 1, 0)
                    quick_write(buf)
                    i += 1
                    while i < len(pixels):
                        x = pixels[i][1]
                        y = pixels[i][0]
                        if sx <= (len(display.linebuffer) // 4) and not bool(sy & 1):
                            y //= 2
                        if bp <= x < (bp + count) and sy_count == y:
                            set_window(x, y, 1, 1)
                            _fill(buf, palette[px], 1, 0)
                            quick_write(buf)
                            i += 1
                        else:
                            break
                    if i >= len(pixels):
                        #TODO revisar como salir elegantemente de ambos for y while.
                        display.quick_end()
                        return

                bp += count
                rl -= count

                if bp >= sx:
                    sy_count += 1
                    bp = 0

        display.quick_end()


# @micropython.native
# def get_rle2bit_pixel_color(self, image, x, y, fg=0xffff, c1=0x4a69, c2=0x7bef):
#     """TODO Decode and draw a 2-bit RLE image."""
#     display = self._display
#     # quick_write = display.quick_write
#     sx = image[1]  # ancho imagen
#     sy = image[2]  # alto imagen
#     rle = memoryview(image)[3:]  # informacion codificada de la imagen
#     print("sx inicial: ", sx)
#     print("sy inical: ", sy)
#     # display.set_window(x, y, sx, sy) #prepara el area de pintar.
#
#     if sx <= (len(display.linebuffer) // 4) and not bool(sy & 1):
#         sx *= 2
#         sy //= 2
#         print("sx modificado: ", sx)
#         print("sy modificado: ", sy)
#         y //= 2  # TODO escalo la y deseada tmb
#
#     palette = array.array('H', (
#     0, c1, c2, fg))  # Array de unsigned shrot (int) Con los 4 valores que le pasa. No se que es c1 y c2.
#     next_color = 1
#     rl = 0
#     # buf = memoryview(display.linebuffer)[0:2*sx] #prepara la lnea del buffer a llenar.
#     bp = 0
#
#     y_count = 0  #
#
#     # display.quick_start()
#     for op in rle:
#         # print("empieza el for")
#         # aqui creo que calcula la longutid de losa bits con el mismo color.
#         if rl == 0:
#             px = op >> 6
#             rl = op & 0x3f
#             if 0 == rl:
#                 rl = -1
#                 continue
#             if rl >= 63:
#                 continue
#         elif rl > 0:
#             rl += op
#             if op >= 255:
#                 continue
#         else:
#             palette[next_color] = _clut8_rgb565(op)
#             if next_color < 3:
#                 next_color += 1
#             else:
#                 next_color = 1
#             rl = 0
#             continue
#         # print("rl is: ", rl)
#         # print("empieza el while")
#         while rl:
#             count = min(sx - bp, rl)
#             # print("sx is: ", sx) #es el ancho de la imgen o de la pantall? siempre fijo.
#             # print("bp is: ",bp)
#             # print("rl is: ",rl)
#             # print("count is: ", count)
#
#             # yo creo que no tengo que tener en cuenta la poxicion en el eje de las x.
#             # TODO solo consigo la primera fila. no se como leer el resto :(. me falta saber como calcular las filas.
#             # if (sx-bp) > rl:
#             if bp + rl >= sx:
#                 y_count += 1
#             if bp <= x and (bp + count) > x and y_count / 2 == y:  # TODO no tengo claro si deberia ser count o rl.
#                 # color = palette[px]
#                 # color = (color >> 8) + ((color & 0xff) << 8)
#                 print("y count: ", y_count)
#                 return palette[px]  #
#
#             # _fill(buf, palette[px], count, bp) #preapra el buffer con los colores. el bp es el offset.
#             bp += count
#             rl -= count
#             # print("nuevo rl es: ", rl)
#             # print ("nuevo bp es: ", bp)
#
#             if bp >= sx:  # compreba que no se salte de ancho y si no lo pinta. nunca entra cn la imagen del rainbow
#                 # return 0xffff #"aqui mi error"
#                 y_count += 1  #
#                 # print("ajajajaja")
#                 # print(y_count)
#                 # quick_write(buf)
#                 bp = 0
#
#             # y_count += 1  #
#         # print("acaba el while")
#         # TODO, lo sigo sin encontrar....
#         # y_count += 1  # aqui seguro que no va, no lo cuenta bien
#         # print('y count: ', y_count)
#
#     # display.quick_end()
#
#     # return 0x005F #sirve?
