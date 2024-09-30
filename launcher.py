import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox, Toplevel
from PIL import Image, ImageTk
import subprocess
import time
import psutil
import locale
import os
import json
import shlex

# Set locale for Czech date format
try:
    locale.setlocale(locale.LC_TIME, 'cs_CZ')
    
except locale.Error:
    messagebox.showwarning("Chyba Locale", "České nastavení locale nebylo nalezeno. Formát data nemusí být správný.")

# Cesta ke konfiguračnímu souboru
KONFIGURAČNÍ_SOUBOR = "button_config.json"

# Heslo pro úpravy
HESLO_PRO_UPRAVU = "m"

# Barvy a styl pro futuristický design
BACKGROUND_COLOR = "#1a1a1a"
BUTTON_COLOR = "#333333"
BUTTON_HIGHLIGHT = "#00ffcc"
TEXT_COLOR = "#ffffff"
FONT = ("Helvetica", 24, "bold")
MARGIN_SIZE = 20

root = tk.Tk()
root.attributes("-fullscreen", True)  # Aplikace v režimu celé obrazovky
root.title("Miele application launcher")
root.configure(bg=BACKGROUND_COLOR)  # Tmavší, moderní pozadí
# Set the application icon
try:
    app_icon = Image.open("icon.png")  # Replace with your icon's path
    app_icon_photo = ImageTk.PhotoImage(app_icon)
    root.iconphoto(False, app_icon_photo)
except Exception as e:
    messagebox.showerror("Chyba ikony", f"Nahrání ikony aplikace selhalo:\n{e}")

# Ukončení režimu celé obrazovky pomocí klávesy 'Escape'
def ukoncit_cela_obrazovka(event):
    root.attributes("-fullscreen", False)

root.bind("<Escape>", ukoncit_cela_obrazovka)

# Stav admin módu (ve výchozím nastavení False)
admin_mode = False

# Logo (placed at the top)
try:
    logo_image = Image.open("logo.png")  # Update with your logo's path
    logo_image = logo_image.resize((200, 77))  # Resize as needed
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(root, image=logo_photo, bg=BACKGROUND_COLOR)
    logo_label.pack(side=tk.TOP, anchor='n', pady=0)  # Align to top
except Exception as e:
    messagebox.showerror("Chyba obrázku", f"Nahrání loga selhalo:\n{e}")

