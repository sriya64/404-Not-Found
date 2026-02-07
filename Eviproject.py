import sqlite3
from datetime import datetime, date
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Database file:
FILE = "ecotrack.db"

LOGO = "logo.jpg"
IMG = "pic.jpg"

# Transport categories with elements like time taken and km traveled:
TRANSPORT = {
    "Travel: Car": {"unit": "km", "kg_per_unit": 0.192, "kg_per_hour": 0.30},
    "Travel: Bus": {"unit": "km", "kg_per_unit": 0.105, "kg_per_hour": 0.10},
    "Travel: Metro/Train": {"unit": "km", "kg_per_unit": 0.041, "kg_per_hour": 0.03},
    "Travel: Motorcycle": {"unit": "km", "kg_per_unit": 0.090, "kg_per_hour": 0.15},
}

# Rating for the daily carbon footprints:
GOODLIMIT = 6.0
OKLIMIT = 12.0

# Colors used accross code:
LIGREEN = "#DFF5D8"
DRGREEN = "#1F5F3B"
YLW = "#FAF9E1"
DARK = "#1B3A2F"
BRGREEN = "#8CCF9A"

# Create the logs table if it does not already exist:
def createDtb():
    with sqlite3.connect(FILE) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                duration_hours REAL NOT NULL DEFAULT 0,
                kg_co2 REAL NOT NULL,
                note TEXT
            )
            """
        )
        conn.commit()


def Emissions(category: str, km: float, hr: float) -> float:
    perunit = TRANSPORT[category]["kg_per_unit"]
    perhr = TRANSPORT[category].get("kg_per_hour", 0.0)
    return round((km * perunit) + (hr * perhr), 3)


def fmtDate(d: date) -> str:
    return d.isoformat()  # YYYY-MM-DD


def totalLimit(total_kg: float) -> str:
    if total_kg <= GOODLIMIT:
        return "LOW (low footprint today)"
    elif total_kg <= OKLIMIT:
        return "OK (decent footprint today)"
    else:
        return "HIGH (very high footprint today, try reducing emissions)"


def parse_hours(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    return float(s)


class Main(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("EcoTrack - Carbon Footprint Monitor")
        self.geometry("920x560")
        self.minsize(880, 520)

        self.configure(bg=LIGREEN)
        createDtb()

        # --- Style ---
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.style.configure("Green.TFrame", background=LIGREEN)
        self.style.configure("Green.TLabel", background=LIGREEN, foreground=DARK)
        self.style.configure("Green.TLabelframe", background=LIGREEN, bordercolor=BRGREEN)
        self.style.configure(
            "Green.TLabelframe.Label",
            background=LIGREEN,
            foreground=DARK,
            font=("Segoe UI", 10, "bold"),
        )
        self.style.configure(
            "BoldGreen.TLabel",
            background=LIGREEN,
            foreground=DARK,
            font=("Segoe UI", 14, "bold"),
        )
        self.style.configure(
            "SmallGreen.TLabel",
            background=LIGREEN,
            foreground="gray",
            font=("Segoe UI", 9),
        )

        self.style.configure("TNotebook", background=LIGREEN, borderwidth=0)
        self.style.configure("TNotebook.Tab", padding=(12, 6))

        self.style.configure(
            "Yellow.TButton",
            background=YLW,
            foreground=DARK,
            font=("Segoe UI", 10, "bold"),
            padding=(10, 6),
            borderwidth=1,
        )
        self.style.map(
            "Yellow.TButton",
            background=[("active", "#F1F0D2"), ("pressed", "#E7E6C2")],
        )

        # --- Header ---
        header = ttk.Frame(self, padding=12, style="Green.TFrame")
        header.pack(fill="x")
        ttk.Label(
            header,
            text="ECOTRACK",
            font=("Segoe UI", 40),
            style="Green.TLabel",
        ).pack(side="left")


        ttk.Label(
            header,
            text="Logs → CO₂ Used → View History \nSlogan -> Track with ECOTRACK",
            font=("Segoe UI", 10),
            style="Green.TLabel",
        ).pack(side="left")

        try:
            img = Image.open(LOGO)
            img = img.resize((70, 70))
            self.co2_photo = ImageTk.PhotoImage(img)
            ttk.Label(header, image=self.co2_photo, style="Green.TLabel").pack(side="right")
        except Exception as e:
            print("Logo not loaded:", e)

        # --- Tabs ---
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tab_log = ttk.Frame(self.nb, padding=12, style="Green.TFrame")
        self.tab_history = ttk.Frame(self.nb, padding=12, style="Green.TFrame")

        self.nb.add(self.tab_log, text="Add logs")
        self.nb.add(self.tab_history, text="History")

        self.addLogs()
        self.historyBttn()

        # Initial load
        self.historyLoad()
        self.upt()

    def btn(self, parent, text, command, side="left", padx=0, pady=0, anchor=None):
        bg = tk.Frame(parent, bg=DRGREEN, padx=4, pady=4)
        if anchor is not None:
            bg.pack(anchor=anchor, padx=padx, pady=pady)
        else:
            bg.pack(side=side, padx=padx, pady=pady)

        ttk.Button(bg, text=text, style="Yellow.TButton", command=command).pack()
        return bg

    def addLogs(self):
        left = ttk.Frame(self.tab_log, style="Green.TFrame")
        left.pack(side="left", fill="y")

        right = ttk.Frame(self.tab_log, style="Green.TFrame")
        right.pack(side="left", fill="both", expand=True, padx=(18, 0))

        form = ttk.LabelFrame(left, text="New log entry", padding=12, style="Green.TLabelframe")
        form.pack(fill="x")

        ttk.Label(form, text="Date (YYYY-MM-DD):", style="Green.TLabel").grid(row=0, column=0, sticky="w", pady=6)
        self.date_var = tk.StringVar(value=fmtDate(date.today()))
        ttk.Entry(form, textvariable=self.date_var, width=18).grid(row=0, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Category:", style="Green.TLabel").grid(row=1, column=0, sticky="w", pady=6)
        self.cat_var = tk.StringVar(value=list(TRANSPORT.keys())[0])
        self.cat_combo = ttk.Combobox(
            form,
            textvariable=self.cat_var,
            values=list(TRANSPORT.keys()),
            state="readonly",
            width=24,
        )
        self.cat_combo.grid(row=1, column=1, sticky="w", pady=6)
        self.cat_combo.bind("<<ComboboxSelected>>", lambda e: self.unitLabel())

        ttk.Label(form, text="Amount:", style="Green.TLabel").grid(row=2, column=0, sticky="w", pady=6)
        self.amount_var = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.amount_var, width=18).grid(row=2, column=1, sticky="w", pady=6)

        self.unit_label = ttk.Label(form, text="", style="Green.TLabel")
        self.unit_label.grid(row=2, column=2, sticky="w", padx=(8, 0))
        self.unitLabel()

        ttk.Label(form, text="Time spent (hours):", style="Green.TLabel").grid(row=3, column=0, sticky="w", pady=6)
        self.time_var = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.time_var, width=18).grid(row=3, column=1, sticky="w", pady=6)
        ttk.Label(form, text="hours", style="Green.TLabel").grid(row=3, column=2, sticky="w", padx=(8, 0))

        ttk.Label(form, text="Note (optional):", style="Green.TLabel").grid(row=4, column=0, sticky="w", pady=6)
        self.note_var = tk.StringVar(value="")
        ttk.Entry(form, textvariable=self.note_var, width=28).grid(row=4, column=1, columnspan=2, sticky="w", pady=6)

        btns = ttk.Frame(form, style="Green.TFrame")
        btns.grid(row=5, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.btn(btns, "Add Log", self.svLog, side="left")
        self.btn(btns, "Clear", self.reset, side="left", padx=8)

        preview = ttk.LabelFrame(right, text="Today’s total + rating", padding=12, style="Green.TLabelframe")
        preview.pack(fill="x")

        row = ttk.Frame(preview, style="Green.TFrame")
        row.pack(fill="x", anchor="w")

        text_frame = ttk.Frame(row, style="Green.TFrame")
        text_frame.pack(side="left", fill="y")

        self.today_total_lbl = ttk.Label(text_frame, text="—", style="BoldGreen.TLabel")
        self.today_total_lbl.pack(anchor="w")

        self.today_rating_lbl = ttk.Label(text_frame, text="—", style="Green.TLabel")
        self.today_rating_lbl.pack(anchor="w", pady=(6, 0))

        self.limits_lbl = ttk.Label(
            text_frame,
            text=f"Limits: Good ≤ {GOODLIMIT} kg/day | OK ≤ {OKLIMIT} kg/day | High > {OKLIMIT}",
            style="SmallGreen.TLabel",
        )
        self.limits_lbl.pack(anchor="w", pady=(6, 0))

        img_frame = ttk.Frame(row, style="Green.TFrame")
        img_frame.pack(side="right", fill="both", expand=True)

        try:
            icon = Image.open(IMG)
            icon = icon.resize((240, 240))
            self.today_icon_photo = ImageTk.PhotoImage(icon)
            ttk.Label(img_frame, image=self.today_icon_photo, style="Green.TLabel").pack(anchor="e")
        except Exception as e:
            print("Image not loaded:", e)

        self.btn(preview, "Refresh", self.upt, side=None, anchor="w", pady=(10, 0))

        recent = ttk.LabelFrame(right, text="Today’s logs", padding=12, style="Green.TLabelframe")
        recent.pack(fill="both", expand=True, pady=(12, 0))

        cols = ("id", "category", "amount", "time", "kg")
        self.today_tree = ttk.Treeview(recent, columns=cols, show="headings", height=10)

        self.today_tree.heading("id", text="ID")
        self.today_tree.heading("category", text="Category")
        self.today_tree.heading("amount", text="Amount")
        self.today_tree.heading("time", text="Time (h)")
        self.today_tree.heading("kg", text="kg CO₂")

        self.today_tree.column("id", width=90, anchor="w")
        self.today_tree.column("category", width=220, anchor="w")
        self.today_tree.column("amount", width=120, anchor="e")
        self.today_tree.column("time", width=90, anchor="e")
        self.today_tree.column("kg", width=120, anchor="e")

        self.today_tree.pack(fill="both", expand=True)

    def unitLabel(self):
        cat = self.cat_var.get()
        unit = TRANSPORT.get(cat, {}).get("unit", "")
        self.unit_label.config(text=unit)

    def reset(self):
        self.date_var.set(fmtDate(date.today()))
        self.cat_var.set(list(TRANSPORT.keys())[0])
        self.amount_var.set("0")
        self.time_var.set("0")
        self.note_var.set("")
        self.unitLabel()

    def svLog(self):
        try:
            d = datetime.strptime(self.date_var.get().strip(), "%Y-%m-%d").date()
            cat = self.cat_var.get()
            if cat not in TRANSPORT:
                raise ValueError("Invalid category.")

            amount = float(self.amount_var.get())
            if amount <= 0:
                raise ValueError("Amount must be > 0.")

            hrs = parse_hours(self.time_var.get())
            if hrs < 0:
                raise ValueError("Time must be ≥ 0.")

            kg = Emissions(cat, amount, hrs)
            note = self.note_var.get().strip()

            with sqlite3.connect(FILE) as conn:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO logs (log_date, category, amount, duration_hours, kg_co2, note) VALUES (?, ?, ?, ?, ?, ?)",
                    (fmtDate(d), cat, amount, hrs, kg, note if note else None),
                )
                conn.commit()

            messagebox.showinfo("Saved", f"Added: {kg:.3f} kg CO₂")
            self.upt()
            self.historyLoad()
            self.reset()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def upt(self):
        today = fmtDate(date.today())
        with sqlite3.connect(FILE) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT category, amount, duration_hours, kg_co2, id FROM logs WHERE log_date = ? ORDER BY id DESC",
                (today,),
            )
            rows = cur.fetchall()

        # ✅ sum kg_co2 (index 3), not hours
        total = round(sum(r[3] for r in rows), 3)
        self.today_total_lbl.config(text=f"{total:.3f} kg CO₂ today")
        self.today_rating_lbl.config(text=f"Rating: {totalLimit(total)}")

        for item in self.today_tree.get_children():
            self.today_tree.delete(item)

        for cat, amount, hrs, kg, log_id in rows[:50]:
            self.today_tree.insert("", "end", values=(log_id, cat, f"{amount:g}", f"{hrs:g}", f"{kg:.3f}"))

    def historyBttn(self):
        top = ttk.Frame(self.tab_history, style="Green.TFrame")
        top.pack(fill="x")

        ttk.Label(top, text="Filter date (YYYY-MM-DD or blank for all):", style="Green.TLabel").pack(side="left")

        self.filter_date_var = tk.StringVar(value="")
        ttk.Entry(top, textvariable=self.filter_date_var, width=16).pack(side="left", padx=8)

        self.btn(top, "Apply", self.historyLoad, side="left")
        self.btn(top, "Delete Selected Log", self.deleteLog, side="left", padx=8)

        summary = ttk.Frame(self.tab_history, style="Green.TFrame")
        summary.pack(fill="x", pady=(10, 0))

        self.history_total_lbl = ttk.Label(summary, text="—", font=("Segoe UI", 11, "bold"), style="Green.TLabel")
        self.history_total_lbl.pack(anchor="w")

        cols = ("date", "category", "amount", "time", "kg", "note", "id")
        self.hist_tree = ttk.Treeview(self.tab_history, columns=cols, show="headings")

        self.hist_tree.heading("date", text="Date")
        self.hist_tree.heading("category", text="Category")
        self.hist_tree.heading("amount", text="Amount")
        self.hist_tree.heading("time", text="Time (h)")
        self.hist_tree.heading("kg", text="kg CO₂")
        self.hist_tree.heading("note", text="Note")
        self.hist_tree.heading("id", text="ID")

        self.hist_tree.column("date", width=110, anchor="w")
        self.hist_tree.column("category", width=260, anchor="w")
        self.hist_tree.column("amount", width=110, anchor="e")
        self.hist_tree.column("time", width=90, anchor="e")
        self.hist_tree.column("kg", width=110, anchor="e")
        self.hist_tree.column("note", width=220, anchor="w")
        self.hist_tree.column("id", width=70, anchor="e")

        self.hist_tree.pack(fill="both", expand=True, pady=(10, 0))

    def historyLoad(self):
        f = self.filter_date_var.get().strip()
        query = """SELECT log_date, category, amount, duration_hours, kg_co2, COALESCE(note,''), id FROM logs"""
        params = ()
        if f:
            try:
                datetime.strptime(f, "%Y-%m-%d")
            except Exception:
                messagebox.showerror("Error", "Filter date must be YYYY-MM-DD or blank.")
                return
            query += " WHERE log_date = ?"
            params = (f,)
        query += " ORDER BY log_date DESC, id DESC"

        with sqlite3.connect(FILE) as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()

        for item in self.hist_tree.get_children():
            self.hist_tree.delete(item)

        total = 0.0
        for r in rows:
            total += r[4]
            self.hist_tree.insert(
                "", "end",
                values=(r[0], r[1], f"{r[2]:g}", f"{r[3]:g}", f"{r[4]:.3f}", r[5], r[6])
            )

        self.history_total_lbl.config(text=f"Total shown: {total:.3f} kg CO₂")

    def deleteLog(self):
        sel = self.hist_tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a row first.")
            return

        values = self.hist_tree.item(sel[0], "values")
        log_id = values[-1]

        if not messagebox.askyesno("Confirm", f"Delete log ID {log_id}?"):
            return

        with sqlite3.connect(FILE) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM logs WHERE id = ?", (log_id,))
            conn.commit()

        self.historyLoad()
        self.upt()


if __name__ == "__main__":
    Main().mainloop()
