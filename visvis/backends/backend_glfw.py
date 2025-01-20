# -*- coding: utf-8 -*-
# Copyright (C) 2012, Almar Klein
#
# Visvis is distributed under the terms of the (new) BSD License.
# The full license can be found in 'license.txt'.

"""The GLFW backend."""

import os
import sys
import time
import weakref
import asyncio

import visvis
from visvis import BaseFigure, events, constants

import glfw


# Make sure that glfw is new enough
glfw_version_info = tuple(int(i) for i in glfw.__version__.split(".")[:2])
if glfw_version_info < (1, 9):
    raise ImportError("visvis requires glfw 1.9 or higher.")

# Do checks to prevent pitfalls on hybrid Xorg/Wayland systems
is_wayland = False
if sys.platform.startswith("linux"):
    is_wayland = "wayland" in os.getenv("XDG_SESSION_TYPE", "").lower()
    if is_wayland and not hasattr(glfw, "get_wayland_window"):
        raise RuntimeError(
            "We're on Wayland but Wayland functions not available. "
            + "Did you apt install libglfw3-wayland?"
        )

# Some glfw functions are not always available
set_window_content_scale_callback = lambda *args: None  # noqa: E731
set_window_maximize_callback = lambda *args: None  # noqa: E731
get_window_content_scale = lambda *args: (1, 1)  # noqa: E731

if hasattr(glfw, "set_window_content_scale_callback"):
    set_window_content_scale_callback = glfw.set_window_content_scale_callback
if hasattr(glfw, "set_window_maximize_callback"):
    set_window_maximize_callback = glfw.set_window_maximize_callback
if hasattr(glfw, "get_window_content_scale"):
    get_window_content_scale = glfw.get_window_content_scale


KEY_MAP = {
    glfw.KEY_DOWN: constants.KEY_DOWN,
    glfw.KEY_UP: constants.KEY_UP,
    glfw.KEY_LEFT: constants.KEY_LEFT,
    glfw.KEY_RIGHT: constants.KEY_RIGHT,
    glfw.KEY_PAGE_UP: constants.KEY_PAGEUP,
    glfw.KEY_PAGE_DOWN: constants.KEY_PAGEDOWN,
    glfw.KEY_DELETE: constants.KEY_DELETE,
    glfw.KEY_LEFT_SHIFT: constants.KEY_SHIFT,
    glfw.KEY_RIGHT_SHIFT: constants.KEY_SHIFT,
    glfw.KEY_LEFT_CONTROL: constants.KEY_CONTROL,
    glfw.KEY_RIGHT_CONTROL: constants.KEY_CONTROL,
    glfw.KEY_LEFT_ALT: constants.KEY_ALT,
    glfw.KEY_RIGHT_ALT: constants.KEY_ALT,
}


KEY_MAP_MOD = {
    glfw.KEY_LEFT_SHIFT: constants.KEY_SHIFT,
    glfw.KEY_RIGHT_SHIFT: constants.KEY_SHIFT,
    glfw.KEY_LEFT_CONTROL: constants.KEY_CONTROL,
    glfw.KEY_RIGHT_CONTROL: constants.KEY_CONTROL,
    glfw.KEY_LEFT_ALT: constants.KEY_ALT,
    glfw.KEY_RIGHT_ALT: constants.KEY_ALT,
}


# Make uppercase letters be lowercase
for i in range(ord("A"), ord("Z")):
    KEY_MAP[i] = i + 32


