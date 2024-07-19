import sys
import polib
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QLabel,
    QComboBox,
    QHeaderView,
    QProgressBar,
    QStatusBar,
)
from PyQt5.QtCore import Qt
from argostranslate import package, translate

FROM_CODES = ['en']
TO_CODES = ['fr', 'it', 'ja', 'ru', 'ug', 'vn', 'ur', 'th', 'zt', 'bn']


class TranslationTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PO File Translation Tool')
        self.setGeometry(100, 100, 800, 600)
        
        self.install_argos_packages(FROM_CODES, TO_CODES)
        self.installed_languages = translate.get_installed_languages()
        

        for lang in self.installed_languages:
            print(f"Language Name: {lang.name}, Language Code: {lang.code}")

        self.loadButton = QPushButton('Load .po File', self)
        self.loadButton.clicked.connect(self.load_po_file)
        
        self.fromLanguageLabel = QLabel('Translation:', self)
        self.fromLanguageComboBox = QComboBox(self)
        for lang in FROM_CODES:
            self.fromLanguageComboBox.addItem(lang)
        self.toLanguageLabel = QLabel('->', self)
        self.toLanguageComboBox = QComboBox(self)
        for lang in TO_CODES:
            self.toLanguageComboBox.addItem(lang)
        self.translateOneButton = QPushButton('Translate Selected Cell', self)
        self.translateOneButton.clicked.connect(self.translate_one)
        self.translateAllButton = QPushButton('Translate All Cells', self)
        self.translateAllButton.clicked.connect(self.translate_all)
        
        languageLayout = QHBoxLayout()
        languageLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        languageLayout.addWidget(self.fromLanguageLabel)
        languageLayout.addWidget(self.fromLanguageComboBox)
        languageLayout.addWidget(self.toLanguageLabel)
        languageLayout.addWidget(self.toLanguageComboBox)
        languageLayout.addWidget(self.translateOneButton)
        languageLayout.addWidget(self.translateAllButton)
        
        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels([
            'Source Text',
            'Translated Text',
            # 'Translator Comments',
            # 'Extracted Comments',
            # 'Occurences',
            # 'Flags',
        ])
        self.table.setColumnWidth(0, 400)
        self.table.setColumnWidth(1, 400)
        # self.table.setColumnWidth(2, 150)
        # self.table.setColumnWidth(3, 150)
        # self.table.setColumnWidth(4, 150)
        # self.table.setColumnWidth(5, 150)
        # self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        self.saveButton = QPushButton('Save .po File', self)
        self.saveButton.clicked.connect(self.save_po_file)
        
        layout = QVBoxLayout()
        layout.addWidget(self.loadButton)
        layout.addLayout(languageLayout)
        layout.addWidget(self.table)
        layout.addWidget(self.saveButton)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def install_argos_packages(self, from_codes, to_codes):
        package.update_package_index()
        available_packages = package.get_available_packages()
        for pkg in available_packages:
            print(f"Package: From {pkg.from_code} to {pkg.to_code}")

        for from_code in from_codes:
            for to_code in to_codes:
                if from_code != to_code:
                    package_to_install = next(
                        filter(
                            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
                        ),
                        None
                    )
                    if package_to_install:
                        print(f'Installing package: {from_code} -> {to_code}')
                        package.install_from_path(package_to_install.download())
    
    def load_po_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        fileName, _ = QFileDialog.getOpenFileName(self, "Open .po File", "", "PO Files (*.po);;All Files (*)", options=options)
        if fileName:
            self.parse_po_file(fileName)
    
    def parse_po_file(self, file_path):
        self.po_entries = polib.pofile(file_path)
        self.metadata = self.po_entries.metadata
        self.table.setRowCount(len(self.po_entries))
        for row, entry in enumerate(self.po_entries):
            self.table.setItem(row, 0, QTableWidgetItem(entry.msgid))
            self.table.setItem(row, 1, QTableWidgetItem(entry.msgstr))
            # self.table.setItem(row, 2, QTableWidgetItem(entry.tcomment))
            # self.table.setItem(row, 3, QTableWidgetItem(entry.comment))
            # self.table.setItem(row, 4, QTableWidgetItem(self.occurences_to_str(entry.occurrences)))
            # self.table.setItem(row, 5, QTableWidgetItem(self.flags_to_str(entry.flags)))
        self.table.cellChanged.connect(self.cell_changed)
    
    # def occurences_to_str(self, occurrences_as_lst):
    #     return ';'.join([f'{file}:{line}' for file, line in occurrences_as_lst])
    
    # def occurences_from_str(self, occurrences_as_str):
    #     return [(occurrence.split(':')[0], occurrence.split(':')[1]) for occurrence in occurrences_as_str.split(';')]
    
    # def flags_to_str(self, flags_as_lst):
    #     return ','.join(flags_as_lst)
    
    # def flags_from_str(self, flags_as_str):
    #     return flags_as_str.split(',')
    
    def cell_changed(self, row, column):
        if column == 1:
            self.table.cellChanged.disconnect(self.cell_changed)
            self.po_entries[row].msgstr = self.table.item(row, column).text()
            if row < self.table.rowCount() - 1:
                next_row = row + 1
                self.table.setCurrentCell(next_row, column)
                self.table.editItem(self.table.item(next_row, column))
            self.table.cellChanged.connect(self.cell_changed)
    
    def translate_one(self):
        self.table.cellChanged.disconnect(self.cell_changed)
        translation = self.get_translation()
        current_row = self.table.currentRow()
        if current_row != -1:
            source_text = self.table.item(current_row, 0).text()
            translated_text = translation.translate(source_text)
            self.table.setItem(current_row, 1, QTableWidgetItem(translated_text))
            self.po_entries[current_row].msgstr = self.table.item(current_row, 1).text()
        self.table.cellChanged.connect(self.cell_changed)
    
    def translate_all(self):
        self.table.cellChanged.disconnect(self.cell_changed)
        translation = self.get_translation()
        for row in range(self.table.rowCount()):
            source_text = self.table.item(row, 0).text()
            translated_text = translation.translate(source_text)
            self.table.setItem(row, 1, QTableWidgetItem(translated_text))
            self.po_entries[row].msgstr = self.table.item(row, 1).text()
        self.table.cellChanged.connect(self.cell_changed)
    
    def get_translation(self):
        from_code = self.fromLanguageComboBox.currentText()
        to_code = self.toLanguageComboBox.currentText()
        from_lang = list(filter(
                lambda x: x.code == from_code,
                self.installed_languages
            ))[0]
        to_lang = list(filter(
                lambda x: x.code == to_code,
                self.installed_languages
            ))[0]
        return from_lang.get_translation(to_lang)
    
    def save_po_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save .po File", "", "PO Files (*.po);;All Files (*)", options=options)
        if fileName:
            self.po_entries.save(fileName)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translation_tool = TranslationTool()
    translation_tool.show()
    sys.exit(app.exec_())
