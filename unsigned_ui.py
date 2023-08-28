# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from typing import Sequence

from PyQt5 import QtCore
from PyQt5.QtCore import QTimer, QSize
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget

from utils import (MyFonts, MyLabel, MyPushButton, WindowGeometry,
                   setupQFontDataBase)

'''
  Config:
  - Normal Small Blind value
  - Normal Small Blind step
  - Normal Level Time period
  - Heads Up Small Blind value
  - Heads Up Small Blind step
  - Heads Up Level Time period
'''

class PokerTimerWindow(QMainWindow):
  def __init__(self,
               geometry : QSize = WindowGeometry.FHD,
               max_geometry : QSize = WindowGeometry.UHD,
               init_level_period_m : int = 10,
               init_small_blind_step : int = 200):
    super().__init__()
    # POKER
    self.level_period = [init_level_period_m, 0]
    self.m = init_level_period_m
    self.s = 0
    self.l = 1
    self.sb = init_small_blind_step
    self.sec_cnt = 0
    self.time_step_ms = 10
    self.timer_running = False
    # Setup the Window
    self.setMaximumHeight(max_geometry.height())
    self.setMaximumWidth(max_geometry.width())
    self.setup_window(geometry)
    self.show()

  def setup_window(self,
                   geometry : WindowGeometry = WindowGeometry.FHD):
    # QT
    self.setObjectName("MainWindow")
    self.resize(geometry)
    from pathlib import Path
    img = Path("dumb.jpg")
    self.setStyleSheet("#MainWindow { "
                       f" border-image: url({img.absolute()}) 0 0 0 0 stretch stretch;"
                       "}")
    self.gridLayout = QGridLayout(self)
    self.gridLayout.setObjectName("gridLayout")
    # QFontDataBase
    self.qfontdb = setupQFontDataBase()
    # QTWidgets
    ## Timer
    self.timer = QTimer(self.gridLayout)
    ## Labels
    self.timer_label = MyLabel("Timer", MyFonts.Timer)
    self.level_label = MyLabel("Level", MyFonts.Blinds, border_color="transparent", bg_color="transparent",
                               layout_dir=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter)
    self
    self.blinds_label = MyLabel("CurBlinds", MyFonts.Blinds)
    self.next_blinds_label = MyLabel("NxtBlinds", MyFonts.Blinds, border_color="transparent", bg_color="transparent",
                                     layout_dir=QtCore.Qt.AlignmentFlag.AlignBottom | QtCore.Qt.AlignmentFlag.AlignHCenter)
    ## PushButtons
    self.pb_prev_level = MyPushButton("prev_lvl_pb")
    self.pb_next_lvl = MyPushButton("next_lvl_pb")
    self.pb_headsup = MyPushButton("headsup_pb")
    self.pb_reset = MyPushButton("reset_pb")
    self.pb_start_stop = MyPushButton("start_stop_pb")

    # Add Widgets to Layout
    # Upper section
    self.gridLayout.addWidget(self.timer_label      , 0, 2, 3, 3)
    self.gridLayout.addWidget(self.blinds_label     , 0, 0, 3, 2)
    self.gridLayout.addWidget(self.level_label      , 0, 0, 1, 2)
    self.gridLayout.addWidget(self.next_blinds_label, 2, 0, 1, 2)
    # Lower section
    self.gridLayout.addWidget(self.pb_prev_level, 3, 2, 1, 1)
    self.gridLayout.addWidget(self.pb_start_stop, 3, 3, 1, 1)
    self.gridLayout.addWidget(self.pb_next_lvl  , 3, 4, 1, 1)
    self.gridLayout.addWidget(self.pb_reset     , 3, 0, 1, 2)
    self.gridLayout.addWidget(self.pb_headsup   , 4, 0, 1, 2)

    self.retranslateUi() # change labels

    # Setup the Central Widget
    widget = QWidget()
    widget.setLayout(self.gridLayout)
    self.setCentralWidget(widget)

    QtCore.QMetaObject.connectSlotsByName(self)

    # Connect widgets to actions
    self.pb_next_lvl.clicked.connect(self.next_level_button_action) # type: ignore
    self.pb_prev_level.clicked.connect(self.prev_level_button_action) # type: ignore
    self.pb_headsup.clicked.connect(self.headsup_button_action) # type: ignore
    self.pb_reset.clicked.connect(self.reset_button_action)
    self.pb_start_stop.clicked.connect(self.start_stop_timer)
    self.timer.timeout.connect(self.showTime)

    # Initialize texts
    self.update_texts()

    # Resize Event
    self.resizeEvent = self.customResizeEvent

  # Event methods
  def customResizeEvent(self, event):
    self.updateFonts()

  def update_texts(self):
    self.timer_label.setText(f"{self.m}{self.vanishing_comma(self.sec_cnt)}{self.s:02d}")
    self.blinds_label.setText(f"{self.l * self.sb}/{self.l * self.sb * 2}")
    self.next_blinds_label.setText(f"nextB:{(self.l+1) * self.sb}/{(self.l+1) * self.sb * 2}")
    self.level_label.setText(f"Level {self.l:02d}")

  # method called by timer
  def showTime(self):
    self.sec_cnt += self.time_step_ms
    if self.sec_cnt == 1000:
      self.sec_cnt = 0
      self.l, self.m, self.s = self.update_level_and_time(self.l, self.m, self.s)
    self.update_texts()

  def vanishing_comma(self,
                      sec_cnt: int,
                      on_time: int = 100,
                      position: int = 300):
    if (sec_cnt > position) and (sec_cnt < (position + on_time)):
      return " "
    return ":"

  def start_stop_timer(self):
    if self.timer_running:
      self.timer.stop()
      self.pb_start_stop.setText("Start")
      self.pb_start_stop.setStyleSheet("background-color: rgba(220,220,220,95%);"
                                       "border: 2px solid black;"
                                       "color: black;")
    else:
      self.timer.start(self.time_step_ms)
      self.pb_start_stop.setText("Stop")
      self.pb_start_stop.setStyleSheet("background-color: rgba(40,40,40,95%);"
                                       "border: 2px solid black;"
                                       "color: white;")
    self.timer_running = not self.timer_running
    self.pb_start_stop.repaint()

  def update_level_and_time(self, l, m, s):
    if m == 0 and s == 0:
      return l+1, *self.level_period
    if s == 0:
      return l, m-1, 59
    return l, m, s-1

  # Actions
  def next_level_button_action(self):
    self.l += 1
    self.m, self.s = self.level_period
    self.update_texts()

  def prev_level_button_action(self):
    if self.l != 1:
      self.l -= 1
    self.m, self.s = self.level_period
    self.update_texts()

  def headsup_button_action(self):
    self.l = 1
    self.m, self.s = 10, 0
    self.sb = 1000
    self.update_texts()

  def reset_button_action(self):
    self.l = 1
    self.m, self.s = self.level_period
    self.sb = 100
    self.update_texts()

  def updateFonts(self, dividers : Sequence = [8,18,30]):
    # Calculate font sizes based on window width and height
    width = self.width()
    if width >= self.maximumWidth():
      width = self.maximumWidth()

    class FontReSize:
      S1 = int(width / dividers[0])
      S2 = int(width / dividers[1])
      S3 = int(width / dividers[2])
      S4 = int(width / 30)

    def update_font(obj, font_size):
      # Update font sizes keeping other font parameters correct
      font = obj.font()
      font.setPointSize(font_size)
      obj.setFont(font)
      return obj

    self.timer_label = update_font(self.timer_label, FontReSize.S1)
    self.blinds_label = update_font(self.blinds_label, FontReSize.S2)
    self.level_label = update_font(self.level_label, FontReSize.S3)
    self.pb_next_lvl = update_font(self.pb_next_lvl, FontReSize.S3)
    self.pb_prev_level = update_font(self.pb_prev_level, FontReSize.S3)
    self.pb_headsup = update_font(self.pb_headsup, FontReSize.S3)
    self.pb_start_stop = update_font(self.pb_start_stop, FontReSize.S3)
    self.pb_reset = update_font(self.pb_reset, FontReSize.S3)
    self.next_blinds_label = update_font(self.next_blinds_label, FontReSize.S4)

  def retranslateUi(self):
    _translate = QtCore.QCoreApplication.translate
    self.setWindowTitle(_translate("MainWindow", "PokerTimer"))
    self.timer_label.setText(_translate("MainWindow", "TextLabel"))
    self.blinds_label.setText(_translate("MainWindow", "TextLabel"))
    self.next_blinds_label.setText(_translate("MainWindow", "TextLabel"))
    self.level_label.setText(_translate("MainWindow", "TextLabel"))
    self.pb_prev_level.setText(_translate("MainWindow", "<="))
    self.pb_next_lvl.setText(_translate("MainWindow", "=>"))
    self.pb_headsup.setText(_translate("MainWindow", "HeadsUp"))
    self.pb_reset.setText(_translate("MainWindow", "Reset"))
    self.pb_start_stop.setText(_translate("MainWindow", "Start"))


if __name__ == "__main__":
  import sys
  app = QApplication(sys.argv)
  import argparse as argp
  parser = argp.ArgumentParser()
  parser.add_argument("--sb-step", default=200, type=int)
  parser.add_argument("--round-period", default=10, type=int)
  args = parser.parse_args()
  ptw = PokerTimerWindow(geometry=WindowGeometry.VGA,
                         init_level_period_m=args.round_period,
                         init_small_blind_step=args.sb_step)
  sys.exit(app.exec_())