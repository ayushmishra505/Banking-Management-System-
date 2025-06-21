from tkinter import *
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime

class Customer:
    def __init__(self, name, age, salary):
        self.name = name
        self.age = age
        self.salary = salary
        self.accounts = []
        

class Account:
    def __init__(self, account_number, customer, pin, balance=0.0):
        self.account_number = account_number
        self.customer = customer
        self.pin = pin
        self.balance = balance
        self.transactions = []
        customer.accounts.append(self)

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount
        self.record_transaction(f"Deposit: +₹{amount:,.2f}")
        return self.balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.record_transaction(f"Withdrawal: -₹{amount:,.2f}")
        return self.balance

    def record_transaction(self, description):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transactions.append(f"{timestamp} - {description} - Balance: ₹{self.balance:,.2f}")

    def get_transaction_history(self):
        return self.transactions

class CheckingAccount(Account):
    def __init__(self, account_number, customer, pin, balance=0.0, overdraft_limit=500):
        super().__init__(account_number, customer, pin, balance)
        self.overdraft_limit = overdraft_limit
        self.account_type = "Checking"

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > (self.balance + self.overdraft_limit):
            raise ValueError("Exceeds overdraft limit")
        self.balance -= amount
        self.record_transaction(f"Withdrawal: -₹{amount:,.2f}")
        return self.balance

class SavingsAccount(Account):
    def __init__(self, account_number, customer, pin, balance=0.0, interest_rate=0.01):
        super().__init__(account_number, customer, pin, balance)
        self.interest_rate = interest_rate
        self.account_type = "Savings"

    def apply_interest(self):
        interest = self.balance * self.interest_rate
        self.balance += interest
        self.record_transaction(f"Interest: +₹{interest:,.2f}")
        return self.balance

class Bank:
    def __init__(self, name):
        self.name = name
        self.customers = []
        self.accounts = {}
        self.account_counter = 1000

    def create_customer(self, name, age, salary):
        customer = Customer(name, age, salary)
        self.customers.append(customer)
        return customer

    def create_account(self, account_type, customer, pin, balance=0.0, **kwargs):
        self.account_counter += 1
        account_number = str(self.account_counter)

        if account_type.lower() == "checking":
            account = CheckingAccount(account_number, customer, pin, balance, **kwargs)
        elif account_type.lower() == "savings":
            account = SavingsAccount(account_number, customer, pin, balance, **kwargs)
        else:
            raise ValueError("Invalid account type")

        self.accounts[account_number] = account
        return account

    def get_account_by_pin(self, pin):
        for account in self.accounts.values():
            if account.pin == pin:
                return account
        return None

    def authenticate(self, name, pin):
        account = self.get_account_by_pin(pin)
        if account and account.customer.name == name:
            return account
        return None

