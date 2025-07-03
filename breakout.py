import sys
import math
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QFont, QPen


class Breakout(QWidget):
    def __init__(self):
        super().__init__()
        self.bricks = [] # Initialize bricks here, before initUI
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Breakout')
        self.setGeometry(300, 300, 400, 500)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(10)
        self.reset_game()

    def reset_game(self):
        self.game_over = False
        self.game_won = False
        self.paused = False
        self.score = 0
        self.initial_paddle_width = 100
        self.paddle_shrink_amount = 5 # How much paddle shrinks per brick
        self.min_paddle_width = 30 # Minimum paddle width
        self.paddle = QRectF(150, 440, self.initial_paddle_width, 10)
        self.ball = QRectF(195, 420, 10, 10)
        
        # Ball speed and direction
        self.ball_speed = 3
        self.ball_dx = 0.5
        self.ball_dy = -0.5
        self.normalize_ball_speed()

        self.create_bricks()

    def normalize_ball_speed(self):
        length = math.sqrt(self.ball_dx**2 + self.ball_dy**2)
        if length > 0:
            self.ball_dx = (self.ball_dx / length) * self.ball_speed
            self.ball_dy = (self.ball_dy / length) * self.ball_speed

    def create_bricks(self):
        self.bricks.clear()
        for y in range(5):
            for x in range(6):
                brick = QRectF(x * 65 + 10, y * 25 + 50, 60, 20)
                self.bricks.append(brick)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(0, 0, 0))
        painter.drawRect(self.rect())

        if self.game_over:
            self.draw_text(painter, "Game Over\n\n마우스 클릭 또는 R키로 재시작")
        elif self.game_won:
            self.draw_text(painter, "You Won!\n\n마우스 클릭 또는 R키로 재시작")
        else:
            painter.setBrush(QColor(200, 200, 200))
            painter.drawRect(self.paddle)
            painter.setBrush(QColor(255, 255, 255))
            painter.drawEllipse(self.ball)
            painter.setPen(QPen(QColor(50, 50, 50)))
            for i, brick in enumerate(self.bricks):
                color = QColor.fromHsv((i * 15) % 360, 200, 255)
                painter.setBrush(color)
                painter.drawRect(brick)
            self.draw_hud(painter)

    def draw_text(self, painter, text):
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 16, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, text)

    def draw_hud(self, painter):
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Arial', 12))
        painter.drawText(10, 20, f"Score: {self.score}")
        
        painter.setFont(QFont('Arial', 10))
        pause_text = "일시정지/해제 : P"
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(pause_text)
        painter.drawText(self.width() - text_width - 10, 20, pause_text)

    def timerEvent(self):
        if self.paused or self.game_over or self.game_won:
            return
        self.move_ball()
        self.check_collisions()
        self.update()

    def move_ball(self):
        self.ball.translate(self.ball_dx, self.ball_dy)

    def check_collisions(self):
        # Wall collisions
        if self.ball.left() <= 0 or self.ball.right() >= self.width():
            self.ball_dx *= -1
        if self.ball.top() <= 0:
            self.ball_dy *= -1
        
        if self.ball.bottom() >= self.height():
            self.game_over = True
            self.timer.stop()

        # Paddle collision
        if self.ball.intersects(self.paddle):
            self.ball_dy *= -1
            paddle_center = self.paddle.center().x()
            ball_center = self.ball.center().x()
            diff = ball_center - paddle_center
            self.ball_dx = float(diff / (self.paddle.width() / 4))
            self.normalize_ball_speed()

        # Brick collisions
        for brick in self.bricks[:]:
            if self.ball.intersects(brick):
                self.bricks.remove(brick)
                self.ball_dy *= -1
                self.score += 10

                # Shrink paddle
                new_width = self.paddle.width() - self.paddle_shrink_amount
                if new_width < self.min_paddle_width:
                    new_width = self.min_paddle_width
                
                # Adjust paddle position to keep it centered
                old_center_x = self.paddle.center().x()
                self.paddle.setWidth(new_width)
                self.paddle.moveCenter(QPointF(old_center_x, self.paddle.center().y()))
        
        if not self.bricks:
            self.game_won = True
            self.timer.stop()

    def keyPressEvent(self, event):
        key = event.key()
        paddle_speed = 20

        if not self.game_over and not self.game_won:
            if key == Qt.Key_Left:
                new_x = self.paddle.x() - paddle_speed
                if new_x < 0:
                    new_x = 0
                self.paddle.moveTo(new_x, self.paddle.y())
            elif key == Qt.Key_Right:
                new_x = self.paddle.x() + paddle_speed
                if new_x > self.width() - self.paddle.width():
                    new_x = self.width() - self.paddle.width()
                self.paddle.moveTo(new_x, self.paddle.y())
        
        if key == Qt.Key_P:
            self.paused = not self.paused
        elif key == Qt.Key_R:
            if self.game_over or self.game_won:
                self.reset_game()
                self.timer.start()
        elif key == Qt.Key_Escape:
            self.close()

    def mouseMoveEvent(self, event):
        if not self.paused and not self.game_over and not self.game_won:
            new_x = event.x() - self.paddle.width() / 2
            if 0 <= new_x <= self.width() - self.paddle.width():
                self.paddle.moveTo(new_x, self.paddle.y())

    def mousePressEvent(self, event):
        if self.game_over or self.game_won:
            self.reset_game()
            self.timer.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = Breakout()
    game.show()
    sys.exit(app.exec_())