class GLWidget:
    """Implementation of the GL_window, which passes a number of
    events to the Figure object that wraps it.
    """

    def __init__(self, figure, *args, **kwargs):
        self.figure = figure

        # Set window hints
        glfw.window_hint(glfw.CLIENT_API, glfw.OPENGL_API)
        glfw.window_hint(glfw.RESIZABLE, True)
        # see https://github.com/FlorianRhiem/pyGLFW/issues/42
        # Alternatively, from pyGLFW 1.10 one can set glfw.ERROR_REPORTING='warn'
        if sys.platform.startswith("linux"):
            if is_wayland:
                glfw.window_hint(glfw.FOCUSED, False)  # prevent Wayland focus error

        # Create the window (the initial size may not be in logical pixels)
        self._window = glfw.create_window(640, 480, "Visvis GLFW figure", None, None)

        # Other internal variables
        self._need_draw = False
        self._request_draw_timer_running = False
        self._changing_pixel_ratio = False
        self._is_minimized = False
        self._last_draw_time = 0
        self._max_fps = 60.0
        self._logical_size = 640, 480

        # Register ourselves
        glfw.all_glfw_canvases.add(self)

        # Register callbacks. We may get notified too often, but that's
        # ok, they'll result in a single draw.
        glfw.set_framebuffer_size_callback(self._window, self._on_size_change)
        glfw.set_window_close_callback(self._window, self._on_close)
        glfw.set_window_refresh_callback(self._window, self._on_window_dirty)
        glfw.set_window_focus_callback(self._window, self._on_focus)
        set_window_content_scale_callback(self._window, self._on_pixelratio_change)
        set_window_maximize_callback(self._window, self._on_window_dirty)
        glfw.set_window_iconify_callback(self._window, self._on_iconify)

        # User input
        self._key_modifiers = set()
        self._pointer_buttons = set()
        self._pointer_pos = 0, 0
        self._double_click_state = {"clicks": 0}
        glfw.set_mouse_button_callback(self._window, self._on_mouse_button)
        glfw.set_cursor_pos_callback(self._window, self._on_cursor_pos)
        glfw.set_scroll_callback(self._window, self._on_scroll)
        glfw.set_key_callback(self._window, self._on_key)

        # Initialize the size
        self._pixel_ratio = -1
        self._screen_size_is_logical = False
        self._request_draw()

    # Callbacks to provide a minimal working canvas

    def _on_pixelratio_change(self, *args):
        if self._changing_pixel_ratio:
            return
        self._changing_pixel_ratio = True  # prevent recursion (on Wayland)
        try:
            self._set_logical_size(self._logical_size)
        finally:
            self._changing_pixel_ratio = False
        self._request_draw()

    def _on_size_change(self, *args):
        self._determine_size()
        self._request_draw()
        self.figure._OnResize()

    def _on_close(self, *args):
        glfw.all_glfw_canvases.discard(self)
        glfw.hide_window(self._window)
        if self.figure:
            self.figure.Destroy()

    def _on_window_dirty(self, *args):
        self._request_draw()

    def _on_iconify(self, window, iconified):
        self._is_minimized = bool(iconified)

    def _on_focus(self, *args):
        BaseFigure._currentNr = self.figure.nr
        self._on_window_dirty()

    # helpers

    def _mark_ready_for_draw(self):
        self._request_draw_timer_running = False
        self._need_draw = True  # The event loop looks at this flag
        glfw.post_empty_event()  # Awake the event loop, if it's in wait-mode

    def _determine_size(self):
        # Because the value of get_window_size is in physical-pixels
        # on some systems and in logical-pixels on other, we use the
        # framebuffer size and pixel ratio to derive the logical size.
        pixel_ratio = get_window_content_scale(self._window)[0]
        psize = glfw.get_framebuffer_size(self._window)
        psize = int(psize[0]), int(psize[1])

        self._pixel_ratio = pixel_ratio
        self._physical_size = psize
        self._logical_size = psize[0] / pixel_ratio, psize[1] / pixel_ratio

        self.figure._devicePixelRatio = self._pixel_ratio

    def _set_logical_size(self, new_logical_size):
        # There is unclarity about the window size in "screen pixels".
        # It appears that on Windows and X11 its the same as the
        # framebuffer size, and on macOS it's logical pixels.
        # See https://github.com/glfw/glfw/issues/845
        # Here, we simply do a quick test so we can compensate.

        # The current screen size and physical size, and its ratio
        pixel_ratio = get_window_content_scale(self._window)[0]
        ssize = glfw.get_window_size(self._window)
        psize = glfw.get_framebuffer_size(self._window)

        # Apply
        if is_wayland:
            # Not sure why, but on Wayland things work differently
            screen_ratio = ssize[0] / new_logical_size[0]
            glfw.set_window_size(
                self._window,
                int(new_logical_size[0] / screen_ratio),
                int(new_logical_size[1] / screen_ratio),
            )
        else:
            screen_ratio = ssize[0] / psize[0]
            glfw.set_window_size(
                self._window,
                int(new_logical_size[0] * pixel_ratio * screen_ratio),
                int(new_logical_size[1] * pixel_ratio * screen_ratio),
            )
        self._screen_size_is_logical = screen_ratio != 1
        # If this causes the widget size to change, then _on_size_change will
        # be called, but we may want force redetermining the size.
        if pixel_ratio != self._pixel_ratio:
            self._determine_size()

    # API

    def set_title(self, title):
        glfw.set_window_title(self._window, title)

    def make_current(self):
        glfw.make_context_current(self._window)

    def swap_buffers(self):
        glfw.swap_buffers(self._window)

    def get_pixel_ratio(self):
        return self._pixel_ratio

    def get_logical_size(self):
        return self._logical_size

    def get_physical_size(self):
        return self._physical_size

    def set_logical_size(self, width, height):
        if width < 0 or height < 0:
            raise ValueError("Window width and height must not be negative")
        self._set_logical_size((float(width), float(height)))

    def set_pos(self, x, y):
        glfw.set_window_pos(self._window, x, y)

    def get_pos(self):
        return glfw.get_window_pos(self._window)

    def _request_draw(self):
        if not self._request_draw_timer_running:
            self._request_draw_timer_running = True
            call_later(self._get_draw_wait_time(), self._mark_ready_for_draw)

    def _get_draw_wait_time(self):
        """Get time (in seconds) to wait until the next draw in order to honour max_fps."""
        now = time.perf_counter()
        target_time = self._last_draw_time + 1.0 / self._max_fps
        return max(0, target_time - now)

    def close(self):
        glfw.set_window_should_close(self._window, True)
        self._on_close()

    def is_closed(self):
        return glfw.window_should_close(self._window)

    # User events

    def _on_mouse_button(self, window, but, action, mods):
        if not self.figure:
            return
        # Map button being changed, which we use to update self._pointer_buttons.
        button_map = {
            glfw.MOUSE_BUTTON_1: 1,  # == MOUSE_BUTTON_LEFT
            glfw.MOUSE_BUTTON_2: 2,  # == MOUSE_BUTTON_RIGHT
            glfw.MOUSE_BUTTON_3: 3,  # == MOUSE_BUTTON_MIDDLE
            glfw.MOUSE_BUTTON_4: 4,
            glfw.MOUSE_BUTTON_5: 5,
            glfw.MOUSE_BUTTON_6: 6,
            glfw.MOUSE_BUTTON_7: 7,
            glfw.MOUSE_BUTTON_8: 8,
        }
        button = button_map.get(but, 0)

        if action == glfw.PRESS:
            event_type = "down"
            self._pointer_buttons.add(button)
        elif action == glfw.RELEASE:
            event_type = "up"
            self._pointer_buttons.discard(button)
        else:
            return

        x = int(self._pointer_pos[0] + 0.499)
        y = int(self._pointer_pos[1] + 0.499)
        modifiers = tuple(self._key_modifiers)

        self.figure._GenerateMouseEvent(event_type, x, y, button, modifiers)

        # Maybe emit a double-click event
        self._follow_double_click(action, button)

    def _follow_double_click(self, action, button):
        # If a sequence of down-up-down-up is made in nearly the same
        # spot, and within a short time, we emit the double-click event.

        x, y = self._pointer_pos[0], self._pointer_pos[1]
        state = self._double_click_state

        timeout = 0.25
        distance = 5

        # Clear the state if it does no longer match
        if state["clicks"] > 0:
            d = ((x - state["x"]) ** 2 + (y - state["y"]) ** 2) ** 0.5
            if (
                d > distance
                or time.perf_counter() - state["time"] > timeout
                or button != state["button"]
            ):
                self._double_click_state = {"clicks": 0}

        clicks = self._double_click_state["clicks"]

        # Check and update order. Emit event if we make it to the final step
        if clicks == 0 and action == glfw.PRESS:
            self._double_click_state = {
                "clicks": 1,
                "button": button,
                "time": time.perf_counter(),
                "x": x,
                "y": y,
            }
        elif clicks == 1 and action == glfw.RELEASE:
            self._double_click_state["clicks"] = 2
        elif clicks == 2 and action == glfw.PRESS:
            self._double_click_state["clicks"] = 3
        elif clicks == 3 and action == glfw.RELEASE:
            self._double_click_state = {"clicks": 0}
            x = int(self._pointer_pos[0] + 0.499)
            y = int(self._pointer_pos[1] + 0.499)
            modifiers = tuple(self._key_modifiers)
            self.figure._GenerateMouseEvent("double", x, y, button, modifiers)

    def _on_cursor_pos(self, window, x, y):
        if not self.figure:
            return
        # Store pointer position in logical coordinates
        if self._screen_size_is_logical:
            self._pointer_pos = x, y
        else:
            self._pointer_pos = x / self._pixel_ratio, y / self._pixel_ratio

        x = int(self._pointer_pos[0] + 0.499)
        y = int(self._pointer_pos[1] + 0.499)
        modifiers = tuple(self._key_modifiers)
        self.figure._GenerateMouseEvent("motion", x, y, 0, modifiers)

    def _on_scroll(self, window, dx, dy):
        if not self.figure:
            return
        # wheel is 1 or -1 in glfw, in jupyter_rfb this is ~100
        x = int(self._pointer_pos[0] + 0.499)
        y = int(self._pointer_pos[1] + 0.499)
        modifiers = tuple(self._key_modifiers)
        self.figure._GenerateMouseEvent("scroll", x, y, dx, dy, modifiers)

    def _on_key(self, window, key, scancode, action, mods):
        if not self.figure:
            return
        modifier = KEY_MAP_MOD.get(key, None)

        if action == glfw.PRESS:
            event_type = "keydown"
            if modifier:
                self._key_modifiers.add(modifier)
        elif action == glfw.RELEASE:
            event_type = "keyup"
            if modifier:
                self._key_modifiers.discard(modifier)
        else:  # glfw.REPEAT
            return

        # Note that if the user holds shift while pressing "5", will result in "5",
        # and not in the "%" that you'd expect on a US keyboard. Glfw wants us to
        # use set_char_callback for text input, but then we'd only get an event for
        # key presses (down followed by up). So we accept that GLFW is less complete
        # in this respect.
        if key in KEY_MAP:
            keyname = KEY_MAP[key]
        else:
            try:
                keyname = chr(key)
            except ValueError:
                return  # Probably a special key that we don't have in our KEY_MAP
            if "Shift" not in self._key_modifiers:
                keyname = keyname.lower()

        modifiers = tuple(self._key_modifiers)
        self.figure._GenerateKeyEvent(event_type, keyname, keyname, modifiers)


