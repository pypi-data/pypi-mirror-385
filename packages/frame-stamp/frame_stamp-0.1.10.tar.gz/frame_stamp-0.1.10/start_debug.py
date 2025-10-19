from PySide6.QtWidgets import QApplication

from frame_stamp.viewer.dialog import TemplateViewer

app = QApplication([])
v = TemplateViewer()
v.show()
app.exec()