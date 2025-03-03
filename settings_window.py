from pathlib import Path

import pyqtgraph as pg
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (QFileDialog, QGridLayout, QHBoxLayout, QLineEdit,
                             QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView)

from utils import *





class SettingsWindow(QWidget):
  def __init__(self, config: PokerConfig, bg_color: str = "rgb(120,120,120)"):
    super().__init__()
    self.resize(WindowGeometry.SETTINGS.value)
    self.setStyleSheet(f" background-color: {bg_color};")
    self.cfg = config
    if self.cfg.LEVELS == list() or self.cfg.LEVELS == -1: # if uninitialized
      raise ValueError("LEVELS are empty in the config file")

    self.x = range(len(self.cfg.LEVELS))

    self.sizePolicy_Std = get_std_size_policy(self)
    grand_layout = QHBoxLayout(self)
    self.setLayout(grand_layout)

    self.config_label = MyLabel("config_label", self.cfg.NAME)

    # Buttons
    self.buttons = {}
    self.buttons["load_config"] = MyPushButton("config_load", text="Load Config", whats_this="Loads Config from file")
    self.buttons["save_config"] = MyPushButton("config_save", text="Save Config", whats_this="Saves Config to a file")

    # Config
    tablewidget= QTableWidget()
    tablewidget.setSizePolicy(get_std_size_policy(tablewidget))
    tablewidget.setColumnCount(2)
    tablewidget.setRowCount(len(self.cfg.LEVELS))
    tablewidget.setAutoFillBackground(True)
    tablewidget.setAlternatingRowColors(True)
    tablewidget.setHorizontalHeaderItem(0, QTableWidgetItem("BIG BLIND"))
    tablewidget.setHorizontalHeaderItem(1, QTableWidgetItem("PERIOD"))
    tablewidget.setStyleSheet("text-align: center; color: black")
    for level in self.cfg.LEVELS:
      lid = level["id"]
      bb = level["bb"]
      period = level["period"]
      tablewidget.setItem(lid, 0,  QTableWidgetItem(f"{bb}"))
      tablewidget.setItem(lid, 1,  QTableWidgetItem(f"{period.m}:{period.s}"))


    tablewidget.itemChanged.connect(self.update_config_on_cell_changed)

    tablewidget.horizontalHeader().setStretchLastSection(True)
    tablewidget.horizontalHeader().setSectionResizeMode(
        QHeaderView.Stretch)
    self.tablewidget = tablewidget


    # Graph
    self.graphWidget = pg.PlotWidget(self)
    self.graphWidget.setSizePolicy(self.sizePolicy_Std)

    pen = pg.mkPen(width=10, style=QtCore.Qt.DashDotDotLine)
    bb_values = [level["bb"] for level in self.cfg.LEVELS]
    self.data_line_y = self.graphWidget.plot(self.x, bb_values, name="X", pen=pen, symbol="o", symbolSize=30, symbolBrush=('r'))
    styles = {'color':'r', 'font-size':'20px'}
    self.graphWidget.setLabel('left', 'BigBlind', **styles)
    self.graphWidget.setLabel('bottom', 'Level', **styles)
    self.graphWidget.addLegend()
    self.graphWidget.setMouseEnabled(False,False)
    self.graphWidget.showGrid(x=True, y=True)
    self.graphWidget.setBackground('w')


    HLay = QHBoxLayout()
    HLay.addWidget(self.buttons["load_config"])
    HLay.addWidget(self.buttons["save_config"])

    VLay = QVBoxLayout()
    VLay.addWidget(self.config_label)
    VLay.addWidget(self.tablewidget)
    VLay.addLayout(HLay)

    self.grand_lay_objs = [self.graphWidget,
                           VLay]

    for x in self.grand_lay_objs:
      if isinstance(x, QGridLayout | QHBoxLayout | QVBoxLayout):
        grand_layout.addLayout(x)
      else:
        grand_layout.addWidget(x)

    # Events + Actions
    self.resizeEvent = self.customResizeEvent
    self.buttons["load_config"].clicked.connect(self.load_config_from_a_file)
    self.buttons["save_config"].clicked.connect(self.save_config_to_a_file)

  def load_config_from_a_file(self):
    json_path = Path(QFileDialog(self, directory="configs").getOpenFileName(filter="File (*.json)")[0])
    config = load_config_from_json(json_path)
    if config:
      print(f"Valid config found at {json_path}!")
      for name, val in config.__dict__.items():
        setattr(self.cfg, name, val)
      print(self.cfg)
      self.update()

  def save_config_to_a_file(self):
    config_writeable = dump_config_to_json(self.cfg)
    if config_writeable:
      json_path = Path(QFileDialog(self, directory="configs").getSaveFileName(filter="File (*.json)")[0])
      if ".json" != json_path.suffix:
        json_path = json_path.with_suffix(".json")

      config_writeable["NAME"] = json_path.name.rstrip(json_path.suffix).upper()
      json_object = json.dumps(config_writeable, indent=4)
      with open(json_path, "w") as outfile:
          outfile.write(json_object)

  def update_config_on_cell_changed(self, item : QTableWidgetItem):
      level_id = item.row()
      if item.column() == 0:
        key = "bb"
        new_cell_value = int(item.data(0))
      if item.column() == 1:
        key = "period"
        time_list = [int(x) for x in item.data(0).split(":")]
        print(time_list)
        new_cell_value = MyTime(*time_list)

      self.cfg.LEVELS[level_id][key] = new_cell_value
      self.update_data_line_y()
      
  def customResizeEvent(self, event) -> None:
    width = self.width()
    height = self.height()
    if width >= self.maximumWidth():
      width = self.maximumWidth()
    ButtonLCFontSize = int(width / 60)
    font = self.buttons["load_config"].font()
    font.setPointSize(ButtonLCFontSize)
    self.buttons["load_config"].setFont(font)
    self.buttons["save_config"].setFont(font)
    self.config_label.setFont(font)

    from math import floor
    w = floor(width*0.45)
    self.graphWidget.setMinimumWidth(w)
    self.tablewidget.setMinimumHeight(int(height*0.6))
    font = self.tablewidget.font()
    ButtonLCFontSize = int(width / 80)
    font.setPointSize(ButtonLCFontSize)
    self.tablewidget.setFont(font)
    self.tablewidget.resizeRowsToContents()
    self.tablewidget.resizeColumnsToContents()
    self.tablewidget.horizontalHeader().setFont(font)
    self.tablewidget.verticalHeader().setFont(font)
    self.tablewidget.horizontalHeaderItem(0).setFont(font)
    self.tablewidget.horizontalHeaderItem(1).setFont(font)

  def update_data_line_y(self):
    self.x = range(len(self.cfg.LEVELS))
    bb_values = [level["bb"] for level in self.cfg.LEVELS]
    self.data_line_y.setData(self.x, bb_values)

  def update(self):
    self.x = range(len(self.cfg.LEVELS))
    bb_values = [level["bb"] for level in self.cfg.LEVELS]
    self.data_line_y.setData(self.x, bb_values)

    self.config_label.setText(self.cfg.NAME)

    for x in range(self.tablewidget.rowCount()):
      self.tablewidget.removeRow(x)
    self.tablewidget.setRowCount(len(bb_values))
    for id, level in enumerate(self.cfg.LEVELS):
      self.tablewidget.setItem(id, 0,  QTableWidgetItem(str(level["bb"])))
      self.tablewidget.setItem(id, 1,  QTableWidgetItem(f"{level['period'].m}:{level['period'].s}"))

