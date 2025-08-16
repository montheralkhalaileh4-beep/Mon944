# main.py
import random
import datetime
from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ListProperty, BooleanProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

# للمحاولة بالنطق عبر plyer على الأندرويد (اختياري على سطح المكتب)
try:
    from plyer import tts
    HAS_TTS = True
except Exception:
    HAS_TTS = False

# ====== قاعدة الأفعال (عينة — وسّعها لاحقًا إلى 250+ فعل) ======
verbs = [
    ["go", "went", "gone", "يذهب"],
    ["eat", "ate", "eaten", "يأكل"],
    ["see", "saw", "seen", "يرى"],
    ["drink", "drank", "drunk", "يشرب"],
    ["write", "wrote", "written", "يكتب"],
    ["read", "read", "read", "يقرأ"],
    ["be", "was/were", "been", "يكون"],
    ["do", "did", "done", "يفعل"],
    ["take", "took", "taken", "يأخذ"],
    ["give", "gave", "given", "يعطي"],
    ["speak", "spoke", "spoken", "يتكلم"],
    ["run", "ran", "run", "يجري"],
    ["swim", "swam", "swum", "يسبح"],
    ["know", "knew", "known", "يعرف"],
    ["think", "thought", "thought", "يفكر"],
    ["find", "found", "found", "يجد"],
]

KV = r"""
#:import Factory kivy.factory.Factory

<Header@BoxLayout>:
    size_hint_y: None
    height: dp(58)
    padding: dp(10)
    spacing: dp(10)
    canvas.before:
        Color:
            rgba: 0.93, 0.96, 0.98, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [0, 0, 18, 18]
    Label:
        text: root.title if hasattr(root, 'title') else ""
        font_size: '18sp'
        bold: True
        color: 0,0,0,1

<StartScreen>:
    name: "start"
    BoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(16)
        Header:
            title: "مرحباً! أدخل اسمك للبدء"
        TextInput:
            id: name_input
            hint_text: "اكتب اسمك هنا"
            font_size: '18sp'
            size_hint_y: None
            height: dp(52)
            multiline: False
        Button:
            text: "ابدأ التدريب"
            size_hint_y: None
            height: dp(52)
            on_release: root.start(name_input.text)

<QuizScreen>:
    name: "quiz"
    username: app.username
    BoxLayout:
        orientation: "vertical"
        padding: dp(10)
        spacing: dp(8)

        Header:
            title: "أكمل الأجزاء الناقصة للفعل - مرحباً [b]{}[/b]".format(app.username)
        BoxLayout:
            size_hint_y: None
            height: dp(34)
            spacing: dp(10)
            Label:
                id: score_lbl
                text: "النقاط: {}".format(root.score)
                bold: True
                color: 0,0.5,0,1
            Label:
                id: tries_lbl
                text: "محاولات: {}".format(root.attempts)
                color: 0.2,0.2,0.2,1
            Label:
                id: ahsant_lbl
                text: root.ahsant_text
                color: 0,0,1,1
                bold: True

        GridLayout:
            cols: 2
            row_default_height: dp(46)
            row_force_default: True
            col_default_width: self.width/2
            col_force_default: False
            padding: dp(6)
            spacing: dp(6)

            Label: text: "Present:"
            TextInput:
                id: present_in
                multiline: False
                readonly: root.readonly_index==0
                background_color: (0.95,0.95,0.95,1) if self.readonly else (1,1,1,1)
                on_text_validate: root.focus_next(self)

            Label: text: "Past:"
            TextInput:
                id: past_in
                multiline: False
                readonly: root.readonly_index==1
                background_color: (0.95,0.95,0.95,1) if self.readonly else (1,1,1,1)
                on_text_validate: root.focus_next(self)

            Label: text: "Past Participle:"
            TextInput:
                id: pp_in
                multiline: False
                readonly: root.readonly_index==2
                background_color: (0.95,0.95,0.95,1) if self.readonly else (1,1,1,1)
                on_text_validate: root.focus_next(self)

            Label: text: "Arabic Meaning:"
            TextInput:
                id: ar_in
                multiline: False
                readonly: root.readonly_index==3
                background_color: (0.95,0.95,0.95,1) if self.readonly else (1,1,1,1)
                on_text_validate: root.focus_next(self)

        BoxLayout:
            size_hint_y: None
            height: dp(52)
            spacing: dp(10)
            Button:
                text: "تحقق"
                on_release: root.check_answers()
            Button:
                text: "التالي"
                on_release: root.next_verb(save_current=True)
            Button:
                text: "تصدير الشهادة"
                on_release: root.open_certificate_designer()

        BoxLayout:
            size_hint_y: None
            height: dp(32)
            padding: dp(4)
            Label:
                text: "الأفعال الصحيحة"
                bold: True
            Label:
                text: "الأفعال الخاطئة"
                bold: True

        BoxLayout:
            size_hint_y: 0.42
            spacing: dp(8)
            canvas.before:
                Color: rgba: 1,1,1,1
                Rectangle: pos: self.pos; size: self.size

            # صحيحة
            RecycleView:
                viewclass: 'Label'
                data: [{'text': item, 'font_size':'14sp'} for item in root.correct_lines]
                RecycleBoxLayout:
                    default_size: None, dp(32)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'

            # خاطئة
            RecycleView:
                viewclass: 'Label'
                data: [{'text': item, 'font_size':'14sp'} for item in root.wrong_lines]
                RecycleBoxLayout:
                    default_size: None, dp(32)
                    default_size_hint: 1, None
                    size_hint_y: None
                    height: self.minimum_height
                    orientation: 'vertical'
"""

