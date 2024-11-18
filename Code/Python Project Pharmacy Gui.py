#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  7 09:14:25 2024

@author: soham
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import os

MEDICINE_DB = 'Medicine_Database.csv'
SALES_DB = 'Sales_Records.csv'
LOW_STOCK_THRESHOLD = 10  

USER_CREDENTIALS = {
    "admin": "123",  
    "staff": "1234"  
}

ACCESS_PERMISSIONS = {
    "admin": {"add_medicine", "update_stock", "check_stock", "generate_inventory_report",
              "sell_medicine", "view_sales_records", "backup_data", "analyze_top_selling", 
              "calculate_statistics", "plot_sales_over_time", "plot_top_selling_medicines"},
    "staff": {"sell_medicine", "check_stock", "view_sales_records", "backup_data", 
              "generate_inventory_report"}
}

class PharmacyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pharmacy Management System")
        self.geometry("600x600")
        self.configure(bg="lightblue")
        self.role = None
        self.permissions = set()
        self.create_widgets()

    def create_widgets(self):
        self.login_frame = tk.Frame(self, bg="lightblue")
        self.login_frame.pack(pady=20)

        tk.Label(self.login_frame, text="Username:", bg="lightblue").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.login_frame, text="Password:", bg="lightblue").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.login_frame, show='*')
        self.password_entry.grid(row=1, column=1)

        self.login_button = tk.Button(self.login_frame, text="Login", command=self.authenticate_user)
        self.login_button.grid(row=2, columnspan=2, pady=10)

    def authenticate_user(self):
        username = self.username_entry.get().strip().lower()
        password = self.password_entry.get().strip()

        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            self.role = username
            self.permissions = ACCESS_PERMISSIONS[username]
            self.login_frame.pack_forget()
            self.show_main_menu()
        else:
            messagebox.showerror("Login Error", "Incorrect username or password.")
    def logout(self):
        
        self.menu_frame.pack_forget()
        self.login_frame.pack(pady=20)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        
    def show_main_menu(self):
        self.menu_frame = tk.Frame(self, bg="lightblue")
        self.menu_frame.pack(pady=20)

        tk.Label(self.menu_frame, text="Welcome, " + self.role.capitalize(), bg="lightblue", font=("Arial", 16)).pack(pady=10)

        if "add_medicine" in self.permissions:
            tk.Button(self.menu_frame, text="Add Medicine", command=self.add_medicine).pack(pady=5)
        if "update_stock" in self.permissions:
            tk.Button(self.menu_frame, text="Update Stock", command=self.update_stock).pack(pady=5)
        tk.Button(self.menu_frame, text="Check Stock", command=self.check_stock).pack(pady=5)
        tk.Button(self.menu_frame, text="Generate Inventory Report", command=self.generate_inventory_report).pack(pady=5)
        tk.Button(self.menu_frame, text="Sell Medicine", command=self.sell_medicine).pack(pady=5)
        tk.Button(self.menu_frame, text="View Sales Records", command=self.view_sales_records).pack(pady=5)
        if "analyze_top_selling" in self.permissions:
            tk.Button(self.menu_frame, text="Analyze Top-Selling Medicines", command=self.inventory_analysis).pack(pady=5)
        if "calculate_statistics" in self.permissions:
            tk.Button(self.menu_frame, text="Calculate Price and Stock Statistics", command=self.calculate_statistics).pack(pady=5)
        if "plot_top_selling_medicines" in self.permissions:
            tk.Button(self.menu_frame, text="View Top-Selling Medicines", command=self.plot_top_selling_medicines).pack(pady= 5)

        tk.Button(self.menu_frame, text="LogOut", command=self.logout).pack(pady=20)

    def add_medicine(self):
        name = simpledialog.askstring("Add Medicine", "Enter medicine name:").capitalize()
        price = simpledialog.askfloat("Add Medicine", "Enter price:")
        stock = simpledialog.askinteger("Add Medicine", "Enter stock quantity:")
        prescription_needed = simpledialog.askstring("Add Medicine", "Prescription needed (yes/no):").strip().lower() == "yes"

        new_medicine = Medicine(name, price, stock, prescription_needed)

        df = pd.read_csv(MEDICINE_DB)
        new_entry = pd.DataFrame([[new_medicine.name, new_medicine.price, new_medicine.stock, prescription_needed]], 
                                 columns=['Medicine Name', 'Price', 'Stock Quantity', 'Prescription Needed'])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(MEDICINE_DB, index=False)
        messagebox.showinfo("Success", f"Medicine '{new_medicine.name}' added successfully.")
        auto_backup()

    def update_stock(self):
        name = simpledialog.askstring("Update Stock", "Enter medicine name:").capitalize()
        additional_stock = simpledialog.askinteger("Update Stock", "Enter additional stock quantity:")

        df = pd.read_csv(MEDICINE_DB)
        if name in df['Medicine Name'].values:
            df.loc[df['Medicine Name'] == name, 'Stock Quantity'] += additional_stock
            df.to_csv(MEDICINE_DB, index=False)
            messagebox.showinfo("Success", f"Stock updated successfully for {name}.")
        else:
            messagebox.showerror("Error", f"Medicine '{name}' not found.")
        auto_backup()

    def check_stock(self):
        name = simpledialog.askstring("Check Stock", "Enter medicine name:").capitalize()
        df = pd.read_csv(MEDICINE_DB)
        if name in df['Medicine Name'].values:
            stock = df.loc[df['Medicine Name'] == name, 'Stock Quantity'].values[0]
            alert = " (Low Stock!)" if stock <= LOW_STOCK_THRESHOLD else ""
            messagebox.showinfo("Stock Info", f"Medicine: {name}, Stock: {stock}{alert}")
        else:
            messagebox.showerror("Error", f"Medicine '{name}' not found in stock.")

    def generate_inventory_report(self):
        df = pd.read_csv(MEDICINE_DB)
        if 'Stock Quantity' in df.columns and 'Medicine Name' in df.columns:
            df['Status'] = df['Stock Quantity'].apply(lambda x: "Low Stock!" if x <= LOW_STOCK_THRESHOLD else "In Stock")
            report = df[['Medicine Name', 'Price', 'Stock Quantity', 'Status']].to_string(index=False)
            messagebox.showinfo("Inventory Report", report)
        else:
            messagebox.showerror("Error", "Required columns not found in the DataFrame.")

    def sell_medicine(self):
        name = simpledialog.askstring("Sell Medicine", "Enter medicine name to sell:").capitalize()
        quantity = simpledialog.askinteger("Sell Medicine", "Enter quantity to sell:")
        customer_name = simpledialog.askstring("Sell Medicine", "Enter customer name:")
        customer_number = simpledialog.askstring("Sell Medicine", "Enter customer contact number:")

        df = pd.read_csv(MEDICINE_DB)
        if name in df['Medicine Name'].values:
            stock = df.loc[df['Medicine Name'] == name, 'Stock Quantity'].values[0]
            price = df.loc[df['Medicine Name'] == name, 'Price'].values[0]
            prescription_needed = df.loc[df['Medicine Name'] == name, 'Prescription Needed'].values[0]

            if prescription_needed:
                doctor_name = simpledialog.askstring("Sell Medicine", "Enter doctor's name for prescription:")
                doctor_address = simpledialog.askstring("Sell Medicine", "Enter doctor's address:")
            else:
                doctor_name, doctor_address = None, None

            medicine = Medicine(name, price, stock, prescription_needed)
            total_price = medicine.sell(quantity)

            if total_price is not None:
                df.loc[df['Medicine Name'] == name, 'Stock Quantity'] -= quantity
                df.to_csv(MEDICINE_DB, index=False)

                sales_df = pd.read_csv(SALES_DB)
                new_sale = pd.DataFrame([[name, quantity, total_price, datetime.now(), customer_name, customer_number, doctor_name, doctor_address]], 
                                        columns=['Medicine Name', 'Quantity Sold', 'Total Price', 'Sale Date', 'Customer Name', 'Customer Contact', 'Doctor Name', 'Doctor Address'])
                sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
                sales_df.to_csv(SALES_DB, index=False)

                messagebox.showinfo("Success", f"Sold {quantity} of {name}. Total price: Rs. {total_price:.2f}")
                auto_backup()
            else:
                messagebox.showerror("Error", "Insufficient stock.")
        else:
            messagebox.showerror("Error", f"Medicine '{name}' not found.")

    def view_sales_records(self):
        df = pd.read_csv(SALES_DB)
        records = df[['Sale Date', 'Medicine Name', 'Quantity Sold', 'Total Price', 'Customer Name', 'Customer Contact', 'Doctor Name', 'Doctor Address']].to_string(index=False)
        messagebox.showinfo("Sales Records", records)

    def inventory_analysis(self):
        sales_df = pd.read_csv(SALES_DB)
        sales_df['Quantity Sold'] = pd.to_numeric(sales_df['Quantity Sold'], errors='coerce')
        sales_df = sales_df.dropna(subset=['Quantity Sold'])
        sales_summary = sales_df.groupby('Medicine Name')['Quantity Sold'].sum().nlargest(5)
        
        report = sales_summary.to_string()
        messagebox.showinfo("Top-Selling Medicines", report)

    def calculate_statistics(self):
        data = pd.read_csv(MEDICINE_DB)
        price_stats = {
            'Mean Price': np.mean(data['Price']),
            'Median Price': np.median(data['Price']),
            'Standard Deviation Price': np.std(data['Price']),
        }
        stock_stats = {
            'Mean Stock Quantity': np.mean(data['Stock Quantity']),
            'Median Stock Quantity': np.median(data['Stock Quantity']),
            'Standard Deviation Stock Quantity': np.std(data['Stock Quantity']),
        }

        stats_report = "Price Statistics:\n" + "\n".join([f"{stat}: {value:.2f}" for stat, value in price_stats.items()]) + "\n\n" + \
                       "Stock Statistics:\n" + "\n".join([f"{stat}: {value:.2f}" for stat, value in stock_stats.items()])
        messagebox.showinfo("Statistics", stats_report)

    def plot_top_selling_medicines(self):
        sales_df = pd.read_csv(SALES_DB)
 
        sales_df['Quantity Sold'] = pd.to_numeric(sales_df['Quantity Sold'], errors='coerce')


        sales_df = sales_df.dropna(subset=['Quantity Sold'])

        top_selling = sales_df.groupby('Medicine Name')['Quantity Sold'].sum().nlargest(5)
        
        plt.figure(figsize=(8, 5))
        top_selling.plot(kind='bar', color='skyblue')
        plt.xlabel('Medicine Name')
        plt.ylabel('Total Quantity Sold')
        plt.title('Top 5 Selling Medicines')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


def auto_backup():
    os.makedirs("backup", exist_ok=True)
    pd.read_csv(MEDICINE_DB).to_csv("backup/Medicine_Database_backup.csv", index=False)
    pd.read_csv(SALES_DB).to_csv("backup/Sales_Records_backup.csv", index=False)
    print("Auto-backup completed.")

class Medicine:
    def __init__(self, name, price, stock, prescription_needed):
        self.name = name
        self.price = price
        self.stock = stock
        self.prescription_needed = prescription_needed

    def update_stock(self, additional_stock):
        self.stock += additional_stock

    def sell(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            return self.price * quantity
            auto_backup()
        else:
            return None

if __name__ == "__main__":
    app = PharmacyApp()
    app.mainloop()