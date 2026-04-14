import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide6 import QtWidgets, QtCore
from shiboken6 import wrapInstance


def get_maya_main_window():
    """Return the Maya Main Window"""
    main_win_address = omui.MQtUtil.mainWindow()

    return wrapInstance(int(main_win_address), QtWidgets.QWidget)


def build_bracelet_curve(bracelet_length):
    """Function that Creates and Returns Bracelet Curve"""
    circle_curve = cmds.circle(name='bracelet_curve',
                               radius=bracelet_length * 2,
                               normal=(0, 1, 0))[0]
    return circle_curve


def build_beads(circle_curve, width_slider):
    """Function that Creates and Returns Bead Geometry"""
    beads = []
    length = cmds.arclen(circle_curve)
    spacing = width_slider * 2
    amount = int(length / spacing)

    for bead_index in range(amount):
        bead = cmds.polySphere(radius=width_slider)[0]

        motion = cmds.pathAnimation(bead, curve=circle_curve, follow=True,
                                    fractionMode=True)
        cmds.cutKey(motion)
        cmds.setAttr(f"{motion}.uValue", bead_index / float(amount))
        beads.append(bead)

    bead_group = cmds.group(beads, name='beads_geo')

    return bead_group


def build_bead_wood_texture(bead_group, color):
    wood_lambert_mat = cmds.shadingNode('lambert', asShader=True,
                                        name='wood_lambert')
    wood_shading_grp = cmds.sets(renderable=True, noSurfaceShader=True,
                                 empty=True, name='wood_lambertSG')
    cmds.connectAttr(f'{wood_lambert_mat}.outColor',
                     f'{wood_shading_grp}.surfaceShader')

    place3d = cmds.shadingNode('place3dTexture', asUtility=True,
                               name='wood_place3d')
    wood_texture = cmds.shadingNode('wood', asTexture=True, name='wood_texture')
    cmds.connectAttr(f'{place3d}.worldInverseMatrix[0]',
                     f'{wood_texture}.placementMatrix')
    cmds.connectAttr(f'{wood_texture}.outColor', f'{wood_lambert_mat}.color')

    r, g, b = color[0]/255, color[1]/255, color[2]/255
    cmds.setAttr(f'{wood_texture}.fillerColor', r, g, b, type='double3')
    cmds.setAttr(f'{wood_texture}.veinColor', r * 0.2, g * 0.2, b * 0.2,
                 type='double3')
    cmds.setAttr(f'{wood_texture}.layerSize', 0.5)

    all_beads = cmds.listRelatives(bead_group, allDescendents=True,
                                   type='mesh')
    for bead in all_beads:
        cmds.sets(bead, edit=True, forceElement=wood_shading_grp)


def build_bead_marble_texture(bead_group, color):
    marble_lambert_mat = cmds.shadingNode('lambert', asShader=True,
                                          name='marble_lambert')
    marble_shading_grp = cmds.sets(renderable=True, noSurfaceShader=True,
                                   empty=True, name='marble_lambertSG')
    cmds.connectAttr(f'{marble_lambert_mat}.outColor',
                     f'{marble_shading_grp}.surfaceShader')

    place3d = cmds.shadingNode('place3dTexture', asUtility=True,
                               name='marble_place3d')
    marble_texture = cmds.shadingNode('marble', asTexture=True,
                                      name='marble_texture')
    cmds.connectAttr(f'{place3d}.worldInverseMatrix[0]',
                     f'{marble_texture}.placementMatrix')
    cmds.connectAttr(f'{marble_texture}.outColor',
                     f'{marble_lambert_mat}.color')

    r, g, b = color[0]/255, color[1]/255, color[2]/255
    cmds.setAttr(f'{marble_texture}.fillerColor', r, g, b, type='double3')
    cmds.setAttr(f'{marble_texture}.veinColor', r * 0.2, g * 0.2, b * 0.2,
                 type='double3')

    all_beads = cmds.listRelatives(bead_group, allDescendents=True,
                                   type='mesh')
    for bead in all_beads:
        cmds.sets(bead, edit=True, forceElement=marble_shading_grp)


