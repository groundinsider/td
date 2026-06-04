from __future__ import annotations

import random
import tkinter as tk
from tkinter import ttk, font

from vocabulary_quiz_app.quiz_logic import Word, check_answer, draw_word


class VocabularyQuizApp:
    def __init__(self, root: tk.Tk, words: list[Word]):
        self.words = words
        self.rng = random.Random()

        self.current = None
        self.checked = False
        self.score = 0
        self.total = 0

        # 추가: 이전/다음 이동을 위해 나온 단어들을 순서대로 저장한다.
        self.history = []
        self.current_index = -1

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="NanumGothic", size=12)

        root.title("Vocabulary Quiz")
        root.geometry("420x280")
        root.resizable(False, False)

        self.word_var = tk.StringVar(value="단어를 불러오는 중...")
        self.feedback_var = tk.StringVar(value="")
        self.score_var = tk.StringVar(value="Score: 0/0")

        ttk.Label(root, text="영단어").pack(pady=(16, 4))

        ttk.Label(
            root,
            textvariable=self.word_var,
            font=("NanumGothic", 24)
        ).pack()

        self.answer_entry = ttk.Entry(
            root,
            font=("NanumGothic", 14)
        )
        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)

        button_frame = ttk.Frame(root)
        button_frame.pack(pady=6)

        # 추가: 이전에 나왔던 단어로 이동하는 버튼
        self.prev_button = ttk.Button(
            button_frame,
            text="이전",
            command=self.prev_word
        )
        self.prev_button.pack(side=tk.LEFT, padx=6)

        self.check_button = ttk.Button(
            button_frame,
            text="채점",
            command=self.check_current
        )
        self.check_button.pack(side=tk.LEFT, padx=6)

        ttk.Button(
            button_frame,
            text="다음",
            command=self.next_word
        ).pack(side=tk.LEFT, padx=6)

        ttk.Label(
            root,
            textvariable=self.feedback_var
        ).pack(pady=8)

        ttk.Label(
            root,
            textvariable=self.score_var
        ).pack()

        self.next_word()

    # 추가: 현재 단어를 화면에 표시하는 공통 처리 함수
    def show_word(self):
        """현재 단어를 화면에 표시하고 입력창과 채점 상태를 초기화한다."""
        if self.current is None:
            return

        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)

        self.feedback_var.set("")
        self.checked = False

        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    # 추가: 이전 단어로 이동하는 함수
    def prev_word(self):
        """단어 기록에서 이전에 나왔던 단어로 이동한다."""
        if self.current_index > 0:
            self.current_index -= 1
            self.current = self.history[self.current_index]
            self.show_word()

    def next_word(self):
        """다음 단어로 이동한다. 기록이 있으면 기록에서 이동하고, 없으면 새 단어를 뽑는다."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            self.current = self.history[self.current_index]
            self.show_word()
            return
        # 추가: 이미 지나간 다음 단어가 있으면 새로 뽑지 않고 기록에서 가져온다.

        self.current = draw_word(self.words, self.rng)

        # 추가: 새로 뽑은 단어를 이동 기록에 저장한다.
        self.history.append(self.current)
        self.current_index += 1

        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)

        self.feedback_var.set("")
        self.checked = False

        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self):
        if self.current is None or self.checked:
            return

        self.checked = True
        self.total += 1

        user_answer = self.answer_entry.get()

        if check_answer(self.current, user_answer):
            self.score += 1
            self.feedback_var.set("정답입니다!")
        else:
            self.feedback_var.set(
                f"오답입니다. 정답: {self.current.meaning}"
            )

        self.score_var.set(
            f"Score: {self.score}/{self.total}"
        )

        self.check_button.state(["disabled"])
