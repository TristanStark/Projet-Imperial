import json
import os
import re
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QFileDialog, QMessageBox, QSpinBox
)
from PySide6.QtCore import Qt

class CityApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Créateur de Ville")
        self.setMinimumWidth(300)

        self.layout = QVBoxLayout()

        # Nom
        self.layout.addWidget(QLabel("Nom de la ville :"))
        self.nom_input = QLineEdit()
        self.layout.addWidget(self.nom_input)

        # Habitants
        self.layout.addWidget(QLabel("Nombre d'habitants :"))
        self.habitants_input = QSpinBox()
        self.habitants_input.setMaximum(1_000_000_000)
        self.layout.addWidget(self.habitants_input)

        # Type de ville
        self.layout.addWidget(QLabel("Type de ville :"))
        self.type_input = QComboBox()
        self.type_input.addItems(["Village", "Bourg", "Cité", "Métropole", "Ruines"])
        self.layout.addWidget(self.type_input)

        # Lier image
        self.png_path = None
        self.png_button = QPushButton("Lier une image (.png, .jpg, .webp)")
        self.png_button.clicked.connect(self.lier_image)
        self.layout.addWidget(self.png_button)

        # Sauvegarder
        self.save_button = QPushButton("Sauvegarder")
        self.save_button.clicked.connect(self.sauvegarder)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

        os.makedirs("villes", exist_ok=True)

    def lier_image(self):
        fichier, _ = QFileDialog.getOpenFileName(
            self, "Choisir une image", "", "Images (*.png *.jpg *.webp *.jpeg)"
        )
        if fichier:
            self.png_path = fichier
            nom_fichier = os.path.basename(fichier)
            self.png_button.setText(f"Image liée : {nom_fichier}")

            # Si le champ habitants est vide, essayer de l'extraire depuis le nom du fichier
            if self.habitants_input.value() == 0:
                match = re.match(r"^(\d+)", nom_fichier)
                if match:
                    self.habitants_input.setValue(int(match.group(1)))

    def sauvegarder(self):
        nom = self.nom_input.text().strip()
        if not nom:
            QMessageBox.warning(self, "Erreur", "Le nom de la ville est requis.")
            return

        data = {
            "nom": nom,
            "habitants": self.habitants_input.value(),
            "type": self.type_input.currentText(),
            "image": self.png_path or ""
        }

        fichier_json = f"./data/villes/{nom}.json"
        with open(fichier_json, "a+", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "Succès", f"Ville '{nom}' sauvegardée avec succès !")
        self.clear_fields()

    def clear_fields(self):
        self.nom_input.clear()
        self.habitants_input.setValue(0)
        self.type_input.setCurrentIndex(0)
        self.png_path = None
        self.png_button.setText("Lier une image (.png, .jpg, .webp)")

if __name__ == "__main__":
    app = QApplication([])
    window = CityApp()
    window.show()
    app.exec()
