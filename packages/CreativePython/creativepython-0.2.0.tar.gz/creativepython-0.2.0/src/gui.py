#######################################################################################
# gui.py       Version 1.0     13-May-2025
# Taj Ballinger, Trevor Ritchie, Bill Manaris, and Dana Hughes
#
#######################################################################################
#
# [LICENSING GOES HERE]
#
#######################################################################################
#
#
#######################################################################################
import PySide6.QtWidgets as _QtWidgets
import PySide6.QtGui as _QtGui
import PySide6.QtCore as _QtCore
import PySide6.QtOpenGLWidgets as _QtOpenGL
import numpy as np
from copy import deepcopy
#######################################################################################

### QT
# PySide6 is a Python binding for Qt, a popular C++ framework for GUI
# development.  QApplication is the heart of this framework.

# In a typical GUI, the QApplication is created early in the main script,
#  and its .exec() method is called at the end of the program to start
#  the event loop.
# However, we want to allow the user to run and execute scripts dynamically,
#  so we can't call .exec() without occupying the main thread.  Fortunately,
#  Qt has an alternative event loop that runs in a separate thread, but only
#  while the Python interpreter is running.
# To hide the Qt event loop from the user, and allow dynamic scripting, we
#  require the user to run scripts with the -i option, which enables this
#  secondary, hidden event loop, and always makes the interpreter available.

#
if "_QTAPP_" not in globals():
   _QTAPP_ = None  # claim global variable for QApplication

if "_DISPLAYS_" not in globals():
   _DISPLAYS_ = []  # track all displays created


def _ensureApp():
   """Guarantee that a QApplication is running."""
   # this function is called whenever we create a new display,
   # or queue a function that modifies the display (or the display's items)
   global _QTAPP_
   if _QTAPP_ is None:
      # try to find an existing QApplication instance
      _QTAPP_ = _QtWidgets.QApplication.instance()
      if _QTAPP_ is None:
         # if no existing QApplication, create a new instance
         _QTAPP_ = _QtWidgets.QApplication([])
         _QTAPP_.setApplicationName("CreativePython")
         _QTAPP_.setStyleSheet(  # force ToolTip font color to black
            """
            QToolTip {
               color: black;
            }
            """)

_ensureApp()


# def _paint(function, *args, **kwargs):
#    """Queue a function to call in the QTimer event thread."""
#    # this function must be called to modify the display or its items safely
#    _ensureApp()
#    _QtCore.QTimer.singleShot(0, partial(function, *args, **kwargs))


# def _start():
#    """Begin the QApplication event loop."""
#    # print("Attempting to start the application...")
#    if _APP_ is not None:
#       # print("Starting the application...")
#       _APP_.exec()

#    # print("Exiting the application...")


# # Register the start function to call after the user script loads,
# # but only if we're not in interactive mode (i.e., running from a script).
# if not bool(getattr(sys, 'ps1', sys.flags.interactive)):
#    atexit.register(_start)


#######################################################################################
# Virtual Key Constants
#######################################################################################
# Java 8 VK codes            PySide6 (Qt) key codes
VK_0                         = _QtCore.Qt.Key.Key_0
VK_1                         = _QtCore.Qt.Key.Key_1
VK_2                         = _QtCore.Qt.Key.Key_2
VK_3                         = _QtCore.Qt.Key.Key_3
VK_4                         = _QtCore.Qt.Key.Key_4
VK_5                         = _QtCore.Qt.Key.Key_5
VK_6                         = _QtCore.Qt.Key.Key_6
VK_7                         = _QtCore.Qt.Key.Key_7
VK_8                         = _QtCore.Qt.Key.Key_8
VK_9                         = _QtCore.Qt.Key.Key_9

VK_A                         = _QtCore.Qt.Key.Key_A
VK_B                         = _QtCore.Qt.Key.Key_B
VK_C                         = _QtCore.Qt.Key.Key_C
VK_D                         = _QtCore.Qt.Key.Key_D
VK_E                         = _QtCore.Qt.Key.Key_E
VK_F                         = _QtCore.Qt.Key.Key_F
VK_G                         = _QtCore.Qt.Key.Key_G
VK_H                         = _QtCore.Qt.Key.Key_H
VK_I                         = _QtCore.Qt.Key.Key_I
VK_J                         = _QtCore.Qt.Key.Key_J
VK_K                         = _QtCore.Qt.Key.Key_K
VK_L                         = _QtCore.Qt.Key.Key_L
VK_M                         = _QtCore.Qt.Key.Key_M
VK_N                         = _QtCore.Qt.Key.Key_N
VK_O                         = _QtCore.Qt.Key.Key_O
VK_P                         = _QtCore.Qt.Key.Key_P
VK_Q                         = _QtCore.Qt.Key.Key_Q
VK_R                         = _QtCore.Qt.Key.Key_R
VK_S                         = _QtCore.Qt.Key.Key_S
VK_T                         = _QtCore.Qt.Key.Key_T
VK_U                         = _QtCore.Qt.Key.Key_U
VK_V                         = _QtCore.Qt.Key.Key_V
VK_W                         = _QtCore.Qt.Key.Key_W
VK_X                         = _QtCore.Qt.Key.Key_X
VK_Y                         = _QtCore.Qt.Key.Key_Y
VK_Z                         = _QtCore.Qt.Key.Key_Z

VK_NUMPAD0                   = _QtCore.Qt.Key.Key_0
VK_NUMPAD1                   = _QtCore.Qt.Key.Key_1
VK_NUMPAD2                   = _QtCore.Qt.Key.Key_2
VK_NUMPAD3                   = _QtCore.Qt.Key.Key_3
VK_NUMPAD4                   = _QtCore.Qt.Key.Key_4
VK_NUMPAD5                   = _QtCore.Qt.Key.Key_5
VK_NUMPAD6                   = _QtCore.Qt.Key.Key_6
VK_NUMPAD7                   = _QtCore.Qt.Key.Key_7
VK_NUMPAD8                   = _QtCore.Qt.Key.Key_8
VK_NUMPAD9                   = _QtCore.Qt.Key.Key_9

VK_F1                        = _QtCore.Qt.Key.Key_F1
VK_F2                        = _QtCore.Qt.Key.Key_F2
VK_F3                        = _QtCore.Qt.Key.Key_F3
VK_F4                        = _QtCore.Qt.Key.Key_F4
VK_F5                        = _QtCore.Qt.Key.Key_F5
VK_F6                        = _QtCore.Qt.Key.Key_F6
VK_F7                        = _QtCore.Qt.Key.Key_F7
VK_F8                        = _QtCore.Qt.Key.Key_F8
VK_F9                        = _QtCore.Qt.Key.Key_F9
VK_F10                       = _QtCore.Qt.Key.Key_F10
VK_F11                       = _QtCore.Qt.Key.Key_F11
VK_F12                       = _QtCore.Qt.Key.Key_F12

VK_ESCAPE                    = _QtCore.Qt.Key.Key_Escape
VK_TAB                       = _QtCore.Qt.Key.Key_Tab
VK_CAPS_LOCK                 = _QtCore.Qt.Key.Key_CapsLock
VK_SHIFT                     = _QtCore.Qt.Key.Key_Shift
VK_CONTROL                   = _QtCore.Qt.Key.Key_Control
VK_ALT                       = _QtCore.Qt.Key.Key_Alt
VK_SPACE                     = _QtCore.Qt.Key.Key_Space
VK_ENTER                     = _QtCore.Qt.Key.Key_Return
VK_BACK_SPACE                = _QtCore.Qt.Key.Key_Backspace
VK_DELETE                    = _QtCore.Qt.Key.Key_Delete
VK_HOME                      = _QtCore.Qt.Key.Key_Home
VK_END                       = _QtCore.Qt.Key.Key_End
VK_PAGE_UP                   = _QtCore.Qt.Key.Key_PageUp
VK_PAGE_DOWN                 = _QtCore.Qt.Key.Key_PageDown
VK_UP                        = _QtCore.Qt.Key.Key_Up
VK_DOWN                      = _QtCore.Qt.Key.Key_Down
VK_LEFT                      = _QtCore.Qt.Key.Key_Left
VK_RIGHT                     = _QtCore.Qt.Key.Key_Right

VK_INSERT                    = _QtCore.Qt.Key.Key_Insert
VK_PAUSE                     = _QtCore.Qt.Key.Key_Pause
VK_PRINTSCREEN               = _QtCore.Qt.Key.Key_Print
VK_SCROLL_LOCK               = _QtCore.Qt.Key.Key_ScrollLock
VK_NUM_LOCK                  = _QtCore.Qt.Key.Key_NumLock
VK_SEMICOLON                 = _QtCore.Qt.Key.Key_Semicolon
VK_EQUALS                    = _QtCore.Qt.Key.Key_Equal
VK_COMMA                     = _QtCore.Qt.Key.Key_Comma
VK_MINUS                     = _QtCore.Qt.Key.Key_Minus
VK_PERIOD                    = _QtCore.Qt.Key.Key_Period
VK_SLASH                     = _QtCore.Qt.Key.Key_Slash
VK_BACK_SLASH                = _QtCore.Qt.Key.Key_Backslash
VK_OPEN_BRACKET              = _QtCore.Qt.Key.Key_BracketLeft
VK_CLOSE_BRACKET             = _QtCore.Qt.Key.Key_BracketRight
VK_QUOTE                     = _QtCore.Qt.Key.Key_Apostrophe
VK_BACK_QUOTE                = _QtCore.Qt.Key.Key_QuoteLeft


#######################################################################################
# Color
#######################################################################################
class Color:
   """
   Color class for creating and manipulating colors.

   This class provides functionality for creating and manipulating RGB colors.
   It mirrors Java's Color class functionality from JythonMusic, including:
   - RGB color creation with optional alpha
   - Color constants (RED, BLUE, etc.)
   - Color manipulation (brighter, darker)
   - Conversion to various formats
   """

   def __init__(self, red, green, blue, alpha=255):
      # store color values as 0-255 integers
      self.red   = int(red)
      self.green = int(green)
      self.blue  = int(blue)
      self.alpha = int(alpha)

   def __str__(self):
      return f'Color(red = {self.getRed()}, green = {self.getGreen()}, blue = {self.getBlue()}, alpha = {self.getAlpha()})'

   def __repr__(self):
      return str(self)

   def getRed(self):
      """
      Returns the red value of the color.
      """
      return self.red

   def getGreen(self):
      """
      Returns the green value of the color.
      """
      return self.green

   def getBlue(self):
      """
      Returns the blue value of the color.
      """
      return self.blue

   def getAlpha(self):
      """
      Returns the alpha value of the color.
      """
      return self.alpha

   def getRGB(self):
      """
      Returns the color as a tuple of RGB values.
      """
      return (self.red, self.green, self.blue)

   def getRGBA(self):
      """
      Returns the color as a tuple of RGBA values.
      """
      return (self.red, self.green, self.blue, self.alpha)

   def getHex(self):
      """
      Returns the color as a hex string.
      """
      hex = f'#{self.red:02x}{self.green:02x}{self.blue:02x}'  # base hex string

      if self.alpha != 255:
         hex += f'{self.alpha:02x}'  # add alpha if not fully opaque

      return hex

   def brighter(self):
      # increase each component by 10% while keeping within 0-255
      return Color(
         min(255, int(self.red * 1.1)),
         min(255, int(self.green * 1.1)),
         min(255, int(self.blue * 1.1)),
         self.alpha
      )


   def darker(self):
      # decrease each component by 10% while keeping within 0-255
      return Color(
         max(0, int(self.red * 0.9)),
         max(0, int(self.green * 0.9)),
         max(0, int(self.blue * 0.9)),
         self.alpha
      )


# preset colors defined as global properties, mirroring JColor syntax
Color.BLACK      = Color(  0,   0,   0)
Color.BLUE       = Color(  0,   0, 255)
Color.CYAN       = Color(  0, 255, 255)
Color.DARK_GRAY  = Color( 44,  44,  44)
Color.GRAY       = Color(128, 128, 128)
Color.GREEN      = Color(  0, 255,   0)
Color.LIGHT_GRAY = Color(211, 211, 211)
Color.MAGENTA    = Color(255,   0, 255)
Color.ORANGE     = Color(255, 165,   0)
Color.PINK       = Color(255, 192, 203)
Color.RED        = Color(255,   0,   0)
Color.WHITE      = Color(255, 255, 255)
Color.YELLOW     = Color(255, 255,   0)
Color.CLEAR      = Color(  0,   0,   0,   0)


#######################################################################################
# Color gradient
#
# A color gradient is a smooth color progression from one color to another,
# which creates the illusion of continuity between the two color extremes.
#
# The following auxiliary function may be used used to create a color gradient.
# This function returns a list of RGB colors (i.e., a list of lists) starting with color1
# (e.g., [0, 0, 0]) and ending (without including) color2 (e.g., [251, 147, 14], which is orange).
# The number of steps equals the number of colors in the list returned.
#
# For example, the following creates a gradient list of 12 colors:
#
# >>> colorGradient([0, 0, 0], [251, 147, 14], 12)
# [[0, 0, 0], [20, 12, 1], [41, 24, 2], [62, 36, 3], [83, 49, 4], [104, 61, 5], [125, 73, 7],
# [146, 85, 8], [167, 98, 9], [188, 110, 10], [209, 122, 11], [230, 134, 12]]
#
# Notice how the above excludes the final color (i.e.,  [251, 147, 14]).  This allows to
# create composite gradients (without duplication of colors).  For example, the following
#
# black = [0, 0, 0]         # RGB values for black
# orange = [251, 147, 14]   # RGB values for orange
# white = [255, 255, 255]   # RGB values for white
#
# cg = colorGradient(black, orange, 12) + colorGradient(orange, white, 12) + [white]
#
# creates a list of gradient colors from black to orange, and from orange to white.
# Notice how the final color, white, has to be included separately (using list concatenation).
# Now, gc contains a total of 25 unique gradient colors.
#
# For convenience, colorGradient() also works with Color objects, in which case
# it returns a list of Color objects.
#
#######################################################################################
def colorGradient(color1, color2, steps):
   """
   Returns a list of RGB colors creating a "smooth" gradient between 'color1'
   and 'color2'.  The amount of smoothness is determined by 'steps', which specifies
   how many intermediate colors to create. The result includes 'color1' but not
   'color2' to allow for connecting one gradient to another (without duplication
   of colors).
   """
   gradientList = []   # holds RGB lists of individual gradient colors

   # check if using Color objects
   if isinstance(color1, Color) and isinstance(color2, Color):
      # extract RGB values
      red1, green1, blue1 = color1.getRed(), color1.getGreen(), color1.getBlue()
      red2, green2, blue2 = color2.getRed(), color2.getGreen(), color2.getBlue()

   else:  # otherwise, assume RGB list
      # extract RGB values
      red1, green1, blue1 = color1
      red2, green2, blue2 = color2

   # find difference between color extremes
   differenceR = red2   - red1     # R component
   differenceG = green2 - green1   # G component
   differenceB = blue2  - blue1    # B component

   # interpolate RGB values between extremes
   for i in range(steps):
      gradientR = red1   + i * differenceR / steps
      gradientG = green1 + i * differenceG / steps
      gradientB = blue1  + i * differenceB / steps

      # ensure color values are integers
      gradientList.append([int(gradientR), int(gradientG), int(gradientB)])
   # now, gradient list contains all the intermediate colors, including color1
   # but not color2

   # if input was Color objects (e.g., Color.RED), return Color objects
   # otherwise, keep as RGB lists (e.g., [255, 0, 0]
   if isinstance(color1, Color):
      gradientList = [Color(rgb[0], rgb[1], rgb[2]) for rgb in gradientList]

   return gradientList


########################################################################################
# Font
########################################################################################
class Font:

   PLAIN      = (_QtGui.QFont.Weight.Normal, False)
   BOLD       = (_QtGui.QFont.Weight.Bold,   False)
   ITALIC     = (_QtGui.QFont.Weight.Normal, True)
   BOLDITALIC = (_QtGui.QFont.Weight.Bold,   True)

   def __init__(self, fontName, style=PLAIN, fontSize=-1):
      # store internal attributes
      self.name      = fontName
      self.style     = style
      self.size      = fontSize

      # create Qt object
      qtObject = _QtGui.QFont(self.name, self.size)
      qtObject.setWeight(self.style[0])
      qtObject.setItalic(self.style[1])

      self._qtObject = qtObject


   def __str__(self):
      return f'Font("fontName={self.name}", style={self.style}, fontSize={self.size})'

   def __repr__(self):
      return str(self)