class StartScreen(Screen):
    def start(self, name_text):
        name = (name_text or "").strip()
        if not name:
            self._toast("من فضلك اكتب اسمك أولاً.")
            return
        app = App.get_running_app()
        app.username = name
        self.manager.current = "quiz"

    def _toast(self, msg):
        Popup(title="تنبيه", content=Label(text=msg), size_hint=(0.7, 0.3)).open()

class QuizScreen(Screen):
    username = StringProperty("")
    score = NumericProperty(0)
    attempts = NumericProperty(0)
    ahsant_text = StringProperty("")
    readonly_index = NumericProperty(-1)  # أي حقل معروض (مقفل)

    current_verb = ListProperty([])
    correct_verbs = ListProperty([])
    wrong_verbs = ListProperty([])
    correct_lines = ListProperty([])  # لعرض في RecycleView كـ نص
    wrong_lines = ListProperty([])

    # حقول إدخال (يتم ربطها عند الدخول للشاشة)
    def on_pre_enter(self, *args):
        self.username = App.get_running_app().username
        self.next_verb(save_current=False)

    # تركيز التالي
    def focus_next(self, widget):
        widget.focus = False

    def _line_fmt(self, v):
        return f"{v[0]}  -  {v[1]}  -  {v[2]}  -  {v[3]}"

    def _popup(self, title, msg):
        Popup(title=title, content=Label(text=msg), size_hint=(0.8, 0.5)).open()

    def speak_ahsant(self):
        if HAS_TTS and platform == "android":
            try:
                tts.speak("أحسنت")
            except Exception:
                pass  # تجاهل الخطأ على المنصات غير الداعمة

    def fill_shown_part(self):
        # وضع القيمة الصحيحة في الحقل المعروض وجعله مقفل (readonly)
        ids = self.ids
        fields = [ids.present_in, ids.past_in, ids.pp_in, ids.ar_in]
        for i, ti in enumerate(fields):
            ti.readonly = (i == self.readonly_index)
            ti.text = self.current_verb[i] if i == self.readonly_index else ""

    def next_verb(self, save_current=True):
        # احفظ الإجابة الحالية قبل الانتقال (إن طُلِب)
        if save_current and self.current_verb:
            self._save_current_answer_if_any()

        # إعداد فعل جديد
        self.attempts = 0
        self.ahsant_text = ""
        self.current_verb = random.choice(verbs)
        self.readonly_index = random.randint(0, 3)
        self.fill_shown_part()

    def _save_current_answer_if_any(self):
        ids = self.ids
        fields = [ids.present_in, ids.past_in, ids.pp_in, ids.ar_in]
        answered = False
        all_correct = True
        for i, ti in enumerate(fields):
            if i == self.readonly_index:
                continue
            user = ti.text.strip()
            if user:
                answered = True
                if user.lower() != self.current_verb[i].strip().lower():
                    all_correct = False
        if not answered:
            return  # لا تحفظ شيء إذا لم يكتب شيئًا

        line = self._line_fmt(self.current_verb)
        # امنع التكرار
        if all_correct:
            if line not in self.correct_lines:
                self.correct_verbs.append(self.current_verb[:])
                self.correct_lines.append(line)
                self.score += 1
        else:
            if line not in self.wrong_lines and self.current_verb not in self.wrong_verbs:
                self.wrong_verbs.append(self.current_verb[:])
                self.wrong_lines.append(line)

    def check_answers(self):
        ids = self.ids
        fields = [ids.present_in, ids.past_in, ids.pp_in, ids.ar_in]
        self.attempts += 1
        all_correct = True
        feedback_lines = []

        for i, ti in enumerate(fields):
            if i == self.readonly_index:
                continue
            user = ti.text.strip().lower()
            correct = self.current_verb[i].strip().lower()
            if user == correct:
                feedback_lines.append(f"{['Present','Past','Past Participle','Arabic'][i]} ✅ صحيح")
            else:
                feedback_lines.append(f"{['Present','Past','Past Participle','Arabic'][i]} ❌")
                all_correct = False

        if all_correct:
            self.score += 1
            self.ahsant_text = "أحسنت! 🎉"
            self.speak_ahsant()
            line = self._line_fmt(self.current_verb)
            if line not in self.correct_lines:
                self.correct_verbs.append(self.current_verb[:])
                self.correct_lines.append(line)
            self.next_verb(save_current=False)
        else:
            if self.attempts >= 3:
                # أعرض الإجابات الصحيحة كمساعدة، وسجّلها كخاطئة
                help_text = "الإجابات الصحيحة:\n" + \
                    f"Present: {self.current_verb[0]}\nPast: {self.current_verb[1]}\nPast Participle: {self.current_verb[2]}\nArabic: {self.current_verb[3]}"
                self._popup("مساعدة", "\n".join(feedback_lines) + "\n\n" + help_text)
                line = self._line_fmt(self.current_verb)
                if line not in self.wrong_lines:
                    self.wrong_verbs.append(self.current_verb[:])
                    self.wrong_lines.append(line)
                self.next_verb(save_current=False)
            else:
                self._popup("النتيجة", "\n".join(feedback_lines) + f"\n\nحاول مرة أخرى! (محاولة {self.attempts}/3)")

    # ===== شهادة: مصمم + حفظ =====
    def open_certificate_designer(self):
        # نافذة صغيرة لأخذ العنوان والملاحظات
        content = Builder.load_string("""
BoxLayout:
    orientation: 'vertical'
    padding: dp(10); spacing: dp(8)
    Label:
        text: "عنوان الشهادة:"
        size_hint_y: None
        height: dp(24)
    TextInput:
        id: title_in
        text: "شهادة تدريب الأفعال الإنجليزية"
        size_hint_y: None
        height: dp(44)
        multiline: False
    Label:
        text: "ملاحظات إضافية:"
        size_hint_y: None
        height: dp(24)
    TextInput:
        id: notes_in
        size_hint_y: None
        height: dp(100)
    BoxLayout:
        size_hint_y: None
        height: dp(46)
        spacing: dp(8)
        Button:
            text: "إلغاء"
            on_release: root_popup.dismiss()
        Button:
            text: "تصدير"
            on_release:
                app.root.get_screen("quiz").export_certificate(title_in.text, notes_in.text)
                root_popup.dismiss()
""")
        popup = Popup(title="تصميم الشهادة", content=content, size_hint=(0.85, 0.65))
        content.ids['title_in'].focus = True
        # تمرير الـ popup لجذر الـ kv المحلي
        content.ids if hasattr(content, 'ids') else None
        content.root_popup = popup
        popup.open()

    def export_certificate(self, title_text, notes_text):
        if not self.correct_verbs and not self.wrong_verbs:
            self._popup("تنبيه", "لم تقم بالإجابة على أي أفعال بعد.")
            return

        app = App.get_running_app()
        # مجلد تخزين آمن للتطبيق
        base_dir = app.user_data_dir
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safe_name = "".join(c for c in app.username if c.isalnum() or c in (' ', '_', '-')).strip() or "user"
        filename = f"{base_dir}/certificate_{safe_name}_{ts}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{title_text.strip() or 'شهادة تدريب الأفعال الإنجليزية'}\n")
            f.write(f"اسم الطالب: {app.username}\n")
            f.write(f"تاريخ الاختبار: {ts}\n")
            f.write(f"عدد الأفعال الصحيحة: {len(self.correct_verbs)}\n")
            f.write(f"عدد الأفعال الخاطئة: {len(self.wrong_verbs)}\n\n")
            if (notes_text or "").strip():
                f.write("ملاحظات:\n" + notes_text.strip() + "\n\n")

            f.write("الأفعال الصحيحة:\n")
            for v in self.correct_verbs:
                f.write(f"{v[0]} - {v[1]} - {v[2]} - {v[3]}\n")

            f.write("\nالأفعال الخاطئة:\n")
            for v in self.wrong_verbs:
                f.write(f"{v[0]} - {v[1]} - {v[2]} - {v[3]}\n")

        self._popup("تم", f"تم حفظ الشهادة بنجاح في:\n{filename}")

class RootManager(ScreenManager):
    pass

class VerbTrainerApp(App):
    username = StringProperty("طالب")

    def build(self):
        self.title = "تدريب الأفعال الإنجليزية"
        Builder.load_string(KV)
        sm = RootManager()
        sm.add_widget(StartScreen())
        sm.add_widget(QuizScreen())
        return sm

if __name__ == "__main__":
    VerbTrainerApp().run()