class BankSystem:
    def __init__(self, master):
        self.master = master
        self.master.title("Bank Management System")
        self.master.attributes('-fullscreen', True)
        self.master.bind("<Escape>", lambda e: self.master.destroy())
        self.master.configure(bg="#1f1f2e")

        # Bank instance
        self.bank = Bank("Python Bank")

        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TNotebook', background="#1f1f2e", borderwidth=0)
        self.style.configure('TNotebook.Tab', background="#4a6fa5", foreground="white", padding=(10, 5), font=("Segoe UI", 15, 'bold'))
        self.style.map("TNotebook.Tab", background=[("selected", "#354f7c")])

        self.style.configure('TFrame', background='#2b2b40')
        self.style.configure('TLabel', background='#2b2b40', foreground='white', font=('Segoe UI', 15))
        self.style.configure('Header.TLabel', font=('Segoe UI', 50, 'bold'), background='#1f1f2e', foreground='#ffffff')
        self.style.configure('TButton', font=('Segoe UI', 15), padding=6, relief='flat')
        self.style.configure('Accent.TButton', background='#3498db', foreground='white')
        self.style.configure('Success.TButton', background='#2ecc71', foreground='black')
        self.style.configure('Warning.TButton', background='#f1c40f', foreground='black')
        self.style.configure('Danger.TButton', background='#e74c3c', foreground='white')

        self.style.map('TButton',
            background=[('active', '#555')],
            foreground=[('disabled', '#999')]
        )

        self.header = ttk.Label(master, text="Bank Management System", style='Header.TLabel')
        self.header.pack(pady=20)

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill=BOTH, expand=True, padx=20, pady=10)

        self.create_account_frame = ttk.Frame(self.notebook)
        self.login_frame = ttk.Frame(self.notebook)
        self.user_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.create_account_frame, text="Create Account")
        self.notebook.add(self.login_frame, text="Login")
        self.notebook.add(self.user_frame, text="User Dashboard", state='hidden')

        self.current_account = None
        self.setup_create_account_tab()
        self.setup_login_tab()
        self.setup_user_dashboard()

        self.status_var = StringVar()
        self.status_bar = ttk.Label(master, textvariable=self.status_var, relief='sunken', anchor='w')
        self.status_bar.pack(fill=X, padx=10, pady=15)
        self.status_var.set("Welcome to Bank Management System")

    def setup_create_account_tab(self):
        form_frame = ttk.Frame(self.create_account_frame)
        form_frame.pack(pady=30)

        fields = [
            ("Name", "name_entry"),
            ("Age", "age_entry"),
            ("Salary", "salary_entry"),
            ("Account Type", "account_type_entry"),
            ("Initial Deposit", "initial_deposit_entry"),
            ("PIN (4 digits)", "pin_entry")
        ]

        self.entries = {}
        for i, (label, var_name) in enumerate(fields):
            ttk.Label(form_frame, text=label+":").grid(row=i, column=0, padx=10, pady=5, sticky='e')

            if var_name == "account_type_entry":
                account_types = ["Checking", "Savings"]
                entry = ttk.Combobox(form_frame, values=account_types, state="readonly", font=("Segoe UI", 12))
                entry.current(0)
            else:
                entry = ttk.Entry(form_frame, font=("Segoe UI", 20))

            entry.grid(row=i, column=1, padx=10, pady=5, ipady=5)
            self.entries[var_name] = entry

        self.entries['pin_entry'].config(show="*")

        create_btn = ttk.Button(form_frame, text="Create Account", style='Success.TButton', command=self.create_account)
        create_btn.grid(row=len(fields), column=1, pady=20, sticky='e')

    def setup_login_tab(self):
        login_form = ttk.Frame(self.login_frame)
        login_form.pack(pady=50)

        ttk.Label(login_form, text="Name:").grid(row=0, column=0, padx=10, pady=10, sticky='e')
        self.login_name_entry = ttk.Entry(login_form, font=("Segoe UI", 14))
        self.login_name_entry.grid(row=0, column=1, padx=10, pady=10, ipady=5)

        ttk.Label(login_form, text="PIN:").grid(row=1, column=0, padx=10, pady=10, sticky='e')
        self.login_pin_entry = ttk.Entry(login_form, show="*", font=("Segoe UI", 14))
        self.login_pin_entry.grid(row=1, column=1, padx=10, pady=10, ipady=5)

        login_btn = ttk.Button(login_form, text="Login", style='Accent.TButton', command=self.login)
        login_btn.grid(row=2, column=1, pady=20, sticky='e')
        self.master.bind('<Return>', lambda event: self.login())

    def setup_user_dashboard(self):
        info_frame = ttk.Frame(self.user_frame)
        info_frame.pack(fill=X, padx=20, pady=20)

        self.user_details = {
            'name': ttk.Label(info_frame, font=('Segoe UI', 25)),
            'age': ttk.Label(info_frame, font=('Segoe UI', 25)),
            'salary': ttk.Label(info_frame, font=('Segoe UI', 25)),
            'account_type': ttk.Label(info_frame, font=('Segoe UI', 25)),
            'account_number': ttk.Label(info_frame, font=('Segoe UI', 25)),
            'balance': ttk.Label(info_frame, font=('Segoe UI', 25, 'bold'), foreground="#f00f1e")
        }

        for i, (key, label) in enumerate(self.user_details.items()):
            ttk.Label(info_frame, text=f"{key.replace('_', ' ').title()}:", font=('Segoe UI', 30, 'bold')).grid(row=i, column=0, padx=10, pady=5, sticky='e')
            label.grid(row=i, column=1, padx=10, pady=5, sticky='w')

        btn_frame = ttk.Frame(self.user_frame)
        btn_frame.pack(fill=X, padx=20, pady=20)

        actions = [
            ("View Transactions", 'Accent.TButton', self.view_transaction_log),
            ("Deposit", 'Success.TButton', self.deposit),
            ("Withdraw", 'Warning.TButton', self.withdraw),
            ("Apply Interest", 'Accent.TButton', self.apply_interest),
            ("Logout", 'Danger.TButton', self.logout)
        ]

        for i, (text, style, cmd) in enumerate(actions):
            btn = ttk.Button(btn_frame, text=text, style=style, command=cmd)
            btn.grid(row=0, column=i, padx=5, pady=10, ipadx=5)

    def create_account(self):
        name = self.entries['name_entry'].get()
        age = self.entries['age_entry'].get()
        salary = self.entries['salary_entry'].get()
        account_type = self.entries['account_type_entry'].get()
        initial_deposit = self.entries['initial_deposit_entry'].get()
        pin = self.entries['pin_entry'].get()

        if not all([name, age, salary, account_type, initial_deposit, pin]):
            messagebox.showerror("Error", "All fields are required!")
            return
        if not age.isdigit():
            messagebox.showerror("Error", "Age must be a number!")
            return
        if not salary.replace('.', '').isdigit():
            messagebox.showerror("Error", "Salary must be a number!")
            return
        if not initial_deposit.replace('.', '').isdigit():
            messagebox.showerror("Error", "Initial deposit must be a number!")
            return
        if not pin.isdigit() or len(pin) != 4:
            messagebox.showerror("Error", "PIN must be a 4-digit number!")
            return

        if self.bank.get_account_by_pin(pin):
            messagebox.showerror("Error", "This PIN is already registered!")
            return

        try:
            customer = self.bank.create_customer(name, age, salary)
            account = self.bank.create_account(account_type, customer, pin, float(initial_deposit))
            for entry in self.entries.values():
                if isinstance(entry, ttk.Entry):
                    entry.delete(0, END)
                elif isinstance(entry, ttk.Combobox):
                    entry.set('')
            messagebox.showinfo("Success", f"{account_type} account created successfully!\nAccount Number: {account.account_number}")
            self.status_var.set("Account created successfully!")
            self.notebook.select(self.login_frame)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def login(self):
        name = self.login_name_entry.get()
        pin = self.login_pin_entry.get()

        if not name or not pin:
            messagebox.showerror("Error", "Please enter both name and PIN")
            return

        account = self.bank.authenticate(name, pin)
        if account:
            self.current_account = account
            self.update_user_dashboard()
            self.notebook.tab(self.user_frame, state='normal')
            self.notebook.select(self.user_frame)
            self.notebook.tab(self.login_frame, state='hidden')
            self.notebook.tab(self.create_account_frame, state='hidden')
            self.login_name_entry.delete(0, END)
            self.login_pin_entry.delete(0, END)
            self.status_var.set(f"Welcome, {name}!")
        else:
            messagebox.showerror("Error", "Invalid name or PIN")
            self.status_var.set("Login failed - invalid credentials")

    def update_user_dashboard(self):
        customer = self.current_account.customer
        self.user_details['name'].config(text=customer.name)
        self.user_details['age'].config(text=customer.age)
        self.user_details['salary'].config(text=f"₹{float(customer.salary):,.2f}")
        self.user_details['account_type'].config(text=self.current_account.account_type)
        self.user_details['account_number'].config(text=self.current_account.account_number)
        self.user_details['balance'].config(text=f"₹{self.current_account.balance:,.2f}")

    def deposit(self):
        amount = simpledialog.askstring("Deposit", "Enter amount to deposit:")
        if not amount:
            return
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            self.current_account.deposit(amount)
            self.update_user_dashboard()
            self.status_var.set(f"Deposit of ₹{amount:,.2f} successful")
            messagebox.showinfo("Success", f"₹{amount:,.2f} deposited successfully!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def withdraw(self):
        amount = simpledialog.askstring("Withdraw", "Enter amount to withdraw:")
        if not amount:
            return
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            self.current_account.withdraw(amount)
            self.update_user_dashboard()
            self.status_var.set(f"Withdrawal of ₹{amount:,.2f} successful")
            messagebox.showinfo("Success", f"₹{amount:,.2f} withdrawn successfully!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def apply_interest(self):
        if isinstance(self.current_account, SavingsAccount):
            try:
                interest = self.current_account.balance * self.current_account.interest_rate
                self.current_account.apply_interest()
                self.update_user_dashboard()
                self.status_var.set(f"Interest of ₹{interest:,.2f} applied")
                messagebox.showinfo("Success", f"Interest applied: ₹{interest:,.2f}\nNew balance: ₹{self.current_account.balance:,.2f}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showerror("Error", "Interest only applies to savings accounts")

    def view_transaction_log(self):
        log_window = Toplevel(self.master)
        log_window.title("Transaction History")
        log_window.geometry("600x400")

        scrollbar = Scrollbar(log_window)
        scrollbar.pack(side=RIGHT, fill=Y)

        text_area = Text(log_window, yscrollcommand=scrollbar.set, font=('Courier New', 12), padx=10, pady=10)
        text_area.pack(fill=BOTH, expand=True)
        scrollbar.config(command=text_area.yview)

        transactions = self.current_account.get_transaction_history()
        if not transactions:
            text_area.insert(END, "No transactions yet")
        else:
            for trans in reversed(transactions):
                text_area.insert(END, f"{trans}\n\n")

        text_area.config(state=DISABLED)

    def logout(self):
        self.current_account = None
        self.notebook.tab(self.login_frame, state='normal')
        self.notebook.tab(self.create_account_frame, state='normal')
        self.notebook.tab(self.user_frame, state='hidden')
        self.notebook.select(self.login_frame)
        self.status_var.set("Logged out successfully")

def main():
    root = Tk()
    app = BankSystem(root)
    root.mainloop()

if __name__ == '__main__':
    main()