#######################################################################################
# Interactable
#######################################################################################
class Interactable:
   """
   Abstract for interactive objects.

   This class stores callbacks for keyboard, mouse and display events
   to match JythonMusic's event handling system. Objects that inherit from Interactable
   can register callback functions for various keyboard, mouse, and display events.
   """
   def __init__(self):
      self.display = None
      self.group   = None
      self._callbackFunctions = {}

   def __str__( self ):
      return f'Interactable()'

   def __repr__( self ):
      return str(self)

   # def _event(self, type="", args=[]):
   def _receiveEvent(self, event):
      """
      This method is called by the Display when an event occurs.
      It filters events and calls the corresponding callback function,
      if it has been defined.
      """
      if event.type in self._callbackFunctions:          # is event defined?
         callback = self._callbackFunctions[event.type]  # yes, get callback
         if callable(callback):                          # is callback callable?
            callback(*event.args)                        # yes, call it with args
            event.handled = True                         # mark event as handled

      return event.handled

   def _hasCallback(self, type=""):
      return self._callbackFunctions.get(type) is not None

   def _registerCallback(self):
      if self.display is not None:            # if this object is already on a display,
         self.display._eventDispatcher.add(self)  # register the new event with its event filter


   ### USER METHODS ###

   def onMouseClick(self, function):
      """
      Set callback for mouse click events (click means both press and release).
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse click.
      """
      self._callbackFunctions['mouseClick'] = function
      self._registerCallback()


   def onMouseDown(self, function):
      """
      Set callback for mouse button press events.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse press.
      """
      self._callbackFunctions['mouseDown'] = function
      self._registerCallback()


   def onMouseUp(self, function):
      """
      Set callback for mouse button release events.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse release.
      """
      self._callbackFunctions['mouseUp'] = function
      self._registerCallback()


   def onMouseMove(self, function):
      """
      Set callback for mouse movement events within this object.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse movement.
      """
      self._callbackFunctions['mouseMove'] = function
      self._registerCallback()


   def onMouseDrag(self, function):
      """
      Set callback for mouse drag events within this object.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of the mouse movement.
      """
      self._callbackFunctions['mouseDrag'] = function
      self._registerCallback()


   def onMouseEnter(self, function):
      """
      Set callback for when mouse enters this object's bounds.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of where the mouse entered.
      """
      self._callbackFunctions['mouseEnter'] = function
      self._registerCallback()


   def onMouseExit(self, function):
      """
      Set callback for when mouse exits this object's bounds.
      The callback function should accept two parameters (x, y),
      which are the x and y coordinates of where the mouse exited.
      """
      self._callbackFunctions['mouseExit'] = function
      self._registerCallback()


   def onKeyType(self, function):
      """
      Set callback for key type events.
      The callback function should accept one parameter (a character),
      which is the character typed.
      """
      self._callbackFunctions['keyType'] = function
      self._registerCallback()


   def onKeyDown(self, function):
      """
      Set callback for key press events.
      The callback function should accept one parameter (an int),
      which is the virtual key code of the key pressed.
      """
      self._callbackFunctions['keyDown'] = function
      self._registerCallback()


   def onKeyUp(self, function):
      """
      Set callback for key release events.
      The callback function should accept one parameter (an int),
      which is the virtual key code of the key released.
      """
      self._callbackFunctions['keyUp'] = function
      self._registerCallback()

#######################################################################################
# Event Dispatcher
#######################################################################################
class Event():
   """
   Generic Event class for storing relevant event data.
   """
   def __init__(self, type, *args):
      self.type    = str(type)
      self.args    = []
      self.handled = False

      for a in args:
         self.args.append(a)  # unnecessary? can we just store *args as self.args?

   def __str__(self):
      return f'Event(type = {self.type}, args = {self.args})'


class EventDispatcher(_QtCore.QObject):
   """
   EventDispatchers attach to Displays, connecting Qt's events to JythonMusic events.
      QT EVENTS    -> JYTHONMUSIC EVENTS
      MousePress   -> onMouseDown
      MouseRelease -> onMouseUp + onMouseClick (if mouse didn't move)
      MouseMove    -> onMouseMove or onMouseDrag (if mouse is pressed)
      MouseEnter   -> onMouseEnter
      MouseLeave   -> onMouseExit
      KeyPress     -> onKeyDown + onKeyType
      KeyRelease   -> onKeyUp

   When an event occurs, the Display always sees the event first.
   Mouse events deliver to the topmost item at the event's position, that has a corresponding callback.
   Key events deliver to the most recent, topmost item that a mouseDown event occurred at
      ("the last item you clicked on").
   """

   def __init__(self, display):
      super().__init__()
      self.display = display
      self.lastMouseDown = None     # last location mouse down event occured (set to None when mouse is up)
      self.lastMouseMove = None     # last known mouse movement/position
      self.moveThreshold = 5        # maximum distance to trigger a mouse click (down/up in the same place)
      self.draggingItem  = None     # last item clicked on
      self.itemsUnderMouse = set()  # set of items under last known mouse position

      self.display._view.viewport().installEventFilter(self)  # redirect mouse events
      self.display._view.installEventFilter(self)             # redirect key events
      # _QtWidgets.QApplication.instance().installEventFilter(self)  # redirect global events

      # Each EventDispatcher keeps track of the objects in its display that have callbacks registered
      # for each type of event.  These lists are ordered by z-order and updated whenever an object is
      # added or removed from the display, or when a new callback is registered to an object.
      # Maintaining these lists saves us from having to search the entire list of added objects each time an event fires,
      #   simplifying the work to only searching the list of objects with a relevant callback registered.
      self.eventHandlers = {
         'mouseDown':    [],
         'mouseUp':      [],
         'mouseClick':   [],
         'mouseMove':    [],
         'mouseDrag':    [],
         'mouseEnter':   [],
         'mouseExit':    [],
         'keyType':      [],
         'keyDown':      [],
         'keyUp':        []
      }


   def eventFilter(self, object, qEvent):
      """
      eventFilter is a Qt-defined method that implements our custom event handler logic.
      We filter mouse events through the viewport, and key events through the view.
         (Mouse events can be delivered through either, but key events are only through view.
            However, mouse events delivered through view are sometimes missing important positional data.
         If we did not filter this way, mouse events would be duplicated with missing information.)
      """
      isHandled = False

      view = self.display._view
      view.setUpdatesEnabled(False)  # pause display updates during event processing

      # there are many other events that will filter through, but we only care about these
      if qEvent.type() == _QtCore.QEvent.Type.MouseButtonPress:
         if object == self.display._view.viewport():  # only respond to events from viewport()
            isHandled = self.handleMousePress(qEvent)

      elif qEvent.type() == _QtCore.QEvent.Type.MouseButtonRelease:
         if object == self.display._view.viewport():  # only respond to events from viewport()
            isHandled = self.handleMouseRelease(qEvent)

      elif qEvent.type() == _QtCore.QEvent.Type.MouseMove:
         if object == self.display._view.viewport():  # only respond to events from viewport()
            isHandled = self.handleMouseMove(qEvent)

      elif qEvent.type() == _QtCore.QEvent.Type.Enter:
         if object == self.display._view.viewport():  # only respond to events from viewport()
            isHandled = self.handleEnterEvent(qEvent)

      elif qEvent.type() == _QtCore.QEvent.Type.Leave:
         if object == self.display._view.viewport():  # only respond to events from viewport()
            isHandled = self.handleLeaveEvent(qEvent)

      elif qEvent.type() == _QtCore.QEvent.Type.KeyPress:
         if object == self.display._view:             # only respond to events from view
            isHandled = self.handleKeyPress(qEvent)

      elif qEvent.type() == _QtCore.QEvent.Type.KeyRelease:
         if object == self.display._view:             # only respond to events from view
            isHandled = self.handleKeyRelease(qEvent)

      view.setUpdatesEnabled(True)  # resume automatic updating
      if isHandled:                 # if we handled an event...
         view.viewport().update()   # ...repaint the Display now

      return isHandled


   def handleMousePress(self, qEvent):
      """
      Determines which display object(s) to deliver mouse down events to.
      """
      # first, we need to find and update some information
      x, y = self._findMousePosition(qEvent)     # find current mouse position
      self.lastMouseDown = (x, y)                # store mouse down position
      self.draggingItem  = self._findTopItemAt(self.eventHandlers['mouseDrag'], x, y)

      # second, send mouseDown event to display and topmost item with corresponding callback
      mouseDownEvent = Event("mouseDown", x, y)
      self._deliverEvent([self.display], mouseDownEvent)
      self._deliverEvent(self.eventHandlers['mouseDown'], mouseDownEvent)

      return mouseDownEvent.handled


   def handleMouseRelease(self, qEvent):
      """
      Determines which objects(s) to deliver mouse up and mouse click events to.
      mouseUp    events happen whenever the mouse is released.
      mouseClick events only happen when the mouse is released close to where it was pressed.
      """
      # first, we need to find and update some information
      x, y = self._findMousePosition(qEvent)      # find current mouse position

      isMouseClick = False                                       # assume this is not a mouseClick
      if self.lastMouseDown is not None:                         # was there a mouseDown event?
         dx = abs(x - self.lastMouseDown[0])                     # yes, how far has the mouse moved?
         dy = abs(y - self.lastMouseDown[1])
         if dx <= self.moveThreshold and dy <= self.moveThreshold:  # is it under the threshold?
            isMouseClick = True                                     # yes, this is also a mouseClick

      self.lastMouseDown = None  # clear mouse down position
      self.draggingItem  = None  # clear dragging item

      # second, send mouseUp event to display and topmost item with corresponding callback
      mouseUpEvent = Event("mouseUp", x, y)
      self._deliverEvent([self.display], mouseUpEvent)
      self._deliverEvent(self.eventHandlers['mouseUp'], mouseUpEvent)

      # last, if this is a mouseClick, send mouseClick event to display and topmost item with corresponding callback
      if isMouseClick:
         mouseClickEvent = Event("mouseClick", x, y)
         self._deliverEvent([self.display], mouseClickEvent)
         self._deliverEvent(self.eventHandlers['mouseClick'], mouseClickEvent)

      return mouseUpEvent.handled or (mouseClickEvent.handled if isMouseClick else False)


   def handleMouseMove(self, qEvent):
      """
      Determines which object(s) to deliver mouse move, drag, enter, and exit events to.
      mouseMove  events happen whenever the mouse moves, unless the mouse is held down.
      mouseDrag  events happen whenever the mouse moves while the mouse is held down.
      mouseEnter events happen whenever the mouse enters the boundaries of an object.
      mouseExit  events happen whenever the mouse exits the boundaries of an object.
         * Mouse Enter and Exit events for displays are triggered in mouseEnterEvent and mouseLeaveEvent below.
      """
      # first, we need to find and update some information
      x, y = self._findMousePosition(qEvent)  # find current mouse position
      self.lastMouseMove = (x, y)             # store current mouse position
      self._updateCoordinateTooltip(x, y)     # refresh tooltip coordinates (if needed)

      # how we proceed depends on whether this is a move or drag event...

      if self.lastMouseDown is None:  # mouse is up, so this is a mouseMove event
         # second, send mouseMove event to display and topmost item with corresponding callback
         mouseMoveEvent = Event("mouseMove", x, y)
         self._deliverEvent([self.display], mouseMoveEvent)
         self._deliverEvent(self.eventHandlers['mouseMove'], mouseMoveEvent)

      else:                           # mouse is down, so this is a mouseDrag event
         # second, send mouseDrag event to display and dragging item
         mouseMoveEvent = Event("mouseDrag", x, y)  # still called mouseMoveEvent for return statement
         self._deliverEvent([self.display], mouseMoveEvent)
         self._deliverEvent([self.draggingItem], mouseMoveEvent)

      # finally, we need to process mouseEnter and mouseExit events
      # we use sets for efficient difference calculations
      # the caveat is that sets aren't ordered, so we can't guarantee z-order for enter/exit events
      candidateSet = set()
      for item in self.display.items:
         if item.contains(x, y):
            candidateSet.add(item)

      enteredSet           = candidateSet - self.itemsUnderMouse     # items we moved into
      exitedSet            = self.itemsUnderMouse - candidateSet     # items we moved out of
      self.itemsUnderMouse = candidateSet                            # store set of items under mouse

      mouseEnterEvent = Event("mouseEnter", x, y)                    # generate enter event
      enterHandlers   = set(self.eventHandlers['mouseEnter'])        # create set of event handlers
      enterHandlers   = enteredSet.intersection(enterHandlers)       # find items in both sets
      self._deliverEventToAll(list(enterHandlers), mouseEnterEvent)  # send event to each intersecting item

      mouseExitEvent = Event("mouseExit", x, y)                      # generate exit event
      exitHandlers   = set(self.eventHandlers['mouseExit'])          # create set of event handlers
      exitHandlers   = exitedSet.intersection(exitHandlers)          # find items in both sets
      self._deliverEventToAll(list(exitHandlers), mouseExitEvent)    # send event to each intersecting item

      return mouseMoveEvent.handled  # we don't care whether enter/exit were handled


   def handleEnterEvent(self, qEvent):
      """
      Delivers mouseEnter events to the display.
      mouseEnter events for objects are handled in handleMouseMove()
      """
      # first, we need to find and update some information
      x, y = self._findMousePosition(qEvent)  # find current mouse position

      # next, send mouseEnter event to display
      mouseEnterEvent = Event("mouseEnter", x, y)
      self._deliverEvent([self.display], mouseEnterEvent)

      return mouseEnterEvent.handled


   def handleLeaveEvent(self, qEvent):
      """
      Delivers mouseExit events to the display.
      mouseExit events for objects are handled in handleMouseMove()
      """
      # first, we need to find and update some information
      x, y = self._findMousePosition(qEvent)  # find current mouse position

      # next, we send event to display
      mouseExitEvent = Event("mouseExit", x, y)
      self._deliverEvent([self.display], mouseExitEvent)

      return mouseExitEvent.handled


   def handleKeyPress(self, qEvent):
      """
      Delivers keyDown and keyType events to the display and each item in the display.
      keyDown uses the numeric code for the pressed key.
      keyType uses the typed character for the pressed key (if any).
      """
      eventHandled = False

      # only process non-auto-repeat events to prevent key repeat issues
      if not qEvent.isAutoRepeat():
         # first, we need to find some information
         key  = qEvent.key()                            # find key code
         char = qEvent.text() if qEvent.text() else ""  # find character

         # second, we send keyDown event to display and all items with corresponding callbacks
         keyDownEvent = Event("keyDown", key)
         self._deliverEvent([self.display], keyDownEvent)
         self._deliverEventToAll(self.eventHandlers['keyDown'], keyDownEvent)

         # last, we send keyType event to display and all items with corresponding callbacks
         keyTypeEvent = Event("keyType", char)
         self._deliverEvent([self.display], keyTypeEvent)
         self._deliverEventToAll(self.eventHandlers['keyType'], keyTypeEvent)

         eventHandled = keyDownEvent.handled or keyTypeEvent.handled

      return eventHandled


   def handleKeyRelease(self, qEvent):
      """
      Delivers keyUp events to the display and each item in the display.
      keyUp uses the numeric code for the pressed key.
      """
      eventHandled = False

      # only process non-auto-repeat events to prevent key repeat issues
      if not qEvent.isAutoRepeat():
         # first, we need to find some information
         key = qEvent.key()                           # find key code

         # second, we send event to display and all items with corresponding callbacks
         keyUpEvent = Event("keyUp", key)
         self._deliverEvent([self.display], keyUpEvent)
         self._deliverEventToAll(self.eventHandlers['keyUp'], keyUpEvent)

         eventHandled = keyUpEvent.handled

      return eventHandled


   def add(self, item):
      """
      Adds the item to each listener list they have a callback for.
      The item is inserted into each list according to its z-order on the display.
      """
      callbackList = item._callbackFunctions.keys()  # get list of registered callbacks
      displayItems = self.display.items              # get list of display items
      displayIndex = displayItems.index(item)        # find index of item in display's z-order

      for eventType in callbackList:                     # for each registered callback,
         if eventType in self.eventHandlers.keys():      # ...that is a known event type,
            handlerList = self.eventHandlers[eventType]  # ...get the appropriate handler list

            # insert item into handler list according to z-order
            if item not in handlerList:
               inserted = False

               # best case, item is topmost so insert at front of handlerList
               if displayIndex == 0:
                  handlerList.insert(0, item)
                  inserted = True

               # otherwise, search for correct position
               i = 0
               while not inserted and i < len(handlerList):
                  otherItem         = handlerList[i]                 # get other item
                  otherDisplayIndex = displayItems.index(otherItem)  # find other item's display index

                  if displayIndex < otherDisplayIndex:  # our item is above otherItem on the display,
                     handlerList.insert(i, item)        # so insert before otherItem in handler list
                     inserted = True

                  i = i + 1

               # worst case, item is bottommost so insert at end of handlerList
               if not inserted:
                  handlerList.append(item)


   def remove(self, item):
      """
      Removes the item from each listener list they're a part of.
      """
      for eventType in self.eventHandlers.keys():            # for each known event type,
         if item in self.eventHandlers[eventType]:           # ... if item is registered,
            self.eventHandlers[eventType].remove(item)       # ... remove it from the appropriate list


   def _findObjectSetAt(self, x, y):
      """
      Find all graphics objects at the given (x,y) position.
      Returns as a set, for contains/comparison operations.
      """
      foundItems = set()

      for item in self.display.items:
         if item.contains(x, y):
            foundItems.add(item)

      return foundItems


   def _findTopItemAt(self, candidateList, x, y):
      """
      Find the topmost graphics object from the given candidateList at the given (x,y) position.
      Returns the graphics object, if found.
      """
      foundItem = None
      i = 0

      while foundItem is None and i < len(candidateList):
         item = candidateList[i]
         if item.contains(x, y):
            foundItem = item
         else:
            i = i + 1

      return foundItem


   def _findMousePosition(self, qEvent):
      """
      Find the current x,y mouse position at the time of the event.
      x and y are relative to the display the event happens in. (i.e. not global)
      """
      if hasattr(qEvent, "position") and callable(qEvent.position):  # if the Qt event has a position() method, we can just use that
         x = int(qEvent.position().x())
         y = int(qEvent.position().y())

      elif self.lastMouseMove is not None:  # if no position available, use last known position
         x = self.lastMouseMove[0]
         y = self.lastMouseMove[1]

      else:  # if no last known position available, default to origin
         x = 0
         y = 0

      return x, y


   def _deliverEvent(self, candidateList, event):
      """
      Deliver an event to the topmost graphics object from the given candidateList.
      """
      i = 0
      if len(candidateList) == 1:           # don't search a single-item list
         if candidateList[0] is not None:   # and don't deliver to None items
            candidateList[0]._receiveEvent(event)

      elif event.type.startswith("mouse"):  # mouse events deliver to topmost item at event location
         x, y = event.args
         while not event.handled and i < len(candidateList):
            item = candidateList[i]         # find candidate item
            if item.contains(x, y):         # ensure event happens at item coordinates
               item._receiveEvent(event)    # send event - event.handled is updated if received
            i = i + 1

      else:                                 # key events deliver to each item in order
         while not event.handled and i < len(candidateList):
            item = candidateList[i]         # find candidate item
            item._receiveEvent(event)       # send event - event.handled is updated if received
            i = i + 1


   def _deliverEventToAll(self, candidateList, event):
      """
      Deliver an event to each graphics object from the given candidateList.
      """
      for item in candidateList:
         item._receiveEvent(event)


   def _updateCoordinateTooltip(self, x, y):
      """
      Implementation of Display's showCoordinates method.
      Whenever this triggers, manually update the display's tooltip to show the current coordinates.
      """
      if self.display.showCoordinates:  # if showing coordinates
         # override any set tooltips to show mouse coordinates instead
         # QToolTips have a delay before appearing, and automatically disappear
         #   after a short time, so we force the tooltip to show immediately,
         #   and refresh it whenever the mouse moves
         globalPos   = self.display._view.mapToGlobal(_QtCore.QPoint(x, y))
         toolTipText = f"({x}, {y})"
         _QtWidgets.QToolTip.showText(globalPos, toolTipText, self.display._view, self.display._view.rect(), 10000)



