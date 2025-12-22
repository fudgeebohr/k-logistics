import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
import bcrypt
import os


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "logistics_tracking",
    "user": "fudge",
    "password": "FugenPG-2025",
}


class AdminSetupWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('K Logistics™ | Sign Up')
        self.root.geometry('700x450')
        self.root.resizable(False, False)
        self.root.configure(bg='#1d446d')

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

        row_pad = 10  # increased vertical padding

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
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            self.db_connected = True
            self.create_btn.config(state='normal', bg='#9e3e1c')
        except Exception as e:
            self.db_connected = False
            self.create_btn.config(state='disabled', bg='#7e6233')
            messagebox.showerror(
                "Database Error",
                f"Cannot connect to database:\n{str(e)}\n\n"
                "Check:\n• PostgreSQL is running\n"
                "• Database 'logistics_tracking' exists\n"
                "• User 'fudge' has access"
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

            conn = psycopg2.connect(**DB_CONFIG)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

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
                f"Account '{username}' created!\n\n"
                f"Login with:\nUsername: {username}\nPassword: [your_password]"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Failed to create account: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = AdminSetupWindow(root)
    root.mainloop()
