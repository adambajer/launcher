import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox, Toplevel
from PIL import Image, ImageTk
import subprocess
import time
import psutil
import locale
import os
import shlex
import platform
import socket
import platform
import getpass
import json
import ctypes
import sys

import shlex

# Set locale for Czech date format
try:
    locale.setlocale(locale.LC_TIME, 'cs_CZ')
except locale.Error:
    messagebox.showwarning("Chyba Locale", "České nastavení locale nebylo nalezeno. Formát data nemusí být správný.")

# Path to configuration file
KONFIGURACNI_SOUBOR = "button_config.json"

# Password for admin mode
HESLO_PRO_UPRAVU = "m"

# Colors and style for futuristic design
BACKGROUND_COLOR = "#1a1a1a"
BUTTON_COLOR = "#333333"
BUTTON_HIGHLIGHT = "#00ffcc"
TEXT_COLOR = "#ffffff"
FONT = ("Helvetica", 24, "bold")
MARGIN_SIZE = 20

root = tk.Tk()
root.attributes("-fullscreen", True)  # Application in full-screen mode
root.title("Miele application launcher")
root.configure(bg=BACKGROUND_COLOR)  # Darker, modern background

# Set the application icon
try:
    app_icon = Image.open("icon.png")  # Replace with your icon's path
    app_icon_photo = ImageTk.PhotoImage(app_icon)
    root.iconphoto(False, app_icon_photo)
except Exception as e:
    messagebox.showerror("Chyba ikony", f"Nahrání ikony aplikace selhalo:\n{e}")

# Exit full-screen mode with 'Escape' key
def ukoncit_cela_obrazovka(event):
    root.attributes("-fullscreen", False)

root.bind("<Escape>", ukoncit_cela_obrazovka)

# Admin mode status (default is False)
admin_mode = False

# Function to create tooltip
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
        admin_button.config(text="U")  # Change button text to show it’s OFF
        vytvorit_tlacitka()  # Refresh buttons to hide admin features
        vytvorit_listu()  # Refresh the taskbar for user mode
        
    else:  # If Admin Mode is OFF, turn it ON
        heslo = simpledialog.askstring("PASSWORD", "", show="*", parent=root)
        if heslo == HESLO_PRO_UPRAVU:
            admin_mode = True
            admin_button.config(text="A")  # Change button text to show it’s ON
            vytvorit_tlacitka()  # Refresh buttons to show admin features
            vytvorit_listu()  # Refresh the taskbar for admin mode
            
        else:
            messagebox.showerror("Error", "Wrong password!")

# Custom Dialog Class
class ParametryDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, initialvalue=None):
        self.initialvalue = initialvalue
        self.result = None
        super().__init__(parent, title=title)

    def body(self, master):
        tk.Label(master, text="Zadejte parametry pro aplikaci (volitelné):").pack(pady=5)
        self.entry = tk.Entry(master)
        self.entry.pack(padx=5)
        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            self.entry.select_range(0, tk.END)
        self.entry.focus_set()  # Set focus to the entry widget
        return self.entry  # Initial focus

    def apply(self):
        self.result = self.entry.get()

# Create a top frame to hold the logo, admin button, and close button
top_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
top_frame.pack(side=tk.TOP, fill=tk.X)

# Configure the grid in top_frame
top_frame.columnconfigure(0, weight=1)
top_frame.columnconfigure(1, weight=1)
top_frame.columnconfigure(2, weight=1)

# Logo (centered at the top)
try:
    logo_image = Image.open("logo.png")  # Update with your logo's path
    logo_image = logo_image.resize((200, 77))  # Resize as needed
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(top_frame, image=logo_photo, bg=BACKGROUND_COLOR)
    logo_label.grid(row=0, column=1, pady=0)
except Exception as e:
    messagebox.showerror("Chyba obrázku", f"Nahrání loga selhalo:\n{e}")

# Admin Mode Toggle Button (placed on the right)
admin_button = tk.Button(
    top_frame,
    text="A",
    font=("Arial", 16),
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    command=toggle_admin_mode,
    cursor="hand2"
)
admin_button.grid(row=0, column=2, padx=(100, 100), pady=0, sticky='e')

