import pygame as pg
import sys, time, os
from bird import Bird
from pipe import Pipe

pg.init()
pg.mixer.init()

# ================= PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.txt")

# ================= BACKGROUND MUSIC =================
pg.mixer.music.load(os.path.join(ASSETS_DIR, "musicplay.mp3"))
pg.mixer.music.set_volume(0.5)
pg.mixer.music.play(-1)


def load_sound(path):
    try:
        return pg.mixer.Sound(path)
    except:
        return None


class Game:
    def __init__(self):
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("Flappy Bird")
        self.clock = pg.time.Clock()

        # ===== SPEED =====
        self.base_speed = 250
        self.move_speed = self.base_speed
        self.max_speed = 550

        self.bird = Bird(self.scale_factor)

        self.is_playing = False
        self.dead = False
        self.grand_winner = False

        self.pipes = []
        self.pipe_counter = 70

        self.score = 0
        self.high_score = self.loadHighScore()

        self.font = pg.font.Font(os.path.join(ASSETS_DIR, "font.ttf"), 36)

        # ===== SOUND EFFECT =====
        self.flap_sound = load_sound(os.path.join(ASSETS_DIR, "sfx", "flap.wav"))
        self.score_sound = load_sound(os.path.join(ASSETS_DIR, "sfx", "score.mp3"))

        # 💀 GAME OVER SOUND
        self.over_sound = load_sound(os.path.join(ASSETS_DIR, "overgame.mp3"))

        # 🏆 WINNER SOUND
        self.winner_sound = load_sound(os.path.join(ASSETS_DIR, "winnergame.mp3"))

        self.setupAssets()
        self.gameLoop()

    def loadHighScore(self):
        if not os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE, "w") as f:
                f.write("0")
            return 0
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read())

    def saveHighScore(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open(HIGHSCORE_FILE, "w") as f:
                f.write(str(self.high_score))

    def gameLoop(self):
        last_time = time.time()
        while True:
            dt = time.time() - last_time
            last_time = time.time()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        self.resetGame()

                    if event.key == pg.K_SPACE and self.is_playing:
                        self.bird.flap(dt)
                        if self.flap_sound:
                            self.flap_sound.play()

            self.update(dt)
            self.checkCollision()
            self.draw()

            pg.display.update()
            self.clock.tick(60)

    def resetGame(self):
        self.is_playing = True
        self.dead = False
        self.grand_winner = False
        self.score = 0
        self.move_speed = self.base_speed
        self.pipes.clear()
        self.bird.rect.center = (150, 350)
        self.bird.velocity = 0
        self.bird.update_on = True

        # ▶️ music jalan lagi
        pg.mixer.music.play(-1)

    # ===== SPEED NAIK SESUAI SCORE =====
    def updateSpeed(self):
        self.move_speed = self.base_speed + (self.score * 4)
        if self.move_speed > self.max_speed:
            self.move_speed = self.max_speed

    def update(self, dt):
        if not self.is_playing:
            return

        self.updateSpeed()

        self.ground1_rect.x -= int(self.move_speed * dt)
        self.ground2_rect.x -= int(self.move_speed * dt)

        if self.ground1_rect.right < 0:
            self.ground1_rect.x = self.ground2_rect.right
        if self.ground2_rect.right < 0:
            self.ground2_rect.x = self.ground1_rect.right

        if self.pipe_counter > 70:
            self.pipes.append(Pipe(self.scale_factor, self.move_speed))
            self.pipe_counter = 0
        self.pipe_counter += 1

        for pipe in self.pipes:
            pipe.update(dt)
            if not pipe.passed and pipe.rect_up.right < self.bird.rect.left:
                pipe.passed = True
                self.score += 1
                if self.score_sound:
                    self.score_sound.play()

                if self.score >= 100:
                    self.winGame()

        if self.pipes and self.pipes[0].rect_up.right < 0:
            self.pipes.pop(0)

        self.bird.update(dt)

    def checkCollision(self):
        if not self.is_playing:
            return

        if self.bird.rect.bottom > 568:
            self.gameOver()

        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.rect_up) or self.bird.rect.colliderect(pipe.rect_down):
                self.gameOver()

    # 💀 GAME OVER
    def gameOver(self):
        if not self.dead:
            pg.mixer.music.stop()
            if self.over_sound:
                self.over_sound.play()
        self.dead = True
        self.is_playing = False
        self.bird.update_on = False
        self.saveHighScore()

    # 🏆 GRAND WINNER
    def winGame(self):
        pg.mixer.music.stop()
        if self.winner_sound:
            self.winner_sound.play()

        self.grand_winner = True
        self.is_playing = False
        self.bird.update_on = False
        self.saveHighScore()

    def draw(self):
        self.win.blit(self.bg_img, (0, -300))

        for pipe in self.pipes:
            pipe.drawPipe(self.win)

        self.win.blit(self.ground1_img, self.ground1_rect)
        self.win.blit(self.ground2_img, self.ground2_rect)
        self.win.blit(self.bird.image, self.bird.rect)

        score_text = self.font.render(f"Score : {self.score}", True, (255, 255, 255))
        high_text = self.font.render(f"High  : {self.high_score}", True, (255, 255, 255))
        self.win.blit(score_text, (20, 20))
        self.win.blit(high_text, (20, 60))

        if self.dead:
            over = self.font.render("GAME OVER", True, (255, 0, 0))
            hint = self.font.render("Press ENTER", True, (255, 255, 255))
            self.win.blit(over, over.get_rect(center=(300, 320)))
            self.win.blit(hint, hint.get_rect(center=(300, 360)))

        if self.grand_winner:
            win = self.font.render("GRAND WINNER!", True, (0, 255, 0))
            hint = self.font.render("Press ENTER", True, (255, 255, 255))
            self.win.blit(win, win.get_rect(center=(300, 320)))
            self.win.blit(hint, hint.get_rect(center=(300, 360)))

    def setupAssets(self):
        self.bg_img = pg.transform.scale_by(
            pg.image.load(os.path.join(ASSETS_DIR, "bg.png")).convert(),
            self.scale_factor
        )
        self.ground1_img = pg.transform.scale_by(
            pg.image.load(os.path.join(ASSETS_DIR, "ground.png")).convert(),
            self.scale_factor
        )
        self.ground2_img = self.ground1_img.copy()

        self.ground1_rect = self.ground1_img.get_rect(topleft=(0, 568))
        self.ground2_rect = self.ground2_img.get_rect(topleft=(self.ground1_rect.right, 568))


game = Game() 