import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime
from tkintermapview import TkinterMapView
import requests
import os
from dotenv import load_dotenv
import bcrypt 

import psycopg2
from urllib.parse import urlparse, unquote_plus
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URI = [redacted for security]

def parse_db_url(db_url):
    """Parse PostgreSQL URI into psycopg2 params"""
    result = urlparse(db_url)
    password = unquote_plus(result.password)
    
    return {
        "dbname": result.path[1:],  
        "user": result.username,
        "password": password,
        "host": result.hostname,
        "port": result.port or 5432,
        "sslmode": "require"
    }

DB_PARAMS = parse_db_url(DATABASE_URL)

class AdminSetupWindow:
    def __init__(self, parent):
        self.parent = parent
        self.root = tk.Toplevel(parent)
        self.root.title('K Logistics™ | Sign Up')
        self.root.geometry('700x450')
        self.root.resizable(False, False)
        self.root.configure(bg='#1d446d')
        self.root.transient(parent)
        self.root.grab_set()

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.confirm_var = tk.StringVar()
        self.db_connected = False

        self.create_widgets()
        self.test_connection_auto()  # Automatic test on startup

    def create_widgets(self):
        # Title
        title_label = tk.Label(
            self.root,
            text='K Logistics™',
            font=('Segoe UI', 24, 'bold'),
            bg='#1d446d',
            fg='#EBF2FA'
        )
        title_label.pack(pady=30)

        subtitle_label = tk.Label(
            self.root,
            text='Account Sign Up',
            font=('Segoe UI', 12),
            bg='#1d446d',
            fg='#99afc4'
        )
        subtitle_label.pack(pady=(0, 30))

        # Form frame centered
        form_frame = tk.Frame(self.root, bg='#1d446d')
        form_frame.pack()

        row_pad = 10

        # Username row
        tk.Label(
            form_frame,
            text='Username:',
            font=('Segoe UI', 11),
            bg='#1d446d',
            fg='#EBF2FA',
            anchor='e',
            width=16
        ).grid(row=0, column=0, padx=(0, 8), pady=row_pad, sticky='e')

        username_entry = tk.Entry(
            form_frame,
            textvariable=self.username_var,
            font=('Segoe UI', 11),
            width=30,
            relief='solid',
            bd=1
        )
        username_entry.grid(row=0, column=1, pady=row_pad, sticky='w')
        username_entry.focus()

        # Password row
        tk.Label(
            form_frame,
            text='Password:',
            font=('Segoe UI', 11),
            bg='#1d446d',
            fg='#EBF2FA',
            anchor='e',
            width=16
        ).grid(row=1, column=0, padx=(0, 8), pady=row_pad, sticky='e')

        password_entry = tk.Entry(
            form_frame,
            textvariable=self.password_var,
            font=('Segoe UI', 11),
            width=30,
            show='*',
            relief='solid',
            bd=1
        )
        password_entry.grid(row=1, column=1, pady=row_pad, sticky='w')

        # Confirm password row
        tk.Label(
            form_frame,
            text='Confirm Password:',
            font=('Segoe UI', 11),
            bg='#1d446d',
            fg='#EBF2FA',
            anchor='e',
            width=16
        ).grid(row=2, column=0, padx=(0, 8), pady=row_pad, sticky='e')

        confirm_entry = tk.Entry(
            form_frame,
            textvariable=self.confirm_var,
            font=('Segoe UI', 11),
            width=30,
            show='*',
            relief='solid',
            bd=1
        )
        confirm_entry.grid(row=2, column=1, pady=row_pad, sticky='w')

        # Buttons
        button_frame = tk.Frame(self.root, bg='#1d446d')
        button_frame.pack(pady=30)

        self.create_btn = tk.Button(
            button_frame,
            text='CREATE ACCOUNT',
            font=('Segoe UI', 12, 'bold'),
            bg='#9e3e1c',
            fg='#EBF2FA',
            width=14,
            height=1,
            relief='flat',
            cursor='hand2',
            command=self.create_admin,
            state='disabled'
        )
        self.create_btn.pack(side='left', padx=(0, 20))

        close_btn = tk.Button(
            button_frame,
            text='CLOSE',
            font=('Segoe UI', 12, 'bold'),
            bg='#201418',
            fg='#EBF2FA',
            width=12,
            height=1,
            relief='flat',
            cursor='hand2',
            command=self.root.destroy
        )
        close_btn.pack(side='right')

        self.root.bind('<Return>', lambda e: self.create_admin())

    def test_connection_auto(self):
        """Test Neon connection"""
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            conn.close()
            self.db_connected = True
            self.create_btn.config(state='normal', bg='#9e3e1c')
            print("✅ Neon database connection successful!")
        except Exception as e:
            self.db_connected = False
            self.create_btn.config(state='disabled', bg='#7e6233')
            messagebox.showerror(
                "Database Error",
                f"Cannot connect to Neon database:\n{str(e)}\n\n"
                "Please check:\n"
                "• .env file exists with DATABASE_URL\n"
                "• Neon connection string is correct\n"
                "• Database 'logistics_tracking' exists in Neon"
            )

    def create_admin(self):
        if not self.db_connected:
            messagebox.showerror("Error", "Database not connected! Fix connection first.")
            return

        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        confirm_password = self.confirm_var.get().strip()

        if not username:
            messagebox.showerror("Error", "Please enter a username!")
            return

        if not password or not confirm_password:
            messagebox.showerror("Error", "Please enter and confirm password!")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match!")
            self.confirm_var.set("")
            return

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters!")
            self.password_var.set("")
            self.confirm_var.set("")
            return

        try:
            password_bytes = password.encode('utf-8')
            hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
            hashed_str = hashed.decode('utf-8')

            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()

            # Create users table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Insert or update user (upsert)
            cursor.execute("""
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                ON CONFLICT (username) DO UPDATE SET
                    password_hash = %s,
                    created_at = CURRENT_TIMESTAMP
            """, (username, hashed_str, hashed_str))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success!",
                f"✅ Account '{username}' created successfully!\n\n"
                "You can now log in with your main app."
            )
            self.username_var.set("")
            self.password_var.set("")
            self.confirm_var.set("")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create account: {str(e)}")


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('K Logistics™ | Log In')
        self.root.geometry('700x400')
        self.root.resizable(False, False)
        self.root.configure(bg='#1d446d')
        
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        self.create_login_widgets()

    def create_login_widgets(self):
        # Title
        title_label = tk.Label(
            self.root,
            text='K Logistics™',
            font=('Segoe UI', 24, 'bold'),
            bg='#1d446d',
            fg='#EBF2FA'
        )
        title_label.pack(pady=30)

        subtitle_label = tk.Label(
            self.root,
            text='Shipment Tracking System',
            font=('Segoe UI', 12),
            bg='#1d446d',
            fg='#99afc4'
        )
        subtitle_label.pack(pady=(0, 30))

        # Username row
        user_frame = tk.Frame(self.root, bg='#1d446d')
        user_frame.pack(pady=5)
        tk.Label(
            user_frame,
            text='Username:',
            font=('Segoe UI', 11),
            bg='#1d446d',
            fg='#EBF2FA'
        ).pack(side='left', padx=(0, 8))
        username_entry = tk.Entry(
            user_frame,
            textvariable=self.username_var,
            font=('Segoe UI', 11),
            width=25,
            relief='solid',
            bd=1
        )
        username_entry.pack(side='left')
        username_entry.focus()

        # Password row
        pass_frame = tk.Frame(self.root, bg='#1d446d')
        pass_frame.pack(pady=(20, 5))
        tk.Label(
            pass_frame,
            text='Password:',
            font=('Segoe UI', 11),
            bg='#1d446d',
            fg='#EBF2FA'
        ).pack(side='left', padx=(0, 8))
        password_entry = tk.Entry(
            pass_frame,
            textvariable=self.password_var,
            font=('Segoe UI', 11),
            width=25,
            show='*',
            relief='solid',
            bd=1
        )
        password_entry.pack(side='left')

        # Button frame for both buttons
        button_frame = tk.Frame(self.root, bg='#1d446d')
        button_frame.pack(pady=30)

        # Login button
        login_btn = tk.Button(
            button_frame,
            text='LOG IN',
            font=('Segoe UI', 12, 'bold'),
            bg='#9e3e1c',
            fg='#EBF2FA',
            width=12,
            height=1,
            relief='flat',
            cursor='hand2',
            command=self.validate_login
        )
        login_btn.pack(side='left', padx=(0, 15))

        # Create User button
        create_user_btn = tk.Button(
            button_frame,
            text='SIGN UP',
            font=('Segoe UI', 12, 'bold'),
            bg='#7e6233',
            fg='#EBF2FA',
            width=12,
            height=1,
            relief='flat',
            cursor='hand2',
            command=self.open_setup_admin
        )
        create_user_btn.pack(side='left')

        self.root.bind('<Return>', lambda e: self.validate_login())
    
    def open_setup_admin(self):
        """Open the AdminSetupWindow as a modal dialog."""
        AdminSetupWindow(self.root)
    
    def validate_login(self):
        """Validate login credentials"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            messagebox.showerror("Login Failed", "Enter username and password!")
            return
        
        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            conn.close()
            
            if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
                self.root.destroy()
                self.open_main_app()
            else:
                messagebox.showerror("Login Failed", "Invalid username or password!")
                self.password_var.set("") 
                self.username_var.set(username) 
                
        except Exception as e:
            messagebox.showerror("Error", f"Database connection failed: {str(e)}")

    def open_main_app(self):
        main_window = tk.Tk()
        app = LogisticsTracking(main_window)
        main_window.mainloop()

class LogisticsTracking:
    def __init__(self, root):
        self.root = root
        self.root.title('K Logistics™ | Shipment Tracking System')
        self.root.geometry('1110x700')
        self.root.resizable(True, True)

        self.colors = {
            'true blue': '#1d446d',
            'powder blue': '#99afc4',
            'dark orange': '#9e3e1c',
            'chocolate': '#7e6233',
            'lapis lazuli': '#4c6176',
            'alice blue': '#EBF2FA',
            'licorice': '#201418',
            'faux white': '#f0f0f0',
        }

        self.geocode_api_key = os.environ.get(
            "GEOCODE_MAPS_CO_API_KEY",
            "693d05e9bbbad455253577zux511e6d"
        )

        self.temp_origin_coords = None
        self.temp_dest_coords = None

        # FIXED: Initialize database connection
        self.conn = None
        self.cursor = None
        self.create_db()
        self.create_widgets()
        self.load_data()
        
        # Bind closing event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_db(self):
        """FIXED: Use DATABASE_URL and create tables safely"""
        try:
            self.conn = psycopg2.connect(**DB_PARAMS)
            self.cursor = self.conn.cursor()

            # Create users table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create shipments table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS shipments (
                    id SERIAL PRIMARY KEY,
                    tracking_number TEXT UNIQUE,
                    customer TEXT,
                    shipper TEXT,
                    origin_address TEXT,
                    destination_address TEXT,
                    shipment_date TEXT,
                    delivery_date TEXT,
                    service_type TEXT,
                    status TEXT,
                    origin_lat DECIMAL(10,8),
                    origin_lon DECIMAL(11,8),
                    dest_lat DECIMAL(10,8),
                    dest_lon DECIMAL(11,8)
                )
            """)
            self.conn.commit()
            print("Database connected and tables ready!")
        except Exception as e:
            print(f"Database setup error: {e}")
            messagebox.showerror("Database Error", f"Failed to connect to Neon database:\n{str(e)}")
            raise

    def create_widgets(self):
        # headers
        header_frame1 = tk.Frame(self.root, bg=self.colors['true blue'], height=40)
        header_frame2 = tk.Frame(self.root, bg=self.colors['alice blue'], height=3)
        header_frame3 = tk.Frame(self.root, bg=self.colors['dark orange'], height=5)
        header_frame1.pack(fill='x')
        header_frame2.pack(fill='x')
        header_frame3.pack(fill='x')

        header_label1 = tk.Label(
            header_frame1,
            text='K Logistics™ | Shipment Tracking System',
            font=('Segoe UI', 20, 'bold'),
            bg=self.colors['true blue'],
            fg=self.colors['alice blue'],
            pady=10)
        header_label1.pack()

        # input frame
        input_frame = tk.Frame(self.root, bg=self.colors['powder blue'], pady=20)
        input_frame.pack(fill='x', padx=15, pady=15)

        self.TrackingNumber = tk.StringVar()
        self.Customer = tk.StringVar()
        self.Shipper = tk.StringVar()
        self.OriginAddress = tk.StringVar()
        self.DestinationAdd = tk.StringVar()
        self.ShipmentDate = tk.StringVar()
        self.DeliveryDate = tk.StringVar()
        self.ServiceType = tk.StringVar()
        self.Status = tk.StringVar()

        self.register_validator = self.root.register(self.validate_address)

        self.create_input_field(input_frame, 'Tracking Number: ', self.TrackingNumber, 0, 0)
        self.create_input_field(input_frame, 'Customer / Recipient: ', self.Customer, 0, 2)
        self.create_input_field(input_frame, 'Shipper / Sender: ', self.Shipper, 0, 4)
        self.create_address_field(input_frame, 'Origin Address: ', self.OriginAddress, 1, 0)
        self.create_address_field(input_frame, 'Destination Address: ', self.DestinationAdd, 1, 2)
        self.create_input_field(input_frame, 'Shipment Date: ', self.ShipmentDate, 1, 4)
        self.create_input_field(input_frame, 'Delivery Date: ', self.DeliveryDate, 2, 0)
        self.create_input_field(input_frame, 'Service Type: ', self.ServiceType, 2, 2)
        self.create_input_field(input_frame, 'Status: ', self.Status, 2, 4)

        # buttons
        button_frame = tk.Frame(self.root, bg=self.colors['powder blue'], pady=10)
        button_frame.pack(fill='x', padx=15)

        tk.Button(button_frame, text='Add Entry',
                  bg=self.colors['true blue'], fg=self.colors['alice blue'],
                  width=15, command=self.add_entry).pack(side='left', padx=10)
        tk.Button(button_frame, text='Update Entry',
                  bg=self.colors['dark orange'], fg=self.colors['alice blue'],
                  width=15, command=self.update_entry).pack(side='left', padx=10)
        tk.Button(button_frame, text='Search Entry',
                  bg=self.colors['chocolate'], fg=self.colors['alice blue'],
                  width=15, command=self.search_entry).pack(side='left', padx=10)
        tk.Button(button_frame, text='Clear Entry',
                  bg=self.colors['lapis lazuli'], fg=self.colors['alice blue'],
                  width=15, command=self.clear_entry).pack(side='left', padx=10)
        tk.Button(button_frame, text='Delete Entry',
                  bg=self.colors['licorice'], fg=self.colors['alice blue'],
                  width=15, command=self.delete_entry).pack(side='left', padx=10)

        # bottom area: separate frames for map and table
        bottom_frame = tk.Frame(self.root, bg=self.colors['faux white'])
        bottom_frame.pack(fill='both', expand=True, padx=15, pady=(15, 15))

        # LEFT: map frame
        self.maps_frame = tk.Frame(
            bottom_frame,
            bg=self.colors['powder blue'],
            bd=2,
            width=350
        )
        self.maps_frame.pack(side='left', fill='both', expand=False, padx=(0, 20))
        self.maps_frame.pack_propagate(False)

        self.map_widget = TkinterMapView(
            self.maps_frame,
            width=350,
            height=500,
            corner_radius=0,
            max_zoom=22
        )
        self.map_widget.pack(fill='both', expand=True)

        self.map_widget.set_tile_server(
            "https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga",
            max_zoom=22
        )

        self.map_widget.set_position(14.32894, 121.06986)
        self.map_widget.set_zoom(15)

        # RIGHT: table frame
        self.table_frame = tk.Frame(bottom_frame, bg=self.colors['powder blue'])
        self.table_frame.pack(side='right', fill='both', expand=True)

        columns = (
            'ID', 'Tracking', 'Customer', 'Shipper',
            'Origin', 'Dest', 'Ship Date', 'Del Date',
            'Service', 'Status'
        )

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.tree.heading('ID', text='ID')
        self.tree.heading('Tracking', text='Tracking Number')
        self.tree.heading('Customer', text='Customer / Recipient')
        self.tree.heading('Shipper', text='Shipper / Sender')
        self.tree.heading('Origin', text='Origin Address')
        self.tree.heading('Dest', text='Destination Address')
        self.tree.heading('Ship Date', text='Shipment Date')
        self.tree.heading('Del Date', text='Delivery Date')
        self.tree.heading('Service', text='Service Type')
        self.tree.heading('Status', text='Status')

        self.tree.column('ID', width=60, anchor='center')
        self.tree.column('Tracking', width=140, anchor='w')
        self.tree.column('Customer', width=160, anchor='w')
        self.tree.column('Shipper', width=140, anchor='w')
        self.tree.column('Origin', width=200, anchor='w')
        self.tree.column('Dest', width=200, anchor='w')
        self.tree.column('Ship Date', width=110, anchor='center')
        self.tree.column('Del Date', width=110, anchor='center')
        self.tree.column('Service', width=120, anchor='w')
        self.tree.column('Status', width=100, anchor='center')

        v_scroll = ttk.Scrollbar(self.table_frame, orient='vertical', command=self.tree.yview)
        h_scroll = ttk.Scrollbar(self.table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')

        self.table_frame.rowconfigure(0, weight=1)
        self.table_frame.columnconfigure(0, weight=1)

        style = ttk.Style()
        style.configure('Treeview', rowheight=24, font=('Segoe UI', 9))
        style.configure('Treeview.Heading', font=('Segoe UI', 10, 'bold'))

    def create_input_field(self, parent, label_text, variable, row, col):
        label = tk.Label(
            parent,
            text=label_text,
            font=('Segoe UI', 10),
            fg=self.colors['licorice'],
            bg=self.colors['powder blue'],
            anchor='w'
        )
        label.grid(row=row, column=col, sticky='w', padx=(10, 5), pady=8)

        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Segoe UI', 10),
            width=25
        )
        entry.grid(row=row, column=col + 1, sticky='ew', padx=(0, 10), pady=8)
        parent.columnconfigure(col + 1, weight=1)

    def create_address_field(self, parent, label_text, variable, row, col):
        label = tk.Label(
            parent,
            text=label_text,
            font=('Segoe UI', 10),
            fg=self.colors['licorice'],
            bg=self.colors['powder blue'],
            anchor='w'
        )
        label.grid(row=row, column=col, sticky='w', padx=(10, 5), pady=8)
        
        entry = tk.Entry(
            parent,
            textvariable=variable,
            font=('Segoe UI', 10),
            width=25,
            validate='key',
            validatecommand=(self.register_validator, '%P', 'origin' if 'Origin' in label_text else 'dest')
        )
        entry.grid(row=row, column=col + 1, sticky='ew', padx=(0, 10), pady=8)
        parent.columnconfigure(col + 1, weight=1)
        
        if 'Origin' in label_text:
            entry.bind('<KeyRelease>', lambda e: self.update_address_feedback(entry, variable.get(), 'origin'))
        else:
            entry.bind('<KeyRelease>', lambda e: self.update_address_feedback(entry, variable.get(), 'dest'))

    def validate_address(self, text, field_type):
        if len(text.strip()) < 3:
            return True
        self.root.after(500, lambda: self.async_geocode_and_validate(text.strip(), field_type))
        return True

    def async_geocode_and_validate(self, address, field_type):
        coords = self.geocode_address(address)
        if coords:
            if field_type == 'origin':
                self.temp_origin_coords = coords
            else:
                self.temp_dest_coords = coords
        else:
            if field_type == 'origin':
                self.temp_origin_coords = None
            else:
                self.temp_dest_coords = None

    def update_address_feedback(self, entry, address, field_type):
        if len(address.strip()) < 3:
            entry.config(bg='white')
            return
        
        coords = self.geocode_address(address)
        if coords:
            entry.config(bg='#d4edda', relief='solid', bd=2)
        else:
            entry.config(bg='#f8d7da', relief='solid', bd=2)

    def geocode_address(self, address):
        if not address or len(address.strip()) < 3:
            return None
        try:
            url = "https://geocode.maps.co/search"
            params = {"q": address.strip(), "api_key": self.geocode_api_key, "limit": 1}
            resp = requests.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data and len(data) > 0:
                return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            print(f"Geocoding error for '{address}': {e}")
        return None

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            # CHANGED: ORDER BY id ASC instead of DESC
            self.cursor.execute("SELECT * FROM shipments ORDER BY id ASC")
            rows = self.cursor.fetchall()
            for row in rows:
                display_row = list(row)
                if len(str(display_row[4])) > 25:
                    display_row[4] = str(display_row[4])[:25] + "..."
                if len(str(display_row[5])) > 25:
                    display_row[5] = str(display_row[5])[:25] + "..."
                self.tree.insert('', 'end', values=tuple(display_row))
        except Exception as e:
            print(f"Load data error: {e}")


    def add_entry(self):
        try:
            origin_coords = self.temp_origin_coords
            dest_coords = self.temp_dest_coords
            
            if not origin_coords or not dest_coords:
                messagebox.showerror("Error", "Please validate both addresses first (they should turn green)")
                return

            self.cursor.execute("""
                INSERT INTO shipments (
                    tracking_number, customer, shipper,
                    origin_address, destination_address,
                    shipment_date, delivery_date,
                    service_type, status,
                    origin_lat, origin_lon, dest_lat, dest_lon
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                self.TrackingNumber.get().strip(),
                self.Customer.get().strip(),
                self.Shipper.get().strip(),
                self.OriginAddress.get().strip(),
                self.DestinationAdd.get().strip(),
                self.ShipmentDate.get().strip(),
                self.DeliveryDate.get().strip(),
                self.ServiceType.get().strip(),
                self.Status.get().strip(),
                origin_coords[0], origin_coords[1],
                dest_coords[0], dest_coords[1]
            ))
            self.conn.commit()
            messagebox.showinfo("Success", "Entry added successfully!")
            self.clear_entry()
            self.load_data()
        except psycopg2.errors.UniqueViolation:
            self.conn.rollback()
            messagebox.showerror("Error", "Tracking number already exists!")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", f"Add failed: {str(e)}")

    def update_entry(self):
        tracking = self.TrackingNumber.get().strip()
        if not tracking:
            messagebox.showerror("Error", "Enter tracking number to update")
            return
        try:
            origin_coords = self.temp_origin_coords
            dest_coords = self.temp_dest_coords
            
            self.cursor.execute("""
                UPDATE shipments
                SET customer=%s, shipper=%s, origin_address=%s, destination_address=%s,
                    shipment_date=%s, delivery_date=%s, service_type=%s, status=%s,
                    origin_lat=%s, origin_lon=%s, dest_lat=%s, dest_lon=%s
                WHERE tracking_number=%s
            """, (
                self.Customer.get().strip(),
                self.Shipper.get().strip(),
                self.OriginAddress.get().strip(),
                self.DestinationAdd.get().strip(),
                self.ShipmentDate.get().strip(),
                self.DeliveryDate.get().strip(),
                self.ServiceType.get().strip(),
                self.Status.get().strip(),
                origin_coords[0] if origin_coords else None,
                origin_coords[1] if origin_coords else None,
                dest_coords[0] if dest_coords else None,
                dest_coords[1] if dest_coords else None,
                tracking))
            self.conn.commit()
            if self.cursor.rowcount > 0:
                messagebox.showinfo("Success", "Entry updated")
                self.clear_entry()
                self.load_data()
            else:
                messagebox.showerror("Error", "Tracking number not found")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", str(e))

    def search_entry(self):
        tracking = self.TrackingNumber.get().strip()
        if not tracking:
            messagebox.showerror("Error", "Enter tracking number to search")
            return
        try:
            self.cursor.execute("SELECT * FROM shipments WHERE tracking_number=%s", (tracking,))
            row = self.cursor.fetchone()
            if row:
                self.Customer.set(row[2] or "")
                self.Shipper.set(row[3] or "")
                self.OriginAddress.set(row[4] or "")
                self.DestinationAdd.set(row[5] or "")
                self.ShipmentDate.set(row[6] or "")
                self.DeliveryDate.set(row[7] or "")
                self.ServiceType.set(row[8] or "")
                self.Status.set(row[9] or "")
                
                # Update map with stored coordinates
                self.update_map(row[4], row[5], row[10], row[11], row[12], row[13])
            else:
                messagebox.showerror("Error", "Tracking number not found")
        except Exception as e:
            messagebox.showerror("Error", f"Search failed: {str(e)}")

    def clear_entry(self):
        self.TrackingNumber.set("")
        self.Customer.set("")
        self.Shipper.set("")
        self.OriginAddress.set("")
        self.DestinationAdd.set("")
        self.ShipmentDate.set("")
        self.DeliveryDate.set("")
        self.ServiceType.set("")
        self.Status.set("")
        self.temp_origin_coords = None
        self.temp_dest_coords = None
        
        # Reset map and entry backgrounds
        self.map_widget.set_position(14.32894, 121.06986)
        self.map_widget.set_zoom(15)
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()

    def delete_entry(self):
        tracking = self.TrackingNumber.get().strip()
        if not tracking:
            messagebox.showerror("Error", "Enter tracking number to delete")
            return
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete this entry?"):
            return
        try:
            self.cursor.execute("DELETE FROM shipments WHERE tracking_number=%s", (tracking,))
            self.conn.commit()

            if self.cursor.rowcount > 0:
                self.clear_entry()
                self.load_data()
                messagebox.showinfo("Success", "Entry deleted")
            else:
                messagebox.showerror("Error", "Tracking number not found")
        except Exception as e:
            self.conn.rollback()
            messagebox.showerror("Error", str(e))

    def update_map(self, origin, destination, origin_lat=None, origin_lon=None, dest_lat=None, dest_lon=None):
        try:
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()

            if origin_lat and origin_lon and dest_lat and dest_lon:
                origin_coords = (float(origin_lat), float(origin_lon))
                dest_coords = (float(dest_lat), float(dest_lon))
            else:
                origin_coords = self.geocode_address(origin)
                dest_coords = self.geocode_address(destination)
                if not origin_coords or not dest_coords:
                    raise ValueError("Could not geocode addresses")

            origin_lat, origin_lng = origin_coords
            dest_lat, dest_lng = dest_coords

            self.map_widget.set_position((origin_lat + dest_lat) / 2, (origin_lng + dest_lng) / 2)

            self.map_widget.set_marker(
                origin_lat, origin_lng,
                text=f"Origin: {origin}",
                marker_color_circle="green",
                marker_color_outside="green"
            )

            self.map_widget.set_marker(
                dest_lat, dest_lng,
                text=f"Destination: {destination}",
                marker_color_circle="red",
                marker_color_outside="red"
            )

            self.map_widget.set_path([origin_coords, dest_coords])
            self.map_widget.fit_bounding_box(origin_coords, dest_coords)

        except Exception as e:
            print(f"Map update error: {e}")
            self.map_widget.delete_all_marker()
            self.map_widget.delete_all_path()
            self.map_widget.set_position(14.32894, 121.06986)
            self.map_widget.set_zoom(15)

    def on_closing(self):
        if self.conn:
            self.conn.close()
        self.root.destroy()

if __name__ == "__main__":
    # Test Neon connection first
    try:
        test_conn = psycopg2.connect(**DB_PARAMS)
        test_conn.close()
        print("✅ Neon connection successful!")
    except Exception as e:
        print(f"❌ Neon connection failed: {e}")
        print("Please check your .env file and Neon connection string.")
        input("Press Enter to exit...")
        exit(1)
    
    # Start login window
    login_window = tk.Tk()
    login_app = LoginWindow(login_window)
    login_window.protocol("WM_DELETE_WINDOW", lambda: (
        login_window.quit() if messagebox.askokcancel("Quit", "Exit application?") else None
    ))
    login_window.mainloop()
