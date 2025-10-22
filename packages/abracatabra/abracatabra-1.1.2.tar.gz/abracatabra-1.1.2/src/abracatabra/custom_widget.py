from matplotlib.backends.qt_compat import QtWidgets
from typing import Callable


class CustomWidget(QtWidgets.QWidget):
    """
    A Qt widget that contains a custom Qt widget. Inherits from `QWidget`. This
    is used solely to provide a way to register animation callbacks for custom
    widgets so that they can be updated during animations.

    Methods:
        `update_widget`: Updates the widget with the registered callback function.
        `register_animation_callback`: Registers a callback function for how to
            update the widget during an animation.
    """

    def __init__(self, widget: QtWidgets.QWidget, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget, stretch=1)
        self.setLayout(layout)

        def callback(idx: int = 0) -> None:
            return

        self._animation_callback = callback
        self._callback_registered = False
        self._latest_callback_idx = 0

    def update_widget(self, callback_idx: int = 0) -> None:
        """
        Updates the custom widget during an animation by calling the registered
        callback function.

        Args:
            callback_idx (int): An index passed to the registered animation
                callback function. This index is intended to specify which frame
                in the animation to draw.
        """
        # Attempting to detect if the same frame as last time to avoid re-drawing
        if self._callback_registered and callback_idx == self._latest_callback_idx:
            # print("Skipping custom widget update; same frame as last time.")
            return
        self._animation_callback(callback_idx)
        self._latest_callback_idx = callback_idx

    def register_animation_callback(self, callback: Callable[[int], None]) -> None:
        """
        Registers a callback function for how to update the custom widget during
        an animation.

        Args:
            callback (Callable[[int], None]): A function specifying how to update
                the widget. The function should take a single integer argument,
                which is the index of the current frame in the animation to draw.
                Registering callbacks allows abracatabra to better manage the
                timing of updates.
        """
        self._animation_callback = callback
        self._callback_registered = True