# Create the 'X' close button (placed to the right of admin button)
close_app_btn = tk.Button(
    top_frame,
    text="X",
    font=("Arial", 16, "bold"),
    bg=BUTTON_COLOR,
    fg=TEXT_COLOR,
    command=root.quit,
    relief='flat',
    cursor="hand2"
)
close_app_btn.grid(row=0, column=2, padx=(100, 10), pady=0, sticky='e')

# Optional: Add a tooltip to the 'X' button
vytvorit_tooltip(close_app_btn, "Zavřít aplikaci")

# Load configuration from file
def nacist_konfiguraci():
    if os.path.exists(KONFIGURACNI_SOUBOR):
        with open(KONFIGURACNI_SOUBOR, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Save configuration to file
def ulozit_konfiguraci():
    with open(KONFIGURACNI_SOUBOR, 'w', encoding='utf-8') as file:
        json.dump(button_commands, file, ensure_ascii=False, indent=4)

# Store button paths and details
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

        # Check if the selected file is cmd.exe
        if os.path.basename(cesta).lower() == 'cmd.exe':
            messagebox.showwarning("Neplatný soubor", "Nelze použít cmd.exe jako aplikaci.")
            return

        # Ask the user for the button name
        nazev = simpledialog.askstring("Vstup", "Zadejte název tlačítka:", parent=root)
        if not nazev:
            messagebox.showwarning("Bez názvu", "Musíte zadat název pro tlačítko.")
            return

        # Ask for optional parameters using the custom dialog
        parametry_dialog = ParametryDialog(root, title="Parametry")
        parametry = parametry_dialog.result

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

            if os.path.basename(cesta).lower() == 'cmd.exe':
                messagebox.showwarning("Nelze spustit", "Použití cmd.exe není povoleno.")
                return

            if parametry:
                params = parametry
            else:
                params = ""

            # Use ShellExecuteEx to run the application with elevation
            class SHELLEXECUTEINFO(ctypes.Structure):
                _fields_ = [
                    ('cbSize', ctypes.c_ulong),
                    ('fMask', ctypes.c_ulong),
                    ('hwnd', ctypes.c_void_p),
                    ('lpVerb', ctypes.c_wchar_p),
                    ('lpFile', ctypes.c_wchar_p),
                    ('lpParameters', ctypes.c_wchar_p),
                    ('lpDirectory', ctypes.c_wchar_p),
                    ('nShow', ctypes.c_int),
                    ('hInstApp', ctypes.c_void_p),
                    ('lpIDList', ctypes.c_void_p),
                    ('lpClass', ctypes.c_wchar_p),
                    ('hkeyClass', ctypes.c_void_p),
                    ('dwHotKey', ctypes.c_ulong),
                    ('hIcon', ctypes.c_void_p),
                    ('hProcess', ctypes.c_void_p),
                ]

            SEE_MASK_NOCLOSEPROCESS = 0x00000040

            # Prepare the SHELLEXECUTEINFO structure
            execute_info = SHELLEXECUTEINFO()
            execute_info.cbSize = ctypes.sizeof(execute_info)
            execute_info.fMask = SEE_MASK_NOCLOSEPROCESS
            execute_info.hwnd = None
            execute_info.lpVerb = 'runas'  # This will prompt for elevation
            execute_info.lpFile = cesta
            execute_info.lpParameters = params
            execute_info.lpDirectory = None
            execute_info.nShow = 1  # SW_SHOWNORMAL
            execute_info.hInstApp = None

            # Call ShellExecuteEx
            if not ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(execute_info)):
                error_code = ctypes.GetLastError()
                messagebox.showerror("Chyba", f"Spuštění aplikace selhalo s chybou {error_code}.")
            else:
                # Optionally, wait for the process to finish
                pass

        except Exception as e:
            messagebox.showerror("Chyba", f"Spuštění aplikace selhalo:\n{e}")
    else:
        messagebox.showwarning("Žádná aplikace", "K tomuto tlačítku není přiřazena žádná aplikace.")
# Dynamically create buttons
buttons_frame = tk.Frame(root, bg=BACKGROUND_COLOR)
buttons_frame.pack(pady=MARGIN_SIZE, expand=True, fill=tk.BOTH)

