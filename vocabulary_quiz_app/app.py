from __future__ import annotations

import random
import tkinter as tk

from tkinter import ttk, font

from vocabulary_quiz_app.quiz_logic import Word, check_answer


class VocabularyQuizApp:
    """영단어 퀴즈 화면과 전체 진행 상태를 관리하는 클래스."""

    def __init__(self, root: tk.Tk, words: list[Word]):
        """퀴즈 앱의 화면 요소와 초기 상태를 설정한다."""
        self.words = words
        self.rng = random.Random()

        self.current = None
        self.checked = False
        self.score = 0
        self.total = 0

        # 이미 출제된 단어를 저장하는 리스트
        # 이 리스트에 들어간 단어는 다시 출제되지 않는다.
        self.used_words: list[Word] = []

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

        self.check_button = ttk.Button(
            button_frame,
            text="채점",
            command=self.check_current
        )
        self.check_button.pack(side=tk.LEFT, padx=6)

        self.next_button = ttk.Button(
            button_frame,
            text="다음",
            command=self.next_word
        )
        self.next_button.pack(side=tk.LEFT, padx=6)

        self.restart_button = ttk.Button(
            root,
            text="퀴즈 시작",
            command=self.restart_quiz
        )

        ttk.Label(
            root,
            textvariable=self.feedback_var
        ).pack(pady=8)

        ttk.Label(
            root,
            textvariable=self.score_var
        ).pack()

        self.next_word()

    def next_word(self):
        """아직 나오지 않은 단어 중 하나를 랜덤으로 선택하여 화면에 표시한다."""
        remaining_words = [
            word for word in self.words
            if word not in self.used_words
        ]

        # 더 이상 출제할 단어가 없으면 완료 화면으로 전환한다.
        if not remaining_words:
            self.show_finished_screen()
            return

        self.current = self.rng.choice(remaining_words)

        # 현재 단어를 출제 완료 목록에 추가하여 중복 출제를 막는다.
        self.used_words.append(self.current)

        self.word_var.set(self.current.term)
        self.answer_entry.delete(0, tk.END)

        # 새 문제로 넘어왔으므로 채점 여부를 초기화한다.
        self.feedback_var.set("")
        self.checked = False

        self.check_button.state(["!disabled"])
        self.answer_entry.focus()

    def check_current(self):
        """사용자가 입력한 답을 현재 단어의 뜻과 비교하여 채점한다."""
        if self.current is None or self.checked:
            return

        # 한 문제를 채점했으므로 전체 풀이 수를 1 증가시킨다.
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

        # 같은 문제를 여러 번 채점하지 못하도록 버튼을 비활성화한다.
        self.check_button.state(["disabled"])

    def show_finished_screen(self):
        """모든 단어를 확인했을 때 완료 문구와 재시작 버튼을 보여준다."""
        self.current = None
        self.word_var.set("모든 단어를 확인하였습니다")
        self.feedback_var.set("")
        self.answer_entry.delete(0, tk.END)

        # 퀴즈가 끝났으므로 입력창과 기존 버튼을 숨긴다.
        self.answer_entry.pack_forget()
        self.check_button.pack_forget()
        self.next_button.pack_forget()

        self.restart_button.pack(pady=10)

    def restart_quiz(self):
        """퀴즈를 처음 상태로 초기화하고 다시 시작한다."""
        self.used_words.clear()
        self.score = 0
        self.total = 0
        self.checked = False

        self.score_var.set("Score: 0/0")
        self.feedback_var.set("")

        # 재시작 버튼은 숨기고 다시 문제 풀이 화면을 복구한다.
        self.restart_button.pack_forget()

        self.answer_entry.pack(pady=12, ipadx=6, ipady=4)
        self.check_button.pack(side=tk.LEFT, padx=6)
        self.next_button.pack(side=tk.LEFT, padx=6)

        self.next_word()
