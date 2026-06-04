from __future__ import annotations

import random
import tkinter as tk

from tkinter import ttk, font, messagebox

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]) -> None:
        self.words = words
        self.rng = random.Random()
        self.current: Word | None = None
        self.checked = False
        self.score = 0
        self.total = 0

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x500")
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중.")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")

        ttk.Label(root, text="영단어").pack(pady=(16, 4))
        ttk.Label(root, textvariable=self.word_var, font=("NanumGothic", 24)).pack()

        self.answer_entry = ttk.Entry(root, font=("NanumGothic", 14))
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        buttons = ttk.Frame(root)
        buttons.pack(pady=6)

        self.check_button = ttk.Button(buttons, text="채점", command=self.check_current)
        self.check_button.pack(side=tk.LEFT, padx=6)

        ttk.Button(buttons, text="다음", command=self.next_word).pack(
            side=tk.LEFT, padx=6
        )

        ttk.Label(root, textvariable=self.feedback_var).pack(pady=8)
        ttk.Label(root, textvariable=self.score_var).pack()

        ttk.Separator(root).pack(fill="x", pady=10)

        ttk.Label(root, text="단어 관리").pack()

        input_frame = ttk.Frame(root)
        input_frame.pack(pady=6)

        ttk.Label(input_frame, text="영어").grid(row=0, column=0, padx=4)
        self.term_entry = ttk.Entry(input_frame, width=18)
        self.term_entry.grid(row=0, column=1, padx=4)

        ttk.Label(input_frame, text="뜻").grid(row=1, column=0, padx=4)
        self.meaning_entry = ttk.Entry(input_frame, width=18)
        self.meaning_entry.grid(row=1, column=1, padx=4)

        manage_buttons = ttk.Frame(root)
        manage_buttons.pack(pady=6)

        ttk.Button(manage_buttons, text="추가", command=self.add_word).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(manage_buttons, text="수정", command=self.update_word).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(manage_buttons, text="삭제", command=self.delete_word).pack(
            side=tk.LEFT, padx=4
        )

        self.word_listbox = tk.Listbox(root, width=42, height=7)
        self.word_listbox.pack(pady=8)
        self.word_listbox.bind("<<ListboxSelect>>", self.select_word)

        self.refresh_word_list()
        self.next_word()

    def refresh_word_list(self) -> None:
        """현재 단어 목록을 화면의 리스트박스에 다시 표시한다."""
        self.word_listbox.delete(0, tk.END)

        # self.words는 퀴즈와 단어 관리에서 함께 사용하는 전체 단어 목록이다.
        for word in self.words:
            self.word_listbox.insert(tk.END, f"{word.term} - {word.meaning}")

    def select_word(self, event=None) -> None:
        """리스트박스에서 선택한 단어를 입력창에 표시한다."""
        selected = self.word_listbox.curselection()

        # 선택된 항목이 없으면 입력창을 바꾸지 않는다.
        if not selected:
            return

        index = selected[0]
        word = self.words[index]

        self.term_entry.delete(0, tk.END)
        self.term_entry.insert(0, word.term)

        self.meaning_entry.delete(0, tk.END)
        self.meaning_entry.insert(0, word.meaning)

    def add_word(self) -> None:
        """입력한 영어 단어와 뜻을 단어 목록에 추가한다."""
        term = self.term_entry.get().strip()
        meaning = self.meaning_entry.get().strip()

        # 영어 단어 또는 뜻이 비어 있으면 잘못된 데이터이므로 추가하지 않는다.
        if not term or not meaning:
            messagebox.showwarning("입력 오류", "영어 단어와 뜻을 모두 입력하세요.")
            return

        self.words.append(Word(term=term, meaning=meaning))
        self.refresh_word_list()

        self.term_entry.delete(0, tk.END)
        self.meaning_entry.delete(0, tk.END)

        self.feedback_var.set(f"{term} 추가 완료!")

    def update_word(self) -> None:
        """선택한 단어를 입력창의 내용으로 수정한다."""
        selected = self.word_listbox.curselection()

        # 수정할 단어가 선택되지 않았으면 수정할 수 없다.
        if not selected:
            messagebox.showwarning("선택 오류", "수정할 단어를 목록에서 선택하세요.")
            return

        term = self.term_entry.get().strip()
        meaning = self.meaning_entry.get().strip()

        # 수정할 값이 비어 있으면 잘못된 데이터이므로 저장하지 않는다.
        if not term or not meaning:
            messagebox.showwarning("입력 오류", "영어 단어와 뜻을 모두 입력하세요.")
            return

        index = selected[0]
        old_word = self.words[index]
        new_word = Word(term=term, meaning=meaning)

        # 리스트에서 선택한 위치의 단어를 새 단어 객체로 교체한다.
        self.words[index] = new_word

        # 현재 퀴즈에 표시 중인 단어가 수정된 단어라면 화면도 함께 갱신한다.
        if self.current is not None and self.current == old_word:
            self.current = new_word
            self.word_var.set(new_word.term)

        self.refresh_word_list()
        self.feedback_var.set(f"{term} 수정 완료!")

    def delete_word(self) -> None:
        """선택한 단어를 단어 목록에서 삭제한다."""
        selected = self.word_listbox.curselection()

        # 삭제할 단어가 선택되지 않았으면 삭제할 수 없다.
        if not selected:
            messagebox.showwarning("선택 오류", "삭제할 단어를 목록에서 선택하세요.")
            return

        # 퀴즈가 계속 동작하려면 최소 1개의 단어는 남아 있어야 한다.
        if len(self.words) <= 1:
            messagebox.showwarning("삭제 불가", "단어는 최소 1개 이상 있어야 합니다.")
            return

        index = selected[0]
        deleted = self.words.pop(index)

        self.refresh_word_list()
        self.term_entry.delete(0, tk.END)
        self.meaning_entry.delete(0, tk.END)

        self.feedback_var.set(f"{deleted.term} 삭제 완료!")

        # 현재 표시 중인 단어가 삭제되었을 수 있으므로 새 단어를 다시 뽑는다.
        self.next_word()

    def next_word(self) -> None:
        self.current = draw_word(self.words, self.rng)
        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)
        self.feedback_var.set("")
        self.checked = False
        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self) -> None:
        if self.current is None or self.checked:
            return

        self.checked = True
        self.total += 1

        user_input = self.answer_entry.get()

        if check_answer(self.current, user_input):
            self.score += 1
            self.feedback_var.set("정답입니다!")
        else:
            self.feedback_var.set(f"오답입니다. 정답: {self.current.meaning}")

        self.score_var.set(f"Score: {self.score}/{self.total}")
        self.check_button.state(["disabled"])
