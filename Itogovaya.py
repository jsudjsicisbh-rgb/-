# main.py

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

API_KEY = "YOUR_API_KEY"  # Замените на свой ключ с exchangerate-api.com
API_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD"
HISTORY_FILE = "history.json"

CURRENCIES = [
    "USD", "EUR", "GBP", "JPY", "CNY", "RUB", "CHF", "CAD", "AUD", "SEK"
]

class CurrencyConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер валют")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.rates = {}
        self.history = self.load_history()

        self.create_widgets()
        self.fetch_rates()

    def create_widgets(self):
        # Валюта 'Из'
        tk.Label(self.root, text="Из:", font=("Arial", 12)).pack(pady=5)
        self.from_var = tk.StringVar(value="USD")
        ttk.Combobox(self.root, textvariable=self.from_var,
                     values=CURRENCIES, state="readonly", width=10, font=("Arial", 12)).pack(pady=5)

        # Валюта 'В'
        tk.Label(self.root, text="В:", font=("Arial", 12)).pack(pady=5)
        self.to_var = tk.StringVar(value="EUR")
        ttk.Combobox(self.root, textvariable=self.to_var,
                     values=CURRENCIES, state="readonly", width=10, font=("Arial", 12)).pack(pady=5)

        # Сумма
        tk.Label(self.root, text="Сумма:", font=("Arial", 12)).pack(pady=5)
        self.amount_entry = tk.Entry(self.root, font=("Arial", 12), width=15)
        self.amount_entry.pack(pady=5)

        # Кнопка конвертации
        tk.Button(self.root, text="Конвертировать", font=("Arial", 12),
                  bg="#4CAF50", fg="white", command=self.convert).pack(pady=15)

        # Результат
        self.result_label = tk.Label(self.root, text="Результат: ", font=("Arial", 14, "bold"))
        self.result_label.pack(pady=10)

        # История (с прокруткой)
        history_frame = tk.Frame(self.root)
        history_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(history_frame, yscrollcommand=scrollbar.set,
                                          width=60, height=10, font=("Arial", 10))
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.history_listbox.yview)
        
        self.update_history_list()

    def fetch_rates(self):
        try:
            response = requests.get(API_URL)
            data = response.json()
            if data.get('result') == 'success':
                self.rates = data['conversion_rates']
                messagebox.showinfo("Успех", "Курсы валют успешно загружены!")
            else:
                messagebox.showerror("Ошибка API", f"Не удалось получить курсы: {data.get('error-type')}")
                self.rates = {}
        except Exception as e:
            messagebox.showerror("Ошибка сети", f"Нет подключения к интернету или неверный API-ключ.\n{e}")
            self.rates = {}

    def convert(self):
        from_curr = self.from_var.get()
        to_curr = self.to_var.get()
        
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                raise ValueError("Сумма должна быть положительной")
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Пожалуйста, введите корректную сумму (положительное число).")
            return

        if not self.rates:
            messagebox.showerror("Нет данных", "Сначала загрузите курсы валют.")
            return

        if from_curr not in self.rates or to_curr not in self.rates:
            messagebox.showerror("Ошибка", "Выбрана недоступная валюта.")
            return

        # Конвертация через USD (базовая валюта в этом API)
        if from_curr == "USD":
            result = amount * self.rates[to_curr]
        elif to_curr == "USD":
            result = amount / self.rates[from_curr]
        else:
            result = (amount / self.rates[from_curr]) * self.rates[to_curr]

        result_text = f"{amount} {from_curr} = {result:.2f} {to_curr}"
        self.result_label.config(text=result_text)
        
        # Сохранение в историю
        history_entry = {
            "from": from_curr,
            "to": to_curr,
            "amount": amount,
            "result": result,
            "rate": result / amount if amount != 0 else 0,
            "timestamp": None  # Можно добавить время, если нужно
        }
        
        self.history.append(history_entry)
        self.save_history()
        self.update_history_list()

    def update_history_list(self):
        self.history_listbox.delete(0, tk.END)
        for entry in reversed(self.history[-10:]):  # Показываем последние 10 операций
            line = f"{entry['amount']} {entry['from']} -> {entry['result']:.2f} {entry['to']} (Курс: {entry['rate']:.4f})"
            self.history_listbox.insert(tk.END, line)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_history(self):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyConverterApp(root)
    root.mainloop()
