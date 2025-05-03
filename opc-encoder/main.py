# Standard libraries
import sys, os, platform, traceback, re
from datetime import datetime

# Internal libraries
import encoding_adder as encoder
import encoding_remover as remover

# External libraries
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import *
from concurrent.futures import ThreadPoolExecutor
from screeninfo import get_monitors

class MainWindow(QMainWindow):
    # Encoding flag constants
    MARKER_ENCODING = "0"
    MARKER_ONLY_ENCODING = "0"
    SPECIAL_TOOL_ENCODING = "0"
    FIX_FILE_ENCODING = "0"
    MANUAL_TOOL_CHANGE_ENCODING = "0"
    STITCHED_ENCODING = "0"
    BALSA_ENCODING = "0"
    FLEX_ENCODING = "0"
    PARTIAL_ENCODING = "0"

    # Mappings
    CONTROLS_LIST = ["FAGOR", "FANUC"]

    CUSTOMER_MAP = {
        "GE VERNOVA": "1", "TPI": "2", "JUPITER BACH": "3"
    }

    BLADE_MAP = {
        # LM
        "LM441": "101", 
        "LM473": "102", 
        "LM622": "103",

        # GE
        "GE622": "201",   

        # MISC
        "WT20": "1",
        "2X": "2",  

    }

    CYCLE_MAP = {
        # === Downwind Shell (101–200)
        "DW SHELL": "101",
        "DW SHELL BATCH": "102",

        "DW SHELL FOAM": "111",

        "DW SHELL BALSA": "121",
        "DW SHELL BALSA FLEXLABEL": "122",

        # === Upwind Shell (201–300)
        "UW SHELL": "201",
        "UW SHELL BATCH": "202",

        "UW SHELL FOAM": "211",

        "UW SHELL BALSA": "221",
        "UW SHELL BALSA FLEXLABEL": "222",

        # === Shell Batch (301–400)
        # Shell Batch Foam
        "SHELL BATCH FOAM SHORT": "301",
        "SHELL BATCH FOAM SHORT FLEXLABEL": "302",
        "SHELL BATCH FOAM LONG": "311",
        "SHELL BATCH FOAM LONG FLEXLABEL": "312",

        # Shell Batch Balsa
        "SHELL BATCH BALSA SHORT": "321",
        "SHELL BATCH BALSA SHORT FLEXLABEL": "322",
        "SHELL BATCH BALSA LONG": "331",
        "SHELL BATCH BALSA LONG FLEXLABEL": "332",

        # === FTIP (401–500)
        "FTIP": "401",
        "FTIP SPECIAL TOOL": "402",
        "FTIP BATCH": "403",

        # === TESW / TE (501–600)
        "TESW": "501",
        "TE WEB": "511",
        "TE WEB BATCH": "512",

        # === LESW / LE (601–700)
        "LESW": "601",
        "LE WEB": "611",
        "LE WEB BATCH": "612",

        # === Web Batch (701–800)
        "WEB BATCH SHORT": "701",
        "WEB BATCH LONG": "702",

        # === CORE (801–900)
        # CORE ROOF
        "CORE ROOF": "801",

        # CORE REAR
        "CORE REAR ROOF": "811",
        "CORE REAR RIGHT WALL": "812",
        "CORE REAR LEFT WALL": "813",

        # CORE FRONT
        "CORE FRONT ROOF": "821",
        "CORE FRONT RIGHT WALL": "822",
        "CORE FRONT LEFT WALL": "823",

        # CORE RIGHT
        "CORE RIGHT FRONT": "831",
        "CORE RIGHT WALL": "832",

        # CORE LEFT
        "CORE LEFT FRONT": "841",
        "CORE LEFT WALL": "842",

        # === RIBS (901–1000)
        # RIBS GENERAL
        "RIBS": "901",

        # RIBS CORE
        "RIBS CORE": "911",

        # RIBS ROOF
        "RIBS ROOF REAR": "921",
        "RIBS ROOF FRONT": "922",

        # RIBS REAR
        "RIBS REAR RIGHT WALL": "931",
        "RIBS REAR LEFT WALL": "932",

        # RIBS FRONT
        "RIBS FRONT RIGHT WALL": "941",
        "RIBS FRONT LEFT WALL": "942",

        # === Miscellaneous (1–99)
        "FS": "1",
        "DOGBONES": "2",
        "AUXILIARY": "3",
        "RCO": "4",
        "TFB": "5",
        "TIPSW": "6"
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OPC File Encoder")

        # Size window based on primary monitor
        screen_width = next((m.width for m in get_monitors() if m.is_primary), 1280)
        width = int(screen_width / 3.2)
        height = int(width / 1.15)
        self.setMinimumSize(QSize(width, height))

        # State variables
        self.path = ""
        self.customer_encoding = None        
        self.blade_encoding = None
        self.cycle_encoding = None
        self.customer_rev_encoding = "0"
        self.acs_rev_encoding = "0"

        self.setup_ui()


    def setup_ui(self):
        layout = QVBoxLayout()

        # Create dropdowns and inputs
        self.controls_input = QComboBox()
        self.controls_input.addItems(self.CONTROLS_LIST)

        self.blade_input = QComboBox()
        self.blade_input.addItems(self.BLADE_MAP.keys())

        self.cycle_input = QComboBox()
        self.cycle_input.addItems(self.CYCLE_MAP.keys())

        self.customer_input = QComboBox()
        self.customer_input.addItems(self.CUSTOMER_MAP.keys())

        self.customer_rev_input = QLineEdit()
        self.customer_rev_input.setMaxLength(1)

        self.acs_rev_input = QLineEdit()

        self.file_label = QLabel("Input:")
        self.file_path_display = QLabel()

        self.file_dialog_reopen_button = QPushButton("Reopen")
        self.file_dialog_reopen_button.hide()



        # File dialog
        self.file_dialog = QFileDialog(self, "Select Directory to Encode")
        self.file_dialog.setFileMode(QFileDialog.FileMode.Directory)
        self.file_dialog.setOption(QFileDialog.Option.ShowDirsOnly)
        self.file_dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        self.file_dialog.setDirectory("Z:/NC/")


        # Add widgets to layout
        layout.addWidget(self.file_dialog)        
        layout.addLayout(self.row(self.file_label, self.file_path_display, self.file_dialog_reopen_button))
        layout.addWidget(self.create_row("Blade:", self.blade_input))
        layout.addWidget(self.create_row("Cycle:", self.cycle_input))
        layout.addWidget(self.create_row("Customer:", self.customer_input))
        layout.addWidget(self.create_row("Controller:", self.controls_input))
        layout.addWidget(self.create_row("Customer Rev:", self.customer_rev_input))
        layout.addWidget(self.create_row("ACS Rev:", self.acs_rev_input))
        self.encode_button = QPushButton("Encode")
        layout.addWidget(self.encode_button)

        self.container = QWidget()
        self.container.setLayout(layout)
        self.setCentralWidget(self.container)

        # Signal connections
        self.encode_button.clicked.connect(self.encode)
        self.blade_input.currentIndexChanged.connect(
            lambda index: self.set_encoding('blade', self.blade_input.itemText(index)))
        self.cycle_input.currentIndexChanged.connect(
            lambda index: self.set_encoding('cycle', self.cycle_input.itemText(index)))
        self.customer_input.currentIndexChanged.connect(
            lambda index: self.set_encoding('customer', self.customer_input.itemText(index)))
        self.file_dialog.fileSelected.connect(self.set_file_path)
        self.file_dialog.directoryEntered.connect(self.set_file_path)
        self.file_dialog_reopen_button.clicked.connect(lambda: self.file_dialog.show())

    def row(self, *widgets):
        layout = QHBoxLayout()
        for w in widgets:
            layout.addWidget(w)
        return layout

    def create_row(self, label_text, widget):
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.addWidget(QLabel(label_text))
        row_layout.addWidget(widget)
        row_widget.setLayout(row_layout)
        return row_widget

    def set_encoding(self, kind, name):
        if kind == 'blade':
            self.blade_encoding = self.BLADE_MAP.get(name, "")
        elif kind == 'cycle':
            self.cycle_encoding = self.CYCLE_MAP.get(name, "")
        elif kind == 'customer':
            self.customer_encoding = self.CUSTOMER_MAP.get(name, "")

    def set_file_path(self, path):
        self.path = path
        self.file_path_display.setText(path)
        self.file_dialog_reopen_button.show()

        def normalize_string(s):
            return re.sub(r'[^A-Z0-9]', '', s.upper())

        normalized_path = normalize_string(path)

        # Generic longest match finder
        def find_best_match(name_list):
            best_match = ""
            best_length = 0
            for name in name_list:
                norm_name = normalize_string(name)
                if norm_name in normalized_path and len(norm_name) > best_length:
                    best_match = name
                    best_length = len(norm_name)
            return best_match

        # Controls
        best_controls = find_best_match(self.CONTROLS_LIST)
        if best_controls:
            self.controls_input.setCurrentText(best_controls)

        # Customer
        best_customer = find_best_match(self.CUSTOMER_MAP)
        if best_customer:
            self.customer_input.setCurrentText(best_customer)
            self.set_encoding('customer', best_customer)

        # Blade
        best_blade = find_best_match(self.BLADE_MAP)
        if best_blade:
            self.blade_input.setCurrentText(best_blade)
            self.set_encoding('blade', best_blade)

        # Cycle
        best_cycle = find_best_match(self.CYCLE_MAP)
        if best_cycle:
            self.cycle_input.setCurrentText(best_cycle)
            self.set_encoding('cycle', best_cycle)


    def validate_inputs(self):
        return all([
            self.controls_input.currentText(),
            self.customer_input.currentText(),
            self.blade_input.currentText(),
            self.cycle_input.currentText(),
            self.path
        ])


    def process_file(self, file_path):
        try:
            remover.remove_encoding(file_path)
            encoder.add_encoding_single(
                file_path,
                self.controls_text,
                self.blade_encoding,
                self.cycle_encoding,
                self.MARKER_ENCODING,
                self.MARKER_ONLY_ENCODING,
                self.SPECIAL_TOOL_ENCODING,
                self.FIX_FILE_ENCODING,
                self.MANUAL_TOOL_CHANGE_ENCODING,
                self.STITCHED_ENCODING,
                self.BALSA_ENCODING,
                self.FLEX_ENCODING,
                self.customer_rev_encoding,
                self.acs_rev_encoding,
                self.customer_encoding
            )

        except Exception as e:
            print(f"Error processing file: {file_path}:{e}")
            QMessageBox.critical(self, "Error", f"Failed to process file: {file_path}")

    def process_file(self, file_path, errors):
        try:
            remover.remove_encoding(file_path)
            encoder.add_encoding_single(
                file_path,
                self.controls_text,
                self.blade_encoding,
                self.cycle_encoding,
                self.MARKER_ENCODING,
                self.MARKER_ONLY_ENCODING,
                self.SPECIAL_TOOL_ENCODING,
                self.FIX_FILE_ENCODING,
                self.MANUAL_TOOL_CHANGE_ENCODING,
                self.STITCHED_ENCODING,
                self.BALSA_ENCODING,
                self.FLEX_ENCODING,
                self.customer_rev_encoding,
                self.acs_rev_encoding,
                self.customer_encoding
            )
        except Exception as e:
            errors.append(f"{file_path}: {e}")

    def encode(self):
        # Pull current values freshly from combo boxes
        blade_name = self.blade_input.currentText()
        cycle_name = self.cycle_input.currentText()
        customer_name = self.customer_input.currentText()

        self.controls_text = self.controls_input.currentText()
        self.blade_encoding = self.BLADE_MAP.get(blade_name, "")
        self.cycle_encoding = self.CYCLE_MAP.get(cycle_name, "")
        self.customer_encoding = self.CUSTOMER_MAP.get(customer_name, "")

        if not self.validate_inputs():
            QMessageBox.warning(self, "Invalid Input", "Please complete all fields.")
            return

        if not self.customer_encoding or not self.blade_encoding or not self.cycle_encoding:
            QMessageBox.warning(self, "Invalid Encoding", "Missing encoding for one or more fields.")
            return

        rev = self.customer_rev_input.text().strip().lower()
        self.customer_rev_encoding = str(ord(rev) - ord('a') + 1) if rev.isalpha() and len(rev) == 1 else "0"
        acs_rev = self.acs_rev_input.text().strip()
        self.acs_rev_encoding = acs_rev if acs_rev else "0"

        file_paths = []
        for dirpath, _, filenames in os.walk(self.path):
            if "ARCHIVE" in dirpath.upper() or "TRIAL" in dirpath.upper():
                continue
            for f in filenames:
                if f.lower().endswith('.nc') and "LOOP" not in f.upper():
                    file_path = os.path.join(dirpath, f)
                    file_paths.append(file_path)
                    
        errors = []
        try:
            with ThreadPoolExecutor() as executor:
                for path in file_paths:
                    executor.submit(self.process_file, path, errors)

            if errors:
                error_report = "\n".join(errors[:10])
                more = f"\n\n...and {len(errors) - 10} more." if len(errors) > 10 else ""
                QMessageBox.warning(self, "Some Files Failed", f"Encoding completed with issues:\n\n{error_report}{more}")
            else:
                QMessageBox.information(self, "Success", "Encoding completed successfully")

        except Exception:
            tb = traceback.format_exc()
            QMessageBox.critical(self, "Encoding Error", f"An error occurred:\n{tb}")


class OPCFileEncoderApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.window = MainWindow()
        self.window.show()

if __name__ == "__main__":
    app = OPCFileEncoderApp(sys.argv)
    sys.exit(app.exec())
