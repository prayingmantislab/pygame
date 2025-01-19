import pygame
import random
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # For sound effects
if not pygame.mixer.get_init():
    print("Sound system failed to initialize")

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)  # Used for score text and fallback spaceship
BLACK = (0, 0, 0)  # Used as fallback background if image fails to load
RED = (255, 0, 0)  # Used as fallback for asteroids if image fails
YELLOW = (255, 255, 0)  # Used as fallback for crystals if image fails

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Adventure")


class ScrollingBackground:
    def __init__(self, image):
        self.image = image
        self.rect1 = self.image.get_rect()
        self.rect2 = self.image.get_rect()
        # Start first image at top of screen
        self.rect1.top = 0
        # Place second image directly above first image (no gap)
        self.rect2.bottom = self.rect1.top
        self.scroll_speed = 2

    def update(self):
        # Move both background images down
        self.rect1.y += self.scroll_speed
        self.rect2.y += self.scroll_speed

        # If the first image is completely off screen, move it to top of second image
        if self.rect1.top >= SCREEN_HEIGHT:
            self.rect1.bottom = self.rect2.top

        # If the second image is completely off screen, move it to top of first image
        if self.rect2.top >= SCREEN_HEIGHT:
            self.rect2.bottom = self.rect1.top

    def draw(self, screen):
        screen.blit(self.image, self.rect1)
        screen.blit(self.image, self.rect2)


# Load images
try:
    SPACESHIP_IMG = pygame.image.load("images/spaceship.png")
    BACKGROUND_IMG = pygame.image.load("images/background.png")
    CRYSTAL_IMG = pygame.image.load("images/crystal.png")
    ASTEROID_IMG = pygame.image.load("images/asteroid.png")
    SPACESHIP_IMG = pygame.transform.scale(SPACESHIP_IMG, (40, 60))
    BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (SCREEN_WIDTH, SCREEN_HEIGHT))
    CRYSTAL_IMG = pygame.transform.scale(CRYSTAL_IMG, (60, 60))
    ASTEROID_IMG = pygame.transform.scale(ASTEROID_IMG, (50, 50))
    scrolling_background = ScrollingBackground(BACKGROUND_IMG)
except Exception as e:
    SPACESHIP_IMG = None
    BACKGROUND_IMG = None
    CRYSTAL_IMG = None
    ASTEROID_IMG = None
    scrolling_background = None
    print(f"Error loading images: {e}")


class Spaceship:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.speed = 5
        self.color = WHITE
        self.image = SPACESHIP_IMG

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed

    def draw(self):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback to triangle if image loading failed
            pygame.draw.polygon(screen, self.color, [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ])


class GameObject:
    def __init__(self, x, y, size, color, image=None):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.active = True
        self.image = image

    def draw(self):
        if not self.active:
            return
        if self.image:
            # Center the image on the object's position
            image_rect = self.image.get_rect()
            image_rect.center = (self.x, self.y)
            screen.blit(self.image, image_rect)
        else:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)


def create_objects(count, size, color):
    objects = []
    for _ in range(count):
        x = random.randint(size, SCREEN_WIDTH - size)
        y = random.randint(size, SCREEN_HEIGHT // 2)
        objects.append(GameObject(x, y, size, color))
    return objects


def check_collision(spaceship, obj):
    ship_center = (spaceship.x + spaceship.width // 2, spaceship.y + spaceship.height // 2)
    distance = ((ship_center[0] - obj.x) ** 2 + (ship_center[1] - obj.y) ** 2) ** 0.5
    return distance < obj.size + 20


def main():
    # Game objects
    spaceship = Spaceship()
    asteroids = [GameObject(
        random.randint(20, SCREEN_WIDTH - 20),
        random.randint(20, SCREEN_HEIGHT // 2),
        15, RED, ASTEROID_IMG
    ) for _ in range(5)]
    stars = [GameObject(
        random.randint(20, SCREEN_WIDTH - 20),
        random.randint(20, SCREEN_HEIGHT // 2),
        10, YELLOW, CRYSTAL_IMG
    ) for _ in range(3)]
    score = 0
    clock = pygame.time.Clock()

    # Try to load sound effects
    try:
        point_sound = pygame.mixer.Sound("sounds/point.wav")
        crash_sound = pygame.mixer.Sound("sounds/crash.wav")
    except Exception as e:
        print(f"Error loading sounds: {e}")  # This will show us what's wrong
        point_sound = None
        crash_sound = None

    # Game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # When user clicks X button
                running = False

        # Move spaceship
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:  # Add this line to quit with Escape key
            running = False
        spaceship.move(keys)

        # Check if spaceship reached top
        if spaceship.y <= 0:
            score += 1
            if point_sound:
                point_sound.play()
            spaceship.y = SCREEN_HEIGHT - 100  # Reset position

            # Spawn new crystals when reaching top
            for star in stars:
                if not star.active:  # Only respawn inactive crystals
                    star.x = random.randint(20, SCREEN_WIDTH - 20)
                    star.y = random.randint(20, SCREEN_HEIGHT // 2)
                    star.active = True

        # Check collisions with asteroids and stars
        for asteroid in asteroids:
            if asteroid.active and check_collision(spaceship, asteroid):
                score -= 1
                if crash_sound:
                    crash_sound.play()
                spaceship.y = SCREEN_HEIGHT - 100
                asteroid.active = False

        for star in stars:
            if star.active and check_collision(spaceship, star):
                score += 5
                if point_sound:
                    point_sound.play()
                star.active = False
                # Respawn timer for this star
                pygame.time.set_timer(pygame.USEREVENT + len(stars), 3000)  # 3000ms = 3 seconds

        # Harder level when score reaches 10
        if score >= 10:
            if random.random() < 0.02:  # 2% chance each frame
                new_asteroid = GameObject(
                    SCREEN_WIDTH,
                    random.randint(0, SCREEN_HEIGHT),
                    15, RED, ASTEROID_IMG
                )
                asteroids.append(new_asteroid)

        # Draw everything
        if scrolling_background:
            scrolling_background.update()
            scrolling_background.draw(screen)
        else:
            screen.fill(BLACK)  # Fallback to black if image loading failed
        spaceship.draw()

        for asteroid in asteroids:
            if asteroid.active:
                asteroid.draw()
                if score >= 10:
                    asteroid.x -= 2  # Move asteroids from right to left

        for star in stars:
            if star.active:
                star.draw()

        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Update display
        pygame.display.flip()

        # Control game speed
        clock.tick(FPS)

        # Add event handling for crystal respawn
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Check for crystal respawn events
            elif event.type >= pygame.USEREVENT and event.type < pygame.USEREVENT + len(stars):
                star_index = event.type - pygame.USEREVENT
                if star_index < len(stars) and not stars[star_index].active:
                    # Respawn the crystal at a new random position
                    stars[star_index].x = random.randint(20, SCREEN_WIDTH - 20)
                    stars[star_index].y = random.randint(20, SCREEN_HEIGHT // 2)
                    stars[star_index].active = True

    pygame.quit()  # Clean up pygame
    sys.exit()  # Exit the program


if __name__ == "__main__":
    main()