class Figure(BaseFigure):
    """This is the glfw implementation of the figure class.

    A Figure represents the OpenGl context and is the root
    of the visualization tree; a Figure Wibject does not have a parent.

    A Figure can be created with the function vv.figure() or vv.gcf().
    """

    def __init__(self, *args, **kwargs):
        self._widget = None
        self._widget_args = (args, kwargs)
        if kwargs.get("create_widget", True):
            self.CreateWidget()

        # call original init AFTER we created the widget
        BaseFigure.__init__(self)

    def CreateWidget(self):
        """Create the Figure's widget if necessary, and return the
        widget."""
        if self._widget is None:
            # Make sure there is a native app and the timer is started
            # (also when embedded)
            app.Create()

            # create widget
            updatePosition = False
            args, kwargs = self._widget_args
            if "create_widget" in kwargs:
                updatePosition = True
                kwargs.pop("create_widget")
            self._widget = GLWidget(self, *args, **kwargs)
            if updatePosition:
                self.position._Changed()
        return self._widget

    def _SetCurrent(self):
        """make this scene the current context"""
        if self._widget:
            self._widget.make_current()

    def _SwapBuffers(self):
        """Swap the memory and screen buffer such that
        what we rendered appears on the screen"""
        if self._widget:
            self._widget.swap_buffers()

    def _SetTitle(self, title):
        """Set the title of the figure..."""
        if self._widget:
            self._widget.set_title(title)

    def _SetPosition(self, x, y, w, h):
        """Set the position of the widget."""
        if self._widget:
            # select widget to resize. If it
            widget = self._widget
            # apply
            widget.set_pos(x, y)
            widget.set_logical_size(w, h)

    def _GetPosition(self):
        """Get the position of the widget."""
        if self._widget:
            # select widget to resize. If it
            widget = self._widget
            # get and return
            x, y = widget.get_pos()
            w, h = widget.get_logical_size()
            return x, y, w, h
        return 0, 0, 0, 0

    def _RedrawGui(self):
        if self._widget:
            self._widget._request_draw()

    def _ProcessGuiEvents(self):
        glfw.poll_events()

    def _Close(self, widget=None):
        if widget is None:
            widget = self._widget
        if widget:
            widget.close()


