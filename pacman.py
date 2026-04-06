import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 672, 744
FPS = 60
TILE_SIZE = 24

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
PINK = (255, 184, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 184, 82)

# Map definition
level = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #      # ##.######",
    "      .   #      #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##.......P........##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################"
]

# Create screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pac-Man")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

class DynamicEntity:
    def __init__(self, r, c, color):
        self.r = r
        self.c = c
        self.x = float(c * TILE_SIZE + TILE_SIZE // 2)
        self.y = float(r * TILE_SIZE + TILE_SIZE // 2)
        self.color = color
        self.speed = 2.0
        self.direction = (0, 0)
        self.next_direction = (0, 0)
        self.anim_frame = 0

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), TILE_SIZE // 2 - 2)

    def can_move(self, dr, dc, is_ghost=False):
        # Calculate target position
        tr = self.y + dr * self.speed
        tc = self.x + dc * self.speed
        
        # Determine grid cells that the entity overlaps
        # Calculate bounding box (slightly smaller than tile for smoothness)
        margin = 4
        left = tc - (TILE_SIZE // 2 - margin)
        right = tc + (TILE_SIZE // 2 - margin)
        top = tr - (TILE_SIZE // 2 - margin)
        bottom = tr + (TILE_SIZE // 2 - margin)
        
        # Map indices
        r1, r2 = int(top // TILE_SIZE), int(bottom // TILE_SIZE)
        c1, c2 = int(left // TILE_SIZE), int(right // TILE_SIZE)

        if dr == 0 and dc == 0:
            return True

        # Check all cells that bounding box intersects
        for r in range(r1, r2 + 1):
            for c in range(c1, c2 + 1):
                # wrap around
                c_wrap = c % len(level[0])
                if 0 <= r < len(level):
                    char = level[r][c_wrap]
                    if char == '#':
                        return False
                    if char == '-' and not is_ghost:
                        return False
        return True

    def update(self):
        center_x = self.c * TILE_SIZE + TILE_SIZE // 2
        center_y = self.r * TILE_SIZE + TILE_SIZE // 2
        
        # 1. Try to switch to next_direction
        if (self.next_direction[0] == -self.direction[0] and self.next_direction[1] == -self.direction[1]) and self.next_direction != (0,0):
            # Immediate reversal allowed anywhere
            self.direction = self.next_direction
        elif abs(self.x - center_x) < self.speed and abs(self.y - center_y) < self.speed:
            # At or near a junction/center
            if self.next_direction != (0,0) and self.can_move(self.next_direction[1], self.next_direction[0]):
                self.x = float(center_x)
                self.y = float(center_y)
                self.direction = self.next_direction
            elif self.direction == (0,0) and self.next_direction != (0,0):
                # Start moving if stopped
                if self.can_move(self.next_direction[1], self.next_direction[0]):
                    self.direction = self.next_direction

        # 2. Move in current direction
        if self.can_move(self.direction[1], self.direction[0]):
            self.x += self.direction[0] * self.speed
            self.y += self.direction[1] * self.speed
        else:
            # Blocked, snap to center to prevent jittering but don't force movement
            self.x = float(center_x)
            self.y = float(center_y)
            # If Pac-Man is blocked, we set direction to (0,0) so he stops trying to walk into the wall
            # This is optional but helps with jitter. Let's keep it (0,0) for now.
            self.direction = (0, 0)
        
        # update grid pos
        self.c = int(self.x // TILE_SIZE)
        self.r = int(self.y // TILE_SIZE)
        
        # update animation frame
        if self.direction != (0,0):
            self.anim_frame = (self.anim_frame + 1) % 20

        # Tunnel wrap
        if self.x < 0:
            self.x = (len(level[0]) - 1) * TILE_SIZE
        if self.x > len(level[0]) * TILE_SIZE:
            self.x = 0

class Ghost(DynamicEntity):
    def __init__(self, r, c, color):
        super().__init__(r, c, color)
        self.direction = (0, -1) # Start moving UP to exit the house
        self.speed = 1.5 # Ghosts are slightly slower than Pac-Man for playability
        
    def draw(self):
        # Traditional ghost shape
        x, y = int(self.x), int(self.y)
        r = TILE_SIZE // 2 - 2
        
        # Rounded top
        pygame.draw.circle(screen, self.color, (x, y - 2), r)
        # Rectangular body
        pygame.draw.rect(screen, self.color, (x - r, y - 2, r * 2, r + 4))
        # Wavy bottom
        for i in range(3):
            wx = x - r + (i * 2 + 1) * (r // 3)
            pygame.draw.circle(screen, self.color, (wx, y + r + 2), r // 3)
            
        # Eyes
        eye_color = WHITE
        iris_color = BLUE
        eye_size = 4
        iris_size = 2
        # Offset eye iris based on movement direction
        dx, dy = self.direction
        
        # Left eye
        pygame.draw.circle(screen, eye_color, (x - 5, y - 4), eye_size)
        pygame.draw.circle(screen, iris_color, (x - 5 + dx * 2, y - 4 + dy * 2), iris_size)
        # Right eye
        pygame.draw.circle(screen, eye_color, (x + 5, y - 4), eye_size)
        pygame.draw.circle(screen, iris_color, (x + 5 + dx * 2, y - 4 + dy * 2), iris_size)

    def update(self):
        center_x = self.c * TILE_SIZE + TILE_SIZE // 2
        center_y = self.r * TILE_SIZE + TILE_SIZE // 2
        
        # decision logic only at tile centers
        if abs(self.x - center_x) < self.speed and abs(self.y - center_y) < self.speed:
            self.x = float(center_x)
            self.y = float(center_y)
            
            moves = [(1,0), (-1,0), (0,1), (0,-1)]
            valid = [m for m in moves if self.can_move(m[1], m[0], is_ghost=True)]
            
            if len(valid) > 1:
                opposite = (-self.direction[0], -self.direction[1])
                if opposite in valid:
                    valid.remove(opposite)
            
            if valid:
                in_house = 12 <= self.r <= 16 and 11 <= self.c <= 16
                if in_house and (0, -1) in valid:
                    self.direction = (0, -1)
                else:
                    self.direction = random.choice(valid)
            else:
                self.direction = (-self.direction[0], -self.direction[1])

        # Smooth continuous movement
        if self.can_move(self.direction[1], self.direction[0], is_ghost=True):
            self.x += self.direction[0] * self.speed
            self.y += self.direction[1] * self.speed
        else:
            # force snap and stop to prevent micro-jitter
            self.x = float(center_x)
            self.y = float(center_y)
            self.direction = (0, 0)
            
        self.c = int(self.x // TILE_SIZE)
        self.r = int(self.y // TILE_SIZE)

        if self.x < 0:
            self.x = (len(level[0]) - 1) * TILE_SIZE
        if self.x > len(level[0]) * TILE_SIZE:
            self.x = 0

def main():
    dots = []
    power_pellets = []
    walls = []
    ghosts = []
    
    player_r, player_c = 1, 1

    for r, row in enumerate(level):
        for c, char in enumerate(row):
            if char == '#':
                walls.append((r, c))
            elif char == '.':
                dots.append((r, c))
            elif char == 'o':
                power_pellets.append((r, c))
            elif char == 'P':
                player_r, player_c = r, c
                
    # Place ghosts in ghost house manually
    ghosts.append(Ghost(14, 13, RED))
    ghosts.append(Ghost(14, 14, PINK))
    ghosts.append(Ghost(13, 13, CYAN))
    ghosts.append(Ghost(13, 14, ORANGE))

    player = DynamicEntity(player_r, player_c, YELLOW)
    score = 0
    
    game_over = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    player.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    player.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    player.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    player.next_direction = (1, 0)
        
        if not game_over:
            player.update()
            for ghost in ghosts:
                ghost.update()

            # Collision with dots
            p_r, p_c = player.r, int(player.x // TILE_SIZE) % len(level[0])
            if (player.r, p_c) in dots:
                dots.remove((player.r, p_c))
                score += 10
            
            if (player.r, p_c) in power_pellets:
                power_pellets.remove((player.r, p_c))
                score += 50

            # Collision with ghosts
            for ghost in ghosts:
                if abs(player.x - ghost.x) < TILE_SIZE - 4 and abs(player.y - ghost.y) < TILE_SIZE - 4:
                    game_over = True

            if len(dots) == 0 and len(power_pellets) == 0:
                game_over = True
        
        screen.fill(BLACK)
        
        # draw walls
        for r, row in enumerate(level):
            for c, char in enumerate(row):
                if char == '#':
                    pygame.draw.rect(screen, BLUE, (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE), 2)
                if char == '-':
                    pygame.draw.rect(screen, WHITE, (c * TILE_SIZE, r * TILE_SIZE + TILE_SIZE//2 - 2, TILE_SIZE, 4))
        
        # draw dots
        for r, c in dots:
            pygame.draw.circle(screen, WHITE, (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2), 3)
            
        for r, c in power_pellets:
            pygame.draw.circle(screen, WHITE, (c * TILE_SIZE + TILE_SIZE // 2, r * TILE_SIZE + TILE_SIZE // 2), 8)
            
        # Draw Pac-Man with chomping animation
        player_pos = (int(player.x), int(player.y))
        r = TILE_SIZE // 2 - 2
        
        # Mouth opening angle (0 to 45 degrees)
        import math
        mouth_angle = abs(math.sin(player.anim_frame * 2 * math.pi / 20)) * 45
        
        # Base body
        pygame.draw.circle(screen, player.color, player_pos, r)
        
        # Draw mouth cutout
        if player.direction != (0,0):
            # Calculate base angle based on direction
            if player.direction == (1, 0): base_deg = 0
            elif player.direction == (-1, 0): base_deg = 180
            elif player.direction == (0, -1): base_deg = 90
            else: base_deg = 270 # (0, 1)

            p1 = player_pos
            p2 = (player_pos[0] + r * math.cos(math.radians(base_deg - mouth_angle)), 
                  player_pos[1] - r * math.sin(math.radians(base_deg - mouth_angle)))
            p3 = (player_pos[0] + r * math.cos(math.radians(base_deg + mouth_angle)), 
                  player_pos[1] - r * math.sin(math.radians(base_deg + mouth_angle)))
            pygame.draw.polygon(screen, BLACK, [p1, p2, p3])
        else:
            # Simple mouth for when stopped (static direction indicator)
            if player.direction == (1, 0): # right
                pygame.draw.polygon(screen, BLACK, [player_pos, (player_pos[0] + r, player_pos[1] - r//2), (player_pos[0] + r, player_pos[1] + r//2)])
            elif player.direction == (-1, 0): # left
                pygame.draw.polygon(screen, BLACK, [player_pos, (player_pos[0] - r, player_pos[1] - r//2), (player_pos[0] - r, player_pos[1] + r//2)])
            elif player.direction == (0, -1): # up
                pygame.draw.polygon(screen, BLACK, [player_pos, (player_pos[0] - r//2, player_pos[1] - r), (player_pos[0] + r//2, player_pos[1] - r)])
            elif player.direction == (0, 1): # down
                pygame.draw.polygon(screen, BLACK, [player_pos, (player_pos[0] - r//2, player_pos[1] + r), (player_pos[0] + r//2, player_pos[1] + r)])
             
        for ghost in ghosts:
            ghost.draw()
            
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        if game_over:
            if len(dots) == 0 and len(power_pellets) == 0:
                 over_text = font.render("YOU WIN!", True, YELLOW)
            else:
                 over_text = font.render("GAME OVER", True, RED)
            screen.blit(over_text, (WIDTH // 2 - 80, HEIGHT // 2))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
