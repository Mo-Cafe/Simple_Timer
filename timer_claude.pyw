import sys
import winsound
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSpinBox, QGridLayout, QProgressBar
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QFont, QColor

class TimerWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                color: #333;
                font-family: 'Segoe UI', 'Malgun Gothic', 'Nanum Gothic', sans-serif;
            }
            QPushButton {
                border: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
                padding: 8px;
                color: white;
            }
            QPushButton:hover {
                opacity: 0.8;
            }
            QLabel {
                font-weight: bold;
            }
            QSpinBox {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 18px;
            }
        """)
        
        # Timer display
        self.time_display = QLabel('00:00:00')
        self.time_display.setFont(QFont('Segoe UI', 70, QFont.Bold))
        self.time_display.setStyleSheet("""
            color: #2c3e50;
            background-color: white;
            border-radius: 15px;
            padding: 15px;
        """)
        self.time_display.setAlignment(Qt.AlignCenter)
        self.time_display.setFixedHeight(120)
        main_layout.addWidget(self.time_display)
        
        # Progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid grey;
                border-radius: 5px;
                background-color: #f0f0f0;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #b03112;
            }
        """)
        self.progress_bar.setFixedHeight(25)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Time input layout
        time_input_container = QHBoxLayout()
        time_input_container.setContentsMargins(0, 5, 0, 5)
        
        time_labels = ['시간', '분', '초']
        self.time_inputs = []
        
        for i, label in enumerate(time_labels):
            input_label_layout = QHBoxLayout()
            input_label_layout.setSpacing(2)
            
            spin_box = QSpinBox()
            spin_box.setRange(0, 59 if i > 0 else 23)
            spin_box.setFont(QFont('Segoe UI', 18))
            spin_box.setFixedSize(90, 50)  # 입력 칸 가로 크기 증가
            spin_box.setAlignment(Qt.AlignCenter)
            spin_box.setButtonSymbols(QSpinBox.UpDownArrows)
            spin_box.setSpecialValueText(" ")
            input_label_layout.addWidget(spin_box)
            self.time_inputs.append(spin_box)
            
            label_widget = QLabel(label)
            label_widget.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            label_widget.setStyleSheet("font-size: 18px; color: #34495e; padding-left: 2px;")
            input_label_layout.addWidget(label_widget)
            
            time_input_container.addLayout(input_label_layout)
        
        time_input_container.addStretch(1)
        time_input_container.insertStretch(0, 1)
        
        main_layout.addLayout(time_input_container)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(5, 0, 5, 0)
        
        self.start_button = QPushButton('START')
        self.start_button.setStyleSheet("background-color: #66bb6a;")
        self.start_button.clicked.connect(self.start_timer)
        
        self.reset_button = QPushButton('RESET')
        self.reset_button.setStyleSheet("background-color: #FF6F6F;")
        self.reset_button.clicked.connect(self.reset_timer)
        
        for button in [self.start_button, self.reset_button]:
            button.setFixedHeight(55)
            control_layout.addWidget(button)
        
        main_layout.addLayout(control_layout)
        
        main_layout.addSpacing(10)
        
        # Preset buttons
        preset_layout = QHBoxLayout()
        preset_layout.setContentsMargins(5, 0, 5, 0)
        presets = [('10초', 10), ('1분', 60), ('5분', 300), ('10분', 600), ('30분', 1800), ('1시간', 3600)]
        
        for label, seconds in presets:
            preset_button = QPushButton(label)
            preset_button.setStyleSheet("background-color: #87CEFA; font-size: 15px;")
            preset_button.clicked.connect(lambda _, s=seconds: self.add_preset_time(s))
            preset_button.setFixedHeight(35)
            preset_layout.addWidget(preset_button)
        
        main_layout.addLayout(preset_layout)
        
        self.setLayout(main_layout)
        
        # Timer setup
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.remaining_time = 0
        self.total_time = 0
        self.is_paused = False
        
        self.setWindowTitle('타이머 by Claude')
        self.setFixedSize(600, 450)
        self.show()
        
    def start_timer(self):
        if not self.timer.isActive() and not self.is_paused:
            total_seconds = self.time_inputs[0].value() * 3600 + self.time_inputs[1].value() * 60 + self.time_inputs[2].value()
            if total_seconds > 0:
                self.remaining_time = total_seconds
                self.total_time = total_seconds
                self.update_display()
                self.progress_bar.setMaximum(total_seconds)
                self.progress_bar.setValue(total_seconds)
                self.timer.start(1000)
                self.start_button.setText('일시정지')
                self.start_button.setStyleSheet("background-color: #ffa726;")
            else:
                self.time_display.setText("시간을 설정하세요!")
                self.adjust_font_size()
        elif self.timer.isActive():
            self.timer.stop()
            self.is_paused = True
            self.start_button.setText('재시작')
            self.start_button.setStyleSheet("background-color: #66bb6a;")
        else:  # 일시정지 상태에서 재시작
            self.timer.start(1000)
            self.is_paused = False
            self.start_button.setText('일시정지')
            self.start_button.setStyleSheet("background-color: #ffa726;")
        
    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
            self.progress_bar.setValue(self.remaining_time)
        else:
            self.timer.stop()
            self.is_paused = False
            self.time_display.setText("시간 종료!")
            self.adjust_font_size()
            self.ring_alarm()
            self.start_button.setText('START')
            self.start_button.setStyleSheet("background-color: #66bb6a;")
        
    def reset_timer(self):
        self.timer.stop()
        self.remaining_time = 0
        self.total_time = 0
        self.is_paused = False
        self.update_display()
        self.progress_bar.setValue(0)
        self.start_button.setText('START')
        self.start_button.setStyleSheet("background-color: #66bb6a;")
        for spin_box in self.time_inputs:
            spin_box.setValue(0)
        
    def update_display(self):
        time = QTime(0, 0).addSecs(self.remaining_time)
        self.time_display.setText(time.toString("hh:mm:ss"))
        self.adjust_font_size()
        
    def add_preset_time(self, seconds):
        current_total_seconds = self.time_inputs[0].value() * 3600 + self.time_inputs[1].value() * 60 + self.time_inputs[2].value()
        new_total_seconds = current_total_seconds + seconds
        hours, remainder = divmod(new_total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.time_inputs[0].setValue(hours)
        self.time_inputs[1].setValue(minutes)
        self.time_inputs[2].setValue(seconds)
        if self.timer.isActive() or self.is_paused:
            self.remaining_time += seconds
            self.total_time += seconds
            self.progress_bar.setMaximum(self.total_time)
            self.update_display()
            self.progress_bar.setValue(self.remaining_time)
        
    def ring_alarm(self):
        for _ in range(5):
            winsound.Beep(800, 80)
            QTimer.singleShot(80, lambda: None)
            
    def adjust_font_size(self):
        font = self.time_display.font()
        if self.time_display.text() == "시간 종료!":
            font.setPointSize(int(70 * 0.8))
        else:
            font.setPointSize(70)
        self.time_display.setFont(font)
        
        while self.time_display.sizeHint().width() > self.time_display.width() - 40:
            font_size = font.pointSize() - 1
            if font_size < 20:
                break
            font.setPointSize(font_size)
            self.time_display.setFont(font)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TimerWidget()
    sys.exit(app.exec_())