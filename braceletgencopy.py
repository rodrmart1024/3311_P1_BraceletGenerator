import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance


def get_maya_main_win():
    """Return the Maya Main Window"""
    main_win_addr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_win_addr), QtWidgets.QWidget)


def generate_bracelet_curve(bracelet_length):
    """Function that Creates and Returns Bracelet Curve"""
    circle_curve = cmds.circle(name='bracelet_curve',
                               radius=bracelet_length * 2,
                               normal=(0, 1, 0))[0]

    return circle_curve

def build_beads(curve, width):
    """Function that Creates and Returns Bead Geometry"""
    beads = []
    # Creating the placement of beads to be next to eachother
    length = cmds.arclen(curve)
    spacing = width * 2
    amount = int(length / spacing)

    # Loop that appends spheres along the curve using pathAnimation
    for bead_index in range(amount):
        bead = cmds.polySphere(radius=width)[0]

        motion = cmds.pathAnimation(bead, curve=curve, follow=True,
                                    fractionMode=True)
        cmds.cutKey(motion)
        cmds.setAttr(f"{motion}.uValue", bead_index / float(amount))
        beads.append(bead)

    return cmds.group(beads, name='beads_geo')


class BraceletUI(QtWidgets.QDialog):

    def __init__(self):
        """Creating the Window and calling out to functions"""
        super().__init__(parent=get_maya_main_win())
        self.setWindowTitle("Bracelet Generator")
        self.resize(400, 600)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.lengthwidth_sliders_ui()
        self.material_checkboxes_ui()
        self.texture_checkboxes_ui()
        self.color_swatch_ui()
        self.finish__checkboxes_ui()
        self.bracelet_button_ui()

    def lengthwidth_sliders_ui(self):
        """Function that Creates Sliders for Length and Width"""

        group = QtWidgets.QGroupBox('Size:')
        layout = QtWidgets.QVBoxLayout()

        # Labeled QSliders with Mins and Maxs configured to QVBoxLayout
        # Length
        self.length_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.length_slider.setMinimum(1)
        self.length_slider.setMaximum(4)
        layout.addWidget(QtWidgets.QLabel("Length"))
        layout.addWidget(self.length_slider)

        # Width
        self.width_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(3)
        layout.addWidget(QtWidgets.QLabel("Width"))
        layout.addWidget(self.width_slider)

        group.setLayout(layout)
        self.layout.addWidget(group)

    def material_checkboxes_ui(self):
        """Creates Checkboxes for Materials"""
        group = QtWidgets.QGroupBox('Materials:')
        layout = QtWidgets.QGridLayout()
        # Dictionary to store kay value pairs for .isChecked()
        self.material_checkboxes = {}

        materials = ['Beads', 'Leather', 'Chain']
        # Adds a checkbox to every material in list
        for item, material_type in enumerate(materials):
            checkbox = QtWidgets.QCheckBox(material_type)

            self.material_checkboxes[material_type] = checkbox
            layout.addWidget(checkbox, item // 3, item % 3)

        group.setLayout(layout)
        self.layout.addWidget(group)

    def texture_checkboxes_ui(self):
        """Checkboxes for Material Texture & Formating Label"""
        group = QtWidgets.QGroupBox("Material Texture:")
        layout = QtWidgets.QVBoxLayout()
        # Dictionary to store kay value pairs for .isChecked()
        self.texture_checkboxes = {}

        texture_categories = ['Beads', 'Leather']
        texture_options = [['Wood', 'Pearl',],
                           ['Smooth', 'Rough']]
    
        # Pairs the loops together creating ('Beads', ['Wood', 'Pearl'])
        for category, options in zip(texture_categories, texture_options):
            row = QtWidgets.QHBoxLayout()
            # Two rows with Labels determind by the category
            label = QtWidgets.QLabel(f"{category}:")
            row.addWidget(label)

            # Every texture_type per catergoery gets a checkbox
            for texture_type in options:
                name = f"{category}_{texture_type}"
                checkbox = QtWidgets.QCheckBox(texture_type)
            # Notes the marked status to texture_choice_limiter
                checkbox.stateChanged.connect(self.texture_choice_limiter)

                self.texture_checkboxes[name] = checkbox
                row.addWidget(checkbox)

            layout.addLayout(row)

        group.setLayout(layout)
        self.layout.addWidget(group)

    def color_swatch_ui(self):
        """Color picker for Material Color"""
        group = QtWidgets.QGroupBox("Material Color:")
        layout = QtWidgets.QVBoxLayout()
        # Dictionary to store Label. Swatch, and Color
        self.color_widgets = {}

        material_categories = ['Beads', 'Leather', 'Chain']
        # Labels for every material type om row layout
        for material_type in material_categories:
            row = QtWidgets.QHBoxLayout()

            label = QtWidgets.QLabel(f"{material_type}:")
            row.addWidget(label)

            # Color swatch with fixed size
            swatch = ColorSwatch()
            swatch.setFixedSize(100, 20)
            swatch.setStyleSheet("background-color: rgb(255, 255, 255);")

            # If color swatch is clicked then it connects material to color_picker
            swatch.clicked.connect(
                lambda material_type=material_type: self.color_picker(material_type)
            )

            row.addWidget(swatch)

            # Data stored inside of color_widgets
            self.color_widgets[material_type] = {
                "swatch": swatch,
                "color": (255, 255, 255)
            }

            layout.addLayout(row)

        group.setLayout(layout)
        self.layout.addWidget(group)

    def color_picker(self, material_type):
        color = QtWidgets.QColorDialog.getColor()
        # Popup color selection window
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())

            # Stores the color
            self.color_widgets[material_type]["color"] = rgb

            # Swatch color gets updated when color selection closes
            self.color_widgets[material_type]["swatch"].setStyleSheet(
                f"background-color: rgb{rgb};"
            )

    def finish__checkboxes_ui(self):
        """Checkboxes for Material Finish"""
        group = QtWidgets.QGroupBox("Finish:")
        layout = QtWidgets.QGridLayout()
        # Dictionary to store kay value pairs for .isChecked()
        self.finish_checkboxes = {}

        finishes = ['Worn', 'New', 'Polished']
        # Every finish in list gets a checkbox
        for types, finish in enumerate(finishes):
            checkbox = QtWidgets.QCheckBox(finish)
            # Notes the marked status to finish_choice_limiter
            checkbox.stateChanged.connect(self.finish_choice_limiter)

            self.finish_checkboxes[finish] = checkbox
            layout.addWidget(checkbox, types // 3, types % 3)

        group.setLayout(layout)
        self.layout.addWidget(group)

    def bracelet_button_ui(self):
        """Buttons for Generating Bracelet"""
        layout = QtWidgets.QHBoxLayout()
        # If button is clicked it connects to generate_bracelet
        generate_btn = QtWidgets.QPushButton('Generate Bracelet')
        generate_btn.clicked.connect(self.generate_bracelet)

        layout.addWidget(generate_btn)
        self.layout.addLayout(layout)

    def texture_choice_limiter(self):
        """UI Function that Limits Texture to One"""
        texture_groups = {'Beads': ['Beads_Wood', 'Beads_Pearl'],
                                    'Leather': ['Leather_Smooth',
                                                'Leather_Rough']}
        for group, textures in texture_groups.items():
            selected = []
            # If the texturse checkbox is checked it appends to seleted
            for texture_type in textures:
                if self.texture_checkboxes[texture_type].isChecked():
                    selected.append(texture_type)
            # If amount selected is 1 then other textures are disabled
            if len(selected) == 1:
                for texture_type in textures:
                    if texture_type not in selected:
                        self.texture_checkboxes[texture_type].setEnabled(False)
            else:
                for texture_type in textures:
                    self.texture_checkboxes[texture_type].setEnabled(True)

    def finish_choice_limiter(self):
        """UI Function that Limits Finish to One"""
        selected = []
        # If the finish checkbox is checked it appends to seleted
        for name, checkbox in self.finish_checkboxes.items():
            if checkbox.isChecked():
                selected.append(name)
        # If amount selected is 1 then other finishes are disabled
        if len(selected) >= 1:
            for name, checkbox in self.finish_checkboxes.items():
                if name not in selected:
                    checkbox.setEnabled(False)
        else:
            for checkbox in self.finish_checkboxes.values():
                checkbox.setEnabled(True)

    def generate_bracelet(self):
        """Generates bracelet by calling calling functions"""
        # Gets the length and width slider values
        bracelet_length = self.length_slider.value()
        bracelet_width = self.width_slider.value()

        selected_materials = []
        # Gets the checked material and appends them to selected_materials
        for name, checkbox in self.material_checkboxes.items():
            if checkbox.isChecked():
                selected_materials.append(name)
        # Gets the bracelet curve using the bracelet length
        curve = generate_bracelet_curve(bracelet_length)
        # If materials are selected then calls to thier build function
        if 'Beads' in selected_materials:
            build_beads(curve, bracelet_width)

class ColorSwatch(QtWidgets.QLabel):
    """Dedicated class for ColorSwatch"""
    clicked = QtCore.Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()

def show_ui():
    """Dedicated funtion to call for UI"""
    ui = BraceletUI()
    ui.show()
    return ui
