import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

class PhoneBookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("دفترچه تلفن")
        self.root.geometry("600x500")
        
        # اتصال به پایگاه داده
        self.conn = sqlite3.connect('phonebook.db')
        self.c = self.conn.cursor()
        
        # ایجاد جدول اگر وجود نداشته باشد
        self.c.execute('''CREATE TABLE IF NOT EXISTS contacts
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         name TEXT NOT NULL,
                         phone TEXT NOT NULL)''')
        self.conn.commit()
        
        # ایجاد رابط کاربری
        self.create_widgets()
        self.load_contacts()

    def create_widgets(self):
        # فریم ورودی
        input_frame = Frame(self.root, padx=10, pady=10)
        input_frame.pack(fill=X)
        
        Label(input_frame, text="نام:").grid(row=0, column=0, padx=5, sticky='e')
        self.name_entry = Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        Label(input_frame, text="شماره تلفن:").grid(row=1, column=0, padx=5, sticky='e')
        self.phone_entry = Entry(input_frame, width=30)
        self.phone_entry.grid(row=1, column=1, padx=5)
        
        # فریم دکمه‌های عملیاتی
        btn_frame = Frame(self.root, pady=5)
        btn_frame.pack(fill=X)
        
        add_btn = Button(btn_frame, text="افزودن", command=self.add_contact)
        add_btn.pack(side=RIGHT, padx=5)
        
        search_btn = Button(btn_frame, text="جستجو", command=self.search_contact)
        search_btn.pack(side=RIGHT, padx=5)
        
        update_btn = Button(btn_frame, text="ویرایش", command=self.update_contact)
        update_btn.pack(side=RIGHT, padx=5)
        
        delete_btn = Button(btn_frame, text="حذف", command=self.delete_contact)
        delete_btn.pack(side=RIGHT, padx=5)
        
        show_all_btn = Button(btn_frame, text="نمایش همه", command=self.load_contacts)
        show_all_btn.pack(side=RIGHT, padx=5)
        
        # فریم لیست مخاطبین
        list_frame = Frame(self.root)
        list_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        # Treeview برای نمایش مخاطبین
        self.tree = ttk.Treeview(list_frame, columns=('ID', 'Name', 'Phone'), show='headings')
        self.tree.heading('ID', text='شناسه')
        self.tree.heading('Name', text='نام')
        self.tree.heading('Phone', text='شماره تلفن')
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Name', width=200)
        self.tree.column('Phone', width=150, anchor='center')
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        # رویداد انتخاب مخاطب
        self.tree.bind('<<TreeviewSelect>>', self.on_select)

    def add_contact(self):
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name or not phone:
            messagebox.showwarning("هشدار", "لطفاً نام و شماره تلفن را وارد کنید")
            return
        
        try:
            self.c.execute("INSERT INTO contacts (name, phone) VALUES (?, ?)", (name, phone))
            self.conn.commit()
            self.clear_entries()
            self.load_contacts()
            messagebox.showinfo("موفق", "مخاطب با موفقیت افزوده شد")
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در افزودن مخاطب: {e}")

    def search_contact(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("هشدار", "لطفاً نام برای جستجو وارد کنید")
            return
        
        # پاک کردن لیست فعلی
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            self.c.execute("SELECT id, name, phone FROM contacts WHERE name LIKE ?", (f'%{name}%',))
            contacts = self.c.fetchall()
            
            if not contacts:
                messagebox.showinfo("نتیجه", "مخاطبی یافت نشد")
            else:
                for contact in contacts:
                    self.tree.insert('', 'end', values=contact)
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در جستجو: {e}")

    def update_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک مخاطب را انتخاب کنید")
            return
        
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name or not phone:
            messagebox.showwarning("هشدار", "لطفاً نام و شماره تلفن را وارد کنید")
            return
        
        contact_id = self.tree.item(selected[0])['values'][0]
        try:
            self.c.execute("UPDATE contacts SET name=?, phone=? WHERE id=?", (name, phone, contact_id))
            self.conn.commit()
            self.clear_entries()
            self.load_contacts()
            messagebox.showinfo("موفق", "مخاطب با موفقیت ویرایش شد")
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در ویرایش مخاطب: {e}")

    def delete_contact(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک مخاطب را انتخاب کنید")
            return
        
        if not messagebox.askyesno("تأیید", "آیا مطمئنید که می‌خواهید این مخاطب را حذف کنید؟"):
            return
        
        contact_id = self.tree.item(selected[0])['values'][0]
        try:
            self.c.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
            self.conn.commit()
            self.clear_entries()
            self.load_contacts()
            messagebox.showinfo("موفق", "مخاطب با موفقیت حذف شد")
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در حذف مخاطب: {e}")

    def load_contacts(self):
        # پاک کردن لیست فعلی
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # بارگذاری مخاطبین از پایگاه داده
        try:
            self.c.execute("SELECT id, name, phone FROM contacts ORDER BY name")
            contacts = self.c.fetchall()
            
            for contact in contacts:
                self.tree.insert('', 'end', values=contact)
        except sqlite3.Error as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری مخاطبین: {e}")

    def on_select(self, event):
        selected = self.tree.selection()
        if selected:
            contact = self.tree.item(selected[0])['values']
            self.name_entry.delete(0, END)
            self.name_entry.insert(0, contact[1])
            self.phone_entry.delete(0, END)
            self.phone_entry.insert(0, contact[2])

    def clear_entries(self):
        self.name_entry.delete(0, END)
        self.phone_entry.delete(0, END)

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = Tk()
    app = PhoneBookApp(root)
    root.mainloop()
