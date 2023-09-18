import flet as ft
import random  # ランダムに問題を生成するため
import unicodedata  # 予測した数値を半角で記録するため


# アプリ全体
class HitandBlow(ft.UserControl):
    def build(self):
        # 問題に使う3つの数字をこのリストから取り出す
        self.numbers = [i for i in range(10)]
        # 問題の生成
        self.generate_answer()

        # 予測値の入力方法を知らせる
        self.snack_bar = ft.SnackBar(
            content=ft.Text("0～9の数字から異なる数字を3つ選んで入力してください", text_align="center")
        )

        # 予測結果を記録するデータテーブルの各列名、データテーブルはスクロールできないため列名と記録先を分けた
        self.predictions_head = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("予測値")),
                ft.DataColumn(ft.Text("H")),
                ft.DataColumn(ft.Text("B")),
            ],
        )
        # 予測結果の記録が追加されていくデータテーブル、DataTableにはcolumnsの初期設定が必ず必要そう
        self.predictions_list = ft.DataTable(
            heading_row_height=0,
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("")),
            ],
        )
        # 予測結果を記録するデータテーブル、記録が追加されていく方のデータテーブルをColumnに入れることで、スクロールできるようにした
        self.predictions_field = ft.Column(
            alignment="start",
            horizontal_alignment="center",
            controls=[
                self.predictions_head,
                ft.Column(
                    height=400,
                    controls=[self.predictions_list],
                    scroll=ft.ScrollMode.HIDDEN,
                ),
            ],
        )

        # 予測値入力欄
        self.input = ft.TextField(hint_text="3桁の予測値", width=150, on_submit=self.predict)
        # 答え表示ボタン
        self.show_answer_button = ft.FilledTonalButton(
            text="答えを見る", width=120, on_click=self.show_answer
        )
        # 答え表示欄
        self.answer_view = ft.Text(value=f"正解：", width=150, size=30)
        # 問題生成ボタン
        self.regenerate_answer_button = ft.FilledTonalButton(
            text="次の問題",
            width=120,
            visible=False,
            on_click=self.regenerate_answer,
        )
        # 予測実行ボタン
        self.predict_button = ft.FilledTonalButton(
            text="予測実行",
            width=120,
            on_click=self.predict,
        )
        # 予測入力欄と予測実行ボタン、答え表示欄と答え表示ボタンと問題生成ボタン、ルール説明欄が入ったColumn
        self.input_answer_explanation = ft.Column(
            alignment="spaceEvenly",
            horizontal_alignment="center",
            controls=[
                ft.Column(
                    alignment="spaceEvenly",
                    width=300,
                    height=200,
                    controls=[
                        ft.Row(
                            alignment="spaceBetween",
                            controls=[
                                self.input,
                                self.predict_button,
                            ],
                        ),
                        ft.Row(
                            alignment="spaceBetween",
                            controls=[
                                self.answer_view,
                                ft.Column(
                                    controls=[
                                        self.show_answer_button,
                                        self.regenerate_answer_button,
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
                ft.Text(
                    value="0～9の10個の数字から3つの数字がランダムに選ばれ並べられます\nその数列を予測してください\n\nH:予測した数列に含まれる、値も位置も等しい数字の個数\nB:予測した数列に含まれる、値のみ等しく、位置が異なる数字の個数\n\n問題：043\n予測：034\n　→H = 1、B = 2"
                ),
            ],
        )

        # メモ用の3×10個のボタン
        self.memo_pad = ft.Row(
            controls=[
                ft.Column(controls=[Button(i, self.input) for i in range(10)])
                for i in range(3)
            ]
        )
        # メモ用のボタンとボタンの状態をリセットするボタンが入ったColumn
        self.memo_field = ft.Column(
            alignment="spaceEvenly",
            horizontal_alignment="center",
            controls=[
                self.memo_pad,
                ft.OutlinedButton(text="メモ欄リセット", on_click=self.reset_memos),
            ],
        )

        # HitandBlowクラスによって作成され、pageに追加されるもの
        return ft.Row(
            alignment="center",
            height=500,
            controls=[
                self.predictions_field,
                self.input_answer_explanation,
                self.memo_field,
                self.snack_bar,
            ],
        )

    # 最初の答えを生成する
    def generate_answer(self):
        # ０～９の数字を含むリストから3つランダムに抜き出して並べる
        self.answer = random.sample(self.numbers, 3)
        return self.answer

    # 予測結果を表示するボタンをクリックあるいは、予測値入力後にEnterで実行される処理
    def predict(self, e):
        # 入力欄に３つの異なる数字記入されていたら、入力内容を新しい予測とする
        if (
            len(self.input.value) == 3
            and self.input.value[0] != self.input.value[1] != self.input.value[2]
            and self.input.value.isdecimal()
        ):
            # インスタンスとして直接リストやタプル等のイテラブルなオブジェクトを返すことはできないため、build()して、get_values()した
            prediction = Prediction(self.input.value, self.answer)
            prediction.build()
            self.prediction_value, self.h_value, self.b_value = prediction.get_values()
            self.input.value = ""

            # 正解したら答えを表示し、Enterで次の問題へ
            if self.h_value == 3:
                self.answer_view.value = (
                    f"正解：{self.answer[0]}{self.answer[1]}{self.answer[2]}"
                )
                self.show_answer_button.visible = False
                self.regenerate_answer_button.visible = True
                self.predict_button.visible = False
                # focus()で対象を選択した状態にする、Enterを押すことで選択対象が担う処理を実行できる
                self.regenerate_answer_button.focus()
                self.input.hint_text = "Enterで次の問題へ"
                self.input.text_size = 15
            # 正解でなければ、予測結果をデータテーブルに追加する
            else:
                data = ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(self.prediction_value)),
                        ft.DataCell(ft.Text(str(self.h_value))),
                        ft.DataCell(ft.Text(str(self.b_value))),
                    ]
                )
                self.predictions_list.rows.append(data)
                self.predictions_field.controls[1].scroll_to(offset=-1, duration=10)
                self.input.focus()
        # 入力形式が正しくなければ、入力形式を教えるstack_barを表示する
        else:
            self.open_bar()
            self.input.focus()

        self.update()

    # 次の問題を生成するボタンをクリックすると実行される処理
    def regenerate_answer(self, e):
        self.answer = random.sample(self.numbers, 3)
        self.predictions_list.rows.clear()
        self.answer_view.value = f"正解："
        self.regenerate_answer_button.visible = False
        self.show_answer_button.visible = True

        self.reset_memos(e)
        self.predict_button.visible = True
        self.input.hint_text = "3桁の予測値"
        self.input.text_size = "default"
        self.input.focus()
        self.update()

    # メモ欄のリセット、bgcolorを変更する対象以外からbgcolorを変更する関数は呼び出せなさそう
    def reset_memos(self, e):
        self.memo_pad.controls = [
            ft.Column(controls=[Button(i, self.input) for i in range(10)])
            for i in range(3)
        ]
        self.input.focus()
        self.memo_field.update()

    # 答えを表示する
    def show_answer(self, e):
        self.answer_view.value = f"正解：{self.answer[0]}{self.answer[1]}{self.answer[2]}"
        self.show_answer_button.visible = False
        self.regenerate_answer_button.visible = True
        self.predict_button.visible = False
        self.input.hint_text = "Enterで次の問題へ"
        self.input.text_size = 15
        self.regenerate_answer_button.focus()
        self.update()

    # 入力欄の入力形式が正しくなかった場合に、snack_barを表示する
    def open_bar(self):
        self.snack_bar.open = True
        self.snack_bar.update()


# このクラスを元に各予測結果は生成される
class Prediction(ft.UserControl):
    def __init__(self, prediction_value, generated_answer):
        super().__init__()
        self.prediction_value = prediction_value
        self.prediction_value_list = list(self.prediction_value)
        self.generated_answer = generated_answer

    # 問題と予測を比較し、HとBの数を出力する
    def build(self):
        self.h_value = 0
        self.b_value = 0

        for i in range(3):
            if self.generated_answer[i] == int(self.prediction_value_list[i]):
                self.h_value += 1

            elif int(self.prediction_value_list[i]) in self.generated_answer:
                self.b_value += 1

    # build()の出力とstr形式のprediction_valueを返す
    def get_values(self):
        for i in range(3):
            if (
                self.prediction_value_list[i].isdigit()
                and unicodedata.east_asian_width(self.prediction_value_list[i]) == "F"
            ):
                self.prediction_value_list[i] = unicodedata.normalize(
                    "NFKC", self.prediction_value_list[i]
                )
        self.prediction_value = str(
            self.prediction_value_list[0]
            + self.prediction_value_list[1]
            + self.prediction_value_list[2]
        )
        return [self.prediction_value, self.h_value, self.b_value]


# このクラスをもとにメモ欄のボタンは生成される
class Button(ft.UserControl):
    def __init__(self, i, input):
        super().__init__()
        self.i = i
        self.input = input

    def build(self):
        # ElevatedButtonは数少ないbgcolorが設定できるボタン、汎用性が高い
        self.button = ft.ElevatedButton(
            text=self.i, bgcolor="blue", on_click=self.change_color
        )
        return self.button

    def change_color(self, e):
        if self.button.bgcolor == "blue":
            self.button.bgcolor = "gray"
        else:
            self.button.bgcolor = "blue"
        self.input.focus()
        self.update()


def main(page: ft.Page):
    page.title = "Hit and Blow"
    page.horizontal_alignment = "center"
    page.update()

    app = HitandBlow()
    page.add(app)


ft.app(target=main)
