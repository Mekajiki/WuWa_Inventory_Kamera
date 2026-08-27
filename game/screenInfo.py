import math
from game.gameROI import Coordinates, COORDINATES, ULTRAWIDE_ANCHORS

PRECOMPUTED_RATIOS = [(w / h, (w, h)) for w, h in list(COORDINATES)]

class ScreenInfoObject:
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                setattr(self, key, ScreenInfoObject(value))
            else:
                setattr(self, key, value)

    def __reduce__(self):
        return (self.__class__, (self.__getstate__(),))

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, state):
        self.__dict__.update(state)

class ScreenInfo:
    def __init__(self, width: int | float, height: int | float, monitor: int = 1, originX: int = 0, originY: int = 0):
        self.width = width
        self.height = height
        self.monitor = monitor
        self.originX = originX
        self.originY = originY

        if self.height and self.width / self.height > (16 / 9) * 1.03:
            # wider than 16:9 (ultrawide): the game scales its UI by height
            # and anchors panels to the screen edges
            self.data = self._anchorScreen()
        else:
            try:
                self.data = COORDINATES[self.getRatio()][(self.width, self.height)]
            except KeyError:
                self.data = self._scaleScreen()

        self.data = self._convertToObject(self.data)

    def __reduce__(self):
        return (self.__class__, (self.width, self.height, self.monitor, self.originX, self.originY))

    def _convertToObject(self, obj):
        if isinstance(obj, dict):
            return ScreenInfoObject(obj)
        return obj

    def _anchorScreen(self):
        """Project the 16:9 reference table onto an ultrawide screen: scale
        everything by height and re-anchor horizontal positions according to
        ULTRAWIDE_ANCHORS (left by default, or right/center)."""
        reference = COORDINATES[(16, 9)][(1920, 1080)]
        scale = self.height / 1080

        def anchorFor(path: str) -> str:
            while path:
                if path in ULTRAWIDE_ANCHORS:
                    return ULTRAWIDE_ANCHORS[path]
                path = path.rpartition('.')[0]
            return 'left'

        def projectX(x, anchor):
            if not x:
                return 0
            if anchor == 'right':
                return int(self.width - (1920 - x) * scale)
            if anchor == 'center':
                return int(self.width / 2 + (x - 960) * scale)
            return int(x * scale)

        def project(data, path):
            if isinstance(data, Coordinates):
                anchor = anchorFor(path)
                return Coordinates(
                    x=projectX(data.x, anchor),
                    y=int(data.y * scale) if data.y else 0,
                    w=int(data.w * scale) if data.w else 0,
                    h=int(data.h * scale) if data.h else 0
                )
            elif isinstance(data, dict):
                return {key: project(value, f'{path}.{key}' if path else key) for key, value in data.items()}
            elif isinstance(data, list):
                return [project(item, path) for item in data]
            else:
                return data

        return project(reference, '')

    def _scaleScreen(self):
        """
        Dynamically generate screen scaling data based on the closest known resolution and aspect ratio.
        
        Returns:
            dict: A dynamically scaled dictionary of screen information
        """
        closestRatio = self.closestAspectRatio(self.width, self.height)
        closestResolution = min(list(COORDINATES[closestRatio]), key=lambda size: abs((size[0] / size[1]) - (closestRatio[0]/closestRatio[1])))
        
        referenceData = COORDINATES[closestRatio][closestResolution]
        
        def _scale(data):
            if isinstance(data, Coordinates):
                return Coordinates(
                    x=self._scaleWidth(data.x, closestResolution[0]) if data.x else 0,
                    y=self._scaleHeight(data.y, closestResolution[1]) if data.y else 0,
                    w=self._scaleWidth(data.w, closestResolution[0]) if data.w else 0,
                    h=self._scaleHeight(data.h, closestResolution[1]) if data.h else 0
                )
            elif isinstance(data, dict):
                return {key: _scale(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [_scale(item) for item in data]
            else:
                return data
        
        return _scale(referenceData)

    def __getattr__(self, item):
        """Dynamically access attributes from the nested data dictionary."""
        if isinstance(self.data, dict) and item in self.data:
            return self.data[item]
        if hasattr(self.data, item):
            return getattr(self.data, item)
        raise AttributeError(f"'ScreenInfo' object has no attribute '{item}'")

    @staticmethod
    def reduceRatio(width, height):
        """Reduce width and height to their simplest ratio."""
        divisor = math.gcd(width, height)
        return (width // divisor, height // divisor)

    @staticmethod
    def calculateRatioDifference(actualRatio, standardRatio):
        """Calculate the percentage difference between two aspect ratios."""
        return abs(actualRatio - standardRatio) / actualRatio * 100

    @staticmethod
    def closestAspectRatio(width, height, threshold=3.0):
        """Find the closest standard aspect ratio for the given dimensions."""

        actualWidth, actualHeight = ScreenInfo.reduceRatio(width, height)
        actualRatio = actualWidth / actualHeight

        minDiff = float('inf')
        closestRatio = (16, 9)

        for standardRatio, (w, h) in PRECOMPUTED_RATIOS:
            diff = ScreenInfo.calculateRatioDifference(actualRatio, standardRatio)
            if diff < minDiff:
                minDiff = diff
                closestRatio = (w, h)
            if minDiff == 0: break

        return closestRatio if minDiff <= threshold else (16, 9)

    def getRatio(self):
        """Return the simplified ratio of the screen."""
        return self.closestAspectRatio(self.width, self.height)

    def _scaleWidth(self, value: int | float, resolution: int):
        return self._scale(value, self.width, resolution)

    def _scaleHeight(self, value: int | float, resolution: int):
        return self._scale(value, self.height, resolution)

    def _scale(self, value, dimension, resolution):
        return int(value / resolution * dimension)