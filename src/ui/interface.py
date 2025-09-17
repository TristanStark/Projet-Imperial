import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from src.ui.midjourney import MidjourneyFrame

from src.app.pnj_physique import PNJPhysique
from src.services.chatgpt_service import ChatGPT
from src.models.pnj import PNJQuery


class PNJGeneratorApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Générateur de PNJ")
        self.root.geometry("650x500")
        self.root.resizable(False, False)

        # Service
        self.pnj_service = PNJPhysique(export_path="export")
        self.generated_files = []

        # Variables
        self.pnj_var = tk.StringVar(value="0")
        self.folder_var = tk.StringVar()
        self.job_var = tk.StringVar()

        # Notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self._init_pnj_tab()
        self._init_midjourney_tab()

    def _init_pnj_tab(self):
        self.pnj_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.pnj_tab, text="Générateur de PNJ")

        # Widgets
        tk.Label(self.pnj_tab, text="Nombre de PNJ à générer:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.pnj_tab, textvariable=self.pnj_var, width=20).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.pnj_tab, text="Métier du PNJ (optionnel):").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        tk.Entry(self.pnj_tab, textvariable=self.job_var, width=20).grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self.pnj_tab, text="Dossier de sortie:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        folder_entry = tk.Entry(self.pnj_tab, textvariable=self.folder_var, width=20, state="disabled")
        folder_entry.grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self.pnj_tab, text="Parcourir", command=self.browse_and_open_folder).grid(row=2, column=2, padx=10, pady=5)

        tk.Label(self.pnj_tab, text="Custom Request:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.custom_request = tk.Text(self.pnj_tab, width=30, height=5)
        self.custom_request.grid(row=3, column=1, padx=10, pady=5, columnspan=2)

        self.progress_bar = ttk.Progressbar(self.pnj_tab, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=4, column=0, columnspan=3, pady=10)

        self.progress_label = tk.Label(self.pnj_tab, text="Progression : 0/0")
        self.progress_label.grid(row=5, column=0, columnspan=3, pady=5)

        self.time_label = tk.Label(self.pnj_tab, text="Temps de génération : -")
        self.time_label.grid(row=6, column=0, columnspan=3, pady=5)

        self.spinner = tk.Label(self.pnj_tab, text="⏳ Génération en cours...", font=("Arial", 12))
        self.spinner.grid(row=7, column=0, columnspan=3, pady=5)
        self.spinner.grid_forget()

        tk.Button(self.pnj_tab, text="Générer", command=self.generate_pnjs).grid(row=8, column=0, columnspan=3, pady=10)

    def _init_midjourney_tab(self):
        self.midjourney_tab = MidjourneyFrame(self.notebook)
        self.notebook.add(self.midjourney_tab, text="Midjourney")
        self.notebook.pack(fill="both", expand=True)

    def browse_and_open_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            os.startfile(folder_selected)
            self.folder_var.set(folder_selected)
            self.midjourney_tab.change_path(folder_selected)

    def generate_single_pnj(self, output_folder: str, custom_request: str = None):
        output_path = Path(output_folder)
        self.pnj_service.change_export_path(output_path)

        query = ChatGPT.getMessageWithJSON(custom_request, PNJQuery) if custom_request else None
        pnj = self.pnj_service.generate(custom=query)
        self.pnj_service.export_to_foundry(pnj)
        self.midjourney_tab.add_module(pnj.token_name, pnj.description)


    def generate_pnjs(self):
        try:
            num_pnjs = int(self.pnj_var.get()) if not self.job_var.get() else 1
            custom_request_value = self.custom_request.get("1.0", "end-1c").strip()
            if num_pnjs <= 0 and not custom_request_value:
                raise ValueError("Le nombre de PNJ doit être supérieur à 0.")
            if custom_request_value:
                num_pnjs = 1
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un nombre entier supérieur à 0.")
            return

        output_folder = self.folder_var.get()
        if not output_folder:
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier de sortie.")
            return

        self.progress_bar["maximum"] = num_pnjs
        self.progress_bar["value"] = 0
        self.generated_files.clear()

        start_time = time.time()
        self.spinner.grid()
        self.root.update_idletasks()

        for i in range(num_pnjs):
            file_path = self.generate_single_pnj(output_folder, custom_request_value)
            self.generated_files.append(file_path)
            self.progress_bar["value"] += 1
            self.progress_label.config(text=f"Progression : {i + 1}/{num_pnjs}")
            self.root.update_idletasks()

        elapsed_time = time.time() - start_time
        self.time_label.config(text=f"Temps de génération : {elapsed_time:.2f} sec")
        self.spinner.grid_forget()
        messagebox.showinfo("Succès", f"{num_pnjs} PNJ ont été générés en {elapsed_time:.2f} sec.\nDossier : {output_folder}")
        self.progress_label.config(text="Progression terminée.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = PNJGeneratorApp()
    app.run()