def vytvorit_tlacitka():
    # Clear existing buttons
    for widget in buttons_frame.winfo_children():
        widget.destroy()

    pocet_tlacitek = len(button_commands)
    pocet_sloupcu = int(pocet_tlacitek**0.5) + 1  # Dynamically adjust number of columns
    pocet_radku = (pocet_tlacitek + pocet_sloupcu - 1) // pocet_sloupcu  # Ensure enough rows

    # Dynamically create buttons for each command definition
    for i, cmd_data in enumerate(button_commands):
        try:
            # Handle buttons with two or three elements
            if len(cmd_data) == 2:
                cmd, nazev = cmd_data
                parametry = ""  # No parameters, older configuration
            else:
                cmd, nazev, parametry = cmd_data

            # Button to launch the application (edits are allowed only in admin mode)
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

            # Add option to edit the button only in admin mode
            if admin_mode:
                btn.bind("<Button-3>", lambda e, i=i: pridat_nebo_upravit_tlacitko(i))

        except Exception as e:
            messagebox.showerror("Chyba tlačítka", f"Selhalo vytvoření tlačítka pro {nazev}:\n{e}")

    # Add plus button to add more buttons, visible only in admin mode
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

    # Ensure buttons are rectangular and responsive
    for i in range(pocet_sloupcu):
        buttons_frame.grid_columnconfigure(i, weight=1, uniform="equal")
    for j in range(pocet_radku):
        buttons_frame.grid_rowconfigure(j, weight=1, uniform="equal")

def vytvorit_listu():
    global clock_label, date_label, battery_label, battery_progress, wifi_button, info_label, hostname, username, os_version

    # Destroy existing taskbar if it exists
    if hasattr(root, 'taskbar_frame'):
        root.taskbar_frame.destroy()

    # Create a new taskbar
    root.taskbar_frame = tk.Frame(root, bg="#1f1f1f", height=40)  # Slightly darker than main window
    root.taskbar_frame.pack(side=tk.BOTTOM, fill=tk.X)

    # Left section (Logout, Restart, Shutdown)
    left_frame = tk.Frame(root.taskbar_frame, bg="#1f1f1f")
    left_frame.pack(side=tk.LEFT, padx=10)
        # Middle section (Info labels)
    info_frame = tk.Frame(root.taskbar_frame, bg="#1f1f1f")
    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    # Get static system information
    hostname = socket.gethostname()
    username = getpass.getuser()
    os_version = platform.platform()

    # Create label for the info
    info_label = tk.Label(
        info_frame,
        text="",  # We'll set the text in the update function
        font=("Arial", 10),
        fg="white",
        bg="#1f1f1f",
        anchor='center'
    )
    info_label.pack(expand=True)
    logout_btn = tk.Button(
        left_frame,
        text="Odhlásit",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=odhlasit
    )
    logout_btn.pack(side=tk.LEFT, padx=5)

    reset_btn = tk.Button(
        left_frame,
        text="Restart",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=restartovat
    )
    reset_btn.pack(side=tk.LEFT, padx=5)

    shutdown_btn = tk.Button(
        left_frame,
        text="Vypnout",
        font=("Arial", 12),
        bg=BUTTON_COLOR,
        fg=TEXT_COLOR,
        command=vypnout
    )
    shutdown_btn.pack(side=tk.LEFT, padx=5)

    # In admin mode, show button for opening explorer
    if admin_mode:
        # Button to open explorer.exe (show desktop)
        open_explorer_btn = tk.Button(
            left_frame,
            text="Otevřít Explorer",
            font=("Arial", 12),
            bg=BUTTON_COLOR,
            fg=TEXT_COLOR,
            command=lambda: os.system("start explorer.exe")
        )
        open_explorer_btn.pack(side=tk.LEFT, padx=5)

    # Right section (Clock and date, Battery, WiFi)
    right_frame = tk.Frame(root.taskbar_frame, bg="#1f1f1f")
    right_frame.pack(side=tk.RIGHT, padx=10)

    # Clock and Date (stacked vertically)
    time_frame = tk.Frame(right_frame, bg="#1f1f1f")
    time_frame.pack(side=tk.RIGHT, padx=10)

    clock_label = tk.Label(time_frame, font=("Courier", 12), fg="white", bg="#1f1f1f")
    clock_label.pack()

    date_label = tk.Label(time_frame, font=("Courier", 10), fg="white", bg="#1f1f1f")
    date_label.pack()

    # WiFi Icon
    try:
        # WiFi Ikona (Zástupce: aktualizujte cestu k aktuální ikoně WiFi)
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

        # Tooltip for WiFi (Display actual WiFi SSID)
        wifi_name = ziskat_wifi_ssid()  # Use function to get SSID
        vytvorit_tooltip(wifi_button, f"WiFi: {wifi_name}")

    # Battery Icon
    battery_label = tk.Label(right_frame, font=("Courier", 12), fg="white", bg="#1f1f1f")
    battery_label.pack(side=tk.RIGHT, padx=5)

    battery_progress = ttk.Progressbar(right_frame, length=50, mode='determinate', style="TProgressbar")
    battery_progress.pack(side=tk.RIGHT, padx=5)

    # Bind tooltip to both battery_label and battery_progress
    # The tooltips will be updated in 'aktualizovat_baterii_tooltip'
    vytvorit_tooltip(battery_label, "N/A")
    vytvorit_tooltip(battery_progress, "N/A")
    aktualizovat_info()
    # Start the clock and battery updates
    aktualizovat_cas()
    aktualizovat_baterii()

