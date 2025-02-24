import pyxel
import random

# 定数
WIDTH = 8  # フィールドの幅
HEIGHT = 16  # フィールドの高さ
BLOCK_SIZE = 8  # ブロックのサイズ
NEXT_PUYO_X = 104  # ネクストぷよのX座標
NEXT_PUYO_Y = 16  # ネクストぷよのY座標
SCORE_X = 80  # スコアのX座標
SCORE_Y = 56  # スコアのY座標

# 色 (pyxelの色番号に対応)
EMPTY = 0
RED = 8
GREEN = 11
BLUE = 12
YELLOW = 10
GARBAGE = 7

# ぷよのクラス
class Puyo:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

# ぷよぷよのクラス
class PuyoPuyo:
    def __init__(self):
        pyxel.init(128, 128, title="Puyo Puyo")

        # フィールドの初期化
        self.field = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]

        # 現在のぷよとネクストぷよ
        self.current_puyo = []
        self.next_puyo = []
        self.create_new_puyo()
        self.create_new_puyo()

        # スコア
        self.score = 0

        # ゲームの状態
        self.game_state = "playing"

        # 音楽データ (くるみ割り人形 - 行進曲)
        self.music_data = [
            "G3E3G3E3 G3B3D4C4 ",
            "G3F#3G3F#3 G3E3C3D3 E3F#3G3A3 G3F#3E3D3 ",
            "C3G3E3G3 C4"
        ]

        # 音楽のセットアップ
        self.setup_music()

        # 音楽の再生開始
        self.play_music()

        pyxel.run(self.update, self.draw)

    # 新しいぷよの生成
    def create_new_puyo(self):
        if len(self.current_puyo) == 0:
        # 最初のぷよ
            self.next_puyo = [
            Puyo(0, 0, random.choice([RED, GREEN, BLUE, YELLOW])),
            Puyo(0, 1, random.choice([RED, GREEN, BLUE, YELLOW])),
        ]

    # ネクストぷよを現在のぷよに移動
            self.current_puyo = [
            Puyo(WIDTH // 2 - 1, 0, self.next_puyo[0].color),
            Puyo(WIDTH // 2 - 1, 1, self.next_puyo[1].color),
    ]

    # 新しいネクストぷよを生成
            self.next_puyo = [
            Puyo(0, 0, random.choice([RED, GREEN, BLUE, YELLOW])),
            Puyo(0, 1, random.choice([RED, GREEN, BLUE, YELLOW])),
    ]


    # ぷよの移動
    def move_puyo(self, dx, dy):
        new_puyo = []
        for puyo in self.current_puyo:
            new_x = puyo.x + dx
            new_y = puyo.y + dy
            if 0 <= new_x < WIDTH and new_y < HEIGHT and (new_y < 0 or self.field[new_y][new_x] == EMPTY):
                new_puyo.append(Puyo(new_x, new_y, puyo.color))
            else:
                # 移動できない場合は元の位置に戻す
                return False
        self.current_puyo = new_puyo
        return True

    # ぷよの回転
    def rotate_puyo(self):
        # 軸ぷよを中心に回転
        pivot = self.current_puyo[0]
        rotated_puyo = []
        for puyo in self.current_puyo:
            # 軸ぷよからの相対位置を計算
            rel_x = puyo.x - pivot.x
            rel_y = puyo.y - pivot.y

            # 回転後の相対位置を計算
            new_rel_x = -rel_y
            new_rel_y = rel_x

            # 回転後の絶対位置を計算
            new_x = pivot.x + new_rel_x
            new_y = pivot.y + new_rel_y

            # 回転後の位置がフィールド内かつ他のぷよと重ならないかチェック
            if 0 <= new_x < WIDTH and new_y < HEIGHT and (new_y < 0 or self.field[new_y][new_x] == EMPTY):
                rotated_puyo.append(Puyo(new_x, new_y, puyo.color))
            else:
                # 回転できない場合は元の位置に戻す
                return

        self.current_puyo = rotated_puyo

    # ぷよの落下
    def drop_puyo(self):
        if not self.move_puyo(0, 1):
            # 落下できない場合はぷよを固定
            self.fix_puyo()

    # ぷよの固定
    def fix_puyo(self):
        for puyo in self.current_puyo:
            if puyo.y >= 0:  # 画面外のぷよは無視
                self.field[puyo.y][puyo.x] = puyo.color
        self.current_puyo = []

        # 連鎖をチェック
        self.check_chains()

        # 新しいぷよを生成
        self.create_new_puyo()

        # ゲームオーバー判定
        if self.field[0][WIDTH // 2 - 1] != EMPTY or self.field[1][WIDTH // 2 - 1] != EMPTY:
            self.game_state = "gameover"

    # 連鎖のチェック
    def check_chains(self):
        chained = True
        while chained:
            chained = False
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if self.field[y][x] != EMPTY:
                        count, connected = self.count_connected(x, y, self.field[y][x])
                        if count >= 4:
                            chained = True
                            self.score += count * 10  # スコア加算
                            # ぷよを消す
                            for puyo in connected:
                                self.field[puyo.y][puyo.x] = EMPTY

            # ぷよを落とす
            if chained:
                self.drop_floating_puyo()

    # 連結したぷよの数を数える
    def count_connected(self, x, y, color):
        visited = set()
        connected = []

        def dfs(x, y):
            if (
                0 <= x < WIDTH
                and 0 <= y < HEIGHT
                and (x, y) not in visited
                and self.field[y][x] == color
            ):
                visited.add((x, y))
                connected.append(Puyo(x, y, color))
                dfs(x + 1, y)
                dfs(x - 1, y)
                dfs(x, y + 1)
                dfs(x, y - 1)

        dfs(x, y)
        return len(connected), connected

    # 浮いているぷよを落とす
    def drop_floating_puyo(self):
        for x in range(WIDTH):
            empty_rows = 0
            for y in range(HEIGHT - 1, -1, -1):
                if self.field[y][x] == EMPTY:
                    empty_rows += 1
                elif empty_rows > 0:
                    self.field[y + empty_rows][x] = self.field[y][x]
                    self.field[y][x] = EMPTY

    # 更新処理
    def update(self):
        if self.game_state == "playing":
            if pyxel.btnp(pyxel.KEY_LEFT):
                self.move_puyo(-1, 0)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.move_puyo(1, 0)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.drop_puyo()
            elif pyxel.btnp(pyxel.KEY_SPACE):
                self.rotate_puyo()

            # 自動落下
            if pyxel.frame_count % 30 == 0:
                self.drop_puyo()

        elif self.game_state == "gameover":
            if pyxel.btnp(pyxel.KEY_SPACE):
                # ゲームをリセット
                self.field = [[EMPTY for _ in range(WIDTH)] for _ in range(HEIGHT)]
                self.current_puyo = []
                self.next_puyo = []
                self.create_new_puyo()
                self.create_new_puyo()
                self.score = 0
                self.game_state = "playing"

    # 音楽のセットアップ
    def setup_music(self):
        # 各音色を定義します。ここでは、すべて't'（三角波）に設定します
        pyxel.sounds[0].set(notes=self.music_data[0], tones='t'*len(self.music_data[0]), volumes='4'*len(self.music_data[0]), effects='n'*len(self.music_data[0]), speed=15)
        pyxel.sounds[1].set(notes=self.music_data[1], tones='t'*len(self.music_data[1]), volumes='4'*len(self.music_data[1]), effects='n'*len(self.music_data[1]), speed=15)
        pyxel.sounds[2].set(notes=self.music_data[2], tones='t'*len(self.music_data[2]), volumes='4'*len(self.music_data[2]), effects='n'*len(self.music_data[2]), speed=15)

    # 音楽の再生
    def play_music(self):
        pyxel.play(0, [0, 1, 2], loop=True)  # サウンド0, 1, 2を順番に再生

    # ぷよの描画
    def draw_puyo(self, x, y, color):
        # ぷよの形 (8x8)
        puyo_shape = [
            "00111100",
            "01111110",
            "11011011",
            "11011011",
            "11111111",
            "11100111",
            "01111110",
            "00111100",
        ]

        for py, row in enumerate(puyo_shape):
            for px, pixel in enumerate(row):
                if pixel == '1':
                    pyxel.pset(x * BLOCK_SIZE + px, y * BLOCK_SIZE + py, color)

    # 描画処理
    def draw(self):
        pyxel.cls(1)

        # フィールドの描画
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.field[y][x] != EMPTY:
                    self.draw_puyo(x, y, self.field[y][x])

        # 現在のぷよの描画
        for puyo in self.current_puyo:
            if puyo.y >= 0:  # 画面外のぷよは描画しない
                self.draw_puyo(puyo.x, puyo.y, puyo.color)

        # ネクストぷよの描画
        #for i, puyo in enumerate(self.next_puyo):
        #    self.draw_puyo(NEXT_PUYO_X // BLOCK_SIZE, NEXT_PUYO_Y // BLOCK_SIZE + i, puyo.color)

        # "NEXT"の文字表示
        #pyxel.text(NEXT_PUYO_X - 4, NEXT_PUYO_Y - 8, "NEXT", 7)


        # スコアの描画
        pyxel.text(SCORE_X, SCORE_Y, f"SCORE:{self.score:06}", 7)

        # ゲームオーバー表示
        if self.game_state == "gameover":
            pyxel.text(WIDTH * BLOCK_SIZE // 2 - 20, HEIGHT * BLOCK_SIZE // 2 - 4, "GAME OVER", 7)
            pyxel.text(WIDTH * BLOCK_SIZE // 2 - 28, HEIGHT * BLOCK_SIZE // 2 + 4, "Press Space", 7)

# ゲームの実行
PuyoPuyo()