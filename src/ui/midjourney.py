import tkinter as tk
from tkinter import ttk
import os
from src.utils.tokenizer import Tokenizer

class ModuleFrame(tk.Frame):
    def __init__(self, parent, on_remove_callback):
        super().__init__(parent)
        self.on_remove_callback = on_remove_callback

        # Ligne 1 : nom et description
        tk.Label(self, text="Nom:").grid(row=0, column=0, sticky="w")
        self.entry_nom = tk.Entry(self)
        self.entry_nom.grid(row=0, column=1, padx=5)

        tk.Label(self, text="Description").grid(row=0, column=2, sticky="w", padx=(10, 0))
        self.entry_description = tk.Text(self, height=3, width=20)
        self.entry_description.grid(row=0, column=3, rowspan=2, padx=5, pady=5)

        # Ligne 2 : bouton
        self.bouton = tk.Button(self, text="Transformer", command=self.remove_self)
        self.bouton.grid(row=1, column=1, pady=5)

        # Séparateur horizontal
        ttk.Separator(self, orient='horizontal').grid(row=2, columnspan=4, sticky="ew", pady=5)

    def remove_self(self):
        self.on_remove_callback(self)


class MidjourneyFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.container = ttk.Frame(self)
        self.canvas = tk.Canvas(self.container)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.container.pack(fill="both", expand=True)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.original_path = ""

        self.modules = []

        self.bind_scroll_events()

    def change_path(self, path: str):
        self.original_path = path

    def add_module(self, name: str = "", description: str = ""):
        module = ModuleFrame(self.scrollable_frame, self.remove_module)
        module.pack(fill="x", pady=5, padx=5)
        module.entry_nom.insert(0, name)
        module.entry_description.insert("1.0", description + "--v 7 --style raw --profile r85vb3p")
        self.modules.append(module)

    def remove_module(self, module):
        name = module.entry_nom.get()

        # On essaie de voir si le nom du fichier existe
        if self.original_path:
            file_path = f"{self.original_path}/{name}.png"
            os.rename(file_path, f"{self.original_path}/{name}_RAW.png")
            Tokenizer.tokenize(
                token_name=name,
                base_image=f"{self.original_path}/{name}_RAW",
                bordure_key="default",
                output_folder=file_path,
                midjourney=True
            )

        module.destroy()
        self.modules.remove(module)

    def bind_scroll_events(self):
        # Pour Windows/Linux
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Pour macOS
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")


# Optionnel : exécution autonome pour test
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Test Frame Midjourney")
    root.geometry("500x400")
    root.resizable(False, False)

    frame = MidjourneyFrame(root)
    frame.pack(fill="both", expand=True)

    root.mainloop()