# Add the new function to update the info label
def aktualizovat_info():
    global info_label, hostname, username

    # Get dynamic system information
    cpu_usage = psutil.cpu_percent(interval=None)
    ram_usage = psutil.virtual_memory().percent

    # Update the info label
    info_text = f"{hostname} | Uživatel: {username} | CPU: {cpu_usage:.1f}% | RAM: {ram_usage:.1f}%"
    info_label.config(text=info_text)

    # Schedule the function to run again after 1000 milliseconds (1 second)
    root.after(1000, aktualizovat_info)
def aktualizovat_baterii_tooltip():
    battery = psutil.sensors_battery()
    if battery:
        battery_percent = battery.percent
        if battery.power_plugged:
            status = "Nabíjení" if battery_percent < 100 else "Plně nabito"
        else:
            status = "Vybíjení"
        # Estimated time left
        if battery.secsleft == psutil.POWER_TIME_UNLIMITED:
            time_left = "Vypočítávám čas..."
        elif battery.secsleft == psutil.POWER_TIME_UNKNOWN:
            time_left = "Neznámý čas"
        else:
            hours, remainder = divmod(battery.secsleft, 3600)
            minutes = remainder // 60
            time_left = f"{hours}h {minutes}m zbývá"
        # Update tooltip text
        tooltip_text = f"{status} - {battery_percent}%\n{time_left}"
        # Update the tooltip text for battery_label and battery_progress
        vytvorit_tooltip(battery_label, tooltip_text)
        vytvorit_tooltip(battery_progress, tooltip_text)
    else:
        tooltip_text = "Žádná baterie"
        vytvorit_tooltip(battery_label, tooltip_text)
        vytvorit_tooltip(battery_progress, tooltip_text)

def aktualizovat_baterii():
    try:
        battery = psutil.sensors_battery()
        if battery:
            battery_percent = battery.percent
            is_charging = battery.power_plugged
            battery_progress['value'] = battery_percent
            battery_label.config(text=f"{battery_percent}%")
            aktualizovat_baterii_tooltip()  # Update the tooltip
        else:
            battery_label.config(text="Žádná baterie")
            battery_progress['value'] = 0
            aktualizovat_baterii_tooltip()
    except Exception as e:
        messagebox.showerror("Chyba", f"Aktualizace baterie selhala:\n{e}")
    root.after(60000, aktualizovat_baterii)  # Schedule the function to run again after 60 seconds

def aktualizovat_cas():
    current_time = time.strftime("%H:%M:%S")
    current_date = time.strftime("%d.%m.%Y")
    clock_label.config(text=current_time)
    date_label.config(text=current_date)
    root.after(1000, aktualizovat_cas)  # Schedule the function to run again after 1 second

# Function to get connected WiFi SSID (Windows only)
def ziskat_wifi_ssid():
    try:
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "SSID" in line and "BSSID" not in line:
                return line.split(":")[1].strip()
    except Exception as e:
        return "Neznámá WiFi"
    return "Žádná WiFi"

# Functions for shutdown, restart, and logout
def odhlasit():
    os.system("shutdown -l")

def restartovat():
    os.system("shutdown -r -t 0")

def vypnout():
    os.system("shutdown -s -t 0")

# Create buttons and taskbar at startup
vytvorit_tlacitka()
vytvorit_listu()

root.mainloop()
