# main.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import json
import os
from tasks import TASKS

HISTORY_FILE = "history.json"

class TaskGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных задач")
        self.root.geometry("450x500")
        self.root.resizable(False, False)
        
        self.tasks = TASKS.copy()
        self.history = self.load_history()
        self.current_task = None

        self.create_widgets()
        self.update_history_list()

    def create_widgets(self):
        # Кнопка генерации задачи
        self.generate_btn = tk.Button(
            self.root, text="🎲 Сгенерировать задачу", 
            font=("Arial", 12), command=self.generate_task, bg="#4CAF50", fg="white"
        )
        self.generate_btn.pack(pady=15, fill=tk.X)

        # Текущая задача
        self.task_label = tk.Label(
            self.root, text="Ваша задача появится здесь", 
            font=("Arial", 14), wraplength=400, justify="center"
        )
        self.task_label.pack(pady=10)

        # Фильтр по типу
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(pady=5)
        
        tk.Label(filter_frame, text="Фильтр по типу:").pack(side=tk.LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="все")
        filter_options = ["все", "учёба", "спорт", "работа"]
        
        self.filter_combobox = ttk.Combobox(
            filter_frame, textvariable=self.filter_var,
            values=filter_options, state="readonly", width=10
        )
        self.filter_combobox.pack(side=tk.LEFT, padx=5)
        
        tk.Button(filter_frame, text="Применить", command=self.apply_filter).pack(side=tk.LEFT, padx=5)
        
        # Кнопка добавления новой задачи
        tk.Button(self.root, text="➕ Добавить задачу", command=self.add_new_task).pack(pady=8)

        # История задач (Scrollbar)
        history_frame = tk.Frame(self.root)
        history_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(
            history_frame, yscrollcommand=scrollbar.set,
            width=50, height=12, font=("Arial", 10)
        )
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.history_listbox.yview)

    def generate_task(self):
        if not self.tasks:
            messagebox.showwarning("Нет задач", "Список задач пуст. Добавьте новые задачи.")
            return
            
        self.current_task = random.choice(self.tasks)
        self.task_label.config(text=self.current_task["name"])
        
        # Добавляем в историю только если задача ещё не была сгенерирована последней (опционально)
        if not self.history or self.history[-1] != self.current_task:
            self.history.append(self.current_task)
            self.save_history()
            self.update_history_list()

    def update_history_list(self):
        """Обновляет видимый список истории в GUI."""
        self.history_listbox.delete(0, tk.END)
        
        filter_type = self.filter_var.get()
        
        for task in self.history:
            if filter_type == "все" or task["type"] == filter_type:
                self.history_listbox.insert(tk.END, f"{task['name']} ({task['type']})")

    def apply_filter(self):
        """Применяет выбранный фильтр к истории."""
        self.update_history_list()

    def add_new_task(self):
        """Диалог для добавления новой задачи с валидацией."""
        
        def on_submit():
            name = name_entry.get().strip()
            task_type = type_var.get()
            
            if not name:
                messagebox.showerror("Ошибка", "Название задачи не может быть пустым!")
                return
                
            new_task = {"name": name, "type": task_type}
            TASKS.append(new_task)  # Добавляем в глобальный список
            self.tasks.append(new_task) # Добавляем в текущий экземпляр
            
            add_window.destroy()
            messagebox.showinfo("Успех", f"Задача '{name}' добавлена!")
        
        add_window = tk.Toplevel(self.root)
        add_window.title("Добавить новую задачу")
        add_window.geometry("300x150")
        
        tk.Label(add_window, text="Название задачи:").pack(pady=5)
        name_entry = tk.Entry(add_window, width=35)
        name_entry.pack(pady=5)
        
        type_var = tk.StringVar(value="учёба")
        
        tk.Label(add_window, text="Тип задачи:").pack(pady=5)
        
        for val in ("учёба", "спорт", "работа"):
            tk.Radiobutton(add_window, text=val.capitalize(), variable=type_var, value=val).pack(anchor="w")
            
        submit_btn = tk.Button(add_window, text="Добавить", command=on_submit)
        submit_btn.pack(pady=15)

    def load_history(self):
        """Загружает историю из файла JSON."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []

    def save_history(self):
        """Сохраняет историю в файл JSON."""
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    root = tk.Tk()
    app = TaskGeneratorApp(root)
    root.mainloop()