#######################################################################################
# Drawable
#######################################################################################
class Drawable:
   """
   Base abstract class for all basic geometric objects.
   """

   def __init__(self, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      self._qtObject      = None       # primary Qt object
      self._qtComponents  = {}         # dictionary of Qt objects (for groups)
      self._zValue        = None       # Qt z-order - not the same as CreativePython z-order!
      self.cornerX     = 0          # top-left corner of bounding box
      self.cornerY     = 0          # top-left corner of bounding box
      self.anchorX     = 0          # x coordinate of rotation anchor (relative to cornerX)
      self.anchorY     = 0          # y coordinate of rotation anchor (relative to cornerY)
      self.width       = 0          # width of bounding box
      self.height      = 0          # height of bounding box
      self.color       = color      # current color
      self.fill        = fill       # is the shape filled?
      self.thickness   = thickness  # current outline width
      self.rotation    = rotation   # rotation angle (in degrees, increasing clockwise)
      self.display     = None       # the display this object is on, if any
      self.group       = None       # the group this object is in, if any
      self.toolTipText = None       # the tooltip text for this object, if any

   def __str__( self ):
      return f'Drawable(color = {self.getColor()}, fill = {self.fill}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'

   def __repr__( self ):
      return str(self)


   def getPosition(self):
      """
      Returns the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      return self.cornerX, self.cornerY


   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      # do some basic error checking
      if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
         raise TypeError(f'Drawable.setPosition(): x and y must be numbers (they were {type(x)} and {type(y)})')

      # only update if x or y are different
      if x != self.cornerX or y != self.cornerY:
         # store internal values
         self.cornerX = x
         self.cornerY = y

         if self.group is not None:  # when part of a group, coordinates are relative to the group
            x = self.cornerX - self.group.cornerX
            y = self.cornerY - self.group.cornerY

         # update Qt object
         qtObject = self._qtObject  # get the Qt object

         # how we set the position depends on qtObject's type
         if isinstance(qtObject, _QtWidgets.QGraphicsItem):
            qtObject.setPos(x, y)  # move graphics object
         elif isinstance(qtObject, _QtWidgets.QWidget):
            qtObject.move(x, y)    # move widget
         else:
            print(f'Warning: setPosition() not implemented for {type(qtObject)}')


   def getX(self):
      """
      Returns the shape's x coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      return self.getPosition()[0]


   def setX(self, x):
      """
      Sets the shape's x coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      self.setPosition(x, self.cornerY)


   def getY(self):
      """
      Returns the shape's y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      return self.getPosition()[1]


   def setY(self, y):
      """
      Sets the shape's y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      self.setPosition(self.cornerX, y)


   def getWidth(self):
      """
      Returns the width of the shape's bounding box.
      """
      return self.width


   def getHeight(self):
      """
      Returns the height of the shape's bounding box.
      """
      return self.height


   def getColor(self):
      """
      Returns the shape's current color.
      """
      return self.color


   def setColor(self, color):
      """
      Changes the shape's color to the specified color.
      If color parameter is omitted, a color selection dialog box will be presented.  TODO: add color selection box
      """
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'Drawable.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         qtObject   = self._qtObject                     # get the Qt object
         self.color = color                              # store internal value

         qtColor = _QtGui.QColor(rB, gB, bB, aB)         # build new Qt color
         qtPen   = _QtGui.QPen(qtColor, self.thickness)  # build outline pen
         qtObject.setPen(qtPen)                          # apply pen

         if self.fill:
            qtBrush = _QtGui.QBrush(qtColor)             # build fill brush
            qtObject.setBrush(qtBrush)                   # apply fill


   def getThickness(self):
      """
      Returns the shape outline's current thickness.
      """
      return self.thickness


   def setThickness(self, thickness):
      """
      Changes the shape outline's thickness to the specified value.
      """
      # do some basic error checking
      if not isinstance(thickness, (int, float)):
         raise TypeError(f'Drawable.setThickness(): thickness must be a number (it was {type(thickness)})')

      # onlu update if thickness is different:
      if self.thickness != thickness:
         qtObject       = self._qtObject            # get the Qt object
         self.thickness = thickness                 # store internal value
         r, g, b, a     = self.color.getRGBA()      # extract color values

         qtColor = _QtGui.QColor(r, g, b, a)        # build Qt color
         qtPen   = _QtGui.QPen(qtColor, thickness)  # build outline pen
         qtObject.setPen(qtPen)                     # apply pen


   def getRotation(self):
      """
      Returns the shape's current rotation angle in degrees.
      """
      return self.rotation


   def setRotation(self, rotation, anchorX=None, anchorY=None):
      """
      Sets the shape's rotation angle in degrees.
      Rotation increases clockwise, with 0 degrees being the default orientation.
      Objects rotate around their x, y position (top-left corner, or center for circular shapes).
      """
      # do some basic error checking
      if not isinstance(rotation, (int, float)):
         raise TypeError(f'Drawable.setRotation(): rotation must be a number (it was {type(rotation)})')

      # only update if rotation or anchor has changed
      newRotation = (rotation != self.rotation)
      newAnchorX  = (anchorX  != self.anchorX)
      newAnchorY  = (anchorY  != self.anchorY)

      if newRotation or newAnchorX or newAnchorY:
         # store internal values
         self.rotation = rotation

         if anchorX is not None:
            self.anchorX = anchorX  # store x anchor, if provided
         else:
            anchorX = self.anchorX  # extract x anchor, otherwise

         if anchorY is not None:
            self.anchorY = anchorY  # store y anchor, if provided
         else:
            anchorY = self.anchorY  # extract y anchor, otherwise


         if self.group is not None:  # when part of a group, coordinates are relative to the group
            rotation = rotation - self.group.rotation
            anchorX  = anchorX  - self.group.cornerX
            anchorY  = anchorY  - self.group.cornerY

         # update Qt object
         qtObject = self._qtObject  # get the Qt object

         qtObject.setTransformOriginPoint(anchorX, anchorY)
         qtObject.setRotation(rotation)  # set rotation of Qt object


   def rotate(self, angle, anchorX=None, anchorY=None):
      """
      Rotates the shape by the given angle in degrees.
      """
      self.setRotation(self.rotation + angle, anchorX, anchorY)


   def encloses(self, other):
      """
      Returns True if this shape encloses the other shape.
      """

      if not isinstance(other, Drawable):
         TypeError(f'Drawable.encloses(): other must be a Drawable object (it was {type(other)})')

      qtA = self._qtObject
      qtB = other._qtObject
      encloses = None

      # check conditions for optimizing calculations
      bothGraphics = isinstance(qtA, _QtWidgets.QGraphicsItem) and isinstance(qtB, _QtWidgets.QGraphicsItem)
      sameDisplay  = (self.display == other.display)

      if bothGraphics and sameDisplay:
         # use Qt's spatial hit test
         pathA = qtA.mapToScene(qtA.shape())
         pathB = qtB.mapToScene(qtB.shape())
         encloses = pathA.contains(pathB)

      else:
         # fallback to bounding box calculation
         x1 = self.cornerX
         y1 = self.cornerX
         x2 = x1 + self.width
         y2 = y1 + self.height

         otherX1 = other.cornerX
         otherY1 = other.cornerY
         otherX2 = otherX1 + other.width
         otherY2 = otherY1 + other.height

         xEnclosed = (x1 <= otherX1 <= x2 and x1 <= otherX2 <= x2)
         yEnclosed = (y1 <= otherY1 <= y2 and y1 <= otherY2 <= y2)

         encloses = xEnclosed and yEnclosed

      return encloses


   def intersects(self, other):
      """
      Returns True if this shape intersects the other shape.
      """
      if not isinstance(other, Drawable):
         TypeError(f'Drawable.intersects(): other must be a Drawable object (it was {type(other)})')

      qtA = self._qtObject
      qtB = other._qtObject
      intersects = None

      # check conditions for optimizing calculations
      bothGraphics = isinstance(qtA, _QtWidgets.QGraphicsItem) and isinstance(qtB, _QtWidgets.QGraphicsItem)
      sameDisplay  = (self.display == other.display)

      if bothGraphics and sameDisplay:
         # use Qt's spatial hit test
         pathA = qtA.mapToScene(qtA.shape())
         pathB = qtB.mapToScene(qtB.shape())
         intersects = pathA.intersects(pathB)

      else:
         # fallback to bounding box calculation
         x1 = self.cornerX
         y1 = self.cornerY
         x2 = x1 + self.width
         y2 = y1 + self.height

         otherX1 = other.cornerX
         otherY1 = other.cornerY
         otherX2 = otherX1 + other.width
         otherY2 = otherY1 + other.height

         xIntersecting = (x1 <= otherX1 <= x2 or
                        x1 <= otherX2 <= x2 or
                     otherX1 <= x1      <= otherX2)

         yIntersecting = (y1 <= otherY1 <= y2 or
                        y1 <= otherY2 <= y2 or
                     otherY1 <= y1      <= otherY2)

         intersects = xIntersecting and yIntersecting

      return intersects


   def contains(self, x, y):
      """Check if a point is in the shape's bounding box."""
      # do some basic error checking
      if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
         raise TypeError(f'Drawable.contains(): x and y must be numbers (they were {type(x)} and {type(y)})')

      qtObject = self._qtObject
      scene    = qtObject.scene()
      contains = None

      if isinstance(qtObject, _QtWidgets.QGraphicsItem) and scene is not None:
         # use Qt's spatial hit test
         targetPoint = _QtCore.QPointF(x, y)
         targetPos   = qtObject.mapFromScene(targetPoint)
         contains = qtObject.contains(targetPos)

      else:
         # fallback to bounding box calculation
         x1 = self.cornerX
         y1 = self.cornerY
         x2 = x1 + self.width
         y2 = y1 + self.height

         xContains = (x1 <= x <= x2)
         yContains = (y1 <= y <= y2)
         contains = xContains and yContains

      return contains


   def getOrder(self):
      """
      Get the shape's z-order in its display or group (0=front).
      """
      order = None

      if self.display is not None:
         # get the z-order of this object in the display
         order = self.display.getOrder(self)
      elif self.group is not None:
         # get the z-order of this object in its group
         order = self.group.getOrder(self)

      return order


   def setOrder(self, order):
      """
      Set the shape's z-order in its display or group (0=front).
      """
      if self.display is not None:
         # set the z-order of this object in the display
         self.display.setOrder(self, order)
      elif self.group is not None:
         # set the z-order of this object in its group
         self.group.setOrder(self, order)


   def _getZValue(self):
      """
      Get the shape's internal Qt z-order.
      This isn't the same as Drawable.getOrder()!
      """
      return self._zValue


   def _setZValue(self, order):
      """
      Set the shape's internal Qt z-order.
      This isn't the same as Drawable.setOrder()!
      """
      self._zValue = order

      if isinstance(self._qtObject, _QtWidgets.QGraphicsItem):
         # only QGraphicsItems actually have z-order
         self._qtObject.setZValue(order)


   def setToolTipText(self, text):
      """
      Set the tooltip text for this shape.
      If text is None, the tooltip is removed.
      """
      # store internal value
      self.toolTipText = text

      # update Qt object
      qtObject = self._qtObject              # get the Qt object
      qtObject.setToolTip(self.toolTipText)  # set tooltip text


#######################################################################################
# Display
#######################################################################################
class Display(Interactable):

   def __init__(self, title="", width=600, height=400, x=0, y=50, color=Color.WHITE):
      _ensureApp()            # make sure Qt is running
      _DISPLAYS_.append(self)  # add to global display list

      # store window attributes
      self.title   = title
      self.width   = width
      self.height  = height
      self.x       = x
      self.y       = y
      self.color   = color

      # initialize internal attributes
      self.items = []               # list of items in this display (front=top)
      self.toolTipText     = None   # tooltip text for this display
      self.showCoordinates = False  # show mouse coordinates in tooltip?
      self.hoverItem       = None   # item under mouse cursor
      self.focusItem       = None   # item with focus (i.e., the last item clicked)
      self.lastMouseDown   = None   # last mouse down position (i.e. the last place the mouse was clicked)
      self.lastMousePos    = None   # last mouse position  (i.e. the last place the mouse was moved)
      self.moveThreshold   = 5      # threshold for mouse click distance (in pixels)

      # Qt zorder is opposite of CreativePython's - 
      #   We expect index 0 to be the front, while Qt expects 0 to be the back.
      #   To help manage this, we keep a floating count of zorders.
      #   Whenever an object is inserted at zorder 0,
      #      the zcount increases by 1.0 and object is inserted at that order in Qt.
      #   Whenever an object is inserted deeper,
      #      the zcount doesn't change, and object is inserted slightly under its closest neighbor.
      #   This prevents us from having to regularly update zorders, though 
      self._zCount = 0.0     # float count for object zorder
      self._zDiff  = 0.0001  # how much is "slightly" under - smaller value = more insertions at same deeper zorder

      # initialize event methods
      Interactable.__init__(self)
      self._onClose     = None
      self._onPopupMenu = None

      window = _QtWidgets.QMainWindow()        # create window
      window.setWindowTitle(title)             # set window title
      window.setGeometry(x, y, width, height)  # set window position and size
      window.setFixedSize(width, height)       # prevent resizing
      window.setContextMenuPolicy( _QtCore.Qt.ContextMenuPolicy.CustomContextMenu)                       # disable default right-click menu
      window.show()


      # Display uses an OpenGLWidget to render 2D graphics.
      #   This moves graphics processing to the graphics card, drastically improving performance.
      # Note that only graphics items are rendered this way,
      #   Widgets (such as dropbown boxes and text fields) are still rendered on the CPU

      # First, we need to set some rendering settings.
      antiAliasing   = 4  # MSAA anti-aliasing
      swapBehavior   = _QtGui.QSurfaceFormat.SwapBehavior.DoubleBuffer
      renderableType = _QtGui.QSurfaceFormat.RenderableType.OpenGL
      openGLProfile  = _QtGui.QSurfaceFormat.OpenGLContextProfile.CoreProfile

      # assemble these settings into a QSurfaceFormat
      format = _QtGui.QSurfaceFormat()
      format.setSamples(antiAliasing)
      format.setSwapBehavior(swapBehavior)
      format.setRenderableType(renderableType)
      format.setProfile(openGLProfile)
      _QtGui.QSurfaceFormat.setDefaultFormat(format)  # and set it

      # Next, we need to create the rendering objects
      # - scene is the canvas for Drawables
      # - view renders scene to the display window
      scene  = _QtWidgets.QGraphicsScene(0, 0, width, height)  # create canvas
      view   = _QtWidgets.QGraphicsView(scene)                 # attach canvas to view
      openGL = _QtOpenGL.QOpenGLWidget()                       # create hardware accel widget
      view.setViewport(openGL)                                 # attach hardware accel to view
      # updateMode = _QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
      # updateMode = _QtWidgets.QGraphicsView.ViewportUpdateMode.BoundingRectViewportUpdate
      updateMode = _QtWidgets.QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate
      view.setViewportUpdateMode(updateMode)                   # clear viewport on refresh
      window.setCentralWidget(view)                            # attach view to window

      # Last, we need to set some view and scene properties
      sceneIndex     = _QtWidgets.QGraphicsScene.ItemIndexMethod.NoIndex  # don't update internal index tree
      hoverTracking  = _QtCore.Qt.WidgetAttribute.WA_Hover            # track static mouse location
      mouseTracking  = _QtCore.Qt.WidgetAttribute.WA_MouseTracking    # track dynamic mouse location
      scrollPolicy   = _QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff  # disable scroll bars
      shapeAntiAlias = _QtGui.QPainter.RenderHint.Antialiasing       # smooth shapes
      pixmapSmooth   = _QtGui.QPainter.RenderHint.SmoothPixmapTransform  # smooth images
      textAntiAlias  = _QtGui.QPainter.RenderHint.TextAntialiasing    # smooth text rendering

      scene.setItemIndexMethod(sceneIndex)
      view.setAttribute(hoverTracking, True)
      view.setAttribute(mouseTracking, True)
      view.setHorizontalScrollBarPolicy(scrollPolicy)
      view.setVerticalScrollBarPolicy(scrollPolicy)
      view.setRenderHint(shapeAntiAlias, False)  # use OpenGL AA
      view.setRenderHint(pixmapSmooth, False)    # use OpenGL AA
      view.setRenderHint(textAntiAlias, True)


      # remember window, scene and view objects
      self._window = window
      self._scene  = scene
      self._view   = view

      # create event dispatcher
      self._eventDispatcher = EventDispatcher(self)
      self.setColor(color)  # set display background color


   def __str__( self ):
      return f'Display(title = "{self.getTitle()}", width = {self.getWidth()}, height = {self.getHeight()}, x = {self.getPosition()[0]}, y = {self.getPosition()[1]}, color = {self.getColor()})'


   def show(self):
      """Reveal the display."""
      self._window.show()


   def hide(self):
      """Hide the display."""
      self._window.hide()


   def place(self, object, x=None, y=None, order=0):
      """
      Place an object in the display, at coordinates by x and y.
      If the object already appears on another display it is removed from there, first.
      """
      # do some basic error checking
      if not isinstance(object, Drawable):
         raise TypeError(f'Display.place(): object must be a Drawable object (it was {type(object)})')

      if x is not None:
         if not isinstance(x, (int, float)):
            raise TypeError(f'Display.place(): x must be a None or a number (it was {type(x)})')
      else:  # if x is None, use object's x coordinate
         x = object.getX()

      if y is not None:
         if not isinstance(y, (int, float)):
            raise TypeError(f'Display.place(): y must be a None or a number (it was {type(y)})')
      else:  # if y is None, use object's y coordinate
         y = object.getY()


      # remove object from any other display
      if object.display is not None:
         object.display.remove(object)

      object.display = self  # tell object it is on this display

      # set object's position
      object.setPosition(x, y)

      # set object's z order
      self._insertAtZOrder(object, order)

      # add object to this display
      if isinstance(object._qtObject, _QtWidgets.QGraphicsItem):
         # cacheMode = _QtWidgets.QGraphicsItem.CacheMode.ItemCoordinateCache
         cacheMode = _QtWidgets.QGraphicsItem.CacheMode.DeviceCoordinateCache
         self._scene.addItem(object._qtObject)     # add graphics object
         object._qtObject.setCacheMode(cacheMode)  # set graphics caching strategy

      elif isinstance(object._qtObject, _QtWidgets.QWidget):
         object._qtObject.setParent(self._window)  # add widget object
         object._qtObject.show()                   # make sure widget is visible

      self._eventDispatcher.add(object)  # register any callbacks on the object


   def add(self, object, x=None, y=None):
      """
      Same as place(), i.e., places an object in the display, at coordinates by x and y.
      If the object already appears on another display it is removed from there, first.
      """
      self.place(object, x, y)


   def move(self, object, x, y):
      """
      Moves an object to the specified (x, y) coordinates.
      """
      # do some basic error checking
      if not isinstance(object, Drawable):
         raise TypeError(f'Display.move(): object must be a Drawable object (it was {type(object)})')

      if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
         raise TypeError(f'Display.move(): x and y must be numbers (they were {type(x)}, {type(y)})')

      object.setPosition(x, y)  # set object's position


   def remove(self, object):
      """
      Removes an object from the display.
      """
      # do some basic error checking
      if not isinstance(object, Drawable):
         raise TypeError(f'Display.remove(): object must be a Drawable object (it was {type(object)})')

      # only update if object is on display
      if object in self.items:
         # remove object from display
         if isinstance(object._qtObject, _QtWidgets.QGraphicsItem):
            self._scene.removeItem(object._qtObject)  # remove graphics object
         elif isinstance(object._qtObject, _QtWidgets.QWidget):
            object._qtObject.setParent(None)          # remove widget object
            object._qtObject.hide()                   # hide widget

         self.items.remove(object)  # remove object from display's list of items
         object.display = None      # tell object it is no longer on a display

         self._eventDispatcher.remove(object)  # unregister object's event callbacks


   def removeAll(self):
      """
      Removes all objects from the display.
      """
      self.view.setUpdatesEnabled(False)  # pause Display repainting
      for item in self.items:
         self.remove(item)
      self.view.setUpdatesEnabled(True)   # resume Display repainting
      self.view.viewport().update()       # repaint immediately


   def addOrder(self, object, order, x, y):
      """
      Adds an object to the display at the specified order and coordinates.
      """
      self.place(object, x, y, order)


   def setOrder(self, object, order):
      """
      Sets the z-order of the specified object in this display.
      """
      # do some basic error checking
      if not isinstance(order, (int, float)):
         raise TypeError(f'Display.setOrder(): order must be a number (it was {type(order)})')

      if object in self.items:
         self._insertAtZOrder(order, object)  # update object's new zorder


   def getOrder(self, object):
      """
      Returns the z-order of the specified object in this display.
      """
      order = None

      if object in self.items:  # index in items corresponds to z-order
         order = self.items.index(object)

      return order


   def _insertAtZOrder(self, object, order):
      """
      Inserts a Drawable object at the given z-order.
      """
      order = max(0, min(len(self.items), order))  # clamp order to possible indices

      if object in self.items:          # if already on Display,
         self.items.remove(object)      # remove it from items first

      self.items.insert(order, object)  # insert object into display list at new order

      # now, we need to figure out object's z-order in Qt
      if order == 0:                        # inserting on top...
         self._zCount = self._zCount + 1.0  # increment zCount
         object._setZValue(self._zCount)    # set Qt z-order to top

      elif order >= len(self.items) - 1:    # inserting on bottom...
         neighborZ = 0.0
         if len(self.items) > 1:            # find bottommost object, not including this one
            neighborZ = self.items[-2]._getZValue() - 1.0  # insert 1.0 underneath it
         object._setZValue(neighborZ)

      else:                                 # inserting somewhere in middle...
         frontNeighbor = self.items[order - 1]       # find front neighbor
         backNeighbor  = self.items[order + 1]       # find back neighbor
         zFront        = frontNeighbor._getZValue()  # find their Qt z-orders
         zBack         = backNeighbor._getZValue()
         zMiddle       = (zFront + zBack) / 2.0      # find the average
         object._setZValue(zMiddle)                  # set this object there


   def setToolTipText(self, text=None):
      """
      Sets the tooltip text for this display.
      If text is None, the tooltip is removed.
      """
      # store internal attribute
      self.toolTipText = text

      # update Qt object
      # hideMouseCoordinates does this, and also restores item tooltips if needed
      # To avoid duplicating code, we just call it instead
      self.hideMouseCoordinates()


   def setColor(self, color):
      """
      Sets the background color of the display.
      """
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'Display.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # store internal attribute
         self.color = color  # store color

         # update Qt object
         r, g, b, a = color.getRGBA()  # get color values
         brush = _QtGui.QBrush(_QtGui.QColor(r, g, b, a))
         self._scene.setBackgroundBrush(brush)


   def getColor(self):
      """
      Returns the background color of the display.
      """
      return self.color


   def setTitle(self, title):
      """
      Sets the title of the display.
      """
      # store internal value
      self.title = str(title)

      # update Qt object
      self._window.setWindowTitle(self.title)


   def getTitle(self):
      """
      Returns the title of the display.
      """
      return self.title


   def setSize(self, width, height):
      """
      Sets the size of the display.
      """
      # do some basic error checking
      if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
         raise TypeError(f'Display.setSize(): width and height must be numbers (they were {type(width)}, {type(height)})')

      # store internal values
      self.width  = int(width)
      self.height = int(height)

      # grab window position
      pos = self._window.pos()

      # update Qt object
      self._scene.setSceneRect(0, 0, self.width, self.height)  # adjust scene canvas size
      self._window.setFixedSize(self.width, self.height)       # adjust window size
      self._window.move(pos)                                   # ensure window doesn't move


   def getHeight(self):
      """
      Returns the height of the display.
      """
      return self.height


   def getWidth(self):
      """
      Returns the width of the display.
      """
      return self.width


   def setPosition(self, x, y):
      """
      Sets the position of the display on the screen.
      """
      # do some basic error checking
      if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
         raise TypeError(f'Display.setPosition(): x and y must be numbers (they were {type(x)}, {type(y)})')

      thisX, thisY = self.getPosition()

      # only update if x and y are different
      if (x != thisX) or (y != thisY):
         # store internal values
         self.x = int(x)
         self.y = int(y)

         # update Qt object
         self._window.setGeometry(self.x, self.y, self.width, self.height)


   def getPosition(self):
      """
      Returns the position of the display on the screen.
      """
      # displays can move around, so we need to get the current position
      # from Qt instead of using the stored value

      self.x = self._window.x()  # get x position
      self.y = self._window.y()  # get y position
      return self.x, self.y


   def getItems(self):
      """
      Returns a deep copy of the list of items in the display.
      """
      # TODO: test this.  I suspect the items in the list may keep
      # references to the current display...
      return deepcopy(self.items)


   def showMouseCoordinates(self):
      """
      Shows the mouse coordinates in the display's tooltip.
      """
      self.showCoordinates = True  # set flag to show coordinates
      self._view.setToolTip(None)  # remove any existing tooltip

      # suppress item tooltips
      for item in self.items:
         item._qtObject.setToolTip(None)


   def hideMouseCoordinates(self):
      """
      Hides the mouse coordinates in the display's tooltip.
      """
      self.showCoordinates = False        # set flag to hide coordinates
      self._view.setToolTip(self.toolTipText)  # restore display tooltip

      # restore item tooltips
      for item in self.items:
         item._qtObject.setToolTip(item.toolTipText)


   def close(self):
      """
      Closes the display.
      """

      if 'onClose' in self._callbackFunctions:
         # call callback function, if defined
         callback = self._callbackFunctions['onClose']
         if callable(callback):
            callback()

      self._window.close()     # close window
      self.removeAll()         # remove all objects from display
      _DISPLAYS_.remove(self)  # remove from global display list


   def addMenu(self, menu):
      """Adds a menu to the display's taskbar."""
      # do some basic error checking
      if not isinstance(menu, Menu):
         TypeError(f'Display.addMenu(): menu must be a Menu object (it was {type(menu)})')

      menuBar = self._window.menuBar()  # get this display's menuBar (or create one, if needed)
      menuBar.addMenu(menu._qtObject)   # add Qt menu to display's menu bar


   def addPopupMenu(self, menu):
      """Adds a context menu (right-click) to the display."""
      if not isinstance(menu, Menu):
         raise TypeError(f'Display.addPopupMenu(): menu must be a Menu object (it was {type(menu)})')

      # attach popup menu callback - this tells popup menu where to appear
      self._onPopupMenu = lambda pos: menu._qtObject.exec(self._window.mapToGlobal(pos))  # set callback
      self._window.customContextMenuRequested.connect(self._onPopupMenu)  # connect to event signal


   def onClose(self, function):
      """
      Set callback for when the display is closed.
      """
      self._callbackFunctions['onClose'] = function


   # drawing functions (for convenience)
   def drawLine(self, x1, y1, x2, y2, color=Color.BLACK, thickness=1):
      """
      Draw a line between the points (x1, y1) and (x2, y2) with given color and thickness.

      Returns the line object (in case we want to move it or delete it later).
      """
      line = Line(x1, y1, x2, y2, color, thickness)   # create line
      self.add(line)                                  # add it
      return line                                     # and return it

   def drawCircle(self, x, y, radius, color = Color.BLACK, fill = False, thickness=1):
      """
      Draw a circle at (x, y) with the given radius, color, fill, and thickness.

      Returns the circle object (in case we want to move it or delete it later).
      """
      circle = Circle(x, y, radius, color, fill, thickness)   # create circle
      self.add(circle)   # add it
      return circle      # and return it

   def drawPoint(self, x, y, color = Color.BLACK, thickness=1):
      """
      Draw a point at (x, y) with the given color and thickness.

      Returns the point object (in case we want to move it or delete it later).
      """
      point = Point(x, y, color, thickness)   # create point
      self.add(point)   # add it
      return point      # and return it

   def drawOval(self, x1, y1, x2, y2, color = Color.BLACK, fill = False, thickness = 1):
      """
      Draw an oval using the coordinates of its enclosing rectangle with the given color,
      fill, and thickness.

      Returns the oval object (in case we want to move it or delete it later).
      """
      oval = Oval(x1, y1, x2, y2, color, fill, thickness)   # create oval
      self.add(oval)   # add it
      return oval      # and return it

   def drawArc(self, x1, y1, x2, y2, startAngle, endAngle, color = Color.BLACK, fill = False, thickness = 1):
      """
      Draw an arc using the provided coordinates, arc angles, color, fill, and thickness.

      Returns the arc object (in case we want to move it or delete it later).
      """
      arc = Arc(x1, y1, x2, y2, startAngle, endAngle, color, fill, thickness)   # create arc
      self.add(arc)   # add it
      return arc      # and return it

   def drawRectangle(self, x1, y1, x2, y2, color = Color.BLACK, fill = False, thickness = 1):
      """
      Draw a rectangle using the provided coordinates, color, fill, and thickness.

      Returns the rectangle object (in case we want to move it or delete it later).
      """
      rec = Rectangle(x1, y1, x2, y2, color, fill, thickness)   # create rectangle
      self.add(rec)   # add it
      return rec      # and return it

   def drawPolygon(self, xPoints, yPoints, color = Color.BLACK, fill = False, thickness = 1):
      """
      Draw a polygon using the provided coordinates, color, fill, and thickness.

      Returns the polygon object (in case we want to move it or delete it later).
      """
      poly = Polygon(xPoints, yPoints, color, fill, thickness)   # create polygon
      self.add(poly)   # add it
      return poly      # and return it

   def drawIcon(self, filename, x, y, width = None, height = None):
      """
      Draw an icon (image) from the provided external file (.jpg or .png) at the given coordinates (top-left).
      Also rescale according to provided width and height (if any).

      Returns the icon object (in case we want to move it or delete it later).
      """
      icon = Icon(filename, width, height)   # load image (and rescale, if specified)
      self.add(icon, x, y)   # add it at given coordinates
      return icon            # and return it

   def drawImage(self, filename, x, y, width = None, height = None):
      """
      Same as drawIcon().

      Returns the image object (in case we want to move it or delete it later).
      """
      return self.drawIcon(filename, x, y, width, height)

   def drawLabel(self, text, x, y, color = Color.BLACK, font = None):
      """
      Draw the text label on the display at the given coordinates (top-left) and with the provided
      color and font.

      Returns the label object (in case we want to move it or delete it later).
      """

      # Font example - Font("Serif", Font.ITALIC, 16)
      #
      # see http://docs.oracle.com/javase/tutorial/2d/text/fonts.html#logical-fonts

      label = Label(text, LEFT, color)   # create label
      if font:                     # did they provide a font?
         label.setFont(font)          # yes, so set it
      self.add(label, x, y)        # add it at given coordinates
      return label                 # and return it

   def drawText(self, text, x, y, color = Color.BLACK, font = None):
      """
      Same as drawLabel().

      Returns the label object (in case we want to move it or delete it later).
      """
      return self.drawLabel(text, x, y, color, font)


#######################################################################################
# Graphics (Geometric shapes, text, and images)
#######################################################################################

class Oval(Drawable, Interactable):

   def __init__(self, x1, y1, x2, y2, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new oval."""
      Drawable.__init__(self, color, fill, thickness, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.cornerX = min(x1, x2)   # top-left corner of bounding box
      self.cornerY = min(y1, y2)   # top-left corner of bounding box
      self.width   = abs(x1 - x2)  # width of bounding box
      self.height  = abs(y1 - y2)  # height of bounding box

      # create Qt object
      self._qtObject = _QtWidgets.QGraphicsEllipseItem(0, 0, self.width, self.height)

      self.setPosition(self.cornerX, self.cornerY)  # set position
      self.setColor(color)        # set color (this also sets fill and thickness)
      self.setRotation(rotation)  # set rotation angle


   def __str__(self):
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      return f'Oval(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, color = {self.getColor()}, fill = {self.fill}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Circle(Oval):

   def __init__(self, x, y, radius, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new circle."""

      # store internal attributes
      self.centerX = x
      self.centerY = y
      self.radius  = radius

      # call parent constructor
      x1 = x - radius
      y1 = y - radius
      x2 = x + radius
      y2 = y + radius
      Oval.__init__(self, x1, y1, x2, y2, color, fill, thickness, rotation)
      self.setPosition(x, y)  # set position

   def __str__(self):
      return f'Circle(x = {self.getX()}, y = {self.getY()}, radius = {self.radius}, color = {self.getColor()}, fill = {self.fill}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


   def getPosition(self):
      """
      Returns the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      return self.centerX, self.centerY


   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      # do some basic error checking
      if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
         raise TypeError(f'Circle.setPosition(): x and y must be numbers (they were {type(x)}, {type(y)})')

      # only update if x and y are different
      if (x != self.centerX) or (y != self.centerY):
         # update internal attributes
         self.centerX = x
         self.centerY = y
         self.cornerX = x - self.radius  # top-left corner of bounding box
         self.cornerY = y - self.radius

         if self.group is not None:  # when part of a group
            # coordinates are relative to the group
            relativeCornerX = self.cornerX - self.group.cornerX
            relativeCornerY = self.cornerY - self.group.cornerY

            # update Qt object
            self._qtObject.setPos(relativeCornerX, relativeCornerY)

         else:   # not part of a group
            # update Qt object
            self._qtObject.setPos(self.cornerX, self.cornerY)


class Point(Circle):

   def __init__(self, x, y, color=Color.BLACK):
      """Create a new Point."""
      # call parent constructor
      Circle.__init__(self, x, y, 1, color, True, 0)

   def __str__(self):
      return f'Point(x = {self.getX()}, y = {self.getY()}, color = {self.getColor()})'


# Arc Constants (in degrees)
PI      = 180
HALF_PI = 90
TWO_PI  = 360

PIE   = 0
OPEN  = 1
CHORD = 2

class Arc(Drawable, Interactable):

   def __init__(self, x1, y1, x2, y2, startAngle=PI, endAngle=TWO_PI, style=OPEN, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Arc."""
      Drawable.__init__(self, color, fill, thickness, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.cornerX = min(x1, x2)    # top-left corner of bounding box
      self.cornerY = min(y1, y2)    # top-left corner of bounding box
      self.width   = abs(x1 - x2)   # width of bounding box
      self.height  = abs(y1 - y2)   # height of bounding box

      self.startAngle = startAngle  # starting angle (in degrees)
      self.endAngle   = endAngle    # ending angle (in degrees)
      self.style      = style       # style (PIE, OPEN, CHORD)

      # create Qt object
      arcWidth = -(endAngle - startAngle)  # Qt angles increase clockwise, so negate
      path = _QtGui.QPainterPath()  # create new path
      path.arcMoveTo(0, 0, self.width, self.height, startAngle)  # move to start angle
      path.arcTo(0, 0, self.width, self.height, startAngle, arcWidth)  # create arc

      if style == PIE:
         centerX = self.width  // 2
         centerY = self.height // 2
         path.lineTo(centerX, centerY)  # connect arc to center
         path.closeSubpath()            # return to start point

      elif style == CHORD:
         path.closeSubpath()            # return to start point

      elif style == OPEN:
         pass  # leave open

      self._qtObject = _QtWidgets.QGraphicsPathItem(path)  # create path object

      self.setPosition(self.cornerX, self.cornerY)  # set position
      self.setColor(color)              # set color (this also sets fill and thickness)
      self.setRotation(rotation)        # set rotation angle

   def __str__(self):
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      return f'Arc(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, startAngle = {self.startAngle}, endAngle = {self.endAngle}, style = {self.style}, color = {self.getColor()}, fill = {self.fill}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class ArcCircle(Arc):

   def __init__(self, x, y, radius, startAngle=PI, endAngle=TWO_PI, style=OPEN, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Circle."""

      # store internal attributes
      self.centerX = x
      self.centerY = y
      self.radius  = radius

      # call parent constructor
      x1 = x - radius
      y1 = y - radius
      x2 = x + radius
      y2 = y + radius
      Arc.__init__(self, x1, y1, x2, y2, startAngle, endAngle, style, color, fill, thickness, rotation)

   def __str__(self):
      return f'ArcCircle(x = {self.getX()}, y = {self.getY()}, radius = {self.radius}, startAngle = {self.startAngle}, endAngle = {self.endAngle}, style = {self.style}, color = {self.getColor()}, fill = {self.fill}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


   def getPosition(self):
      """
      Returns the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      return self.centerX, self.centerY


   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """

      # only update if x and y are different
      if (x != self.centerX) or (y != self.centerY):
         # update internal attributes
         self.centerX = x
         self.centerY = y
         self.cornerX = x - self.radius  # top-left corner of bounding box
         self.cornerY = y - self.radius

         if self.group is not None:  # when part of a group, coordinates are relative to the group
            x = self.cornerX - self.group.cornerX
            y = self.cornerY - self.group.cornerY

         # update Qt object
         self._qtObject.setPos(x, y)



class PolyLine(Drawable, Interactable):

   def __init__(self, xPoints, yPoints, color=Color.BLACK, thickness=1, rotation=0):
      """Create a new Polyline."""
      Drawable.__init__(self, color, False, thickness, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.cornerX = min(xPoints)                 # top-left corner of bounding box
      self.cornerY = min(yPoints)                 # top-left corner of bounding box
      self.width   = max(xPoints) - self.cornerX  # width of bounding box
      self.height  = max(yPoints) - self.cornerY  # height of bounding box

      self.xPoints = xPoints  # store coordinates
      self.yPoints = yPoints

      # create Qt object
      path = _QtGui.QPainterPath()

      x = self.xPoints[0] - self.cornerX  # get first point, relative to bounding box
      y = self.yPoints[0] - self.cornerY
      path.moveTo(x, y)                   # move to first point
      for i in range(1, len(self.xPoints)):
         x = self.xPoints[i] - self.cornerX  # get next point, relative to bounding box
         y = self.yPoints[i] - self.cornerY
         path.lineTo(x, y)                   # draw line to next point

      self._qtObject = _QtWidgets.QGraphicsPathItem(path)  # store path object

      self.setPosition(self.cornerX, self.cornerY)  # set position
      self.setColor(color)        # set color (this also sets fill and thickness)
      self.setRotation(rotation)  # set rotation angle


   def __str__(self):
      # find distance between current position and original position
      dx = self.cornerX - min(self.xPoints)
      dy = self.cornerY - min(self.yPoints)

      # create new list of points, relative to current position
      xPoints = [x + dx for x in self.xPoints]
      yPoints = [y + dy for y in self.yPoints]

      return f'PolyLine(xPoints = {xPoints}, yPoints = {yPoints}, color = {self.getColor()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Line(PolyLine):

   def __init__(self, x1, y1, x2, y2, color=Color.BLACK, thickness=1, rotation=0):
      """Create a new Line."""

      # call parent constructor
      xPoints = [x1, x2]
      yPoints = [y1, y2]
      PolyLine.__init__(self, xPoints, yPoints, color, thickness, rotation)

   def __str__(self):
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height

      return f'Line(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, color = {self.getColor()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Polygon(Drawable, Interactable):

   def __init__(self, xPoints, yPoints, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Polygon."""
      Drawable.__init__(self, color, fill, thickness, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.cornerX = min(xPoints)                 # top-left corner of bounding box
      self.cornerY = min(yPoints)                 # top-left corner of bounding box
      self.width   = max(xPoints) - self.cornerX  # width of bounding box
      self.height  = max(yPoints) - self.cornerY  # height of bounding box

      self.xPoints = xPoints  # store coordinates
      self.yPoints = yPoints

      # create Qt object
      polygon = _QtGui.QPolygonF()              # create new polygon
      for i in range(len(self.xPoints)):
         x = self.xPoints[i] - self.cornerX     # get point, relative to bounding box
         y = self.yPoints[i] - self.cornerY
         polygon.append(_QtCore.QPointF(x, y))  # add point to polygon

      self._qtObject = _QtWidgets.QGraphicsPolygonItem(polygon)  # create Qt object

      self.setPosition(self.cornerX, self.cornerY)  # set position
      self.setColor(color)        # set color (this also sets fill and thickness)
      self.setRotation(rotation)  # set rotation angle


   def __str__(self):
      # find distance between current position and original position
      dx = self.cornerX - min(self.xPoints)
      dy = self.cornerY - min(self.yPoints)
      # create new list of points, relative to current position
      xPoints = [x + dx for x in self.xPoints]
      yPoints = [y + dy for y in self.yPoints]

      return f'Polygon(xPoints = {xPoints}, yPoints = {yPoints}, color = {self.getColor()}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Rectangle(Drawable, Interactable):

   def __init__(self, x1, y1, x2, y2, color=Color.BLACK, fill=False, thickness=1, rotation=0):
      """Create a new Rectangle."""
      Drawable.__init__(self, color, fill, thickness, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.cornerX = min(x1, x2)   # top-left corner of bounding box
      self.cornerY = min(y1, y2)   # top-left corner of bounding box
      self.width   = abs(x1 - x2)  # width of bounding box
      self.height  = abs(y1 - y2)  # height of bounding box

      # create Qt object
      self._qtObject = _QtWidgets.QGraphicsRectItem(0, 0, self.width, self.height)

      self.setPosition(self.cornerX, self.cornerY)  # set position
      self.setColor(color)        # set color (this also sets fill and thickness)
      self.setRotation(rotation)  # set rotation angle


   def __str__(self):
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height

      return f'Rectangle(x1 = {self.getX()}, y1 = {self.getY()}, x2 = {x2}, y2 = {y2}, color = {self.getColor()}, fill = {self.fill}, thickness = {self.getThickness()}, rotation = {self.getRotation()})'


class Icon(Drawable, Interactable):

   def __init__(self, filename, width=None, height=None, rotation=0):
      """Create a new Icon."""
      Drawable.__init__(self, Color.BLACK, False, 0, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.filename = filename
      self.width    = width
      self.height   = height
      self.pixmap   = None

      # create Qt object
      try:     # create pixmap from file
         self.pixmap = _QtGui.QPixmap(self.filename)
      except:  # ... or create blank pixmap
         if width is None:
            width = 600
         if height is None:
            height = 400
         self.pixmap = _QtGui.QPixmap(width, height)

      if self.width is None:
         # use pixmap dimensions
         self.width  = self.pixmap.width()
         self.height = self.pixmap.height()

      if self.height is None:
         # scale to maintain aspect ratio
         self.width  = width
         self.height = int(self.pixmap.height() * (self.width / self.pixmap.width()))

      pixmapScaled = self.pixmap.scaled(self.width, self.height)  # create scaled copy of pixmap
      self._qtObject = _QtWidgets.QGraphicsPixmapItem(pixmapScaled)

      self.setPosition(0, 0)           # set position
      self.setRotation(self.rotation)  # set rotation angle


   def __str__(self):
      return f'Icon(filename = "{self.filename}", width = {self.width}, height = {self.height}, rotation = {self.rotation})'

   def setSize(self, width, height=None):
      """Set the icon's size."""
      # update internal attributes
      self.width  = width
      self.height = height

      if self.width is None:
         # use pixmap dimensions
         self.width  = self.pixmap.width()
         self.height = self.pixmap.height()

      if self.height is None:
         # scale to maintain aspect ratio
         self.width  = width
         self.height = int(self.pixmap.height() * (self.width / self.pixmap.width()))

      # update Qt object
      pixmapScaled = self.pixmap.scaled(self.width, self.height)
      self._qtObject.setPixmap(pixmapScaled)  # set scaled pixmap to object


   def crop(self, x, y, width, height):
      """Crop the icon to the specified rectangle.
      Coordinates are relative to the icon's top-left corner."""

      # update internal attributes
      self.width  = width
      self.height = height
      self.pixmap = self.pixmap.copy(x, y, width, height)  # crop internal pixmap

      # update Qt object
      pixmapScaled = self.pixmap.scaled(width, height)  # create scaled copy of pixmap
      self._qtObject.setPixmap(pixmapScaled)            # set scaled pixmap to object
      self._qtObject.moveBy((width/2), (height/2))      # keep icon centered in place


   def getPixel(self, col, row):
      """Get the color of a pixel in the icon as a [r, g, b] list."""
      image = self.pixmap.toImage()       # convert pixmap to image
      color = image.pixelColor(col, row)  # get pixel color
      r = color.red()                     # extract RGB values
      g = color.green()
      b = color.blue()
      a = color.alpha()
      return [r, g, b]


   def setPixel(self, col, row, color):
      """Set the color of a pixel in the icon."""

      # convert color to a QColor object
      r, g, b = color  # extract RGB values
      a = 255          # set alpha to 255 (fully opaque)
      qtColor = _QtGui.QColor(r, g, b, a)     # create color object

      # update pixel color
      image = self.pixmap.toImage()           # convert pixmap to image
      image.setPixelColor(col, row, qtColor)  # set pixel color

      # update internal attributes
      self.pixmap = _QtGui.QPixmap(image)   # create new pixmap from image

      # update Qt object
      pixmapScaled = self.pixmap.scaled(self.width, self.height)  # create scaled copy of pixmap
      self._qtObject.setPixmap(pixmapScaled)   # set scaled pixmap to object


   def getPixels(self):
      """Get the color of all pixels in the icon as a 2D array of [r, g, b] values."""
      # we could iterate through the pixels and extract each color,
      # but we can get better performance by converting the icon to a numpy array
      # and extracting the colors from there.

      # first, we need to convert the pixmap to an image
      image = self.pixmap.toImage().convertToFormat(_QtGui.QImage.Format_RGBA8888)  # convert to RGBA format

      # then, we need to get a pointer to image data
      ptr = image.bits()
      buffer = ptr.tobytes()  # safely convert to bytes

      # now create a numpy array from image data, reshaped to correct dimensions
      arr = np.frombuffer(buffer, dtype=np.uint8).reshape((image.height(), image.width(), 4))

      # slice the array to get only the RGB values
      rgb = arr[:, :, :3]

      # convert back to basic Python list
      return rgb.tolist()


   def setPixels(self, pixels):
      """Set the color of all pixels in the icon."""
      # reversing the process in getPixels()...
      # first, convert pixels to numpy array
      arr = np.array(pixels, dtype=np.uint8)  # shape: [height, width, 3]
      height, width, channels = arr.shape

      # then, add alpha channel
      if channels == 3:
         alpha = np.full((height, width, 1), 255, dtype=np.uint8)
         arr = np.concatenate((arr, alpha), axis=2)

      # ensure array is contiguous
      arr = np.ascontiguousarray(arr)

      # next, create new image from array
      image = _QtGui.QImage(arr.data, width, height, width * 4, _QtGui.QImage.Format_RGBA8888)
      image = image.copy()  # detach the image from numpy array (important!!)

      # finally, create new pixmap from image
      self.pixmap  = _QtGui.QPixmap(image)
      pixmapScaled = self.pixmap.scaled(self.width, self.height)
      self._qtObject.setPixmap(pixmapScaled)  # set scaled pixmap to object


# Label Constants
LEFT   = _QtCore.Qt.AlignmentFlag.AlignLeft
CENTER = _QtCore.Qt.AlignmentFlag.AlignCenter
RIGHT  = _QtCore.Qt.AlignmentFlag.AlignRight

class Label(Drawable, Interactable):

   def __init__(self, text, alignment=LEFT, foregroundColor=Color.BLACK, backgroundColor=Color.CLEAR, rotation=0):
      """Create a new Label."""
      Drawable.__init__(self, foregroundColor, False, 0, rotation)
      Interactable.__init__(self)

      # store internal attributes
      self.text = text
      self.alignment = alignment
      self.backgroundColor = backgroundColor

      # create Qt object
      textItem = _QtWidgets.QGraphicsTextItem(self.text)  # create foreground text
      r, g, b, a = foregroundColor.getRGBA()              # get color values
      qtForegroundColor = _QtGui.QColor(r, g, b, a)       # create Qt color
      textItem.setDefaultTextColor(qtForegroundColor)     # set foreground color
      self._qtComponents['text'] = textItem               # store text item

      background = _QtWidgets.QGraphicsRectItem(textItem.boundingRect())  # create background rectangle
      r, g, b, a = backgroundColor.getRGBA()         # get color values
      backgroundColor = _QtGui.QColor(r, g, b, a)    # create Qt color
      background.setBrush(backgroundColor)           # set background color
      background.setPen(_QtCore.Qt.PenStyle.NoPen)   # remove border
      self._qtComponents['background'] = background  # store background item

      # group foreground and background to move together
      self._qtObject  = _QtWidgets.QGraphicsItemGroup()
      self._qtObject.addToGroup(background)  # add background to group
      self._qtObject.addToGroup(textItem)    # add foreground to group

   def __str__(self):
      return f'Label(text = "{self.getText()}", alignment = {self.alignment}, foregroundColor = {self.getForegroundColor()}, backgroundColor = {self.getBackgroundColor()}, rotation = {self.getRotation()})'


   def getText(self):
      """
      Returns the label's text.
      """
      return self.text


   def setText(self, text):
      """
      Sets the label's text.
      """
      # update internal attributes
      self.text = str(text)

      # update Qt object
      textItem = self._qtComponents['text']  # get text item
      textItem.setPlainText(self.text)       # set text of Qt object


   def getForegroundColor(self):
      """
      Returns the label's foreground color.
      """
      return self.color


   def setForegroundColor(self, color):
      """
      Sets the label's foreground color.
      """

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update Qt object
         qtColor = _QtGui.QColor(rB, gB, bB, aB)  # create Qt color
         textItem = self._qtComponents['text']    # get text item
         textItem.setDefaultTextColor(qtColor)    # set foreground color


   def getBackgroundColor(self):
      """
      Returns the label's background color.
      """
      return self.backgroundColor


   def setBackgroundColor(self, color):
      """
      Sets the label's background color.
      """
      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.backgroundColor = color

         # update Qt object
         qtColor = _QtGui.QColor(rB, gB, bB, aB)  # create Qt color
         background = self._qtComponents['background']  # get background item
         background.setBrush(qtColor)                   # set background color
         background.setPen(_QtCore.Qt.PenStyle.NoPen)   # remove border


   def setFont(self, font):
      """
      Sets the label's font.
      """
      # do some basic error checking
      if not isinstance(font, Font):
         raise TypeError(f'Label.setFont(): font must be a Font object (it was {type(font)})')

      # update internal attributes
      self.font = font

      # update Qt object
      textItem = self._qtComponents['text']  # get text item
      qtFont = font._qtObject                # get Qt font object
      textItem.setFont(qtFont)               # set font of Qt object


class Group(Drawable, Interactable):

   def __init__(self, itemList=[]):
      Drawable.__init__(self, Color.CLEAR, False, 0, 0)
      Interactable.__init__(self)

      # do some basic type checking
      if not isinstance(itemList, list):
         raise TypeError(f'Group(): itemList must be a list object.  (it was {type(itemList)})')

      # initialize internal attributes
      self.itemList  = []                               # Drawable objects
      self._qtObject = _QtWidgets.QGraphicsItemGroup()  # group container
      self._qtWidget = _QtWidgets.QWidget()             # interactive widgets
      self._zCount   = 0.0                              # internal Qt z-order

      for item in itemList:                             # add each item to internal itemList
         self.add(item)

      # items within a group aren't registered with the display's event handler,
      # so we initialize these events to None to guarantee the group gets a chance
      # to see each event
      self.onMouseClick(None)
      self.onMouseDown(None)
      self.onMouseUp(None)
      self.onMouseMove(None)
      self.onMouseDrag(None)
      self.onMouseEnter(None)
      self.onMouseExit(None)
      self.onKeyType(None)
      self.onKeyDown(None)
      self.onKeyUp(None)

   def __str__(self):
      return f'Group(itemList = {self.itemList})'

   def _receiveEvent(self, event):
      """
      Deliver events to items in this group.
      Event behavior should be the same as if the items were on the Display,
      but because the Display isn't directly aware of these items, we handle
      events here.
      """
      Interactable._receiveEvent(self, event)  # first, the group tries to handle the event

      # TODO: this method is inefficient for large groups.  Consider modifying eventDispatcher to handle Group or Display events?

      # if the group didn't handle the event, search for an item that can
      i = 0
      while not event.handled and i < len(self.itemList):
         item = self.itemList[i]    # find item
         item._receiveEvent(event)  # attempt to deliver event
         i = i + 1                  # iterate

      # now,we either handled the event, or there are no items in the group
      # (including the group itself) that are capable of handling the event

   def _updateDimensions(self):
      """
      Calculates the Group's top-left corner, width, and height
      based on the items in itemList.
      """
      # skip if no items
      if len(self.itemList) > 0:

         # find top-left corner of object group
         minX, minY = np.inf, np.inf
         maxX, maxY = -np.inf, -np.inf
         for item in self.itemList:
            # do some basic type checking
            if not isinstance(item, Drawable):
               raise TypeError(f'Group(): each item in itemList must be a Drawable object. ({item} is a {type(item)}')

            # find the top-leftmost and bottom-rightmost coordinates
            minX = min(minX, item.cornerX)
            minY = min(minY, item.cornerY)
            maxX = max(maxX, item.cornerX + item.width)
            maxY = max(maxY, item.cornerY + item.height)

         # store top-left corner of item group
         self.cornerX = minX
         self.cornerY = minY
         # calculate width and height of item group
         self.width  = maxX - minX
         self.height = maxY - minY


   def add(self, item, order=0):
      """
      Adds a given Drawable item to the Group.

      The Group adopts the first Display it comes in contact with.
      So, if a Circle is on a Display, the Group is added to the Display,
      then the Circle is moved from the Display to the Group.

      Z-Order is relative to other items in the same group,
      and is not preserved from previous Displays.
      """
      # do some basic type checking
      if not isinstance(item, Drawable):
         raise TypeError(f'Group.add(): item must be a Drawable object.  (it was {type(item)})')

      # only update if item isn't in this group
      if item not in self.itemList:
         # update item's internal values
         if item.display is not None:        # item has a display,
            if self.display is None:         #     (but this group doesn't...)
               item.display.add(self)        #     (...so add this group to the display)
            item.display.remove(item)        # so remove item from its display

         if item.group is not None:          # item has a group,
            item.group.remove(item)          # so remove item from its group

         item.group = self                   # tell item it's in this group now

         # add item to itemList
         self._insertAtZOrder(item, order)   # insert item at order
         self._updateDimensions()            # update group dimensions

         # calculate item coordinates relative to Group
         x = item.cornerX - self.cornerX
         y = item.cornerY - self.cornerY

         # connect inner Qt objects
         if isinstance(item._qtObject, _QtWidgets.QGraphicsItem):
            self._qtObject.addToGroup(item._qtObject)     # add graphics object
            item._qtObject.setPos(x, y)                   # move object to relative position
         elif isinstance(item._qtObject, _QtWidgets.QWidget):
            item._qtObject.setParent(self._qtWidget)      # add widget object
            item._qtObject.show()                         # make sure widget is visible
            item._qtObject.move(x, y)                     # move object to relative position


   def remove(self, item):
      """
      Removes a given Drawable item from the Group.
      """
      # do some basic type checking
      if not isinstance(item, Drawable):
         raise TypeError(f'Group.remove(): item must be a Drawable object.  (it was {type(item)})')

      # only update if item is in group
      if item in self.itemList:
         # update item's internal values
         item.group = None

         # remove item from itemList
         self.itemList.remove(item)

         # calculate item's global coordinates
         x = item.cornerX
         y = item.cornerY

         # disconnect inner Qt objects
         if isinstance(item._qtObject, _QtWidgets.QGraphicsItem):
            self._qtObject.removeFromGroup(item._qtObject)    # remove graphics object
            item._qtObject.setPos(x, y)                       # return object to absolute position
         elif isinstance(item._qtObject, _QtWidgets.QWidget):
            item._qtObject.setParent(None)                    # remove widget object
            item._qtObject.hide()                             # make sure widget is hidden
            item._qtObject.move(x, y)                         # move object to relative position

         self._updateDimensions()


   def setPosition(self, x, y):
      """
      Sets the shape's x and y coordinate.
      For most shapes, this is the top-left corner of the bounding box.
      For Circles and ArcCircles, this is the center of the circle.
      """
      # do some basic error checking
      if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
         raise TypeError(f'Group.setPosition(): x and y must be numbers (they were {type(x)}, {type(y)})')

      # only update if x or y are different
      if (x != self.cornerX) or (y != self.cornerY):
         deltaX = x - self.cornerX   # calculate change in position
         deltaY = y - self.cornerY

         self.cornerX = x            # update Group attributes
         self.cornerY = y

         for item in self.itemList:  # update attributes of items (but don't actually move them)
            item.cornerX = item.cornerX + deltaX
            item.cornerY = item.cornerY + deltaY
            if hasattr(item, "centerX"):
               item.centerX = item.centerX + deltaX
               item.centerY = item.centerY + deltaY

         self._qtObject.setPos(x, y)  # finally, move group
         self._qtWidget.move(x, y)    # also, move widgets

   def setRotation(self, rotation, anchorX=None, anchorY=None):
      """
      Sets the shape's rotation angle in degrees.
      Rotation increases clockwise, with 0 degrees being the default orientation.
      Objects rotate around their x, y position (top-left corner, or center for circular shapes).
      """
      # do some basic error checking
      if not isinstance(rotation, (int, float)):
         raise TypeError(f'Drawable.setRotation(): rotation must be a number (it was {type(rotation)})')

      # only update if rotation or anchor has changed
      newRotation = (rotation != self.rotation)
      newAnchorX  = (anchorX  != self.anchorX)
      newAnchorY  = (anchorY  != self.anchorY)

      if newRotation or newAnchorX or newAnchorY:
         # update local attributes
         deltaAngle = rotation - self.rotation  # calculate change in angle
         self.rotation = rotation               # update attributes

         if anchorX is not None:
            self.anchorX = anchorX              # update x anchor, if provided

         if anchorY is not None:
            self.anchorY = anchorY              # update y anchor, if provided

         # update inner Qt objects
         self._qtObject.setTransformOriginPoint(self.anchorX, self.anchorY)
         self._qtObject.setRotation(self.rotation)

         # update item attributes (but don't visually change them)
         for item in self.itemList:
            item.rotation = item.rotation + deltaAngle


   def setOrder(self, object, order):
      """
      Sets the z-order of the specified object in this group.
      """
      # do some basic error checking
      if not isinstance(order, (int, float)):
         raise TypeError(f'Display.setOrder(): order must be a number (it was {type(order)})')
      
      # only update if object is in group and order is different
      if (object in self.itemList) and (object.getOrder() != order):
         self._insertAtZOrder(object, order)  # update object's new zorder


   def getOrder(self, object):
      """
      Returns the z-order of the specified object in this group.
      """
      order = None

      if object in self.itemList:  # index in itemList corresponds to z-order
         order = self.itemList.index(object)

      return order


   def _insertAtZOrder(self, object, order):
      """
      Inserts a Drawable object at the given z-order.
      """
      order = max(0, min(len(self.itemList), order))  # clamp order to possible indices

      if object in self.itemList:          # if already in Group,
         self.itemList.remove(object)      # remove it from itemList first

      self.itemList.insert(order, object)  # insert object into itemList at new order

      # now, we need to figure out object's z-order in Qt
      if order == 0:                         # inserting on top...
         self._zCount = self._zCount + 1.0   # increment zCount
         object._setZValue(self._zCount)     # set Qt z-order to top

      elif order >= len(self.itemList) - 1:  # inserting on bottom...
         neighborZ = 0.0
         if len(self.itemList) > 1:          # find bottommost object, not including this one
            neighborZ = self.itemList[-2]._getZValue() - 1.0  # insert 1.0 underneath it
         object._setZValue(neighborZ)

      else:                                  # inserting somewhere in middle...
         frontNeighbor = self.itemList[order - 1]    # find front neighbor
         backNeighbor  = self.itemList[order + 1]    # find back neighbor
         zFront        = frontNeighbor._getZValue()  # find their Qt z-orders
         zBack         = backNeighbor._getZValue()
         zMiddle       = (zFront + zBack) / 2.0      # find the average
         object._setZValue(zMiddle)                  # set this object there



#######################################################################################
# Controls (Event behavior defined by CreativePython)
#######################################################################################

class Control(Group):
   """
   Controls define some common behaviors between Groups with predefined behavior.
   """
   def __init__(self, startValue=None, updateFunction=None):
      Group.__init__(self)
      self.value    = startValue
      self.function = updateFunction
      self.foregroundShape = None
      self.backgroundShape = None
      self.outlineShape = None

      # self._update()  # the last step of a Control's init should be to update its appearance

   def __str__(self):
      return f'Control()'

   def _update(self):
      """
      Updates the control's appearance based on its current value.
      Each Control should override this method based on their function.
      """
      pass

   def _receiveEvent(self, event):
      """
      Injects control-specific events to the event handler.
      Each Control should override this method based on their function.
      """
      Group._receiveEvent(self, event)

   def getValue(self):
      """
      Returns the current value of the control.
      """
      return self.value

   def setValue(self, value):
      """
      Sets the current value of the control, and updates its appearance.
      """
      # only update if value is different
      if self.value != value:
         self.value = value                                     # update value
         self._update()                                         # update appearance

         if self.function is not None and callable(self.function):
            self.function(self.value)                           # call user function

   def getColor(self):
      """
      Returns the control's foreground color.
      """
      return self.foregroundShape.getColor()

   def setColor(self, color):
      """
      Changes the control's foreground color.
      If color parameter is omitted, a color selection dialog box will be presented.
      TODO: add color selection box
      """
      self.foregroundShape.setColor(color)

   def getThickness(self):
      """
      Returns the control outline's current thickness.
      """
      return self.outlineShape.getThickness()

   def setThickness(self, thickness):
      """
      Changes the control outline's thickness to the specified value.
      """
      self.outlineShape.setThickness(thickness)


class HFader(Control):
   def __init__(self, x1, y1, x2, y2, minValue=0, maxValue=999, startValue=None,
                updateFunction=None, foreground=Color.RED, background=Color.BLACK,
                outline=Color.BLACK, thickness=3, rotation=0):
      """Creates a new HFader."""
      # calculate startValue if one isn't provided
      startValue = ((minValue + maxValue)//2) if startValue is None else startValue
      Control.__init__(self, startValue, updateFunction)

      # store internal attributes
      self.minValue = minValue
      self.maxValue = maxValue
      self.padding  = thickness//2 + 1  # amount to reduce foreground rectangle by

      # store direct references to each default item
      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self.itemList
      self.backgroundShape = Rectangle(
         x1, y1, x2, y2,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self.foregroundShape = Rectangle(
         x1, y1, x2, y2,
         color=foreground,
         fill=True,
         thickness=0,
         rotation=0
      )
      self.outlineShape = Rectangle(
         x1, y1, x2, y2,
         color=outline,
         fill=False,
         thickness=thickness,
         rotation=0
      )

      self.add(self.backgroundShape)  # add each component to group
      self.add(self.foregroundShape)
      self.add(self.outlineShape)

      self._update()  # initialize fader appearance

   def __str__(self):
      x1 = self.cornerX
      y1 = self.cornerY
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      foregroundColor = self.foregroundShape.getColor()
      backgroundColor = self.backgroundShape.getColor()
      outlineColor    = self.outlineShape.getColor()
      thickness       = self.outlineShape.getThickness()
      rotation        = self.getRotation()

      return f'HFader(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, minValue = {self.minValue}, maxValue = {self.maxValue}, startValue = {self.value}, updateFunction = {self.function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   def _update(self):
      """
      Updates the fader's appearance based on its current value.
      """
      # calculate internal rectangle dimensions
      valueRatio = (self.value - self.minValue) / (self.maxValue - self.minValue)  # calculate value ratio (0.0 to 1.0)
      qtX    = self.padding  # Qt coordinates are relative to top-left of Group
      qtY    = self.padding
      width  = self.backgroundShape.width  - (2 * self.padding)
      height = self.backgroundShape.height - (2 * self.padding)

      width  = int(width  * valueRatio)  # adjust width based on value

      # since Rectangle can't resize, we update Qt object directly
      # we could create a new Rectangle object, but since we expect this to update rapidly,
      # we want to be a little more memory efficient
      self.foregroundShape._qtObject.setRect(qtX, qtY, width, height)

      # also, update foregroundShape's attributes
      self.foregroundShape.cornerX = qtX + self.backgroundShape.cornerX
      self.foregroundShape.cornerY = qtY + self.backgroundShape.cornerY
      self.foregroundShape.width   = width

   def _receiveEvent(self, event):
      """
      Inject fader-specific events to the event handler.
      """
      # first, look for user event handlers
      Control._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add fader behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         # update fader value based on mouse position (args = [x, y])
         x = event.args[0] - self.backgroundShape.cornerX        # get coordinates relative to fader
         valueRatio = x / self.backgroundShape.width             # calculate value ratio (0.0 to 1.0)
         valueRatio = max(0.0, min(1.0, valueRatio))             # clamp value ratio to range [0.0, 1.0]
         valueRange = self.maxValue - self.minValue              # calculate range of possible values
         value = int(self.minValue + (valueRatio * valueRange))  # calculate value within that range
         self.setValue(value)                                    # set fader value
         event.handled = True                                    # report event handling

   def setValue(self, value):
      """
      Sets the current value of the control, and update its appearance.
      """
      value = max(self.minValue, min(self.maxValue, value))  # clamp value to range
      Control.setValue(self, value)  # update value, appearance, and call user function

   def setThickness(self, thickness):
      self.padding = thickness//2 + 1
      return Control().setThickness(thickness)



class VFader(HFader):
   def __init__(self, x1, y1, x2, y2, minValue=0, maxValue=999, startValue=None,
               updateFunction=None, foreground=Color.RED, background=Color.BLACK,
               outline=Color.BLACK, thickness=3, rotation=0):
      """Creates a new VFader."""
      # call parent constructor
      HFader.__init__(self, x1, y1, x2, y2, minValue, maxValue, startValue,
                      updateFunction, foreground, background,
                      outline, thickness, rotation)

   def __str__(self):
      x1 = self.cornerX
      y1 = self.cornerY
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      foregroundColor = self.foregroundShape.getColor()
      backgroundColor = self.backgroundShape.getColor()
      outlineColor    = self.outlineShape.getColor()
      thickness       = self.outlineShape.getThickness()
      rotation        = self.getRotation()

      return f'VFader(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, minValue = {self.minValue}, maxValue = {self.maxValue}, startValue = {self.value}, updateFunction = {self.function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   def _update(self):
      """
      Updates the fader's appearance based on its current value.
      """
      # calculate internal rectangle dimensions
      valueRatio = (self.value - self.minValue) / (self.maxValue - self.minValue)  # calculate value ratio (0.0 to 1.0)
      width  = self.backgroundShape.width  - (2 * self.padding)
      height = self.backgroundShape.height - (2 * self.padding)
      height = int(height * valueRatio)  # adjust height based on value

      qtX    = self.padding  # Qt coordinates are relative to top-left of Group
      qtY    = self.backgroundShape.height - height - self.padding  # top-left moves up with increasing value, but down numerically

      # since Rectangle can't resize, we update Qt object directly
      # we could create a new Rectangle object, but since we expect this to update rapidly,
      # we want to be a little more memory efficient
      self.foregroundShape._qtObject.setRect(qtX, qtY, width, height)

      # also, update foregroundRect's absolute coordinates
      self.foregroundShape.cornerX = self.backgroundShape.cornerX + qtX
      self.foregroundShape.cornerY = self.backgroundShape.cornerY + qtY
      self.foregroundShape.height  = height

   def _receiveEvent(self, event):
      """
      Inject fader-specific events to the event handler.
      """
      # first, look for user event handlers
      Control._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add fader behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         # update fader value based on mouse position (args = [x, y])
         y = event.args[1] - self.backgroundShape.cornerY        # get coordinates relative to fader
         valueRatio = 1 - (y / self.backgroundShape.height)      # calculate value ratio (0.0 to 1.0)
         valueRatio = max(0.0, min(1.0, valueRatio))             # clamp value ratio to range [0.0, 1.0]
         valueRange = self.maxValue - self.minValue              # calculate range of possible values
         value = int(self.minValue + (valueRatio * valueRange))  # calculate value within that range
         self.setValue(value)                                    # set fader value
         event.handled = True                                    # report event handling


class Rotary(Control):
   def __init__(self, x1, y1, x2, y2, minValue=0, maxValue=999, startValue=None,
               updateFunction=None, foreground=Color.RED, background=Color.BLACK,
               outline=Color.BLUE, thickness=3, arcWidth=300, rotation=0):
      """Creates a new Rotary."""
      # calculate startValue if one isn't provided
      startValue = ((minValue + maxValue)//2) if startValue is None else startValue
      Control.__init__(self, startValue, updateFunction)

      # store internal attributes
      self.minValue = minValue
      self.maxValue = maxValue

      self.arcWidth = arcWidth
      startAngle = 90 + arcWidth//2
      endAngle = startAngle + arcWidth

      # store direct references to each default item
      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self.itemList
      self.backgroundShape = Arc(
         x1, y1, x2, y2,
         startAngle, endAngle,
         style=PIE,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self.foregroundShape = Arc(
         x1, y1, x2, y2,
         startAngle, endAngle,
         style=PIE,
         color=foreground,
         fill=True,
         thickness=0,
         rotation=0
      )
      self.outlineShape = Arc(
         x1, y1, x2, y2,
         startAngle, endAngle,
         style=PIE,
         color=outline,
         fill=False,
         thickness=thickness,
         rotation=0
      )

      self.add(self.backgroundShape)  # add each component to group
      self.add(self.foregroundShape)
      self.add(self.outlineShape)

      self._update()

   def __str__(self):
      x1 = self.cornerX
      y1 = self.cornerY
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      foregroundColor = self.foregroundShape.getColor()
      backgroundColor = self.backgroundShape.getColor()
      outlineColor    = self.outlineShape.getColor()
      thickness       = self.outlineShape.getThickness()
      rotation        = self.getRotation()

      return f'Fader(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, minValue = {self.minValue}, maxValue = {self.maxValue}, startValue = {self.value}, updateFunction = {self.function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   def _update(self):
      """
      Updates the fader's appearance based on its current value.
      """
      # calculate inner arc dimensions
      valueRatio = (self.value - self.minValue) / (self.maxValue - self.minValue)  # calculate value ratio (0.0 to 1.0)
      qtX     = 0
      qtY     = 0
      width   = self.backgroundShape.width
      height  = self.backgroundShape.height

      startAngle = 90 + self.arcWidth//2
      arcWidth   = -self.arcWidth * valueRatio  # negative = counter-clockwise in Qt

      # since Arc can't resize, we update Qt object directly
      # we could create a new Arc object, but since we expect this to update rapidly,
      # we want to be a little more memory efficient
      path = _QtGui.QPainterPath()                               # create new path
      path.arcMoveTo(qtX, qtY, width, height, startAngle)        # first point
      path.arcTo(qtX, qtY, width, height, startAngle, arcWidth)  # arc to end point
      path.lineTo(width//2, height//2)                           # line to center
      path.closeSubpath()                                        # back to start
      self.foregroundShape._qtObject.setPath(path)               # set new arc path

   def _receiveEvent(self, event):
      """
      Inject rotary-specific events to the event handler.
      """
      # first, look for user event handlers
      Control._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add rotary behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         # update rotary value based on mouse position (args = [x, y])
         x = event.args[0] - self.backgroundShape.cornerX  # get coordinates relative to rotary
         y = event.args[1] - self.backgroundShape.cornerY

         dx = x - self.backgroundShape.width//2             # get vector from center to mouse
         dy = self.backgroundShape.height//2 - y
         mouseAngle = np.degrees(np.arctan2(dy, dx)) % 360  # angle in degrees
         startAngle = 90 + self.arcWidth//2                 # starting angle of rotary
         arcWidth   = (startAngle - mouseAngle) % 360       # arcWidth from start angle to mouse angle

         print(f"Rotary Event: StartAngle: {startAngle}, MouseAngle: {mouseAngle}, ArcWidth: {arcWidth}")

         if 0 <= arcWidth <= self.arcWidth:
            # mouse is within arc, calculate value
            valueRatio = arcWidth / self.arcWidth        # calculate value ratio (0.0 to 1.0)
            valueRatio = max(0.0, min(1.0, valueRatio))  # clamp value ratio to range [0.0, 1.0]
            valueRange = self.maxValue - self.minValue
            value = int(np.round(self.minValue + (valueRatio * valueRange)))
            self.setValue(value)                        # set rotary value
            event.handled = True


   def setValue(self, value):
      """
      Sets the current value of the control, and update its appearance.
      """
      value = max(self.minValue, min(self.maxValue, value))  # clamp value to range
      Control.setValue(self, value)  # update value, appearance, and call user function


class Push(Control):
   def __init__(self, x1, y1, x2, y2, updateFunction=None, foreground=Color.RED, background=Color.BLACK, outline=Color.CLEAR, thickness=3, rotation=0):
      """Creates a new Push button."""
      Control.__init__(self, False, updateFunction)

      # store internal attributes
      self.padding  = thickness//2 + 1  # amount to reduce foreground rectangle by

      # store direct references to each default item
      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self.itemList
      self.backgroundShape = Rectangle(
         x1, y1, x2, y2,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )
      self.foregroundShape = Rectangle(
         x1+self.padding,
         y1+self.padding,
         x2-self.padding,
         y2-self.padding,
         color=foreground,
         fill=True,
         thickness=0,
         rotation=0
      )
      self.outlineShape = Rectangle(
         x1, y1, x2, y2,
         color=outline,
         fill=False,
         thickness=thickness,
         rotation=0
      )

      self.add(self.backgroundShape)  # add each component to group
      self.add(self.foregroundShape)
      self.add(self.outlineShape)

      self._update()

   def __str__(self):
      x1 = self.cornerX
      y1 = self.cornerY
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      foregroundColor = self.foregroundShape.getColor()
      backgroundColor = self.backgroundShape.getColor()
      outlineColor    = self.outlineShape.getColor()
      thickness       = self.outlineShape.getThickness()
      rotation        = self.getRotation()

      return f'Push(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, updateFunction = {self.function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   def _update(self):
      """
      Updates the push button's appearance based on its current value.
      """
      if self.value:
         self.foregroundShape._qtObject.show()
      else:
         self.foregroundShape._qtObject.hide()

   def _receiveEvent(self, event):
      """
      Inject push button-specific events to the event handler.
      """
      # first, look for user event handlers
      Group._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add push button behavior
      if event.type in ["mouseDown"]:
         self.setValue(True)
         event.handled = True

      elif event.type in ["mouseUp", "mouseExit"]:
         self.setValue(False)
         event.handled = True

   def setThickness(self, thickness):
      self.padding = thickness//2 + 1
      return Control.setThickness(self, thickness)


class Toggle(Push):
   def __init__(self, x1, y1, x2, y2, updateFunction=None, foreground=Color.RED, background=Color.BLACK, outline=Color.CLEAR, thickness=3, rotation=0):
      """
      Creates a new Toggle button.
      """
      Push.__init__(self, x1, y1, x2, y2, updateFunction, foreground, background, outline, thickness, rotation)

   def __str__(self):
      x1 = self.cornerX
      y1 = self.cornerY
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      foregroundColor = self.foregroundShape.getColor()
      backgroundColor = self.backgroundShape.getColor()
      outlineColor    = self.outlineShape.getColor()
      thickness       = self.outlineShape.getThickness()
      rotation        = self.getRotation()

      return f'Toggle(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, updateFunction = {self.function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, thickness = {thickness}, rotation = {rotation})'

   def _receiveEvent(self, event):
      """
      Inject toggle-specific events to the event handler.
      """
      # first, look for user event handlers
      Control._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add toggle button behavior
      if event.type in ["mouseDown"]:
         self.setValue(not self.value)
         event.handled = True


class XYPad(Control):
   def __init__(self, x1, y1, x2, y2, updateFunction=None, foreground=Color.RED, background=Color.BLACK, outline=Color.CLEAR, outlineThickness=2, trackerRadius=10, crosshairsThickness=None, rotation=0):
      """
      Creates a new XYPad.
      """
      Control.__init__(self, [0, 0], updateFunction)

      if crosshairsThickness is None:
         crosshairsThickness = outlineThickness

      # store direct references to each default item
      # since users can manipulate the Group by adding and removing components,
      # we need a way to identify the original components without referencing self.itemList
      self.backgroundShape = Rectangle(
         x1, y1, x2, y2,
         color=background,
         fill=True,
         thickness=0,
         rotation=0
      )

      # calculate center of XYPad based on background dimensions
      centerX = self.backgroundShape.cornerX + self.backgroundShape.width//2
      centerY = self.backgroundShape.cornerY + self.backgroundShape.height//2

      self.trackerXLine = Line(
         centerX, y1, centerX, y2,
         color=foreground,
         thickness=crosshairsThickness,
         rotation=0
      )
      self.trackerYLine = Line(
         x1, centerY, x2, centerY,
         color=foreground,
         thickness=crosshairsThickness,
         rotation=0
      )
      self.foregroundShape = Circle(
         centerX, centerY,
         trackerRadius,
         color=foreground,
         fill=False,
         thickness=crosshairsThickness,
         rotation=0
      )
      self.outlineShape = Rectangle(
         x1, y1, x2, y2,
         color=outline,
         fill=False,
         thickness=outlineThickness,
         rotation=0
      )

      self.add(self.backgroundShape)
      self.add(self.trackerXLine)
      self.add(self.trackerYLine)
      self.add(self.foregroundShape)
      self.add(self.outlineShape)

      self.setValue(centerX, centerY)

   def __str__(self):
      x1 = self.cornerX
      y1 = self.cornerY
      x2 = self.cornerX + self.width
      y2 = self.cornerY + self.height
      foregroundColor     = self.foregroundShape.getColor()
      backgroundColor     = self.backgroundShape.getColor()
      outlineColor        = self.outlineShape.getColor()
      outlineThickness    = self.outlineShape.getThickness()
      trackerRadius       = self.foregroundShape.getWidth()//2
      crosshairsThickness = self.foregroundShape.getThickness()
      rotation            = self.getRotation()

      return f'XYPad(x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}, updateFunction = {self.function}, foreground = {foregroundColor}, background = {backgroundColor}, outline = {outlineColor}, outlineThickness = {outlineThickness}, trackerRadius = {trackerRadius}, crosshairsThickness = {crosshairsThickness}, rotation = {rotation})'

   def _update(self):
      """
      Updates the XYPad's appearance based on its current value.
      """
      x = self.value[0] + self.cornerX  # calculate global (x,y) values
      y = self.value[1] + self.cornerY

      # move tracker and crosshairs
      self.trackerXLine.setX(x)
      self.trackerYLine.setY(y)
      self.foregroundShape.setPosition(x, y)

   def _receiveEvent(self, event):
      """
      Inject XYPad-specific events to the event handler.
      """
      # first, look for user event handlers
      Control._receiveEvent(self, event)

      # then, regardless of whether the event was handled, add XYPad behavior
      if event.type in ["mouseDown", "mouseDrag"]:
         x = event.args[0] - self.cornerX  # adjust coordinates relative to XYPad
         y = event.args[1] - self.cornerY
         self.setValue(x, y)
         event.handled = True

   def setValue(self, x, y):
      """
      Sets the current (x,y) position of the XYPad tracker.
      """
      x = max(0, min(self.width,  x))  # clamp to XYPad bounds
      y = max(0, min(self.height, y))

      Control.setValue(self, [x, y])


#######################################################################################
# Widgets (Event behavior defined by Qt)
#######################################################################################

class Button(Drawable, Interactable):

   def __init__(self, text="", function=None):
      """Create a new button."""
      Drawable.__init__(self, Color.LIGHT_GRAY, False, 0)
      Interactable.__init__(self)

      # store internal attributes
      self.x        = 0
      self.y        = 0

      self.text     = text
      self.function = function

      # create qt object
      qtObject = _QtWidgets.QPushButton(self.text)
      qtObject.clicked.connect(self.function)  # connect button to function
      qtObject.move(self.x, self.y)            # set default position
      qtObject.adjustSize()                    # adjust size to fit text
      self.width  = qtObject.width()           # get width
      self.height = qtObject.height()          # get height

      self._qtObject = qtObject

      self.setColor(self.color)  # set default color


   def __str__(self):
      return f'Button(text = "{self.text}", function = {self.function})'

   def setColor(self, color):
      """Set the button color."""
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'Button.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update qt object
         self._qtObject.setStyleSheet(
            f"""
            QPushButton {{
               background-color: {color.getHex()};
               color: black;
            }}
            QPushButton::pressed {{
               background-color: {color.darker().getHex()};
            }}
            """)


class CheckBox(Drawable, Interactable):

   def __init__(self, text="", function=None):
      """Create a new checkbox."""
      Drawable.__init__(self, Color.CLEAR, False, 0)
      Interactable.__init__(self)

      # store internal attributes
      self.x        = 0
      self.y        = 0
      # self.width    = 0  # gets updated below
      # self.height   = 0

      self.text     = text
      self.function = function

      self.state    = False

      # create Qt object
      qtObject = _QtWidgets.QCheckBox(self.text)
      qtObject.stateChanged.connect(self.function)  # connect checkbox to function
      qtObject.move(self.x, self.y)                 # set default position
      qtObject.adjustSize()                         # adjust size to fit text
      self.width  = qtObject.width()                # get width
      self.height = qtObject.height()               # get height

      self._qtObject = qtObject

      self.setColor(self.color)  # set default color


   def __str__(self):
      return f'CheckBox(text = "{self.text}", function = {self.function})'


   def isChecked(self):
      """Returns True if the checkbox is checked, False otherwise."""
      return self.state


   def check(self):
      """Checks the checkbox."""
      # only update if state is different
      if not self.state:
         # update internal attributes
         self.state = True  # update state

         # update qt object
         self._qtObject.setChecked(True)


   def uncheck(self):
      """Unchecks the checkbox."""
      # only update if state is different
      if self.state:
         # update internal attributes
         self.state = False  # update state

         # update qt object
         self._qtObject.setChecked(False)


   def setColor(self, color):
      """Set the checkbox background color."""
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'Button.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update Qt object
         self._qtObject.setStyleSheet(
            f"""
            QCheckBox {{
               background-color: {color.getHex()};
               color: black;
            }}
            """)


HORIZONTAL = _QtCore.Qt.Orientation.Horizontal
VERTICAL   = _QtCore.Qt.Orientation.Vertical

class Slider(Drawable, Interactable):

   def __init__(self, orientation=HORIZONTAL, lower=0, upper=100, start=None, function=None):
      """Create a new slider."""
      Drawable.__init__(self, Color.BLACK, False, 0)
      Interactable.__init__(self)

      # store internal attributes
      self.x        = 0
      self.y        = 0
      # self.width    = 0  # gets updated below
      # self.height   = 0

      self.orientation = orientation
      self.lower       = lower
      self.upper       = upper
      self.start       = start if start is not None else ((lower + upper)//2)
      self.function    = function

      # create Qt object
      qtObject = _QtWidgets.QSlider(self.orientation)
      qtObject.setRange(self.lower, self.upper)
      qtObject.setValue(self.start)  # set default value
      qtObject.valueChanged.connect(self.function)  # connect slider to function
      qtObject.move(self.x, self.y)                 # set default position
      qtObject.adjustSize()                         # adjust size
         # TODO: investigate auto sizing, decide if we want to set manually
      self.width  = qtObject.width()                # get width
      self.height = qtObject.height()               # get height

      self._qtObject = qtObject


   def __str__(self):
      return f'Slider(orientation = {self.orientation}, lower = {self.lower}, upper = {self.upper}, start = {self.getValue()}, function = {self.function})'


   def getValue(self):
      """Returns the current value of the slider."""
      return self._qtObject.value()


   def setValue(self, value):
      """Sets the current value of the slider."""
      # only update if value is different
      if value != self.getValue():
         # update qt object
         self._qtObject.setValue(value)

   def setColor(self, color):
      """Set the slider color."""
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'Slider.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update Qt object
         ## TODO: set color of slider - which part??


class DropDownList(Drawable, Interactable):

   def __init__(self, items=[], function=None):
      """Create a new dropdown list."""
      Drawable.__init__(self, Color.LIGHT_GRAY, False, 0)
      Interactable.__init__(self)

      # store internal attributes
      self.x        = 0
      self.y        = 0
      # self.width    = 0  # gets updated below
      # self.height   = 0

      self.items     = items
      self.function  = function

      # create Qt object
      qtObject = _QtWidgets.QComboBox()
      qtObject.addItems(self.items)
      qtObject.activated.connect(self._callback)    # connect dropdown to function
      qtObject.adjustSize()                         # adjust size to fit text
      qtObject.move(self.x, self.y)                 # set default position
      self.width  = qtObject.width()                # get width
      self.height = qtObject.height()               # get height

      self._qtObject = qtObject                     # store Qt object

      self.setColor(self.color)  # set default color


   def __str__(self):
      return f'DropDownList(items = {self.items}, function = {self.function})'

   def _callback(self, index):
      """Calls user function using item at given index."""
      if self.function is not None and callable(self.function):
         self.function(self.items[index])  # call function with selected item

   def setColor(self, color):
      """Set the dropdown list color."""
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'DropDownList.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update Qt object
         self._qtObject.setStyleSheet(
            f"""
            QComboBox {{
               background-color: {color.getHex()};
               color: black;
            }}
            QComboBox QAbstractItemView {{
               background-color: {color.getHex()};
               color: black;
            }}
            """)


class TextField(Drawable, Interactable):
   def __init__(self, text="", columns=8, function=None):
      """Create a new text field."""
      Drawable.__init__(self, Color.WHITE, False, 0)
      Interactable.__init__(self)

      # store internal attributes
      self.x        = 0
      self.y        = 0
      # self.width    = 0  # gets updated below
      # self.height   = 0

      self.columns     = columns
      self.function    = function

      # create qt object
      qtObject = _QtWidgets.QLineEdit(str(text))
      qtObject.returnPressed.connect(self._callback)  # connect text field to function
      fontMetrics = _QtGui.QFontMetrics(qtObject.font())
      charWidth   = fontMetrics.averageCharWidth()  # get character width
      lineWidth   = self.columns * charWidth + 16   # get line width with padding
      qtObject.setFixedWidth(lineWidth)       # set width
      qtObject.adjustSize()                   # autosize height to fit text

      self.width  = qtObject.width()          # store dimensions
      self.height = qtObject.height()
      qtObject.move(self.x, self.y)               # set default position

      self._qtObject = qtObject                   # store Qt object

      self.setColor(self.color)  # set default color

   def __str__(self):
      return f'TextField(text = "{self.getText()}", columns = {self.columns}, function = {self.function})'

   def _callback(self):
      """Calls user function using text in field."""
      if self.function is not None and callable(self.function):
         self.function(self._qtObject.text()) # call function with text in field

   def setColor(self, color):
      """Set the text field color."""
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'TextField.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update qt object
         self._qtObject.setStyleSheet(
            f"""
            QLineEdit {{
               background-color: {color.getHex()};
               color: black;
            }}
            """)


   def getText(self):
      """Returns the text in the field."""
      return self._qtObject.text()

   def setText(self, text):
      """Sets the text in the field."""
      # only update if text is different
      if text != self.getText():
         # update qt object
         self._qtObject.setText(text)


   def setFont(self, font):
      """Sets the font of the text field."""
      # do some basic error checking
      if not isinstance(font, Font):
         raise TypeError(f'TextField.setFont(): font must be a Font object (it was {type(font)})')

      # update internal attributes
      self.font = font

      # update qt object
      self._qtObject.setFont(font._qtObject)
      fontMetrics = _QtGui.QFontMetrics(self._qtObject.font())
      charWidth   = fontMetrics.averageCharWidth()  # get character width
      lineWidth   = self.columns * charWidth + 16   # get line width with padding
      self._qtObject.setFixedWidth(lineWidth)       # set width

      self._qtObject.adjustSize()                   # autosize height to fit text
      self.width  = self._qtObject.width()          # store dimensions
      self.height = self._qtObject.height()


class TextArea(Drawable, Interactable):

   def __init__(self, text="", columns=8, rows=5):
      """Create a new text field."""
      Drawable.__init__(self, Color.WHITE, False, 0)
      Interactable.__init__(self)

      # store internal attributes
      self.x        = 0
      self.y        = 0
      # self.width    = 0  # gets updated below
      # self.height   = 0

      self.columns     = columns
      self.rows        = rows

      # create qt object
      qtObject = _QtWidgets.QTextEdit(str(text))
      fontMetrics = _QtGui.QFontMetrics(qtObject.font())
      charWidth   = fontMetrics.averageCharWidth()  # get character width
      charHeight  = fontMetrics.height()            # get character height
      lineWidth   = self.columns * charWidth + 20   # get line width with padding
      lineHeight  = self.rows * (charHeight + 6)    # get line height with padding
      qtObject.setFixedSize(lineWidth, lineHeight)  # set field size
      self.width  = qtObject.width()                # store dimensions
      self.height = qtObject.height()
      qtObject.move(self.x, self.y)                 # set default position

      self._qtObject = qtObject                     # store Qt object

      self.setColor(self.color)  # set default color


   def __str__(self):
      return f'TextArea(text = "{self.getText()}", columns = {self.columns}, rows = {self.rows})'

   def setColor(self, color):
      """Set the text area color."""
      # do some basic error checking
      if not isinstance(color, Color):
         raise TypeError(f'TextArea.setColor(): color must be a Color object (it was {type(color)})')

      rA, gA, bA, aA = self.color.getRGBA()
      rB, gB, bB, aB = color.getRGBA()

      # only update if color values are different
      if (rA != rB) or (gA != gB) or (bA != bB) or (aA != aB):
         # update internal attributes
         self.color = color

         # update Qt object
         self._qtObject.setStyleSheet(
            f"""
            QTextEdit {{
               background-color: {color.getHex()};
               color: black;
            }}
            """)


   def getText(self):
      """Returns the text in the field."""
      return self._qtObject.toPlainText()

   def setText(self, text):
      """Sets the text in the field."""
      # only update if text is different
      if text != self.getText():
         # update Qt object
         self._qtObject.setText(text)


   def setFont(self, font):
      """Sets the font of the text field."""
      # do some basic error checking
      if not isinstance(font, Font):
         raise TypeError(f'TextField.setFont(): font must be a Font object (it was {type(font)})')

      # update internal attributes
      self.font = font

      # update qt object
      self._qtObject.setFont(font._qtObject)
      fontMetrics = _QtGui.QFontMetrics(self._qtObject.font())
      charWidth   = fontMetrics.averageCharWidth()          # get character width
      charHeight  = fontMetrics.height()                    # get character height

      self.width  = self.columns * charWidth + 20           # set field width with padding
      self.height = self.rows * (charHeight + 5)            # set field height with padding         self._qtObject.setFixedSize(self.width, self.height)  # set field size


class Menu():

   def __init__(self, menuName):
      """Create a new menu."""

      # store internal attributes
      self.name   = menuName
      self.items  = []

      # create qt object
      self._qtObject = _QtWidgets.QMenu(self.name)

   def __str__(self):
      return f'Menu(menuName = "{self.name}")'

   def __repr__(self):
      return str(self)


   def addItem(self, item="", functionName=None):
      """Add an item to the menu."""

      qtAction = _QtGui.QAction(item, self._qtObject)   # create new action
      if callable(functionName):
         qtAction.triggered.connect(functionName)  # attach callback, if any
      self._qtObject.addAction(qtAction)           # add action to menu
      self.items.append(qtAction)                  # remember action item


   def addItemList(self, itemList=[""], functionNameList=[None]):
      """Add a list of items to the menu."""
      for i in range(len(itemList)):
         # get item and function (if available, None otherwise)
         item         = itemList[i]
         functionName = functionNameList[i] if i < len(functionNameList) else None
         # add item to menu
         self.addItem(item, functionName)


   def addSeparator(self):
      """Add a separator to the menu."""
      # update qt object
      separator = _QtGui.QAction(self._qtObject)  # create new action
      separator.setSeparator(True)                # set action as separator
      self._qtObject.addAction(separator)         # add separator to menu
      self.items.append(separator)                # remember action item


   def addSubmenu(self, menu):
      """Add a submenu to this menu."""

      if not isinstance(menu, Menu):
         raise ValueError(f'Menu.addSubmenu(): menu must be a Menu object (it was {type(menu)})')

      # update qt object
      submenu = menu._qtObject            # get submenu's underlying Qt Menu
      if submenu is not None:
         self._qtObject.addMenu(submenu)  # add submenu to this menu
         self.items.append(submenu)       # remember action item


   def enable(self):
      """Enable the menu."""
      self._qtObject.setEnabled(True)


   def disable(self):
      """Disable the menu."""
      self._qtObject.setEnabled(False)


#######################################################################################
# Test
#######################################################################################

if __name__ == "__main__":

   def testMenu():
      d = Display()

      menu = Menu("Test Menu")
      menu.addItem("Test Item 1", lambda: print("Test Item 1 clicked"))
      menu.addSeparator()
      menu.addItem("Test Item 2", lambda: print("Test Item 2 clicked"))

      submenu = Menu("Test Submenu")
      submenu.addItem("Submenu Item 1", lambda: print("Submenu Item 1 clicked"))
      submenu.addItem("Submenu Item 2", lambda: print("Submenu Item 2 clicked"))
      menu.addSubmenu(submenu)

      menu.addItem("Test Item 3", lambda: print("Test Item 3 clicked"))
      menu.addSeparator()
      menu.addItem("Test Item 4", lambda: print("Test Item 4 clicked"))

      # menu.disable()
      # submenu.disable()

      d.addMenu(menu)
      d.addPopupMenu(menu)


   def testShapes():
      d = Display()

      oval = Oval(50, 50, 150, 100, color=Color.RED, fill=True)
      d.add(oval)

      circle = Circle(200, 200, 50, color=Color.BLUE, fill=False)
      d.add(circle)

      point = Point(300, 300, color=Color.BLACK)
      d.add(point)

      arc = Arc(350, 50, 450, 150, startAngle=0, endAngle=270, style=OPEN, color=Color.ORANGE, fill=True)
      d.add(arc)

      arcCircle = ArcCircle(500, 200, 50, startAngle=0, endAngle=180, style=PIE, color=Color.GRAY, fill=True)
      d.add(arcCircle)

      line = Line(50, 200, 150, 300, color=Color.MAGENTA, thickness=2)
      d.add(line)

      polyline = PolyLine([50, 50, 150], [50, 100, 25], color=Color.GREEN, thickness=2)
      d.add(polyline)

      polygon = Polygon([200, 250, 300], [50, 150, 100], color=Color.YELLOW, fill=True)
      d.add(polygon)

      rectangle = Rectangle(350, 50, 450, 150, color=Color.CYAN, fill=False)
      d.add(rectangle)

      icon = Icon("images/de-brazzas-monkey.jpg", 100, 100)
      d.add(icon)


   def testEvents():
      d = Display()

      centerX = d.getWidth()/2
      centerY = d.getHeight()/2
      length  = 100
      shape = Rectangle(0, 0, length, length, Color.RED, True)
      shape.setPosition(centerX-length/2, centerY-length/2)
      d.add(shape)

      d.onMouseClick(lambda x,y: print("Display Mouse Click at", x, y))
      shape.onMouseClick(lambda x,y: print("Shape Mouse Click at", x, y))

      d.onMouseDown(lambda x,y: print("Display Mouse Down at", x, y))
      shape.onMouseDown(lambda x,y: print("Shape Mouse Down at", x, y))

      d.onMouseUp(lambda x,y: print("Display Mouse Up at", x, y))
      shape.onMouseUp(lambda x,y: print("Shape Mouse Up at", x, y))

      d.onMouseMove(lambda x,y: print("Display Mouse Move at", x, y))
      shape.onMouseMove(lambda x,y: print("Shape Mouse Move at", x, y))

      d.onMouseDrag(lambda x,y: print("Display Mouse Drag at", x, y))
      shape.onMouseDrag(lambda x,y: print("Shape Mouse Drag at", x, y))

      d.onMouseEnter(lambda x,y: print("Display Mouse Enter at", x, y))
      shape.onMouseEnter(lambda x,y: print("Shape Mouse Enter at", x, y))

      d.onMouseExit(lambda x,y: print("Display Mouse Exit at", x, y))
      shape.onMouseExit(lambda x,y: print("Shape Mouse Exit at", x, y))

      d.onKeyDown(lambda x: print("Display Key Down", x))
      shape.onKeyDown(lambda x: print("Shape Key Down", x))

      d.onKeyUp(lambda x: print("Display Key Up", x))
      shape.onKeyUp(lambda x: print("Shape Key Up", x))

      d.onKeyType(lambda x: print("Display Key Type", x))
      shape.onKeyType(lambda x: print("Shape Key Type", x))


   def testToolTip():
      d = Display()
      d.setToolTipText("This is a display tooltip")

      label = Label("Hello World!", LEFT, Color.BLACK, Color.CYAN)
      label.setPosition(50, 50)
      label.setToolTipText("This is a label tooltip")
      d.add(label)

      icon = Icon("images/de-brazzas-monkey.jpg", 100, 100)
      icon.setPosition(200, 50)
      icon.setToolTipText("This is an icon tooltip")
      d.add(icon)

      circle = Circle(300, 100, 50, Color.RED, True)
      circle.setToolTipText("This is a circle tooltip")
      d.add(circle)


   def testWidgets():
      d = Display()

      button = Button("Click Me", lambda: print("Button clicked!"))
      button.setPosition(50, 50)
      d.add(button)

      checkbox = CheckBox("Check Me", lambda: print(f'Checkbox state: {checkbox.isChecked()}!'))
      checkbox.setPosition(50, 100)
      d.add(checkbox)

      hSlider = Slider(HORIZONTAL, 0, 100, 50, lambda: print(f'Horizontal slider value: {hSlider.getValue()}!'))
      hSlider.setPosition(50, 150)
      d.add(hSlider)

      vSlider = Slider(VERTICAL, 0, 200, 50, lambda: print(f'Vertical slider value: {vSlider.getValue()}!'))
      vSlider.setPosition(150, 50)
      d.add(vSlider)

      dropdown = DropDownList(["Option 1", "Option 2", "Option 3"], lambda s: print(f'Dropdown selected: {s}!'))
      dropdown.setPosition(50, 250)
      d.add(dropdown)

      textField = TextField("Type here", 20, lambda s: print(f'Text field input: {s}!'))
      textField.setPosition(50, 300)
      d.add(textField)

      textArea = TextArea("Type here", 20, 5)
      textArea.setPosition(300, 50)
      d.add(textArea)


   def testControls():
      d = Display()

      hFader = HFader(50, 50, 150, 100, 0, 100, 50, lambda v: print(f'Horizontal fader value: {v}!'))
      d.add(hFader)

      vFader = VFader(50, 150, 100, 250, 0, 100, 50, lambda v: print(f'Vertical fader value: {v}!'))
      d.add(vFader)

      rotary = Rotary(50, 275, 150, 375, 0, 100, 50, lambda v: print(f'Rotary value: {v}!'))
      d.add(rotary)

      push = Push(200, 50, 250, 100, lambda v: print(f'Push button value: {v}!'))
      d.add(push)

      toggle = Toggle(200, 150, 250, 200, lambda v: print(f'Toggle button value: {v}!'))
      d.add(toggle)

      xyPad = XYPad(300, 50, 400, 150, lambda x,y: print(f'XYPad value: {x}, {y}!'))
      d.add(xyPad)

   def testZOrder():
      d = Display()

      # Create two overlapping rectangles
      rect1 = Rectangle(50, 50, 150, 150, Color.RED, True)
      rect2 = Rectangle(100, 100, 200, 200, Color.BLUE, True)
      rect3 = Rectangle(150, 150, 250, 250, Color.GREEN, True)

      # Add them to the display
      d.add(rect1)
      d.add(rect2)
      d.add(rect3)


      print(f'Initial Z-Orders:')
      print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # remove rectangle 2
      d.remove(rect2)

      print(f'\nAfter removing Rectangle 2:')
      print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # add rectangle 2 back to front
      # d.add(rect2)

      # print(f'\nAfter adding Rectangle 2 to front:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # remove rectangle 3
      # d.remove(rect3)

      # print(f'\nAfter removing Rectangle 3:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')

      # # insert rectangle 3 to middle
      # d.addOrder(rect3, 1)
      # print(f'\nAfter inserting Rectangle 3 to middle:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # remove rectangle 1
      # d.remove(rect1)

      # print(f'\nAfter removing Rectangle 1:')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')

      # # add rectangle 1 to back
      # d.addOrder(rect1, 99)

      # print(f'\nAfter adding Rectangle 1 to back:')
      # print(f'\tRectangle 1 Z-Order: {rect1.getOrder()}')
      # print(f'\tRectangle 2 Z-Order: {rect2.getOrder()}')
      # print(f'\tRectangle 3 Z-Order: {rect3.getOrder()}')


   # testMenu()
   # testShapes()
   # testEvents()
   # testToolTip()
   # testWidgets()
   # testControls()
   # testZOrder()