def build_leather(circle_curve, width_slider, color, leather_texture='Smooth'):
    """Function that Creates and Returns Leather Geometry"""
    yscale_conversion = {1: 1.4, 2: 2.0, 3: 2.4}
    y_scale = yscale_conversion.get(width_slider, 1.4)

    old_transforms = set(cmds.ls(type='transform'))
    cmds.sweepMeshFromCurve(circle_curve)
    new_transforms = set(cmds.ls(type='transform'))

    sweep_transform = list(new_transforms - old_transforms)[0]
    cmds.setAttr(f"{sweep_transform}.scaleY", y_scale)

    leather_geo = cmds.rename(sweep_transform, "leather_geo#")
    leather_grp = cmds.group(leather_geo, name="leather_grp#")
    build_leather_texture(leather_grp, color, leather_texture)

    return leather_grp


def build_leather_texture(leather_grp, color, leather_texture='Smooth'):
    leather_lambert_mat = cmds.shadingNode('lambert', asShader=True,
                                           name='leather_lambert')
    leather_shading_grp = cmds.sets(renderable=True, noSurfaceShader=True,
                                    empty=True, name='leather_lambertSG')
    cmds.connectAttr(f'{leather_lambert_mat}.outColor',
                     f'{leather_shading_grp}.surfaceShader')

    place3d = cmds.shadingNode('place3dTexture', asUtility=True,
                               name='leather_place3d')
    leather_texture_node = cmds.shadingNode('leather', asTexture=True,
                                            name='leather_texture')

    cmds.connectAttr(f'{place3d}.worldInverseMatrix[0]',
                     f'{leather_texture_node}.placementMatrix')
    cmds.connectAttr(f'{leather_texture_node}.outColor',
                     f'{leather_lambert_mat}.color')
    cmds.setAttr(f'{leather_texture_node}.density', 0.1)
    if leather_texture == 'Rough':
        cmds.setAttr(f'{leather_texture_node}.cellSize', 0.0)
        cmds.setAttr(f'{leather_texture_node}.density', 0.4)

    r, g, b = color[0]/255, color[1]/255, color[2]/255
    cmds.setAttr(f'{leather_texture_node}.cellColor', r, g, b, type='double3')
    cmds.setAttr(f'{leather_texture_node}.creaseColor',
                 r * 0.5, g * 0.5, b * 0.5, type='double3')

    leather_mesh = cmds.listRelatives(leather_grp, allDescendents=True,
                                      type='mesh')[0]
    cmds.sets(leather_mesh, edit=True, forceElement=leather_shading_grp)


