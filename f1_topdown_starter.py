import math
import pygame

# --- Config ---
WIDTH, HEIGHT = 1200, 800
FPS = 60

# Colors
BG_GRASS = (20, 80, 35)
TRACK_COLOR = (85, 85, 85)
WHITE = (240, 240, 240)
BLACK = (10, 10, 10)
RED = (200, 30, 30)

Vec2 = pygame.math.Vector2

class Car:
    def __init__(self, x, y):
        self.pos = Vec2(x, y)
        self.angle = -90
        self.speed = 0.0

        self.max_speed = 420.0
        self.max_reverse = 160.0
        self.accel = 650.0
        self.brake_accel = 800.0
        self.drag = 320.0
        self.steer_rate = 190.0

        w, h = 60, 30
        base = pygame.Surface((w, h), pygame.SRCALPHA)

        # Main body (low and sleek)
        pygame.draw.rect(base, RED, (10, 8, 40, 14), border_radius=4)

        # Front nose
        pygame.draw.polygon(base, BLACK, [(10, 8), (0, 15), (10, 22)])

        # Rear wing
        pygame.draw.rect(base, BLACK, (50, 10, 8, 10))

        # Wheels
        pygame.draw.ellipse(base, BLACK, (5, 0, 10, 6))   # front-left
        pygame.draw.ellipse(base, BLACK, (5, 24, 10, 6))  # front-right
        pygame.draw.ellipse(base, BLACK, (45, 0, 10, 6))  # rear-left
        pygame.draw.ellipse(base, BLACK, (45, 24, 10, 6)) # rear-right

        # Cockpit
        pygame.draw.ellipse(base, (30,30,30), (25, 10, 10, 10))

        self.base_image = base
        self.image = base
        self.rect = self.image.get_rect(center=(x, y))



    def _forward(self) -> Vec2:
        rad = math.radians(self.angle)
        return Vec2(math.cos(rad), math.sin(rad))

    def handle_input(self, keys):
        accel_input = 0
        steer_input = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            accel_input += 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            accel_input -= 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            steer_input -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            steer_input += 1
        return accel_input, steer_input

    def update(self, dt: float, accel_input: int, steer_input: int, track_mask):
        # Longitudinal motion
        if accel_input > 0:
            self.speed += self.accel * dt
        elif accel_input < 0:
            self.speed -= self.brake_accel * dt
        else:
            if self.speed > 0:
                self.speed -= self.drag * dt
                if self.speed < 0: self.speed = 0
            elif self.speed < 0:
                self.speed += self.drag * dt
                if self.speed > 0: self.speed = 0

        self.speed = max(-self.max_reverse, min(self.speed, self.max_speed))

        # Steering
        if abs(self.speed) > 5:
            speed_factor = max(0.2, min(1.0, abs(self.speed) / self.max_speed))
            direction = 1 if self.speed >= 0 else -1
            self.angle += steer_input * self.steer_rate * speed_factor * direction * dt

        next_pos = self.pos + self._forward() * self.speed * dt
        x, y = int(next_pos.x), int(next_pos.y)
        if 0 <= x < track_mask.get_size()[0] and 0 <= y < track_mask.get_size()[1]:
            pixel_color = track_mask.get_at((x, y))[:3]  # ignore alpha
            if pixel_color != TRACK_COLOR:
                self.speed -= self.drag * 0.3 * dt  # reduced off-track slowdown
        self.pos += self._forward() * self.speed * dt

        self.image = pygame.transform.rotate(self.base_image, -self.angle)
        self.rect = self.image.get_rect(center=(self.pos.x, self.pos.y))

    def draw(self, surf: pygame.Surface):
        surf.blit(self.image, self.rect)



def draw_track_from_image(filename):
    track_surf = pygame.image.load(filename).convert()
    track_surf = pygame.transform.scale(track_surf, (WIDTH, HEIGHT))
    return track_surf


def draw_hud(surf: pygame.Surface, car: Car, laps, font: pygame.font.Font):
    spd_kph = int(car.speed * 0.36)
    text = font.render(f"Speed: {spd_kph} kph   Angle: {int(car.angle)%360}°   Laps: {laps}", True, WHITE)
    surf.blit(text, (20, 20))
    hint = font.render("Arrows/WASD to drive, ESC to quit", True, WHITE)
    surf.blit(hint, (20, 50))


def main():
    pygame.init()
    pygame.display.set_caption("F1 2D – Realistic Track")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)

    car = Car(WIDTH * 0.5, HEIGHT * 0.75)
    laps = 0
    crossed_finish = False

    # Replace 'track.png' with your top-down track image
    track_surf = draw_track_from_image('track.png.png')
    track_mask = pygame.mask.from_surface(track_surf)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        accel, steer = car.handle_input(keys)
        car.update(dt, accel, steer, track_surf)


        # Lap detection
        # You will need to mark a finish line in the track image and use a rect here
        # Lap detection using finish line rectangle
        finish_rect = pygame.Rect(WIDTH//2 - 30, HEIGHT - 80, 60, 10)  # adjust to your track
        if car.rect.colliderect(finish_rect) and not crossed_finish:
            laps += 1
            crossed_finish = True
        elif not car.rect.colliderect(finish_rect) and crossed_finish:
            crossed_finish = False


        screen.blit(track_surf, (0, 0))
        car.draw(screen)
        draw_hud(screen, car, laps, font)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
