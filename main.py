import tkinter as tk
from tkinter import messagebox, ttk, simpledialog, filedialog
import random
import datetime
import pyttsx3  # للنطق

# قائمة الأفعال (يمكن توسيعها لاحقًا لأكثر من 250 فعل)
verbs = [
    ["go", "went", "gone", "يذهب"], ["eat", "ate", "eaten", "يأكل"], ["see", "saw", "seen", "يرى"],
    ["drink", "drank", "drunk", "يشرب"], ["write", "wrote", "written", "يكتب"], ["read", "read", "read", "يقرأ"]
]

class VerbQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("تدريب الأفعال الإنجليزية")
        self.root.geometry("750x650")
        self.root.configure(bg="#e8f0f8")

        # إدخال اسم المستخدم
        self.username = simpledialog.askstring("اسم المستخدم", "يرجى إدخال اسمك:")
        if not self.username:
            self.username = "طالب مجهول"

        self.current_verb = []
        self.part_to_show = -1
        self.attempts = 0
        self.score = 0
        self.correct_verbs = []
        self.wrong_verbs = []

        # إعداد محرك النطق
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 11, "bold"), padding=6)
        self.style.configure("TLabel", font=("Arial", 11), background="#e8f0f8")
        self.style.configure("TEntry", font=("Arial", 11))

        self.create_widgets()
        self.next_verb()

    def create_widgets(self):
        title_label = ttk.Label(self.root, text=f"مرحباً {self.username}! أكمل الأجزاء الناقصة للفعل", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        self.prompt_label = ttk.Label(self.root, text="", font=("Arial", 12, "bold"), foreground="#333")
        self.prompt_label.pack(pady=5)

        # حقول إدخال الأفعال
        self.labels = ["Present:", "Past:", "Past Participle:", "Arabic Meaning:"]
        self.entries = []
        form_frame = ttk.Frame(self.root)
        form_frame.pack(pady=10)
        for i, text in enumerate(self.labels):
            lbl = ttk.Label(form_frame, text=text)
            lbl.grid(row=i, column=0, sticky="w", padx=5, pady=5)
            entry = ttk.Entry(form_frame, width=30)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entries.append(entry)

        # أزرار التحقق والتالي وتصميم الشهادة
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="تحقق", command=self.check_answers).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="التالي", command=self.next_verb).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="تصدير الشهادة", command=self.export_certificate).grid(row=0, column=2, padx=10)

        # عرض النقاط وكلمة أحسنت
        self.score_label = ttk.Label(self.root, text=f"النقاط: {self.score}", font=("Arial", 12, "bold"), foreground="green")
        self.score_label.pack(pady=5)
        self.congrats_label = tk.Label(self.root, text="", font=("Arial", 24, "bold"), fg="blue", bg="#e8f0f8")
        self.congrats_label.pack(pady=5)

        # عرض الأفعال الصحيحة والخاطئة
        correct_frame = ttk.LabelFrame(self.root, text="الأفعال التي أجبت عنها بشكل صحيح")
        correct_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.correct_tree = ttk.Treeview(correct_frame, columns=self.labels, show="headings")
        for col in self.labels:
            self.correct_tree.heading(col, text=col)
            self.correct_tree.column(col, width=150)
        self.correct_tree.pack(fill="both", expand=True)

        wrong_frame = ttk.LabelFrame(self.root, text="الأفعال التي أخطأت فيها")
        wrong_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.wrong_tree = ttk.Treeview(wrong_frame, columns=self.labels, show="headings")
        for col in self.labels:
            self.wrong_tree.heading(col, text=col)
            self.wrong_tree.column(col, width=150)
        self.wrong_tree.pack(fill="both", expand=True)

    def next_verb(self):
        # حفظ الإجابة الحالية قبل الانتقال
        if self.current_verb:
            answered = False
            all_correct = True
            for i, entry in enumerate(self.entries):
                if i == self.part_to_show:
                    continue
                user_answer = entry.get().strip()
                if user_answer:
                    answered = True
                    if user_answer.lower() != self.current_verb[i].strip().lower():
                        all_correct = False
            if answered:
                if all_correct and self.current_verb not in self.correct_verbs:
                    self.score += 1
                    self.score_label.config(text=f"النقاط: {self.score}")
                    self.correct_verbs.append(self.current_verb)
                    self.correct_tree.insert("", tk.END, values=self.current_verb)
                elif not all_correct and self.current_verb not in self.wrong_verbs:
                    self.wrong_verbs.append(self.current_verb)
                    self.wrong_tree.insert("", tk.END, values=self.current_verb)

        # إعادة تهيئة المحاولات وعرض الفعل الجديد
        self.attempts = 0
        self.congrats_label.config(text="")
        for entry in self.entries:
            entry.config(state=tk.NORMAL)
            entry.delete(0, tk.END)

        self.current_verb = random.choice(verbs)
        self.part_to_show = random.randint(0, 3)
        self.prompt_label.config(text="أكمل باقي المعلومات لهذا الفعل:")

        entry_to_show = self.entries[self.part_to_show]
        entry_to_show.insert(0, self.current_verb[self.part_to_show])
        entry_to_show.config(state=tk.DISABLED)

    def check_answers(self):
        feedback = ""
        all_correct = True
        self.attempts += 1

        for i, entry in enumerate(self.entries):
            if i == self.part_to_show:
                continue
            user_answer = entry.get().strip().lower()
            correct_answer = self.current_verb[i].strip().lower()
            if user_answer == correct_answer:
                feedback += f"{self.labels[i]} ✅ صحيح\n"
            else:
                feedback += f"{self.labels[i]} ❌"
                all_correct = False

        if all_correct:
            self.score += 1
            self.score_label.config(text=f"النقاط: {self.score}")
            self.congrats_label.config(text="أحسنت! 🎉")
            self.engine.say("أحسنت")
            self.engine.runAndWait()
            self.correct_verbs.append(self.current_verb)
            self.correct_tree.insert("", tk.END, values=self.current_verb)
            self.next_verb()
        else:
            if self.attempts >= 3:
                help_text = "\n\nالإجابات الصحيحة:\n"
                for i, entry in enumerate(self.entries):
                    if i != self.part_to_show:
                        help_text += f"{self.labels[i]}: {self.current_verb[i]}\n"
                messagebox.showinfo("مساعدة", feedback + help_text)
                self.wrong_verbs.append(self.current_verb)
                self.wrong_tree.insert("", tk.END, values=self.current_verb)
                self.next_verb()
            else:
                messagebox.showinfo("النتيجة", feedback + f"\nحاول مرة أخرى! (محاولة {self.attempts}/3)")

    def export_certificate(self):
        if not self.correct_verbs and not self.wrong_verbs:
            messagebox.showwarning("تنبيه", "لم تقم بالإجابة على أي أفعال بعد.")
            return

        # نافذة لتصميم الشهادة قبل التصدير
        design_win = tk.Toplevel(self.root)
        design_win.title("تصميم الشهادة")
        design_win.geometry("400x300")
        design_win.grab_set()

        tk.Label(design_win, text="عنوان الشهادة:", font=("Arial", 12)).pack(pady=5)
        title_entry = tk.Entry(design_win, width=40)
        title_entry.insert(0, "شهادة تدريب الأفعال الإنجليزية")
        title_entry.pack(pady=5)

        tk.Label(design_win, text="ملاحظات إضافية:", font=("Arial", 12)).pack(pady=5)
        notes_entry = tk.Text(design_win, width=40, height=5)
        notes_entry.pack(pady=5)

        def save_certificate():
            title_text = title_entry.get().strip()
            notes_text = notes_entry.get("1.0", tk.END).strip()
            date_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                initialfile=f"شهادة_{self.username}_{date_str}.txt",
                filetypes=[("Text files","*.txt")]
            )
            if filename:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(f"{title_text}\n")
                    f.write(f"اسم الطالب: {self.username}\n")
                    f.write(f"تاريخ الاختبار: {date_str}\n")
                    f.write(f"عدد الأفعال الصحيحة: {len(self.correct_verbs)}\n")
                    f.write(f"عدد الأفعال الخاطئة: {len(self.wrong_verbs)}\n\n")
                    if notes_text:
                        f.write(f"ملاحظات:\n{notes_text}\n\n")
                    f.write("الأفعال الصحيحة:\n")
                    for v in self.correct_verbs:
                        f.write(f"{v[0]} - {v[1]} - {v[2]} - {v[3]}\n")
                    f.write("\nالأفعال الخاطئة:\n")
                    for v in self.wrong_verbs:
                        f.write(f"{v[0]} - {v[1]} - {v[2]} - {v[3]}\n")
                messagebox.showinfo("تم", f"تم حفظ الشهادة بنجاح في:\n{filename}")
                design_win.destroy()

        tk.Button(design_win, text="تصدير الشهادة", command=save_certificate, font=("Arial", 12, "bold")).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = VerbQuizApp(root)
    root.mainloop()
