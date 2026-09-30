import random
import pygame
from game.maze import generate_maze, CELL
from game.entities import Player, Enemy


COLS, ROWS = 13, 11
WIDTH = COLS * CELL
HEIGHT = ROWS * CELL + 50
FPS = 60


class GameEngine:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Maze Chase")

        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("monospace", 22)
        self.big_font = pygame.font.SysFont(
            "monospace",
            38,
            bold=True
        )

        self.reset()

    def reset(self):
        self.walls = generate_maze(COLS, ROWS)

        # Player
        self.player = Player(0, 0)

        # Task 1: Multiple enemies
        self.enemies = [
            Enemy(ROWS - 1, COLS - 1),
            Enemy(ROWS - 1, 0),
            Enemy(0, COLS - 1),
        ]

        # Task 2: Speed up over time
        self.last_speedup = pygame.time.get_ticks()
        self.speed_tier = 0
        self.speed_font = pygame.font.SysFont(None, 24)

        # Exit
        self.exit_rect = pygame.Rect(
            (COLS // 2) * CELL + 5,
            (ROWS // 2) * CELL + 5,
            CELL - 10,
            CELL - 10
        )

        # Task 3: Power pellet / freeze
        self.frozen = False
        self.freeze_end = 0

        player_cell = (
            self.player.rect.centery // CELL,
            self.player.rect.centerx // CELL
        )

        exit_cell = (
            self.exit_rect.centery // CELL,
            self.exit_rect.centerx // CELL
        )

        # Choose a random cell that is not the player
        # starting cell or the exit cell
        free_cells = [
            (r, c)
            for r in range(ROWS)
            for c in range(COLS)
            if (r, c) != player_cell
            and (r, c) != exit_cell
        ]

        pr, pc = random.choice(free_cells)

        self.pellet_rect = pygame.Rect(
            0,
            0,
            16,
            16
        )

        self.pellet_rect.center = (
            pc * CELL + CELL // 2,
            pr * CELL + CELL // 2
        )

        self.pellet_active = True

        # Task 4: Survival score
        self.score = 0

        # Game states
        self.caught = False
        self.won = False

    def handle_events(self):
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset()

        return True

    def update(self):
        # Stop updating after game ends
        if self.caught or self.won:
            return

        now = pygame.time.get_ticks()

        # ==========================================
        # Task 2: Speed Up Over Time
        # ==========================================
        if now - self.last_speedup >= 15000:
            self.last_speedup = now

            if self.enemies[0].move_interval > 5:
                self.speed_tier += 1

            for enemy in self.enemies:
                enemy.move_interval = max(
                    5,
                    enemy.move_interval - 2
                )

        # ==========================================
        # Task 3: End Freeze After 5 Seconds
        # ==========================================
        if self.frozen and now >= self.freeze_end:
            self.frozen = False

        # ==========================================
        # Move Player
        # ==========================================
        keys = pygame.key.get_pressed()

        self.player.move(
            keys,
            self.walls,
            ROWS,
            COLS
        )

        # ==========================================
        # Task 3: Power Pellet Collection
        # ==========================================
        if (
            self.pellet_active
            and self.player.rect.colliderect(
                self.pellet_rect
            )
        ):
            self.pellet_active = False
            self.frozen = True
            self.freeze_end = now + 5000

        # ==========================================
        # Task 1 + Task 2 + Task 3:
        # Update all enemies
        # ==========================================
        if not self.frozen:
            for enemy in self.enemies:
                enemy.update(
                    self.walls,
                    self.player,
                    ROWS,
                    COLS
                )

        # ==========================================
        # Check Enemy Collision
        # ==========================================
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.caught = True

        # ==========================================
        # Check Exit
        # ==========================================
        if self.player.rect.colliderect(self.exit_rect):
            self.won = True

        # ==========================================
        # Task 4: Survival Score
        # ==========================================
        if not self.caught and not self.won:
            self.score += 1

    def draw(self):
        # Background
        self.screen.fill((230, 220, 210))

        # Maze wall color
        wc = (50, 40, 60)

        # ==========================================
        # Draw Maze
        # ==========================================
        for r in range(ROWS):
            for c in range(COLS):

                x = c * CELL
                y = r * CELL

                w = self.walls[r][c]

                # Top wall
                if w[0]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y),
                        (x + CELL, y),
                        3
                    )

                # Bottom wall
                if w[1]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y + CELL),
                        (x + CELL, y + CELL),
                        3
                    )

                # Right wall
                if w[2]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x + CELL, y),
                        (x + CELL, y + CELL),
                        3
                    )

                # Left wall
                if w[3]:
                    pygame.draw.line(
                        self.screen,
                        wc,
                        (x, y),
                        (x, y + CELL),
                        3
                    )

        # ==========================================
        # Draw Exit
        # ==========================================
        pygame.draw.rect(
            self.screen,
            (80, 200, 80),
            self.exit_rect,
            border_radius=4
        )

        lbl = self.font.render(
            "EXIT",
            True,
            (20, 80, 20)
        )

        self.screen.blit(
            lbl,
            (
                self.exit_rect.x + 2,
                self.exit_rect.y + 6
            )
        )

        # ==========================================
        # Task 3: Draw Power Pellet
        # ==========================================
        if self.pellet_active:
            pygame.draw.circle(
                self.screen,
                (255, 255, 0),
                self.pellet_rect.center,
                8
            )

        # ==========================================
        # Draw Player
        # ==========================================
        self.player.draw(self.screen)

        # ==========================================
        # Task 1: Draw Multiple Enemies
        # ==========================================
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # ==========================================
        # Task 3: Frozen Indicator
        # ==========================================
        if self.frozen:

            for enemy in self.enemies:
                pygame.draw.rect(
                    self.screen,
                    (0, 200, 255),
                    enemy.rect.inflate(6, 6),
                    3
                )

            remaining = max(
                0,
                (
                    self.freeze_end
                    - pygame.time.get_ticks()
                    + 999
                ) // 1000
            )

            frozen_text = self.speed_font.render(
                f"FROZEN! {remaining}s",
                True,
                (0, 200, 255)
            )

            self.screen.blit(
                frozen_text,
                (
                    (
                        self.screen.get_width()
                        - frozen_text.get_width()
                    ) // 2,
                    10
                )
            )

        # ==========================================
        # Task 2: Enemy Speed Tier
        # ==========================================
        tier_text = self.speed_font.render(
            f"Enemy speed: tier {self.speed_tier}",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            tier_text,
            (
                self.screen.get_width()
                - tier_text.get_width()
                - 10,
                10
            )
        )

        # ==========================================
        # Task 4: Survival Score
        # ==========================================
        score_text = self.speed_font.render(
            f"Survived: {self.score // 60}s",
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            score_text,
            (
                self.screen.get_width()
                - score_text.get_width()
                - 10,
                34
            )
        )

        # ==========================================
        # Bottom HUD
        # ==========================================
        hud = pygame.Rect(
            0,
            ROWS * CELL,
            WIDTH,
            50
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 50),
            hud
        )

        info = self.font.render(
            "Reach EXIT before the enemy catches you!  R=Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            info,
            (
                8,
                ROWS * CELL + 14
            )
        )

        # ==========================================
        # Game Over: Caught
        # ==========================================
        if self.caught:
            self._overlay(
                "CAUGHT!",
                (220, 60, 60)
            )

        # ==========================================
        # Game Over: Escaped
        # ==========================================
        if self.won:
            self._overlay(
                "ESCAPED!",
                (80, 220, 80)
            )

        # ==========================================
        # Task 4: Final Score
        # ==========================================
        if self.caught or self.won:

            final_text = self.speed_font.render(
                f"Final score: {self.score // 60}s survived",
                True,
                (255, 255, 255)
            )

            self.screen.blit(
                final_text,
                (
                    (
                        self.screen.get_width()
                        - final_text.get_width()
                    ) // 2,
                    self.screen.get_height() // 2 + 40
                )
            )

        pygame.display.flip()

    def _overlay(self, text, color):

        surf = pygame.Surface(
            (WIDTH, ROWS * CELL),
            pygame.SRCALPHA
        )

        surf.fill(
            (0, 0, 0, 140)
        )

        self.screen.blit(
            surf,
            (0, 0)
        )

        msg = self.big_font.render(
            text,
            True,
            color
        )

        sub = self.font.render(
            "Press R to Restart",
            True,
            (200, 200, 200)
        )

        self.screen.blit(
            msg,
            (
                WIDTH // 2
                - msg.get_width() // 2,
                ROWS * CELL // 2 - 30
            )
        )

        self.screen.blit(
            sub,
            (
                WIDTH // 2
                - sub.get_width() // 2,
                ROWS * CELL // 2 + 20
            )
        )

    def run(self):
        running = True

        while running:

            running = self.handle_events()

            self.update()

            self.draw()

            self.clock.tick(FPS)

        pygame.quit()