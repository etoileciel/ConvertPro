"""
ConvertPro - Convertisseur de fichiers universel
Interface graphique moderne avec Tkinter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import subprocess

# ─── Imports conditionnels ────────────────────────────────────────────────────
try:
    from PIL import Image
    PIL_OK = True
except ImportError:
    PIL_OK = False

try:
    import reportlab
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

try:
    import pypdf
    PYPDF_OK = True
except ImportError:
    PYPDF_OK = False

try:
    import img2pdf
    IMG2PDF_OK = True
except ImportError:
    IMG2PDF_OK = False

# ─── Palette & constantes ─────────────────────────────────────────────────────
BG_DARK   = "#0F1117"
BG_PANEL  = "#1A1D27"
BG_CARD   = "#22263A"
ACCENT    = "#6C63FF"
ACCENT2   = "#A78BFA"
TEXT_MAIN = "#E8E9F3"
TEXT_SUB  = "#8B8FA8"
SUCCESS   = "#34D399"
ERROR     = "#F87171"
BORDER    = "#2E3250"

FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_SUB   = ("Segoe UI", 10)
FONT_LABEL = ("Segoe UI", 9)
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_SMALL = ("Segoe UI", 8)

# ─── Conversions disponibles ──────────────────────────────────────────────────
CONVERSIONS = {
    "Image → PDF":       {"exts_in": [".jpg",".jpeg",".png",".bmp",".gif",".webp",".tiff"], "ext_out": ".pdf"},
    "PDF → Images":      {"exts_in": [".pdf"], "ext_out": ".png"},
    "Image → Image":     {"exts_in": [".jpg",".jpeg",".png",".bmp",".gif",".webp",".tiff"], "ext_out": ".png"},
    "PNG → JPEG":        {"exts_in": [".png"], "ext_out": ".jpg"},
    "JPEG → PNG":        {"exts_in": [".jpg",".jpeg"], "ext_out": ".png"},
    "Texte → PDF":       {"exts_in": [".txt",".csv"], "ext_out": ".pdf"},
    "MP4 → MP3 (ffmpeg)":{"exts_in": [".mp4",".avi",".mkv",".mov"], "ext_out": ".mp3"},
    "MP4 → AVI (ffmpeg)":{"exts_in": [".mp4"], "ext_out": ".avi"},
    "Fusion PDF":        {"exts_in": [".pdf"], "ext_out": ".pdf"},
}


# ─── Fonctions de conversion ──────────────────────────────────────────────────
def convert_image_to_pdf(input_path, output_path):
    if IMG2PDF_OK:
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(input_path))
    elif PIL_OK and REPORTLAB_OK:
        img = Image.open(input_path).convert("RGB")
        img_w, img_h = img.size
        page_w, page_h = A4
        ratio = min(page_w / img_w, page_h / img_h)
        new_w, new_h = int(img_w * ratio), int(img_h * ratio)
        c = rl_canvas.Canvas(output_path, pagesize=A4)
        x = (page_w - new_w) / 2
        y = (page_h - new_h) / 2
        c.drawInlineImage(img, x, y, width=new_w, height=new_h)
        c.save()
    else:
        raise RuntimeError("Pillow + ReportLab ou img2pdf requis.")

def convert_pdf_to_images(input_path, output_path):
    try:
        from pdf2image import convert_from_path
        pages = convert_from_path(input_path)
        base, _ = os.path.splitext(output_path)
        for i, page in enumerate(pages):
            page.save(f"{base}_page{i+1}.png", "PNG")
        return f"{len(pages)} page(s) extraites"
    except Exception:
        raise RuntimeError("pdf2image + poppler requis pour PDF→Image.")

def convert_image_to_image(input_path, output_path, fmt):
    if not PIL_OK:
        raise RuntimeError("Pillow requis.")
    img = Image.open(input_path)
    fmt_map = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG",
               ".bmp": "BMP", ".gif": "GIF", ".webp": "WEBP", ".tiff": "TIFF"}
    save_fmt = fmt_map.get(fmt.lower(), "PNG")
    if save_fmt == "JPEG":
        img = img.convert("RGB")
    img.save(output_path, save_fmt)

def convert_text_to_pdf(input_path, output_path):
    if not REPORTLAB_OK:
        raise RuntimeError("ReportLab requis.")
    with open(input_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    c = rl_canvas.Canvas(output_path, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica", 11)
    y = h - 50
    for line in lines:
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = h - 50
        c.drawString(40, y, line.rstrip()[:110])
        y -= 16
    c.save()

def convert_ffmpeg(input_path, output_path, extra_args=None):
    cmd = ["ffmpeg", "-y", "-i", input_path]
    if extra_args:
        cmd += extra_args
    cmd.append(output_path)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg: {result.stderr[-300:]}")

def merge_pdfs(input_paths, output_path):
    if not PYPDF_OK:
        raise RuntimeError("pypdf requis.")
    from pypdf import PdfWriter
    w = PdfWriter()
    for p in input_paths:
        from pypdf import PdfReader
        w.append(PdfReader(p))
    with open(output_path, "wb") as f:
        w.write(f)


# ─── Interface graphique ──────────────────────────────────────────────────────
class ConvertPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ConvertPro — Convertisseur universel")
        self.geometry("820x640")
        self.minsize(720, 560)
        self.configure(bg=BG_DARK)
        try:
            self.iconbitmap(default="")
        except Exception:
            pass

        self.files = []
        self.conv_var  = tk.StringVar(value=list(CONVERSIONS.keys())[0])
        self.out_var   = tk.StringVar()
        self.fmt_var   = tk.StringVar(value=".png")
        self.status_var= tk.StringVar(value="Prêt")

        self._build_ui()

    # ── Constructeurs UI ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=ACCENT, height=4)
        hdr.pack(fill="x")

        top = tk.Frame(self, bg=BG_DARK, pady=18)
        top.pack(fill="x", padx=30)
        tk.Label(top, text="⟳ ConvertPro", font=FONT_TITLE,
                 bg=BG_DARK, fg=TEXT_MAIN).pack(side="left")
        tk.Label(top, text="Convertisseur de fichiers universel",
                 font=FONT_SUB, bg=BG_DARK, fg=TEXT_SUB).pack(side="left", padx=14, pady=6)

        # Main area
        main = tk.Frame(self, bg=BG_DARK)
        main.pack(fill="both", expand=True, padx=30, pady=(0,10))
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_left(main)
        self._build_right(main)
        self._build_footer()

    def _card(self, parent, title, row, col, rowspan=1):
        f = tk.Frame(parent, bg=BG_PANEL, bd=0, relief="flat",
                     padx=16, pady=14)
        f.grid(row=row, column=col, rowspan=rowspan,
               sticky="nsew", padx=(0,8) if col==0 else (8,0), pady=6)
        if title:
            tk.Label(f, text=title, font=("Segoe UI",9,"bold"),
                     bg=BG_PANEL, fg=ACCENT2).pack(anchor="w", pady=(0,8))
        return f

    def _build_left(self, main):
        # Type de conversion
        c1 = self._card(main, "TYPE DE CONVERSION", 0, 0)
        for name in CONVERSIONS:
            rb = tk.Radiobutton(c1, text=name, variable=self.conv_var,
                                value=name, command=self._on_conv_change,
                                font=FONT_LABEL, bg=BG_PANEL,
                                fg=TEXT_MAIN, selectcolor=ACCENT,
                                activebackground=BG_PANEL,
                                activeforeground=ACCENT2,
                                relief="flat", bd=0)
            rb.pack(anchor="w", pady=1)

    def _build_right(self, main):
        right = tk.Frame(main, bg=BG_DARK)
        right.grid(row=0, column=1, sticky="nsew", padx=(8,0), pady=6)
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        # Fichiers
        c2 = self._card(right, "FICHIERS SOURCE", 0, 0)
        c2.pack(fill="both", expand=True, pady=(0,6))

        self.list_frame = tk.Frame(c2, bg=BG_CARD, bd=0)
        self.list_frame.pack(fill="both", expand=True, pady=(0,8))

        self.listbox = tk.Listbox(self.list_frame, bg=BG_CARD, fg=TEXT_MAIN,
                                   selectbackground=ACCENT, bd=0,
                                   font=FONT_SMALL, highlightthickness=0,
                                   relief="flat", activestyle="none")
        self.listbox.pack(side="left", fill="both", expand=True, padx=6, pady=6)
        sb = tk.Scrollbar(self.list_frame, command=self.listbox.yview,
                          bg=BG_PANEL, troughcolor=BG_CARD)
        sb.pack(side="right", fill="y")
        self.listbox.config(yscrollcommand=sb.set)

        btn_row = tk.Frame(c2, bg=BG_PANEL)
        btn_row.pack(fill="x")
        self._btn(btn_row, "＋ Ajouter", self._add_files, ACCENT).pack(side="left", padx=(0,4))
        self._btn(btn_row, "✕ Retirer", self._remove_file, "#4B3F8F").pack(side="left", padx=4)
        self._btn(btn_row, "⌫ Tout vider", self._clear_files, "#3B2F5F").pack(side="left", padx=4)

        # Format de sortie (pour Image→Image)
        self.fmt_frame = tk.Frame(right, bg=BG_PANEL, padx=16, pady=10)
        tk.Label(self.fmt_frame, text="FORMAT DE SORTIE",
                 font=("Segoe UI",9,"bold"), bg=BG_PANEL, fg=ACCENT2).pack(anchor="w")
        fmt_opts = [".png", ".jpg", ".bmp", ".gif", ".webp", ".tiff"]
        fmt_row = tk.Frame(self.fmt_frame, bg=BG_PANEL)
        fmt_row.pack(fill="x", pady=4)
        for f in fmt_opts:
            tk.Radiobutton(fmt_row, text=f, variable=self.fmt_var,
                           value=f, font=FONT_SMALL, bg=BG_PANEL,
                           fg=TEXT_MAIN, selectcolor=ACCENT,
                           activebackground=BG_PANEL, relief="flat").pack(side="left", padx=3)

        # Dossier de sortie
        c3 = tk.Frame(right, bg=BG_PANEL, padx=16, pady=10)
        c3.pack(fill="x", pady=6)
        tk.Label(c3, text="DOSSIER DE SORTIE",
                 font=("Segoe UI",9,"bold"), bg=BG_PANEL, fg=ACCENT2).pack(anchor="w", pady=(0,6))
        out_row = tk.Frame(c3, bg=BG_PANEL)
        out_row.pack(fill="x")
        self.out_entry = tk.Entry(out_row, textvariable=self.out_var,
                                   font=FONT_LABEL, bg=BG_CARD, fg=TEXT_MAIN,
                                   insertbackground=TEXT_MAIN, bd=0,
                                   relief="flat", highlightthickness=1,
                                   highlightbackground=BORDER,
                                   highlightcolor=ACCENT)
        self.out_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0,6))
        self._btn(out_row, "Parcourir", self._choose_dir, "#2E3250").pack(side="left")

        # Bouton Convertir
        self.conv_btn = tk.Button(right, text="⟳  CONVERTIR",
                                   font=FONT_BTN, bg=ACCENT, fg="white",
                                   activebackground=ACCENT2,
                                   activeforeground="white",
                                   bd=0, relief="flat", cursor="hand2",
                                   padx=20, pady=10,
                                   command=self._start_convert)
        self.conv_btn.pack(fill="x", pady=(4,0))

        self._on_conv_change()

    def _build_footer(self):
        bar = tk.Frame(self, bg=BG_PANEL, pady=8)
        bar.pack(fill="x", padx=0)
        tk.Label(bar, textvariable=self.status_var, font=FONT_SMALL,
                 bg=BG_PANEL, fg=TEXT_SUB).pack(side="left", padx=20)

        self.progress = ttk.Progressbar(bar, length=200, mode="indeterminate")
        self.progress.pack(side="right", padx=20)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", troughcolor=BG_CARD,
                         background=ACCENT, bordercolor=BG_CARD)

    def _btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd, font=FONT_SMALL,
                         bg=color, fg=TEXT_MAIN, bd=0, relief="flat",
                         cursor="hand2", padx=10, pady=4,
                         activebackground=ACCENT2, activeforeground="white")

    # ── Logique UI ────────────────────────────────────────────────────────────
    def _on_conv_change(self, *_):
        conv = self.conv_var.get()
        if conv == "Image → Image":
            self.fmt_frame.pack(fill="x", pady=6)
        else:
            self.fmt_frame.pack_forget()

    def _add_files(self):
        conv  = self.conv_var.get()
        exts  = CONVERSIONS[conv]["exts_in"]
        types = [("Fichiers supportés", " ".join(f"*{e}" for e in exts)),
                 ("Tous les fichiers", "*.*")]
        paths = filedialog.askopenfilenames(filetypes=types)
        for p in paths:
            if p not in self.files:
                self.files.append(p)
                self.listbox.insert("end", os.path.basename(p))

    def _remove_file(self):
        sel = self.listbox.curselection()
        for i in reversed(sel):
            self.files.pop(i)
            self.listbox.delete(i)

    def _clear_files(self):
        self.files.clear()
        self.listbox.delete(0, "end")

    def _choose_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.out_var.set(d)

    # ── Conversion ────────────────────────────────────────────────────────────
    def _start_convert(self):
        if not self.files:
            messagebox.showwarning("Aucun fichier", "Ajoutez au moins un fichier.")
            return
        out_dir = self.out_var.get() or os.path.dirname(self.files[0])
        if not os.path.isdir(out_dir):
            messagebox.showerror("Erreur", f"Dossier invalide : {out_dir}")
            return
        self.conv_btn.config(state="disabled", text="Conversion en cours…")
        self.progress.start(10)
        thread = threading.Thread(
            target=self._run_convert,
            args=(list(self.files), out_dir, self.conv_var.get(), self.fmt_var.get()),
            daemon=True)
        thread.start()

    def _run_convert(self, files, out_dir, conv, fmt):
        errors = []
        done   = 0
        try:
            if conv == "Fusion PDF":
                out_path = os.path.join(out_dir, "fusion_output.pdf")
                merge_pdfs(files, out_path)
                done = len(files)
            else:
                ext_out = CONVERSIONS[conv]["ext_out"]
                if conv == "Image → Image":
                    ext_out = fmt

                for fp in files:
                    base = os.path.splitext(os.path.basename(fp))[0]
                    out  = os.path.join(out_dir, base + ext_out)
                    try:
                        if conv == "Image → PDF":
                            convert_image_to_pdf(fp, out)
                        elif conv == "PDF → Images":
                            convert_pdf_to_images(fp, out)
                        elif conv in ("Image → Image","PNG → JPEG","JPEG → PNG"):
                            convert_image_to_image(fp, out, ext_out)
                        elif conv == "Texte → PDF":
                            convert_text_to_pdf(fp, out)
                        elif conv in ("MP4 → MP3 (ffmpeg)","MP4 → AVI (ffmpeg)"):
                            convert_ffmpeg(fp, out)
                        done += 1
                    except Exception as e:
                        errors.append(f"{os.path.basename(fp)}: {e}")
        except Exception as e:
            errors.append(str(e))

        self.after(0, self._finish_convert, done, errors, out_dir)

    def _finish_convert(self, done, errors, out_dir):
        self.progress.stop()
        self.conv_btn.config(state="normal", text="⟳  CONVERTIR")
        if errors:
            msg = f"{done} fichier(s) converti(s).\n\nErreurs:\n" + "\n".join(errors[:5])
            self.status_var.set(f"✓ {done} conv. | {len(errors)} erreur(s)")
            messagebox.showwarning("Terminé avec erreurs", msg)
        else:
            self.status_var.set(f"✓ {done} fichier(s) converti(s) → {out_dir}")
            messagebox.showinfo("Succès !",
                f"✓ {done} fichier(s) converti(s) avec succès !\n\nDossier : {out_dir}")


if __name__ == "__main__":
    app = ConvertPro()
    app.mainloop()