# Načtení konfigurace ze souboru
def nacist_konfiguraci():
    if os.path.exists(KONFIGURAČNÍ_SOUBOR):
        with open(KONFIGURAČNÍ_SOUBOR, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Uložení konfigurace do souboru
def ulozit_konfiguraci():
    with open(KONFIGURAČNÍ_SOUBOR, 'w', encoding='utf-8') as file:
        json.dump(button_commands, file, ensure_ascii=False, indent=4)

# Uložení cest a detailů tlačítek
button_commands = nacist_konfiguraci()
def pridat_nebo_upravit_tlacitko(index=None):
    # This process is available only in admin mode
    if not admin_mode:
        return

    # Let the user select an executable file
    cesta = filedialog.askopenfilename(
        title="Vyberte spustitelný soubor",
        filetypes=[("Spustitelné soubory", "*.exe;*.bat;*.cmd")],
        parent=root
    )
    if cesta:
        # Validate that the selected file is an executable
        if not os.path.isfile(cesta) or not cesta.lower().endswith(('.exe', '.bat', '.cmd')):
            messagebox.showwarning("Neplatný soubor", "Vyberte platný spustitelný soubor (.exe, .bat, .cmd).")
            return

        # Ask the user for the button name
        nazev = simpledialog.askstring("Vstup", "Zadejte název tlačítka:", parent=root)
        if not nazev:
            messagebox.showwarning("Bez názvu", "Musíte zadat název pro tlačítko.")
            return

        # Ask for optional parameters
        parametry = simpledialog.askstring("Parametry", "Zadejte parametry pro aplikaci (volitelné):", parent=root)

        if index is not None:
            button_commands[index] = (cesta, nazev, parametry)  # Modify existing button
        else:
            button_commands.append((cesta, nazev, parametry))  # Add new button

        ulozit_konfiguraci()  # Save configuration
        vytvorit_tlacitka()
def spustit_aplikaci(index):
    if button_commands[index]:
        try:
            cesta, nazev, parametry = button_commands[index]
            print(f"Launching application: cesta={cesta}, parametry={parametry}")
            if parametry:
                cmd = f'"{cesta}" {parametry}'
            else:
                cmd = f'"{cesta}"'
            print(f"Command to execute: {cmd}")
            subprocess.Popen(cmd, shell=True)
        except Exception as e:
            messagebox.showerror("Chyba", f"Spuštění aplikace selhalo:\n{e}")
    else:
        messagebox.showwarning("Žádná aplikace", "K tomuto tlačítku není přiřazena žádná aplikace.")

# Dynamické vytváření tlačítek
buttons_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
buttons_frame.pack(pady=MARGIN_SIZE, expand=True, fill=tk.BOTH)

def vytvorit_tlacitka():
    # Vyčistěte existující tlačítka
    for widget in buttons_frame.winfo_children():
        widget.destroy()

    pocet_tlacitek = len(button_commands)
    pocet_sloupcu = int(pocet_tlacitek**0.5) + 1  # Dynamicky upravte počet sloupců
    pocet_radku = (pocet_tlacitek + pocet_sloupcu - 1) // pocet_sloupcu  # Ujistěte se, že máte dostatek řádků

    # Dynamicky vytvářejte tlačítka pro každou příkazovou definici
    for i, cmd_data in enumerate(button_commands):
        try:
            # Zpracujte tlačítka se dvěma nebo třemi prvky
            if len(cmd_data) == 2:
                cmd, nazev = cmd_data
                parametry = ""  # Žádné parametry, starší konfigurace
            else:
                cmd, nazev, parametry = cmd_data

            # Tlačítko pro spuštění aplikace (úpravy jsou povolené pouze v admin módu)
            btn = tk.Button(
                buttons_frame,
                text=nazev,
                font=FONT,
                bg=BUTTON_COLOR,
                fg=TEXT_COLOR,
                activebackground=BUTTON_HIGHLIGHT,
                command=lambda i=i: spustit_aplikaci(i)
            )
            btn.grid(
                row=i // pocet_sloupcu,
                column=i % pocet_sloupcu,
                padx=MARGIN_SIZE,
                pady=MARGIN_SIZE,
                sticky="nsew"
            )

            # Přidání možnosti úpravy tlačítka pouze v admin módu
            if admin_mode:
                btn.bind("<Button-3>", lambda e, i=i: pridat_nebo_upravit_tlacitko(i))

        except Exception as e:
            messagebox.showerror("Chyba tlačítka", f"Selhalo vytvoření tlačítka pro {nazev}:\n{e}")

    # Přidání tlačítka plus pro přidání dalších tlačítek, pouze viditelné v admin módu
    if admin_mode:
        add_btn = tk.Button(
            buttons_frame,
            text="+",
            font=FONT,
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            activebackground=BUTTON_HIGHLIGHT,
            command=lambda: pridat_nebo_upravit_tlacitko()
        )
        add_btn.grid(
            row=pocet_tlacitek // pocet_sloupcu,
            column=pocet_tlacitek % pocet_sloupcu,
            padx=MARGIN_SIZE,
            pady=MARGIN_SIZE,
            sticky="nsew"
        )

    # Ujistěte se, že tlačítka jsou obdélníková a responzivní
    for i in range(pocet_sloupcu):
        buttons_frame.grid_columnconfigure(i, weight=1, uniform="equal")
    for j in range(pocet_radku):
        buttons_frame.grid_rowconfigure(j, weight=1, uniform="equal")
def vytvorit_tooltip(widget, text):
    tooltip = Toplevel(widget)
    tooltip.withdraw()  # Hide initially
    tooltip.overrideredirect(True)
    tooltip.attributes('-topmost', True)  # Keep the tooltip on top
    tooltip_label = tk.Label(
        tooltip,
        text=text,
        bg="lightyellow",
        padx=5,
        pady=2,
        relief='solid',
        borderwidth=1,
        font=("Arial", 10)
    )
    tooltip_label.pack()

    def zobrazit_tooltip(event):
        tooltip.update_idletasks()
        tooltip_width = tooltip.winfo_width()
        tooltip_height = tooltip.winfo_height()
        x = event.x_root - tooltip_width // 2
        y = event.y_root - tooltip_height - 10  # Position above the cursor

        # Ensure the tooltip doesn't go off the screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Adjust x-coordinate if needed
        if x < 0:
            x = 0
        elif x + tooltip_width > screen_width:
            x = screen_width - tooltip_width

        # Adjust y-coordinate if needed
        if y < 0:
            y = event.y_root + 20  # If no space above, place below the cursor

        tooltip.geometry(f"+{x}+{y}")
        tooltip.deiconify()

    def skryt_tooltip(event):
        tooltip.withdraw()  # Hide the tooltip

    widget.bind("<Enter>", zobrazit_tooltip)
    widget.bind("<Leave>", skryt_tooltip)


# Toggle button for Admin Mode
def toggle_admin_mode():
    global admin_mode

    if admin_mode:  # If Admin Mode is ON, turn it OFF
        admin_mode = False
        admin_button.config(text="ADMIN IS OFF")  # Change button text to show it’s OFF
        vytvorit_tlacitka()  # Refresh buttons to hide admin features
        vytvorit_listu()  # Refresh the taskbar for user mode
        messagebox.showinfo("ADMIN MODE", "ADMIN IS OFF")
    else:  # If Admin Mode is OFF, turn it ON
        heslo = simpledialog.askstring("Admin Mód", "Zadejte heslo:", show="*", parent=root)
        if heslo == HESLO_PRO_UPRAVU:
            admin_mode = True
            admin_button.config(text="ADMIN IS ON")  # Change button text to show it’s ON
            vytvorit_tlacitka()  # Refresh buttons to show admin features
            vytvorit_listu()  # Refresh the taskbar for admin mode
            messagebox.showinfo("ADMIN MODE", "ADMIN IS ON.")
        else:
            messagebox.showerror("Chyba", "Nesprávné heslo!")

def vytvorit_listu():
    global clock_label, date_label, battery_label, battery_progress, battery_button, wifi_button

    # Destroy existing taskbar if it exists
    if hasattr(root, 'taskbar_frame'):
        root.taskbar_frame.destroy()

    # Create a new taskbar
    root.taskbar_frame = tk.Frame(root, bg="#1f1f1f", height=40)  # Mírně tmavší než hlavní okno
    root.taskbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Levá část (Logout, Restart, Shutdown) přidána vlevo
    left_frame = tk.Frame(root.taskbar_frame, bg="#1f1f1f")
    left_frame.pack(side=tk.LEFT, padx=10)

    logout_btn = tk.Button(
        left_frame,
        text="Odhlásit",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=lambda: odhlasit()
    )
    logout_btn.pack(side=tk.LEFT, padx=5)

    reset_btn = tk.Button(
        left_frame,
        text="Restart",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=lambda: restartovat()
    )
    reset_btn.pack(side=tk.LEFT, padx=5)

    shutdown_btn = tk.Button(
        left_frame,
        text="Vypnout",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=lambda: vypnout()
    )
    shutdown_btn.pack(side=tk.LEFT, padx=5)
     # Close Application button (Visible to all users)
    close_app_btn = tk.Button(
        left_frame,
        text="Zavřít aplikaci",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=root.quit
    )
    close_app_btn.pack(side=tk.LEFT, padx=5)

    # V režimu admin se zobrazí tlačítka pro zavření aplikace a exploreru
    if admin_mode:
        close_app_btn = tk.Button(
            left_frame,
            text="Zavřít aplikaci",
            font=("Arial", 12),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            command=root.quit
        )
          

        # Tlačítko pro spuštění explorer.exe (zobrazení plochy)
        open_explorer_btn = tk.Button(
            left_frame,
            text="Otevřít Explorer",
            font=("Arial", 12),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            command=lambda: os.system("start explorer.exe")
        )
        open_explorer_btn.pack(side=tk.LEFT, padx=5)

    # Pravá část (Hodiny a datum, Baterie, WiFi)
    right_frame = tk.Frame(root.taskbar_frame, bg="#1f1f1f")
    right_frame.pack(side=tk.RIGHT, padx=10)

    # Clock and Date (stacked vertically)
    time_frame = tk.Frame(right_frame, bg="#1f1f1f")
    time_frame.pack(side=tk.RIGHT, padx=10)

    global clock_label
    clock_label = tk.Label(time_frame, font=("Courier", 12), fg="white", bg="#1f1f1f")
    clock_label.pack()

    global date_label
    date_label = tk.Label(time_frame, font=("Courier", 10), fg="white", bg="#1f1f1f")
    date_label.pack()

    # WiFi Ikona
    try:
        wifi_icon = Image.open("wifi_icon.png")  # Použijte skutečnou ikonu WiFi
        wifi_icon = wifi_icon.resize((20, 20), Image.Resampling.LANCZOS)
        wifi_photo = ImageTk.PhotoImage(wifi_icon)
    except Exception as e:
        messagebox.showerror("Chyba obrázku", f"Nahrání WiFi ikony selhalo:\n{e}")
        wifi_photo = None

    if wifi_photo:
        wifi_button = tk.Button(
            right_frame,
            image=wifi_photo,
            borderwidth=0,
            bg="#1f1f1f",
            activebackground="#1f1f1f"
        )
        wifi_button.image = wifi_photo
        wifi_button.pack(side=tk.RIGHT, padx=5)

        # Tooltip pro WiFi (Zobrazit skutečné SSID WiFi)
        wifi_name = ziskat_wifi_ssid()  # Použijte funkci pro získání SSID
        vytvorit_tooltip(wifi_button, f"WiFi: {wifi_name}")

    # Ikona baterie
    global battery_label
    battery_label = tk.Label(right_frame, font=("Courier", 12), fg="white", bg="#1f1f1f")
    battery_label.pack(side=tk.RIGHT, padx=5)

    global battery_progress
    battery_progress = ttk.Progressbar(right_frame, length=50, mode='determinate', style="TProgressbar")
    battery_progress.pack(side=tk.RIGHT, padx=5)

    global battery_button
    battery_button = tk.Label(right_frame, bg="#1f1f1f")
    battery_button.pack(side=tk.RIGHT, padx=5)

    # Start the clock and battery updates
    aktualizovat_cas()
    aktualizovat_baterii()
def aktualizovat_baterii_tooltip():
    battery = psutil.sensors_battery()
    if battery:
        battery_percent = battery.percent
        if battery.power_plugged:
            status = "Nabíjení" if battery_percent < 100 else "Plně nabito"
        else:
            status = "Vybíjení"
        # Odhadovaný zbývající čas
        if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
            time_left = "Vypočítávám čas..."
        elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
            time_left = "Neznámý čas"
        else:
            hours, remainder = divmod(battery.secsleft, 3600)
            minutes = remainder // 60
            time_left = f"{hours}h {minutes}m zbývá"
        # Aktualizace textu tooltipu
        tooltip_text = f"{status} - {battery_percent}%\n{time_left}"
        vytvorit_tooltip(battery_label, tooltip_text)  # Bind to battery_label
    else:
        vytvorit_tooltip(battery_label, "Žádná baterie")

def aktualizovat_baterii():
    try:
        battery = psutil.sensors_battery()
        if battery:
            battery_percent = battery.percent
            is_charging = battery.power_plugged
            battery_progress['value'] = battery_percent
            battery_label.config(text=f"{battery_percent}%")
            if is_charging:
                battery_label.config(fg="white")
            else:
                battery_label.config(fg="white")
            aktualizovat_baterii_tooltip()  # Update the tooltip
        else:
            battery_label.config(text="Žádná baterie")
            battery_progress['value'] = 0
            vytvorit_tooltip(battery_button, "Žádná baterie")
    except Exception as e:
        messagebox.showerror("Chyba", f"Aktualizace baterie selhala:\n{e}")
    root.after(60000, aktualizovat_baterii)  # Schedule the function to run again after 60 seconds

def aktualizovat_cas():
    current_time = time.strftime("%H:%M:%S")
    current_date = time.strftime("%d.%m.%Y")
    clock_label.config(text=current_time)
    date_label.config(text=current_date)
    root.after(1000, aktualizovat_cas)  # Schedule the function to run again after 1 second

# Funkce pro získání připojeného SSID WiFi (Pouze pro Windows)
def ziskat_wifi_ssid():
    try:
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":")[1].strip()
    except Exception as e:
        return "Neznámá WiFi"
    return "Žádná WiFi"

# Funkce pro vypnutí, restart a odhlášení
def odhlasit():
    os.system("shutdown -l")

def restartovat():
    os.system("shutdown -r -t 0")

def vypnout():
    os.system("shutdown -s -t 0")

# Tlačítko pro přepnutí Admin Módu
admin_button = tk.Button(
    root,
    text="ADMIN IS OFF",
    font=("Arial", 16),
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    command=toggle_admin_mode
)
admin_button.pack(side=tk.TOP, pady=20)

# Vytvoření tlačítek a lišty na startu
vytvorit_tlacitka()
vytvorit_listu()

root.mainloop()
