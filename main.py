import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog

class CardManager:
    def __init__(self, root, file_path):
        self.root = root
        self.root.title("Менеджер карточек")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self.file_path = file_path
        self.data = self.load_data()
        self.sort_cards()
        
        # Создание интерфейса
        self.create_widgets()
        self.refresh_listbox()
        
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка загрузки файла: {str(e)}")
                return self.create_default_data()
        return self.create_default_data()

    def create_default_data(self):
        return {
            "deckName": "Сверхлюди",
            "isValid": True,
            "proofs": []
        }

    def save_data(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
            return False

    def sort_cards(self):
        self.data['proofs'] = sorted(self.data['proofs'], key=lambda x: x['tagline'].lower())

    def create_widgets(self):
        # Меню
        self.menu_bar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Сохранить", command=self.save_data)
        self.file_menu.add_command(label="Сохранить как...", command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Выход", command=self.root.destroy)
        self.menu_bar.add_cascade(label="Файл", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)
        
        # Фрейм для списка карточек
        list_frame = ttk.LabelFrame(self.root, text="Список свойств")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Список карточек с прокруткой
        self.listbox = tk.Listbox(list_frame, font=("Arial", 11))
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Бинд двойного клика для редактирования
        self.listbox.bind("<Double-Button-1>", self.edit_card)
        
        # Фрейм для кнопок управления
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопки действий
        ttk.Button(button_frame, text="Добавить", command=self.add_card).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редактировать", command=lambda: self.edit_card()).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Удалить", command=self.delete_card).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Импортировать", command=self.import_cards).pack(side=tk.LEFT, padx=5)
        
        # Кнопки справа
        ttk.Button(button_frame, text="Поиск", command=self.search_card).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Сохранить", command=self.save_data).pack(side=tk.RIGHT, padx=5)
        
        # Статус бар
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.update_status()

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for card in self.data['proofs']:
            self.listbox.insert(tk.END, card['tagline'])
        self.update_status()

    def update_status(self):
        count = len(self.data['proofs'])
        self.status_var.set(f"Файл: {os.path.basename(self.file_path)} | Карточек: {count} | Колода: {self.data['deckName']}")

    def add_card(self, tagline=None):
        if tagline is None:
            tagline = simpledialog.askstring("Добавить свойство", "Введите новое свойство:")
        
        if not tagline:
            return
        
        tagline_lower = tagline.lower()
        if any(card['tagline'].lower() == tagline_lower for card in self.data['proofs']):
            messagebox.showerror("Ошибка", "Такое свойство уже существует!")
            return
        
        new_card = {
            "content": "Факт",
            "tagline": tagline,
            "cardType": 3
        }
        
        self.data['proofs'].append(new_card)
        self.sort_cards()
        self.refresh_listbox()
        self.save_data()
        self.listbox.see(tk.END)
        messagebox.showinfo("Успех", f"Свойство добавлено: {tagline}")

    def edit_card(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите свойство для редактирования")
            return
        
        index = selection[0]
        old_tagline = self.data['proofs'][index]['tagline']
        
        new_tagline = simpledialog.askstring(
            "Редактировать свойство", 
            "Измените свойство:", 
            initialvalue=old_tagline
        )
        
        if not new_tagline or new_tagline == old_tagline:
            return
        
        new_tagline_lower = new_tagline.lower()
        # Проверяем уникальность, исключая текущую карточку
        if any(i != index and card['tagline'].lower() == new_tagline_lower 
               for i, card in enumerate(self.data['proofs'])):
            messagebox.showerror("Ошибка", "Такое свойство уже существует!")
            return
        
        self.data['proofs'][index]['tagline'] = new_tagline
        self.sort_cards()
        self.refresh_listbox()
        self.save_data()
        messagebox.showinfo("Успех", "Свойство обновлено")

    def delete_card(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите свойство для удаления")
            return
        
        index = selection[0]
        tagline = self.data['proofs'][index]['tagline']
        
        if messagebox.askyesno("Подтверждение", f"Удалить свойство: {tagline}?"):
            del self.data['proofs'][index]
            self.refresh_listbox()
            self.save_data()
            messagebox.showinfo("Успех", "Свойство удалено")

    def search_card(self):
        query = simpledialog.askstring("Поиск", "Введите текст для поиска:")
        if not query:
            return
        
        query_lower = query.lower()
        matches = [i for i, card in enumerate(self.data['proofs']) 
                 if query_lower in card['tagline'].lower()]
        
        if not matches:
            messagebox.showinfo("Поиск", "Совпадений не найдено")
            return
        
        # Выделяем первое совпадение
        self.listbox.selection_clear(0, tk.END)
        self.listbox.see(matches[0])
        self.listbox.selection_set(matches[0])
        self.listbox.activate(matches[0])
        
        if len(matches) > 1:
            messagebox.showinfo("Поиск", f"Найдено {len(matches)} совпадений. Перейти к следующему?",
                               detail="Используйте клавиши навигации для просмотра результатов")
    
    def import_cards(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл для импорта",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Проверяем структуру файла
            if not isinstance(import_data, dict) or 'proofs' not in import_data:
                messagebox.showerror("Ошибка", "Неправильный формат файла: отсутствует ключ 'proofs'")
                return
                
            new_count = 0
            skipped_count = 0
            current_taglines = {card['tagline'].lower() for card in self.data['proofs']}
            
            for card in import_data['proofs']:
                # Проверяем обязательные поля
                if not all(key in card for key in ['content', 'tagline']):
                    skipped_count += 1
                    continue
                
                # Нормализуем content к виду "Факт"
                normalized_content = self.normalize_content(card['content'])
                
                # Проверяем содержание и уникальность
                if normalized_content == "Факт" and card['tagline'].lower() not in current_taglines:
                    new_card = {
                        "content": "Факт",  # Всегда сохраняем в стандартном виде
                        "tagline": card['tagline'],
                        "cardType": card.get('cardType', 3)
                    }
                    self.data['proofs'].append(new_card)
                    current_taglines.add(card['tagline'].lower())
                    new_count += 1
                else:
                    skipped_count += 1
            
            self.sort_cards()
            self.refresh_listbox()
            self.save_data()
            
            messagebox.showinfo(
                "Импорт завершен",
                f"Успешно импортировано карточек: {new_count}\n"
                f"Пропущено дубликатов/невалидных: {skipped_count}"
            )
            
        except Exception as e:
            messagebox.showerror("Ошибка импорта", f"Не удалось загрузить файл:\n{str(e)}")
    
    def save_as(self):
        """Сохранить колоду как новый файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")],
            title="Сохранить колоду как"
        )
        
        if not file_path:
            return
        
        self.file_path = file_path
        if self.save_data():
            self.update_status()
            messagebox.showinfo("Сохранено", f"Колода успешно сохранена как:\n{file_path}")
    
    def normalize_content(self, content):
        """Приводит значение content к стандартному виду 'Факт' независимо от регистра"""
        if isinstance(content, str) and content.lower() == "факт":
            return "Факт"
        return content
    
    def on_closing(self):
        if self.save_data():
            self.root.destroy()

def show_start_dialog():
    """Показывает начальный диалог выбора действия"""
    root = tk.Tk()
    root.withdraw()  # Скрываем основное окно
    
    # Создаем диалоговое окно
    dialog = tk.Toplevel(root)
    dialog.title("Менеджер карточек")
    dialog.geometry("400x200")
    dialog.resizable(False, False)
    dialog.grab_set()  # Делаем окно модальным
    dialog.focus_set()
    
    # Центрируем окно
    dialog.update_idletasks()
    width = dialog.winfo_width()
    height = dialog.winfo_height()
    x = (dialog.winfo_screenwidth() // 2) - (width // 2)
    y = (dialog.winfo_screenheight() // 2) - (height // 2)
    dialog.geometry(f'+{x}+{y}')
    
    # Создаем элементы интерфейса
    ttk.Label(dialog, text="Выберите действие:", font=("Arial", 12)).pack(pady=20)
    
    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=10, fill=tk.X, padx=50)
    
    # Результат диалога
    result = {"action": None, "file_path": None}
    
    def on_create():
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt")],
            title="Создать новую колоду"
        )
        if file_path:
            # Создаем базовую структуру
            data = {
                "deckName": "Сверхлюди",
                "isValid": True,
                "proofs": []
            }
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                result["action"] = "create"
                result["file_path"] = file_path
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать файл:\n{str(e)}")
    
    def on_open():
        file_path = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt")],
            title="Открыть колоду"
        )
        if file_path:
            result["action"] = "open"
            result["file_path"] = file_path
            dialog.destroy()
    
    ttk.Button(btn_frame, text="Создать новую колоду", command=on_create).pack(pady=5, fill=tk.X)
    ttk.Button(btn_frame, text="Открыть существующую", command=on_open).pack(pady=5, fill=tk.X)
    ttk.Button(btn_frame, text="Отмена", command=dialog.destroy).pack(pady=5, fill=tk.X)
    
    dialog.wait_window(dialog)
    root.destroy()
    return result

def main():
    # Показываем стартовый диалог
    choice = show_start_dialog()
    
    if not choice["file_path"]:
        return  # Пользователь отменил
    
    # Запускаем основное приложение
    root = tk.Tk()
    app = CardManager(root, choice["file_path"])
    root.mainloop()

if __name__ == "__main__":
    main()