def newFigure():
    """Create a window with a figure widget."""
    size = visvis.settings.figureSize
    figure = Figure(size[0], size[1], "Figure")
    size = visvis.settings.figureSize
    figure._widget.set_logical_size(size[0], size[1])
    return figure


class App(events.App):
    """App()

    Application class to wrap the GUI applications in a class
    with a simple interface that is the same for all backends.

    This is the fltk implementation.

    """

    def __init__(self):
        pass

    def _GetNativeApp(self):
        return glfw

    def _ProcessEvents(self):
        glfw.poll_events()

    def _Run(self):
        loop = asyncio.get_event_loop()
        glfw.stop_if_no_more_canvases = True
        loop.run_forever()


def call_later(delay, callback, *args):
    loop = asyncio.get_event_loop()
    loop.call_later(delay, callback, *args)


def update_glfw_canvasses():
    """Call this in your glfw event loop to draw each canvas that needs
    an update. Returns the number of visible canvases.
    """
    # Note that _draw_frame_and_present already catches errors, it can
    # only raise errors if the logging system fails.
    canvases = tuple(glfw.all_glfw_canvases)
    for canvas in canvases:
        if canvas._need_draw and not canvas._is_minimized:
            canvas._need_draw = False
            canvas.figure.OnDraw()
    return len(canvases)


async def mainloop():  # noqa E999: this is invalid below a certain version
    loop = asyncio.get_event_loop()
    processVisvisEvents = events.processVisvisEvents

    while True:
        n = update_glfw_canvasses()
        if glfw.stop_if_no_more_canvases and not n:
            break
        await asyncio.sleep(0.001)
        glfw.poll_events()
        processVisvisEvents()
    loop.stop()
    glfw.terminate()


# Init glfw. Ok to call this multiple times
glfw.init()


# Init event loop
if not hasattr(glfw, "all_glfw_canvases"):
    # Store set of canvases on the glfw module, because the current backand module
    # can be reloaded every time that vv.use() is called.
    glfw.all_glfw_canvases = weakref.WeakSet()
    glfw.stop_if_no_more_canvases = False

    # We start the event loop now, so that in an interactive session
    # this simply gets it running. When not in an interactive session,
    # the task wait until the loop gets started (via App.Run()).
    loop = asyncio.get_event_loop()
    loop.create_task(mainloop())


# Create application instance now
app = App()
