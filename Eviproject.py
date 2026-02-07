import sqlite3
from datetime import datetime, date
import tkinter as tk
from tkinter import tkk, messagebox
from PLI import Image, ImageTk

DTB_NME = "ecotrack.db"

LOGO = "logo.jpg"
IMG = "pic.jpg"

FACTORS = {
    "Travel: Car": {"unit": "km", "kg_per__unit": 0.192}
    "Travel: Bus": {"unit": "km", "kg_per__unit": 0.105}
    "Travel: Metro or Train": {"unit": "km", "kg_per__unit": 0.041}
    "Travel: Motorcycle": {"unit": "km", "kg_per__unit": 0.09}
    "Travel: Cycle": {"unit": "km", "kg_per__unit": 0.005}
}

GL = 6
OL = 12

LIGREEN = '#DFF5D8'
DRGREEN = '#1F5F3B'
YLW = '#FAF9E1'
DARK = '1B3A2F'
BRGREEN = '#8CCF9A'

def createDtb():
    with salite3.connect(DTB_NME) as conn:
        cur = conn.cursor()
        curr.execute("""
            CREATE TABLE IF NOT EXISTS logs(
                id INTEGER PRIMARY KEY AUTOINCRIMENT,
                log_date TEXT NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                kg_co2 REAL NOT NULL,
                note TEXT
            )
        """)
        conn.commit()

def calcEmissions           
    



