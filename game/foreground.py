import re
import ctypes
import logging
import win32gui
import win32con

import pywinctl as pwc
import pymonctl as pmc

from game.screenInfo import ScreenInfo
from properties.config import PROCESS_NAME, WINDOW_NAME

logger = logging.getLogger('WindowManager')

class WindowManager:
	def __init__(self, windowName: str|tuple[str, ...] = WINDOW_NAME, preocessName: str = PROCESS_NAME):
		self.user32 = ctypes.WinDLL('user32', use_last_error=True)
		self.windowName = windowName
		self.preocessName = preocessName
		self.window = self._findWindow()

	def _findWindow(self) -> pwc.Window|None:
		"""Finds the window by title and process name."""
		titles = self.windowName if isinstance(self.windowName, (tuple, list)) else (self.windowName,)
		for title in titles:
			for win in pwc.getWindowsWithTitle(title=title, app=self.preocessName, condition=pwc.Re.CONTAINS):
				return win
		logger.debug(f"Window with WindowName: {self.windowName} and ProcessName: {self.preocessName}, not found.")
		return None

	def setForeground(self) -> tuple:
		"""Brings the window to the foreground and maximizes it."""
		if self.window:
			# self.window.maximize()
			self.window.activate()
			win32gui.PostMessage(self.window._hWnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)

			logger.debug(f"Window {self.windowName} set to foreground.")
			return ("success", "Success", "pass")
		else:
			logger.debug(f"Cannot set {self.windowName} in foreground: window not found.")
			return ("error", "Error", f"Cannot set {self.windowName} in foreground: window not found.")

	def getWindowPosition(self) -> pmc.Point|None:
		"""Return the window's position."""
		if self.window:
			return self.window.position
		else:
			logger.debug("Cannot retrieve window position: window not found.")
			return None
	
	def getWindowSize(self) -> tuple[int, int]|None:
		"""Return the window's size."""
		if self.window:
			return self.window.width, self.window.height
		else:
			logger.debug("Cannot retrieve window size: window not found.")
			return None
	
	def getScreenInfo(self) -> ScreenInfo:
		width, height, originX, originY = self.getClientArea()

		DPI = self.getDPI()
		monitor = self.window.getDisplay()[0] # ['\\\\.\\DISPLAY1']
		match = re.search(r'\d+', monitor)
		if match: monitor = int(match.group())
		else: monitor = 1

		width = int(width / DPI)
		height = int(height / DPI)

		return ScreenInfo(width, height, monitor, originX, originY)

	def getClientArea(self) -> tuple[int, int, int, int]:
		"""Return the client-area size and its top-left corner in virtual-screen coordinates."""
		try:
			_, _, width, height = win32gui.GetClientRect(self.window._hWnd)
			originX, originY = win32gui.ClientToScreen(self.window._hWnd, (0, 0))
			if width and height:
				return width, height, originX, originY
		except Exception as e:
			logger.debug(f"Failed to get client area, falling back to window size: {e}")
		width, height = self.getWindowSize() or (1920, 1080)
		return width, height, 0, 0

	def _getScreen(self) -> pmc.Monitor:
		"""Return the primary screen object."""
		return pmc.getAllMonitors()[0]

	def getScreenSize(self) -> tuple[int, int]:
		"""Retrieves the primary screen size."""
		screen = self._getScreen()
		return screen.size.width, screen.size.height

	def getDPI(self) -> float:
		return self.user32.GetDpiForWindow(self.window._hWnd) / 96.0

	def isForeground(self) -> bool:
		"""Check if the window is still in foreground."""
		if self.window:
			return self.window.isActive
		return False