class BraceletUI(QtWidgets.QDialog):

    def __init__(self):
        """Creating the Window and calling out to functions"""
        super().__init__(parent=get_maya_main_window())
        self.setWindowTitle("Bracelet Generator")
        self.resize(400, 600)
        self.layout = QtWidgets.QVBoxLayout(self)

        self.lengthwidth_sliders_ui()
        self.material_checkboxes_ui()
        self.texture_checkboxes_ui()
        self.color_swatch_ui()
        self.bracelet_button_ui()

    def lengthwidth_sliders_ui(self):
        """Function that Creates Sliders for Length and Width"""

        lwslider_group = QtWidgets.QGroupBox('Size:')
        lwsliders_layout = QtWidgets.QVBoxLayout()

        self.length_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.length_slider.setMinimum(1)
        self.length_slider.setMaximum(4)
        lwsliders_layout.addWidget(QtWidgets.QLabel("Length"))
        lwsliders_layout.addWidget(self.length_slider)

        self.width_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.width_slider.setMinimum(1)
        self.width_slider.setMaximum(3)
        lwsliders_layout.addWidget(QtWidgets.QLabel("Width"))
        lwsliders_layout.addWidget(self.width_slider)

        lwslider_group.setLayout(lwsliders_layout)
        self.layout.addWidget(lwslider_group)

    def material_checkboxes_ui(self):
        """Creates Checkboxes for Materials"""
        material_chebox_group = QtWidgets.QGroupBox('Materials:')
        material_chebox_layout = QtWidgets.QGridLayout()
        self.material_checkboxes = {}
        materials = ['Beads', 'Leather']

        for item, material_type in enumerate(materials):
            checkbox = QtWidgets.QCheckBox(material_type)

            self.material_checkboxes[material_type] = checkbox
            material_chebox_layout.addWidget(checkbox, item // 3, item % 3)

        material_chebox_group.setLayout(material_chebox_layout)
        self.layout.addWidget(material_chebox_group)

    def texture_checkboxes_ui(self):
        """Checkboxes for Material Texture & Formating Label"""
        texture_chebox_group = QtWidgets.QGroupBox("Material Texture:")
        texture_chebox_layout = QtWidgets.QVBoxLayout()
        self.texture_checkboxes = {}
        texture_categories = ['Beads', 'Leather']
        texture_options = [['Wood', 'Marble',], ['Smooth', 'Rough']]

        for category, options in zip(texture_categories, texture_options):
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{category}:")
            row.addWidget(label)

            for texture_type in options:
                name = f"{category}_{texture_type}"
                checkbox = QtWidgets.QCheckBox(texture_type)
                checkbox.stateChanged.connect(self.texture_choice_limiter)

                self.texture_checkboxes[name] = checkbox
                row.addWidget(checkbox)

            texture_chebox_layout.addLayout(row)

        texture_chebox_group.setLayout(texture_chebox_layout)
        self.layout.addWidget(texture_chebox_group)

    def color_swatch_ui(self):
        """Color picker for Material Color"""
        color_swatch_group = QtWidgets.QGroupBox("Material Color:")
        color_swatch_layout = QtWidgets.QVBoxLayout()
        self.color_widgets = {}
        material_categories = ['Beads', 'Leather']

        for material_type in material_categories:
            row = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"{material_type}:")
            row.addWidget(label)

            swatch = ColorSwatch()
            swatch.setFixedSize(100, 20)
            swatch.setStyleSheet("background-color: rgb(255, 255, 255);")
            swatch.clicked.connect(lambda material_type=material_type:
                                   self.color_picker(material_type))

            row.addWidget(swatch)
            self.color_widgets[material_type] = {"swatch": swatch,
                                                 "color": (255, 255, 255)}
            color_swatch_layout.addLayout(row)

        color_swatch_group.setLayout(color_swatch_layout)
        self.layout.addWidget(color_swatch_group)

    def color_picker(self, material_type):
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            rgb = (color.red(), color.green(), color.blue())

            self.color_widgets[material_type]["color"] = rgb
            self.color_widgets[material_type]["swatch"].setStyleSheet(
                f"background-color: rgb{rgb};")

    def bracelet_button_ui(self):
        """Buttons for Generating Bracelet"""
        bracelet_button_layout = QtWidgets.QHBoxLayout()
        generate_btn = QtWidgets.QPushButton('Generate Bracelet')
        generate_btn.clicked.connect(self.generate_bracelet)

        bracelet_button_layout.addWidget(generate_btn)
        self.layout.addLayout(bracelet_button_layout)

    def texture_choice_limiter(self):
        """UI Function that Limits Texture to One"""
        texture_groups = {'Beads': ['Beads_Wood', 'Beads_Marble'],
                          'Leather': ['Leather_Smooth', 'Leather_Rough']}

        for group, textures in texture_groups.items():
            selected = []
            for texture_type in textures:
                if self.texture_checkboxes[texture_type].isChecked():
                    selected.append(texture_type)
            if len(selected) == 1:
                for texture_type in textures:
                    if texture_type not in selected:
                        self.texture_checkboxes[texture_type].setEnabled(False)
            else:
                for texture_type in textures:
                    self.texture_checkboxes[texture_type].setEnabled(True)

    def generate_bracelet(self):
        """Generates bracelet by calling calling functions"""
        bracelet_length = self.length_slider.value()
        width_slider = self.width_slider.value()
        circle_curve = build_bracelet_curve(bracelet_length)
        selected_materials = []

        for name, checkbox in self.material_checkboxes.items():
            if checkbox.isChecked():
                selected_materials.append(name)

        if 'Beads' in selected_materials:
            bead_color = self.color_widgets['Beads']['color']
            bead_group = build_beads(circle_curve, width_slider)
            if self.texture_checkboxes['Beads_Wood'].isChecked():
                build_bead_wood_texture(bead_group, bead_color)
            else:
                build_bead_marble_texture(bead_group, bead_color)

        if 'Leather' in selected_materials:
            leather_color = self.color_widgets['Leather']['color']
            if self.texture_checkboxes['Leather_Rough'].isChecked():
                build_leather(circle_curve, width_slider, leather_color,
                              'Rough')
            else:
                build_leather(circle_curve, width_slider, leather_color,
                              'Smooth')


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
