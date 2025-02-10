import pygame
import math
import random
import sys
import colorsys

# --- Simulation parameters ---
WIDTH, HEIGHT = 800, 800
PARTICLE_RADIUS = 8
G = 6.67430e-2
TRAIL_LENGTH = 100
BG_COLOR = (0, 0, 0)
FPS = 60
DT = 1
SOFTENING = 10.0
MARGIN = 100

def get_user_input():
    """Gets simulation parameters from user via console input"""
    print("=== Simulation Configuration ===")
    
    # Number of bodies
    while True:
        try:
            num_bodies = int(input("Enter number of bodies (2-10): "))
            if 2 <= num_bodies <= 10:
                break
            print("Number of bodies must be between 2 and 10!")
        except ValueError:
            print("Please enter an integer!")

    # Mass configuration choice
    while True:
        choice = input("Generate random masses? (Y/N): ").upper()
        if choice in ['Y', 'N']:
            break
        print("Please choose Y (yes) or N (no)!")
    
    masses = []
    if choice == 'N':
        print("\nEnter masses for each body:")
        for i in range(num_bodies):
            while True:
                try:
                    mass = float(input(f"Mass of body {i+1} (100-10000): "))
                    if 100 <= mass <= 10000:
                        masses.append(mass)
                        break
                    print("Mass must be between 100 and 10000!")
                except ValueError:
                    print("Please enter a valid number!")
    
    # Generate HSV colors for better visual distinction
    colors = []
    for hue in [i/num_bodies for i in range(num_bodies)]:
        rgb = colorsys.hsv_to_rgb(hue, 0.9, 0.9)
        colors.append(tuple(int(255 * x) for x in rgb))
    
    return num_bodies, choice == 'Y', masses, colors

# Get user input before initializing PyGame
num_bodies, random_masses, manual_masses, PARTICLE_COLORS = get_user_input()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(f"{num_bodies}-Body Problem Simulation")
clock = pygame.time.Clock()

class Body:
    def __init__(self, x, y, vx, vy, mass, color):
        """Initialize a celestial body with position, velocity, mass and color"""
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.mass = mass
        self.color = color
        self.trail = []  # Stores position history for trail effect

    def update_position(self):
        """Update position based on velocity and maintain trail"""
        self.x += self.vx * DT
        self.y += self.vy * DT
        self.trail.append((self.x, self.y))
        if len(self.trail) > TRAIL_LENGTH:
            self.trail.pop(0)

    def draw(self, surface):
        """Draw the body and its trail with fading effect"""
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / TRAIL_LENGTH))  # Fade older positions
            pygame.draw.circle(surface, (*self.color, alpha), (int(pos[0]), int(pos[1])), 1)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), PARTICLE_RADIUS)

def compute_gravitational_force(body1, body2):
    """Calculate gravitational force between two bodies using Newton's law"""
    dx = body2.x - body1.x
    dy = body2.y - body1.y
    distance_sq = dx**2 + dy**2 + SOFTENING**2  # Softening to prevent singularity
    distance = math.sqrt(distance_sq)
    
    force = (G * body1.mass * body2.mass) / distance_sq
    angle = math.atan2(dy, dx)
    
    fx = force * math.cos(angle)
    fy = force * math.sin(angle)
    return fx, fy

def update_velocities(bodies):
    """Update velocities of all bodies based on gravitational interactions"""
    for body in bodies:
        ax_total = 0
        ay_total = 0
        for other in bodies:
            if body is not other:
                fx, fy = compute_gravitational_force(body, other)
                ax = fx / body.mass  # F = ma => a = F/m
                ay = fy / body.mass
                ax_total += ax
                ay_total += ay
        
        body.vx += ax_total * DT
        body.vy += ay_total * DT

def create_system():
    """Create a new system of bodies with user-configured parameters"""
    com_x = WIDTH/2
    com_y = HEIGHT/2
    bodies = []
    
    # Generate masses based on user choice
    if random_masses:
        masses = [random.uniform(1000, 3000) for _ in range(num_bodies)]
    else:
        masses = manual_masses
    
    # Generate initial positions and velocities
    positions = [(com_x + random.uniform(-200, 200), com_y + random.uniform(-200, 200)) for _ in range(num_bodies)]
    velocities = [(random.uniform(-1, 1)*0.5, random.uniform(-1, 1)*0.5) for _ in range(num_bodies)]

    # Center of mass velocity correction
    total_mass = sum(masses)
    vx_com = sum(m * vx for m, (vx, vy) in zip(masses, velocities)) / total_mass
    vy_com = sum(m * vy for m, (vx, vy) in zip(masses, velocities)) / total_mass

    for i in range(num_bodies):
        bodies.append(Body(
            x=positions[i][0],
            y=positions[i][1],
            vx=velocities[i][0] - vx_com,
            vy=velocities[i][1] - vy_com,
            mass=masses[i],
            color=PARTICLE_COLORS[i]
        ))
    
    return bodies

def all_bodies_outside(bodies):
    """Check if all bodies have exited the screen area (with margin)"""
    for body in bodies:
        if (0 - MARGIN < body.x < WIDTH + MARGIN and 
            0 - MARGIN < body.y < HEIGHT + MARGIN):
            return False
    return True

# Initialize first system
bodies = create_system()

running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    update_velocities(bodies)
    for body in bodies:
        body.update_position()

    # Restart condition check
    if all_bodies_outside(bodies):
        bodies = create_system()
        print("Simulation restarted! New initial conditions.")

    screen.fill(BG_COLOR)
    for body in bodies:
        body.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()