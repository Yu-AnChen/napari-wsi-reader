"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory, magicgui
from qtpy.QtWidgets import QHBoxLayout, QPushButton, QWidget

if TYPE_CHECKING:
    import napari


class ExampleQWidget(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        btn = QPushButton("Click me!")
        btn.clicked.connect(self._on_click)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")
        print(self.viewer.layers.selection)


@magic_factory
def example_magic_widget(img_layer: "napari.layers.Image"):
    print(f"you have selected {img_layer}")
    print(f"you have selected {img_layer.name}")


from napari import Viewer
@magic_factory(
    # call_button='Reset',
        x={
        "min": -1000,
        "max": 1000,
        "step": 1,
        "widget_type": "Slider",
    },
    y={
        "min": -1000,
        "max": 1000,
        "step": 1,
        "widget_type": "Slider",
    },
    auto_call=True,
)
def manual_transform(
    viewer: Viewer, x=0, y=0
):
    if viewer.layers.selection:
        for layer in viewer.layers.selection:
            layer.translate = (y, x)
