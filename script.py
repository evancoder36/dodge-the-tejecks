import pygame
import random
import sys
import json
import asyncio
import math
import platform

# Cloud leaderboard using npoint.io (FREE, no API key needed!)
# This enables live cross-device leaderboard!
CLOUD_ENABLED = True
NPOINT_ID = "b972a0dc0c169fb73135"  # Your npoint.io endpoint ID

# Check if running in browser (Pygbag/Emscripten)
def is_browser():
    """Check if running in browser environment."""
    return sys.platform == "emscripten"

async def cloud_save(data):
    """Save leaderboard data to cloud (npoint.io)."""
    if not CLOUD_ENABLED:
        return False
    try:
        url = f"https://api.npoint.io/{NPOINT_ID}"
        json_data = json.dumps(data)

        if is_browser() and hasattr(platform, 'window'):
            # Use JavaScript fetch in browser
            js_code = f'''
                fetch("{url}", {{
                    method: "POST",
                    headers: {{ "Content-Type": "application/json" }},
                    body: '{json_data.replace("'", "\\'")}'
                }}).then(r => r.ok).catch(e => false)
            '''
            platform.window.eval(js_code)
            print("Cloud save sent")
            return True
        else:
            # Use urllib for desktop
            import urllib.request
            req = urllib.request.Request(url, data=json_data.encode('utf-8'), method='POST')
            req.add_header('Content-Type', 'application/json')
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.status == 200
    except Exception as e:
        print(f"Cloud save error: {e}")
    return False

async def cloud_load():
    """Load leaderboard data from cloud (npoint.io)."""
    if not CLOUD_ENABLED:
        return None
    try:
        url = f"https://api.npoint.io/{NPOINT_ID}"

        if is_browser() and hasattr(platform, 'window'):
            # Use JavaScript fetch in browser - need to handle async properly
            js_code = f'''
                (function() {{
                    var result = null;
                    var xhr = new XMLHttpRequest();
                    xhr.open("GET", "{url}", false);
                    xhr.send();
                    if (xhr.status === 200) {{
                        result = xhr.responseText;
                    }}
                    return result;
                }})()
            '''
            result = platform.window.eval(js_code)
            if result:
                data = json.loads(result)
                print(f"Cloud load: got {len(data)} users")
                return data
        else:
            # Use urllib for desktop
            import urllib.request
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                print(f"Cloud load: got {len(data)} users")
                return data
    except Exception as e:
        print(f"Cloud load error: {e}")
    return None

def storage_set(key, value):
    """Save to localStorage (browser) or file (desktop)."""
    try:
        if is_browser():
            # Use JavaScript directly via platform.window
            import platform
            if hasattr(platform, 'window'):
                platform.window.localStorage.setItem(key, value)
                print(f"localStorage.setItem({key}) done")
                return True
            else:
                print("No platform.window available!")
        else:
            filename = f"{key}.json" if "leaderboard" in key else f"{key}.txt"
            with open(filename, "w") as f:
                f.write(value)
            return True
    except Exception as e:
        print(f"storage_set error: {e}")
    return False

def storage_get(key):
    """Load from localStorage (browser) or file (desktop)."""
    try:
        if is_browser():
            import platform
            if hasattr(platform, 'window'):
                result = platform.window.localStorage.getItem(key)
                print(f"localStorage.getItem({key}) = {result[:50] if result else None}...")
                return result if result else None
            else:
                print("No platform.window available!")
        else:
            filename = f"{key}.json" if "leaderboard" in key else f"{key}.txt"
            with open(filename, "r") as f:
                return f.read()
    except Exception as e:
        print(f"storage_get error: {e}")
    return None

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions for phone size
SCREEN_WIDTH = 798
SCREEN_HEIGHT = 640

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
PURPLE = (150, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Fonts
FONT = pygame.font.Font(None, 30)
BIG_FONT = pygame.font.Font(None, 50)
SMALL_FONT = pygame.font.Font(None, 24)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge the Tejecks")

# Game variables
points = 0
high_score = 0
current_username = ""  # Current player's username
current_level = "Easy"  # Track current level being played
leaderboard_data = {}  # All players' data
shop_items = {
    "EMDR Tejeck": {"cost": 0, "image": pygame.image.load("emdr_tejeck.png"), "purchased": True},
    "BabyTejeck": {"cost": 200, "image": pygame.image.load("babytejeck.jpeg"), "purchased": False},
    "Amelia": {"cost": 250, "image": pygame.image.load("amelia.jpeg"), "purchased": False},
    "Evan": {"cost": 300, "image": pygame.image.load("me.jpeg"), "purchased": False},
    "Mei": {"cost": 350, "image": pygame.image.load("babes.jpeg"), "purchased": False},
    "Alv": {"cost": 400, "image": pygame.image.load("alvin.jpeg"), "purchased": False},
}
equipped_item = "EMDR Tejeck"
selected_item = 0

# Load all enemy images
enemy_images = [
    pygame.image.load("adeline.jpeg"),
    pygame.image.load("alvin.jpeg"),
    pygame.image.load("amelia.jpeg"),
    pygame.image.load("babes.jpeg"),
    pygame.image.load("babytejeck.jpeg"),
    pygame.image.load("me.jpeg"),
]

# Load boss image
try:
    boss_image = pygame.image.load("tejeck_boss.jpg")
except:
    boss_image = pygame.image.load("babytejeck.jpeg")  # Fallback

# Enemy class for falling characters with random sizes
class Enemy:
    def __init__(self, x):
        self.x = x
        self.y = -50
        self.image = random.choice(enemy_images)
        self.size = random.randint(25, 60)  # Random size from small to big
        self.scaled_image = pygame.transform.scale(self.image, (self.size, self.size))
        self.rotation = random.uniform(-30, 30)  # Slight random rotation
        self.spin_speed = random.uniform(-2, 2)  # Spinning animation
        self.angle = 0

    def update(self, speed):
        self.y += speed
        self.angle += self.spin_speed

    def draw(self, surface, shake_x=0, shake_y=0):
        # Rotate the image for fun spinning effect
        rotated = pygame.transform.rotate(self.scaled_image, self.angle)
        rect = rotated.get_rect(center=(self.x + shake_x, self.y + shake_y))
        surface.blit(rotated, rect)

    def get_rect(self):
        half = self.size // 2
        return pygame.Rect(self.x - half, self.y - half, self.size, self.size)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + self.size

# Boss class for the FINAL VIRTUAL EMDR TEJECK BOSS
class Boss:
    def __init__(self):
        self.size = 150  # Big boss!
        self.x = SCREEN_WIDTH // 2
        self.y = 100
        self.target_x = SCREEN_WIDTH // 2
        self.health = 100
        self.max_health = 100
        self.image = pygame.transform.scale(boss_image, (self.size, self.size))
        self.angle = 0
        self.spin_speed = 1
        self.move_timer = 0
        self.fire_timer = 0
        self.fire_rate = 60  # Frames between fire shots
        self.phase = 1  # Boss phases get harder
        self.hit_flash = 0

    def update(self):
        # Spin animation
        self.angle += self.spin_speed

        # Move towards target
        if abs(self.x - self.target_x) > 5:
            if self.x < self.target_x:
                self.x += 3
            else:
                self.x -= 3

        # Change target position periodically
        self.move_timer += 1
        if self.move_timer > 90:
            self.move_timer = 0
            self.target_x = random.randint(100, SCREEN_WIDTH - 100)

        # Update phase based on health
        if self.health < 30:
            self.phase = 3
            self.fire_rate = 20
            self.spin_speed = 3
        elif self.health < 60:
            self.phase = 2
            self.fire_rate = 40
            self.spin_speed = 2

        # Fire timer
        self.fire_timer += 1

        # Hit flash decay
        if self.hit_flash > 0:
            self.hit_flash -= 1

    def should_fire(self):
        if self.fire_timer >= self.fire_rate:
            self.fire_timer = 0
            return True
        return False

    def draw(self, surface):
        # Draw boss with rotation (ball-shaped spinning)
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))

        # Draw boss
        surface.blit(rotated, rect)

        # Flash effect when hit (simple red ring)
        if self.hit_flash > 0:
            # Draw red rings around boss when hit
            pygame.draw.circle(surface, RED, (int(self.x), int(self.y)), self.size // 2 + 10, 4)
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), self.size // 2 + 5, 3)

        # Draw health bar
        bar_width = 200
        bar_height = 20
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        health_ratio = self.health / self.max_health

        # Background
        pygame.draw.rect(surface, (50, 50, 50), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=5)
        # Health bar
        health_color = GREEN if health_ratio > 0.5 else (YELLOW if health_ratio > 0.25 else RED)
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, int(bar_width * health_ratio), bar_height), border_radius=3)
        # Border
        pygame.draw.rect(surface, WHITE, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), 2, border_radius=5)

        # Boss name
        name_text = FONT.render("FINAL VIRTUAL EMDR TEJECK BOSS", True, RED)
        surface.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, bar_y + 25))

        # Phase indicator
        phase_text = SMALL_FONT.render(f"Phase {self.phase}", True, PURPLE)
        surface.blit(phase_text, (SCREEN_WIDTH // 2 - phase_text.get_width() // 2, bar_y + 50))

    def get_rect(self):
        half = self.size // 2
        return pygame.Rect(self.x - half, self.y - half, self.size, self.size)

    def take_damage(self, amount):
        self.health -= amount
        self.hit_flash = 10
        return self.health <= 0

# Fire projectile class for boss attacks
class Fire:
    def __init__(self, x, y, target_x, target_y, speed=8):
        self.x = x
        self.y = y
        # Calculate direction towards target
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx = (dx / dist) * speed
            self.vy = (dy / dist) * speed
        else:
            self.vx = 0
            self.vy = speed
        self.size = 15
        self.lifetime = 300
        self.angle = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.angle += 10
        self.lifetime -= 1

    def draw(self, surface):
        # Draw fire as animated flame
        colors = [RED, ORANGE, YELLOW]
        for i, color in enumerate(colors):
            size = self.size - i * 3
            if size > 0:
                offset = math.sin(self.angle * 0.1 + i) * 3
                pygame.draw.circle(surface, color, (int(self.x + offset), int(self.y)), size)

        # Fire trail
        for i in range(3):
            trail_x = self.x - self.vx * (i + 1) * 0.5
            trail_y = self.y - self.vy * (i + 1) * 0.5
            trail_size = self.size - i * 4
            if trail_size > 0:
                pygame.draw.circle(surface, ORANGE, (int(trail_x), int(trail_y)), trail_size)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def is_dead(self):
        return (self.lifetime <= 0 or
                self.x < -50 or self.x > SCREEN_WIDTH + 50 or
                self.y < -50 or self.y > SCREEN_HEIGHT + 50)

# Clock for controlling FPS
clock = pygame.time.Clock()

# Sound generation functions (works with Pygbag)
def generate_sound(frequency, duration_ms, volume=0.3):
    """Generate a simple beep sound."""
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration_ms / 1000)
        buf = bytes([int(128 + 127 * volume * math.sin(2 * math.pi * frequency * t / sample_rate))
                     for t in range(n_samples)])
        sound = pygame.mixer.Sound(buffer=buf)
        sound.set_volume(volume)
        return sound
    except:
        return None

# Generate sounds
sound_collect = generate_sound(880, 100, 0.2)
sound_powerup = generate_sound(1200, 150, 0.3)
sound_hit = generate_sound(200, 300, 0.4)
sound_dodge = generate_sound(600, 50, 0.1)
sound_laser = generate_sound(1500, 80, 0.25)
sound_explosion = generate_sound(150, 400, 0.5)
sound_bomb = generate_sound(100, 500, 0.4)

def play_sound(sound):
    """Play a sound if available."""
    try:
        if sound:
            sound.play()
    except:
        pass

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, color, velocity=None, lifetime=30):
        self.x = x
        self.y = y
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        if velocity:
            self.vx, self.vy = velocity
        else:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.lifetime -= 1
        self.size = max(1, int(self.size * 0.95))

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color[:3], alpha) if len(self.color) == 4 else self.color
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

    def is_dead(self):
        return self.lifetime <= 0

# Laser class for shooting
class Laser:
    def __init__(self, x, y, color=RED, speed=15, width=4, double=False):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.width = width
        self.height = 20
        self.double = double
        self.active = True

    def update(self):
        self.y -= self.speed

    def draw(self, surface):
        # Main laser beam
        pygame.draw.rect(surface, self.color, (self.x - self.width // 2, self.y, self.width, self.height))
        # Glow effect
        pygame.draw.rect(surface, WHITE, (self.x - self.width // 4, self.y + 2, self.width // 2, self.height - 4))
        # Trail effect
        for i in range(3):
            alpha_color = (self.color[0], self.color[1], self.color[2])
            trail_y = self.y + self.height + i * 8
            trail_width = self.width - i
            if trail_width > 0:
                pygame.draw.rect(surface, alpha_color, (self.x - trail_width // 2, trail_y, trail_width, 6))

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y, self.width, self.height)

    def is_off_screen(self):
        return self.y < -self.height

# Explosion class for bomb effect
class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.max_radius = 80
        self.growth_speed = 8
        self.active = True
        self.alpha = 255

    def update(self):
        self.radius += self.growth_speed
        self.alpha = max(0, 255 - (self.radius / self.max_radius) * 255)
        if self.radius >= self.max_radius:
            self.active = False

    def draw(self, surface):
        if self.active:
            # Outer ring
            pygame.draw.circle(surface, ORANGE, (int(self.x), int(self.y)), int(self.radius), 4)
            # Inner ring
            pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), int(self.radius * 0.7), 3)
            # Core
            pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), int(self.radius * 0.3))

# Power-up class
class PowerUp:
    TYPES = {
        'coin': {'color': YELLOW, 'symbol': '$', 'duration': 0},
        'shield': {'color': CYAN, 'symbol': 'S', 'duration': 300},
        'speed': {'color': GREEN, 'symbol': '>', 'duration': 300},
        'slowmo': {'color': PURPLE, 'symbol': '~', 'duration': 200},
        'magnet': {'color': ORANGE, 'symbol': 'M', 'duration': 250},
        'bomb': {'color': RED, 'symbol': 'B', 'duration': 0},
        'rapid': {'color': (255, 100, 100), 'symbol': 'R', 'duration': 300},
        'double': {'color': (100, 100, 255), 'symbol': 'D', 'duration': 400},
        'ammo': {'color': (200, 200, 200), 'symbol': 'A', 'duration': 0},
    }

    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.size = 25
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.collected = False

    def update(self, speed):
        self.y += speed * 0.5
        self.bob_offset += 0.1

    def draw(self, surface, shake_x=0, shake_y=0):
        # Bobbing animation
        bob = math.sin(self.bob_offset) * 5
        draw_y = self.y + bob + shake_y
        draw_x = self.x + shake_x

        info = self.TYPES[self.type]
        # Outer glow
        pygame.draw.circle(surface, info['color'], (int(draw_x), int(draw_y)), self.size + 5, 2)
        # Inner circle
        pygame.draw.circle(surface, info['color'], (int(draw_x), int(draw_y)), self.size)
        # Symbol
        text = SMALL_FONT.render(info['symbol'], True, BLACK)
        text_rect = text.get_rect(center=(draw_x, draw_y))
        surface.blit(text, text_rect)

    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + self.size

# Screen shake variables
screen_shake = 0
shake_intensity = 0

def apply_screen_shake():
    global screen_shake, shake_intensity
    if screen_shake > 0:
        screen_shake -= 1
        shake_intensity *= 0.9
        return random.randint(-int(shake_intensity), int(shake_intensity)), random.randint(-int(shake_intensity), int(shake_intensity))
    return 0, 0

def trigger_screen_shake(intensity=10, duration=10):
    global screen_shake, shake_intensity
    screen_shake = duration
    shake_intensity = intensity

# Background animation
bg_particles = []
def update_background():
    global bg_particles
    # Add new background particles occasionally
    if random.random() < 0.1:
        bg_particles.append({
            'x': random.randint(0, SCREEN_WIDTH),
            'y': SCREEN_HEIGHT + 10,
            'speed': random.uniform(0.5, 2),
            'size': random.randint(2, 5),
            'alpha': random.randint(50, 150)
        })

    # Update particles
    for p in bg_particles[:]:
        p['y'] -= p['speed']
        if p['y'] < -10:
            bg_particles.remove(p)

def draw_background(surface, game_active=False):
    # Gradient background
    for y in range(0, SCREEN_HEIGHT, 4):
        ratio = y / SCREEN_HEIGHT
        if game_active:
            color = (int(240 - 40 * ratio), int(248 - 40 * ratio), 255)
        else:
            color = (int(250 - 20 * ratio), int(250 - 20 * ratio), 255)
        pygame.draw.rect(surface, color, (0, y, SCREEN_WIDTH, 4))

    # Draw floating particles
    for p in bg_particles:
        pygame.draw.circle(surface, (200, 200, 255), (int(p['x']), int(p['y'])), p['size'])

# Level unlock requirements: score needed in previous level to unlock next
# Easy is always unlocked, others require score in previous level
level_unlock_requirements = {
    "Easy": 0,        # Always unlocked
    "Medium": 20,     # Need 20 points in Easy
    "Hard": 25,       # Need 25 points in Medium
    "Impossible": 30, # Need 30 points in Hard
    "God Mode": 35,   # Need 35 points in Impossible
    "Creator Mode": 40, # Need 40 points in God Mode
    "BOSS MODE": 45,  # Need 45 points in Creator Mode
}

# Best scores per difficulty level
best_scores = {
    "Easy": 0,
    "Medium": 0,
    "Hard": 0,
    "Impossible": 0,
    "God Mode": 0,
    "Creator Mode": 0,
    "BOSS MODE": 0,
}

def is_level_unlocked(level_name):
    """Check if a level is unlocked based on previous level's best score."""
    level_order = ["Easy", "Medium", "Hard", "Impossible", "God Mode", "Creator Mode", "BOSS MODE"]
    level_idx = level_order.index(level_name)

    if level_idx == 0:
        return True  # Easy is always unlocked

    # Check if previous level's best score meets requirement
    prev_level = level_order[level_idx - 1]
    required_score = level_unlock_requirements[level_name]
    return best_scores[prev_level] >= required_score

# Flag to track if cloud sync is pending
cloud_sync_pending = False

def save_progress():
    """Save current user's progress to leaderboard (local + queue cloud sync)."""
    global high_score, leaderboard_data, cloud_sync_pending

    if not current_username:
        return  # Don't save if no username

    # Update leaderboard data for current user
    leaderboard_data[current_username] = {
        "points": points,
        "high_score": high_score,
        "purchased_items": {item: data["purchased"] for item, data in shop_items.items()},
        "best_scores": best_scores.copy(),
        "current_level": current_level,
    }

    # Save to local storage
    json_data = json.dumps(leaderboard_data)
    storage_set("dodge_leaderboard", json_data)
    storage_set("dodge_lastuser", current_username)
    print(f"Saved locally: {current_username} with {points} points")

    # Mark cloud sync as pending
    cloud_sync_pending = True

async def sync_to_cloud():
    """Sync leaderboard to cloud if pending."""
    global cloud_sync_pending
    if cloud_sync_pending and CLOUD_ENABLED:
        try:
            # First load latest from cloud to merge
            cloud_data = await cloud_load()
            if cloud_data:
                # Merge: keep higher scores for each user
                for username, data in cloud_data.items():
                    if username not in leaderboard_data:
                        leaderboard_data[username] = data
                    elif data.get("points", 0) > leaderboard_data[username].get("points", 0):
                        # Cloud has higher score, but keep local user's current session
                        if username != current_username:
                            leaderboard_data[username] = data

            # Now save merged data to cloud
            await cloud_save(leaderboard_data)
            cloud_sync_pending = False
            print("Cloud sync complete!")
        except Exception as e:
            print(f"Cloud sync error: {e}")

def load_leaderboard():
    """Load all users' data from local storage."""
    global leaderboard_data
    try:
        data = storage_get("dodge_leaderboard")
        if data:
            leaderboard_data = json.loads(data)
            print(f"Loaded {len(leaderboard_data)} users from local")
        else:
            leaderboard_data = {}
            print("No saved data, starting fresh")
    except Exception as e:
        print(f"Load failed: {e}")
        leaderboard_data = {}

async def load_leaderboard_from_cloud():
    """Load and merge leaderboard from cloud."""
    global leaderboard_data
    if not CLOUD_ENABLED:
        return

    try:
        print("Fetching leaderboard from cloud...")
        cloud_data = await cloud_load()
        if cloud_data:
            # Merge cloud data with local data
            for username, data in cloud_data.items():
                if username not in leaderboard_data:
                    leaderboard_data[username] = data
                elif username != current_username:
                    # For other users, take the higher score
                    if data.get("points", 0) > leaderboard_data[username].get("points", 0):
                        leaderboard_data[username] = data
            print(f"Merged cloud data: now {len(leaderboard_data)} users")
    except Exception as e:
        print(f"Cloud load failed: {e}")

def load_user_progress(username):
    """Load a specific user's progress from leaderboard data."""
    global points, high_score, best_scores, current_username

    current_username = username

    if username in leaderboard_data:
        user_data = leaderboard_data[username]
        points = user_data.get("points", 0)
        high_score = user_data.get("high_score", 0)

        # Load purchased items
        purchased = user_data.get("purchased_items", {})
        for item in shop_items:
            shop_items[item]["purchased"] = purchased.get(item, item == "EMDR Tejeck")

        # Load best scores
        saved_scores = user_data.get("best_scores", {})
        for level in best_scores:
            best_scores[level] = saved_scores.get(level, 0)
    else:
        # New user - reset to defaults
        points = 0
        high_score = 0
        for item in shop_items:
            shop_items[item]["purchased"] = (item == "EMDR Tejeck")  # EMDR is free/default
        for level in best_scores:
            best_scores[level] = 0

def get_sorted_leaderboard():
    """Get leaderboard sorted by total points (descending)."""
    sorted_users = sorted(
        leaderboard_data.items(),
        key=lambda x: x[1].get("points", 0),
        reverse=True
    )
    return sorted_users

def draw_text(text, font, color, x, y):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

def draw_text_centered(text, font, color, y):
    render = font.render(text, True, color)
    x = (SCREEN_WIDTH - render.get_width()) // 2
    screen.blit(render, (x, y))

# Touch control button definitions
TOUCH_BUTTON_SIZE = 60
TOUCH_BUTTONS = {
    "left": pygame.Rect(20, SCREEN_HEIGHT - 80, TOUCH_BUTTON_SIZE, TOUCH_BUTTON_SIZE),
    "right": pygame.Rect(90, SCREEN_HEIGHT - 80, TOUCH_BUTTON_SIZE, TOUCH_BUTTON_SIZE),
    "pause": pygame.Rect(SCREEN_WIDTH - 50, 10, 40, 40),
}

def draw_touch_controls(surface):
    """Draw touch control buttons for mobile play (auto-shoot enabled)."""
    # Left button
    pygame.draw.rect(surface, (100, 100, 100), TOUCH_BUTTONS["left"], border_radius=10)
    pygame.draw.polygon(surface, WHITE, [
        (TOUCH_BUTTONS["left"].x + 40, TOUCH_BUTTONS["left"].y + 15),
        (TOUCH_BUTTONS["left"].x + 40, TOUCH_BUTTONS["left"].y + 45),
        (TOUCH_BUTTONS["left"].x + 15, TOUCH_BUTTONS["left"].y + 30),
    ])

    # Right button
    pygame.draw.rect(surface, (100, 100, 100), TOUCH_BUTTONS["right"], border_radius=10)
    pygame.draw.polygon(surface, WHITE, [
        (TOUCH_BUTTONS["right"].x + 20, TOUCH_BUTTONS["right"].y + 15),
        (TOUCH_BUTTONS["right"].x + 20, TOUCH_BUTTONS["right"].y + 45),
        (TOUCH_BUTTONS["right"].x + 45, TOUCH_BUTTONS["right"].y + 30),
    ])

    # Pause button
    pygame.draw.rect(surface, (80, 80, 80), TOUCH_BUTTONS["pause"], border_radius=8)
    pause_x = TOUCH_BUTTONS["pause"].x + 12
    pause_y = TOUCH_BUTTONS["pause"].y + 10
    pygame.draw.rect(surface, WHITE, (pause_x, pause_y, 6, 20))
    pygame.draw.rect(surface, WHITE, (pause_x + 10, pause_y, 6, 20))

def get_touch_input():
    """Get current touch/mouse button states (auto-shoot enabled)."""
    touch_state = {"left": False, "right": False, "pause": False}

    # Check mouse button held (for continuous movement)
    mouse_pressed = pygame.mouse.get_pressed()[0]
    if mouse_pressed:
        mouse_pos = pygame.mouse.get_pos()
        for button_name, button_rect in TOUCH_BUTTONS.items():
            if button_rect.collidepoint(mouse_pos):
                touch_state[button_name] = True

    return touch_state

async def username_entry_screen():
    """Screen for entering username at game start."""
    global current_username

    username = ""
    max_length = 15
    cursor_blink = 0
    error_message = ""

    # Check if there's a saved last user
    try:
        last_user = storage_get("dodge_lastuser")
        if last_user and last_user.strip() in leaderboard_data:
            username = last_user.strip()
    except:
        pass

    while True:
        cursor_blink += 1
        update_background()
        draw_background(screen, False)

        # Title
        draw_text_centered("DODGE THE TEJECKS", BIG_FONT, BLACK, 50)
        draw_text_centered("Enter Your Name", FONT, BLUE, 120)

        # Username input box
        box_width = 300
        box_height = 50
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = 180

        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), border_radius=10)
        pygame.draw.rect(screen, BLUE, (box_x, box_y, box_width, box_height), 3, border_radius=10)

        # Display username with blinking cursor
        cursor = "|" if (cursor_blink // 30) % 2 == 0 else ""
        display_text = username + cursor
        text_surface = FONT.render(display_text, True, BLACK)
        text_x = box_x + 15
        text_y = box_y + (box_height - text_surface.get_height()) // 2
        screen.blit(text_surface, (text_x, text_y))

        # Instructions
        draw_text_centered("Type your name and press ENTER", SMALL_FONT, BLACK, 260)
        draw_text_centered("Your progress will be saved automatically!", SMALL_FONT, GREEN, 290)

        # Error message
        if error_message:
            draw_text_centered(error_message, FONT, RED, 330)

        # Show existing players hint
        if leaderboard_data:
            draw_text_centered(f"({len(leaderboard_data)} players registered)", SMALL_FONT, PURPLE, 370)

        # Show keyboard hint for mobile
        draw_text_centered("Tap here to type on mobile", SMALL_FONT, (100, 100, 100), SCREEN_HEIGHT - 80)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(username.strip()) >= 2:
                        current_username = username.strip()
                        load_user_progress(current_username)
                        save_progress()  # Save immediately to store last user
                        play_sound(sound_powerup)
                        return
                    else:
                        error_message = "Name must be at least 2 characters!"
                        play_sound(sound_hit)
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                    error_message = ""
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif len(username) < max_length:
                    # Only allow alphanumeric and some special chars
                    if event.unicode.isalnum() or event.unicode in " _-":
                        username += event.unicode
                        error_message = ""
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Clicking the input box area (for mobile keyboard trigger)
                if box_x <= event.pos[0] <= box_x + box_width and box_y <= event.pos[1] <= box_y + box_height:
                    pass  # Input box clicked

        await asyncio.sleep(0)
        clock.tick(60)

async def leaderboard_screen():
    """Display the live leaderboard showing all players."""
    scroll_offset = 0
    max_display = 10
    loading_cloud = True
    cloud_loaded = False

    # Start loading from cloud in background
    async def load_cloud_data():
        nonlocal cloud_loaded
        await load_leaderboard_from_cloud()
        await sync_to_cloud()
        cloud_loaded = True

    # Create task to load cloud data
    cloud_task = asyncio.create_task(load_cloud_data())

    while True:
        update_background()
        draw_background(screen, False)

        # Title
        draw_text_centered("LEADERBOARD", BIG_FONT, BLACK, 30)

        # Show loading status
        if not cloud_loaded:
            draw_text_centered("Syncing with cloud...", SMALL_FONT, ORANGE, 55)

        # Current player info
        pygame.draw.rect(screen, (220, 240, 255), (20, 80, SCREEN_WIDTH - 40, 45), border_radius=10)
        pygame.draw.rect(screen, BLUE, (20, 80, SCREEN_WIDTH - 40, 45), 2, border_radius=10)
        draw_text(f"You: {current_username}", FONT, BLUE, 35, 90)
        draw_text(f"Points: {points}", FONT, GREEN, SCREEN_WIDTH - 180, 90)

        # Leaderboard header
        header_y = 140
        pygame.draw.rect(screen, (50, 50, 70), (20, header_y, SCREEN_WIDTH - 40, 35), border_radius=5)
        draw_text("Rank", SMALL_FONT, WHITE, 35, header_y + 8)
        draw_text("Player", SMALL_FONT, WHITE, 100, header_y + 8)
        draw_text("Points", SMALL_FONT, WHITE, 350, header_y + 8)
        draw_text("Best Level", SMALL_FONT, WHITE, 480, header_y + 8)
        draw_text("Playing", SMALL_FONT, WHITE, 620, header_y + 8)

        # Get sorted leaderboard
        sorted_lb = get_sorted_leaderboard()

        # Display leaderboard entries
        entry_y = header_y + 45
        for i, (username, data) in enumerate(sorted_lb[scroll_offset:scroll_offset + max_display]):
            rank = scroll_offset + i + 1
            row_y = entry_y + i * 40

            # Highlight current user
            if username == current_username:
                pygame.draw.rect(screen, (200, 255, 200), (20, row_y - 5, SCREEN_WIDTH - 40, 38), border_radius=5)
            elif i % 2 == 0:
                pygame.draw.rect(screen, (240, 240, 250), (20, row_y - 5, SCREEN_WIDTH - 40, 38), border_radius=5)

            # Rank with medal for top 3
            if rank == 1:
                draw_text("🥇", FONT, YELLOW, 35, row_y)
            elif rank == 2:
                draw_text("🥈", FONT, (192, 192, 192), 35, row_y)
            elif rank == 3:
                draw_text("🥉", FONT, (205, 127, 50), 35, row_y)
            else:
                draw_text(f"#{rank}", SMALL_FONT, BLACK, 35, row_y + 3)

            # Player name (truncate if too long)
            display_name = username[:12] + "..." if len(username) > 12 else username
            name_color = BLUE if username == current_username else BLACK
            draw_text(display_name, FONT, name_color, 100, row_y)

            # Points
            user_points = data.get("points", 0)
            draw_text(f"{user_points:,}", FONT, GREEN, 350, row_y)

            # Find highest unlocked level
            user_best_scores = data.get("best_scores", {})
            levels = ["Easy", "Medium", "Hard", "Impossible", "God Mode", "Creator Mode", "BOSS MODE"]
            highest_level = "Easy"
            for level in levels:
                if user_best_scores.get(level, 0) > 0:
                    highest_level = level

            # Shorten level name for display
            level_short = {
                "Easy": "Easy", "Medium": "Med", "Hard": "Hard",
                "Impossible": "Imp", "God Mode": "God",
                "Creator Mode": "Creator", "BOSS MODE": "BOSS"
            }
            level_color = PURPLE if highest_level in ["God Mode", "Creator Mode", "BOSS MODE"] else BLACK
            draw_text(level_short.get(highest_level, highest_level), SMALL_FONT, level_color, 480, row_y + 3)

            # Current level playing
            current = data.get("current_level", "Easy")
            draw_text(level_short.get(current, current), SMALL_FONT, ORANGE, 620, row_y + 3)

        # Scroll indicators
        if scroll_offset > 0:
            draw_text_centered("▲ UP for more", SMALL_FONT, BLACK, header_y + 45 + max_display * 40 + 10)
        if scroll_offset + max_display < len(sorted_lb):
            draw_text_centered("▼ DOWN for more", SMALL_FONT, BLACK, header_y + 45 + max_display * 40 + 30)

        # Footer
        total_players = len(leaderboard_data)
        draw_text_centered(f"Total Players: {total_players}", SMALL_FONT, PURPLE, SCREEN_HEIGHT - 70)
        draw_text_centered("Press B to return", FONT, BLACK, SCREEN_HEIGHT - 40)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b or event.key == pygame.K_ESCAPE:
                    play_sound(sound_collect)
                    return
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 1)
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(max(0, len(sorted_lb) - max_display), scroll_offset + 1)

        await asyncio.sleep(0)
        clock.tick(60)

async def pause_menu(game_points, level_name="Easy"):
    """Display pause menu."""
    global points, best_scores

    selected = 0
    options = ["Resume", "Quit to Menu"]

    while True:
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        # Draw pause box
        box_width = 250
        box_height = 200
        box_x = (SCREEN_WIDTH - box_width) // 2
        box_y = (SCREEN_HEIGHT - box_height) // 2
        pygame.draw.rect(screen, (50, 50, 70), (box_x, box_y, box_width, box_height), border_radius=15)
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_width, box_height), 3, border_radius=15)

        draw_text_centered("PAUSED", BIG_FONT, WHITE, box_y + 20)
        draw_text_centered(f"Score: {game_points}", FONT, YELLOW, box_y + 70)

        # Draw options
        for i, option in enumerate(options):
            y_pos = box_y + 110 + i * 40
            color = GREEN if i == selected else WHITE
            if i == selected:
                pygame.draw.rect(screen, (80, 80, 100), (box_x + 20, y_pos - 5, box_width - 40, 35), border_radius=8)
            draw_text_centered(option, FONT, color, y_pos)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                points += game_points
                if game_points > best_scores.get(level_name, 0):
                    best_scores[level_name] = game_points
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                    play_sound(sound_collect)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                    play_sound(sound_collect)
                elif event.key == pygame.K_RETURN:
                    play_sound(sound_powerup)
                    if selected == 0:  # Resume
                        return "resume"
                    else:  # Quit
                        points += game_points
                        if game_points > best_scores.get(level_name, 0):
                            best_scores[level_name] = game_points
                        save_progress()
                        return "quit"
                elif event.key == pygame.K_ESCAPE:
                    return "resume"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    y_pos = box_y + 110 + i * 40
                    option_rect = pygame.Rect(box_x + 20, y_pos - 5, box_width - 40, 35)
                    if option_rect.collidepoint(mouse_pos):
                        play_sound(sound_powerup)
                        if i == 0:  # Resume
                            return "resume"
                        else:  # Quit
                            points += game_points
                            if game_points > best_scores.get(level_name, 0):
                                best_scores[level_name] = game_points
                            save_progress()
                            return "quit"

        await asyncio.sleep(0)
        clock.tick(60)

def scale_position(x, y):
    return x * SCREEN_WIDTH // 360, y * SCREEN_HEIGHT // 640

def scale_size(width, height):
    return width * SCREEN_WIDTH // 360, height * SCREEN_HEIGHT // 640

# Menu button animation
menu_hover = -1
menu_animation = [0, 0, 0, 0, 0, 0]  # Added one more for leaderboard

async def main_menu():
    """Display the main menu."""
    global menu_animation
    title_offset = 0
    sync_timer = 0

    # Sync to cloud when entering main menu
    if CLOUD_ENABLED and cloud_sync_pending:
        await sync_to_cloud()

    while True:
        # Periodic cloud sync every 30 seconds
        sync_timer += 1
        if sync_timer >= 1800 and CLOUD_ENABLED:  # 30 seconds at 60fps
            sync_timer = 0
            if cloud_sync_pending:
                asyncio.create_task(sync_to_cloud())
        update_background()
        draw_background(screen, False)

        # Animated title
        title_offset += 0.05
        title_y = 50 + math.sin(title_offset) * 5
        draw_text("Dodge the Tejecks", BIG_FONT, BLACK, *scale_position(60, title_y))

        # Show current player
        draw_text(f"Player: {current_username}", FONT, BLUE, 10, 100)
        draw_text(f"Points: {points}", SMALL_FONT, GREEN, 10, 130)

        # Menu items with hover effect
        menu_items = ["1. PLAY", "2. SHOP", "3. LEADERBOARD", "4. INSTRUCTIONS", "5. CHANGELOG", "6. QUIT"]
        for i, item in enumerate(menu_items):
            y_pos = 180 + i * 45
            # Animate menu items
            menu_animation[i] = min(1, menu_animation[i] + 0.1)
            offset = (1 - menu_animation[i]) * 50
            color = BLUE if i == menu_hover else BLACK
            draw_text(item, FONT, color, scale_position(50, y_pos)[0] + offset, scale_position(50, y_pos)[1])

        # High score display
        draw_text(f"High Score: {high_score}", SMALL_FONT, PURPLE, 10, SCREEN_HEIGHT - 30)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                play_sound(sound_collect)
                if event.key == pygame.K_1:
                    await choose_difficulty()
                elif event.key == pygame.K_2:
                    await shop()
                elif event.key == pygame.K_3:
                    load_leaderboard()  # Refresh leaderboard data
                    await leaderboard_screen()
                elif event.key == pygame.K_4:
                    await instructions_screen()
                elif event.key == pygame.K_5:
                    await changelog_screen()
                elif event.key == pygame.K_6:
                    save_progress()
                    pygame.quit()
                    sys.exit()

        await asyncio.sleep(0)
        clock.tick(60)

async def instructions_screen():
    """Display the instructions screen."""
    while True:
        update_background()
        draw_background(screen, False)

        draw_text_centered("Instructions", BIG_FONT, BLACK, 50)

        instructions = [
            "CONTROLS:",
            "LEFT/RIGHT - Move player",
            "AUTO-SHOOT - Lasers fire automatically!",
            "",
            "POWER-UPS:",
            "$ Coin - Bonus points",
            "S Shield - Block one hit",
            "> Speed - Move faster",
            "~ Slow-Mo - Slow enemies",
            "M Magnet - Attract coins",
            "B Bomb - Clear all enemies!",
            "R Rapid - Fast shooting",
            "D Double - Dual lasers",
            "A Ammo - +10 laser ammo",
        ]

        for i, line in enumerate(instructions):
            color = BLUE if line.startswith("POWER") else BLACK
            draw_text(line, SMALL_FONT, color, 50, 120 + i * 35)

        draw_text_centered("Press B to return", FONT, BLACK, SCREEN_HEIGHT - 80)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    play_sound(sound_collect)
                    return

        await asyncio.sleep(0)
        clock.tick(60)

async def changelog_screen():
    """Display the changelog screen."""
    updates = [
        "Version 1.3:",
        "- SHOOT LASERS with SPACE bar!",
        "- Destroy enemies to earn bonus points!",
        "- New power-ups: Bomb, Rapid Fire, Double Shot!",
        "- Ammo system - collect ammo pickups!",
        "- Explosive visual effects!",
        "",
        "Version 1.2:",
        "- Added power-ups: Shield, Speed, Slow-Mo, Magnet!",
        "- Added coins to collect for bonus points!",
        "- Added sound effects!",
        "- Added visual effects and particles!",
        "- Added screen shake on collision!",
        "- Added animated background!",
        "- Added high score tracking!",
        "",
        "Version 1.1:",
        "- More Items in Shop.",
        "- New Difficulty Levels added",
        "- Implemented saving purchased items.",
        "",
        "Version 1.0:",
        "- Initial release with main gameplay.",
    ]

    scroll_offset = 0

    while True:
        update_background()
        draw_background(screen, False)

        draw_text_centered("Changelog", BIG_FONT, BLACK, 50)

        for i, line in enumerate(updates):
            y_pos = 120 + i * 30 - scroll_offset
            if 100 < y_pos < SCREEN_HEIGHT - 100:
                color = BLUE if line.startswith("Version") else BLACK
                draw_text(line, SMALL_FONT, color, 30, y_pos)

        draw_text_centered("UP/DOWN to scroll, B to return", FONT, BLACK, SCREEN_HEIGHT - 50)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    play_sound(sound_collect)
                    return
                elif event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 30)
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(len(updates) * 30 - 200, scroll_offset + 30)

        await asyncio.sleep(0)
        clock.tick(60)

async def choose_difficulty():
    """Choose difficulty screen."""
    selected = 0
    # Format: (name, speed, color)
    difficulties = [
        ("Easy", 3, GREEN),          # Slower speed (was 5)
        ("Medium", 6, YELLOW),       # Adjusted (was 10)
        ("Hard", 10, ORANGE),        # Adjusted (was 15)
        ("Impossible", 15, RED),     # Adjusted (was 30)
        ("God Mode", 25, PURPLE),    # Adjusted (was 100)
        ("Creator Mode", 35, BLACK), # Adjusted (was 150)
        ("BOSS MODE", -1, RED),      # Special boss mode
    ]

    # Level order for unlock checking
    level_order = ["Easy", "Medium", "Hard", "Impossible", "God Mode", "Creator Mode", "BOSS MODE"]

    while True:
        update_background()
        draw_background(screen, False)

        draw_text_centered("Choose Difficulty", BIG_FONT, BLACK, 50)

        for i, (name, speed, color) in enumerate(difficulties):
            y_pos = 130 + i * 55

            unlocked = is_level_unlocked(name)
            display_color = color if unlocked else (150, 150, 150)

            # Highlight selected
            if i == selected:
                pygame.draw.rect(screen, (*display_color[:3], 50) if len(display_color) == 3 else display_color, (50, y_pos - 5, SCREEN_WIDTH - 100, 48), border_radius=10)
                pygame.draw.rect(screen, display_color, (50, y_pos - 5, SCREEN_WIDTH - 100, 48), 3, border_radius=10)

            # Show level name
            if unlocked:
                draw_text(f"{i+1}. {name}", FONT, display_color, 80, y_pos + 8)
                # Show best score for this level
                if best_scores[name] > 0:
                    draw_text(f"Best: {best_scores[name]}", SMALL_FONT, GREEN, SCREEN_WIDTH - 120, y_pos + 10)
            else:
                draw_text(f"{i+1}. {name} [LOCKED]", FONT, display_color, 80, y_pos + 8)
                # Show requirement to unlock
                prev_level = level_order[i - 1] if i > 0 else "Easy"
                req = level_unlock_requirements[name]
                draw_text(f"Need {req} in {prev_level}", SMALL_FONT, (100, 100, 100), SCREEN_WIDTH - 180, y_pos + 10)

        draw_text_centered("UP/DOWN + ENTER or number key, B = back", SMALL_FONT, BLACK, SCREEN_HEIGHT - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(difficulties)
                    play_sound(sound_collect)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(difficulties)
                    play_sound(sound_collect)
                elif event.key == pygame.K_RETURN:
                    name = difficulties[selected][0]
                    if is_level_unlocked(name):
                        play_sound(sound_powerup)
                        if difficulties[selected][1] == -1:  # Boss mode
                            await boss_game_loop()
                        else:
                            await game_loop(difficulties[selected][1], name)
                    else:
                        play_sound(sound_hit)  # Locked sound
                elif event.key == pygame.K_1:
                    if is_level_unlocked("Easy"):
                        play_sound(sound_powerup)
                        await game_loop(3, "Easy")
                elif event.key == pygame.K_2:
                    if is_level_unlocked("Medium"):
                        play_sound(sound_powerup)
                        await game_loop(6, "Medium")
                    else:
                        play_sound(sound_hit)
                elif event.key == pygame.K_3:
                    if is_level_unlocked("Hard"):
                        play_sound(sound_powerup)
                        await game_loop(10, "Hard")
                    else:
                        play_sound(sound_hit)
                elif event.key == pygame.K_4:
                    if is_level_unlocked("Impossible"):
                        play_sound(sound_powerup)
                        await game_loop(15, "Impossible")
                    else:
                        play_sound(sound_hit)
                elif event.key == pygame.K_5:
                    if is_level_unlocked("God Mode"):
                        play_sound(sound_powerup)
                        await game_loop(25, "God Mode")
                    else:
                        play_sound(sound_hit)
                elif event.key == pygame.K_6:
                    if is_level_unlocked("Creator Mode"):
                        play_sound(sound_powerup)
                        await game_loop(35, "Creator Mode")
                    else:
                        play_sound(sound_hit)
                elif event.key == pygame.K_7:
                    if is_level_unlocked("BOSS MODE"):
                        play_sound(sound_powerup)
                        await boss_game_loop()
                    else:
                        play_sound(sound_hit)
                elif event.key == pygame.K_b:
                    play_sound(sound_collect)
                    return

        await asyncio.sleep(0)
        clock.tick(60)

async def shop():
    """Shop screen."""
    global points, equipped_item, selected_item

    # Error message for insufficient points
    error_message = ""
    error_timer = 0

    while True:
        update_background()
        draw_background(screen, False)

        # Decrement error timer
        if error_timer > 0:
            error_timer -= 1

        draw_text_centered("Shop", BIG_FONT, BLACK, 30)
        draw_text(f"Points: {points}", FONT, GREEN, 10, 80)
        draw_text(f"Equipped: {equipped_item}", FONT, BLUE, 10, 110)

        y_offset = 160
        for idx, (item_name, item_data) in enumerate(shop_items.items()):
            image = item_data["image"]
            purchased = item_data["purchased"]
            cost = item_data["cost"]
            status = "Equipped" if equipped_item == item_name else ("Purchased" if purchased else f"{cost} Points")

            # Highlight the selected item
            if idx == selected_item:
                pygame.draw.rect(screen, (200, 220, 255), (40, y_offset - 10, SCREEN_WIDTH - 80, 55), border_radius=8)
                pygame.draw.rect(screen, BLUE, (40, y_offset - 10, SCREEN_WIDTH - 80, 55), 2, border_radius=8)

            # Display item image
            scaled_image = pygame.transform.scale(image, (45, 45))
            screen.blit(scaled_image, (55, y_offset))

            # Display text
            status_color = GREEN if equipped_item == item_name else (BLUE if purchased else BLACK)
            draw_text(f"{item_name}", FONT, BLACK, 115, y_offset + 5)
            draw_text(status, SMALL_FONT, status_color, 115, y_offset + 30)

            y_offset += 65

        # Display error message popup if active
        if error_timer > 0 and error_message:
            # Draw popup box
            popup_width = 280
            popup_height = 60
            popup_x = (SCREEN_WIDTH - popup_width) // 2
            popup_y = SCREEN_HEIGHT // 2 - popup_height // 2
            pygame.draw.rect(screen, (50, 50, 50), (popup_x, popup_y, popup_width, popup_height), border_radius=10)
            pygame.draw.rect(screen, RED, (popup_x, popup_y, popup_width, popup_height), 3, border_radius=10)
            draw_text_centered(error_message, FONT, RED, popup_y + 18)

        draw_text_centered("UP/DOWN to select, ENTER to buy/equip, B to return", SMALL_FONT, BLACK, SCREEN_HEIGHT - 40)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(shop_items)
                    play_sound(sound_collect)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(shop_items)
                    play_sound(sound_collect)
                elif event.key == pygame.K_RETURN:
                    selected_item_name = list(shop_items.keys())[selected_item]
                    selected_item_data = shop_items[selected_item_name]
                    if not selected_item_data["purchased"]:
                        if points >= selected_item_data["cost"]:
                            points -= selected_item_data["cost"]
                            selected_item_data["purchased"] = True
                            play_sound(sound_powerup)
                        else:
                            # Not enough points - show error
                            needed = selected_item_data["cost"] - points
                            error_message = f"Not Enough Money! Need {needed} More"
                            error_timer = 120  # Show for 2 seconds
                            play_sound(sound_hit)
                    if selected_item_data["purchased"]:
                        equipped_item = selected_item_name
                        play_sound(sound_collect)
                    save_progress()
                elif event.key == pygame.K_b:
                    play_sound(sound_collect)
                    return

        await asyncio.sleep(0)
        clock.tick(60)

async def game_loop(difficulty, level_name="Easy"):
    """Main game loop with power-ups, lasers, and effects."""
    global points, high_score, screen_shake, shake_intensity, best_scores, current_level

    # Track current level for leaderboard
    current_level = level_name
    save_progress()  # Save that we're playing this level

    game_points = 0
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = SCREEN_HEIGHT - 100
    base_player_speed = 12  # Slightly faster player for easier dodging
    player_speed = base_player_speed
    diamond_speed = difficulty
    enemies = []  # Now using Enemy class with random images/sizes
    power_ups = []
    particles = []
    lasers = []
    explosions = []

    # Power-up states
    shields = 0  # Lives system: 0-5 shields (permanent until hit)
    max_shields = 5
    speed_boost_active = 0
    slowmo_active = 0
    magnet_active = 0
    rapid_fire_active = 0
    double_shot_active = 0

    # Laser/shooting system
    laser_cooldown = 0
    base_cooldown = 15  # Frames between shots
    laser_ammo = 10  # Starting ammo
    max_ammo = 30
    enemies_destroyed = 0

    # Combo system
    combo = 0
    combo_timer = 0

    # Animation
    player_bob = 0
    dodge_streak = 0

    # Auto-save timer (save every 30 seconds = 1800 frames at 60fps)
    auto_save_timer = 0

    while True:
        # Auto-save progress periodically
        auto_save_timer += 1
        if auto_save_timer >= 1800:  # Every 30 seconds
            auto_save_timer = 0
            # Update best score for this level
            if game_points > best_scores.get(level_name, 0):
                best_scores[level_name] = game_points
            save_progress()

        # Update background
        update_background()

        # Apply screen shake
        shake_x, shake_y = apply_screen_shake()

        # Create offset surface for shake effect
        draw_background(screen, True)

        # Update power-up timers (shields are permanent lives, not timed)
        if speed_boost_active > 0:
            speed_boost_active -= 1
            player_speed = base_player_speed * 1.5
        else:
            player_speed = base_player_speed
        if slowmo_active > 0:
            slowmo_active -= 1
            current_diamond_speed = diamond_speed * 0.4
        else:
            current_diamond_speed = diamond_speed
        if magnet_active > 0:
            magnet_active -= 1
        if rapid_fire_active > 0:
            rapid_fire_active -= 1
        if double_shot_active > 0:
            double_shot_active -= 1
        if laser_cooldown > 0:
            laser_cooldown -= 1

        # Combo timer
        if combo_timer > 0:
            combo_timer -= 1
        else:
            combo = 0

        # Player bobbing animation
        player_bob += 0.15
        bob_offset = math.sin(player_bob) * 3

        # Load and draw the equipped player's image
        player_image = shop_items[equipped_item]["image"]
        player_image = pygame.transform.scale(player_image, (50, 50))
        player_draw_x = player_x + shake_x
        player_draw_y = player_y + bob_offset + shake_y
        screen.blit(player_image, (player_draw_x, player_draw_y))

        # Draw shield effect (permanent shield aura when shields > 0)
        if shields > 0:
            pygame.draw.circle(screen, CYAN, (int(player_x + 25), int(player_y + 25 + bob_offset)), 35, 3)
            # Pulsing effect
            pulse = int(5 * math.sin(pygame.time.get_ticks() / 150))
            pygame.draw.circle(screen, CYAN, (int(player_x + 25), int(player_y + 25 + bob_offset)), 38 + pulse, 2)

        # Update and draw enemies (random characters with random sizes)
        for enemy in enemies[:]:
            enemy.update(current_diamond_speed)
            if enemy.is_off_screen():
                enemies.remove(enemy)
                game_points += 1 + combo
                dodge_streak += 1
                combo = min(combo + 1, 10)
                combo_timer = 60

                # Play dodge sound occasionally
                if dodge_streak % 5 == 0:
                    play_sound(sound_dodge)

                # Spawn particles for successful dodge
                if dodge_streak % 10 == 0:
                    for _ in range(5):
                        particles.append(Particle(player_x + 25, player_y, GREEN))
            else:
                enemy.draw(screen, shake_x, shake_y)

        # Spawn new enemies (random character, random size)
        # Easy: ~3 per second (0.05), harder levels spawn more
        if difficulty <= 3:
            spawn_rate = 0.05  # Easy: about 3 per second at 60fps
        elif difficulty <= 6:
            spawn_rate = 0.06  # Medium
        elif difficulty <= 10:
            spawn_rate = 0.07  # Hard
        elif difficulty <= 15:
            spawn_rate = 0.08  # Impossible
        elif difficulty <= 25:
            spawn_rate = 0.10  # God Mode
        else:
            spawn_rate = 0.12  # Creator Mode
        if random.random() < spawn_rate:
            enemy_x = random.randint(50, SCREEN_WIDTH - 50)
            enemies.append(Enemy(enemy_x))

        # Update and draw lasers
        for laser in lasers[:]:
            laser.update()
            if laser.is_off_screen():
                lasers.remove(laser)
                continue
            laser.draw(screen)

            # Check laser collision with enemies
            laser_rect = laser.get_rect()
            for enemy in enemies[:]:
                if laser_rect.colliderect(enemy.get_rect()):
                    # Destroy enemy
                    enemies.remove(enemy)
                    if laser in lasers:
                        lasers.remove(laser)
                    enemies_destroyed += 1
                    game_points += 3 + combo
                    play_sound(sound_explosion)
                    trigger_screen_shake(3, 3)
                    # Explosion particles
                    for _ in range(15):
                        particles.append(Particle(enemy.x, enemy.y, ORANGE))
                    break

        # Update and draw explosions
        for explosion in explosions[:]:
            explosion.update()
            explosion.draw(screen)
            if not explosion.active:
                explosions.remove(explosion)

        # Spawn power-ups occasionally
        if random.random() < 0.01:
            power_type = random.choices(
                ['coin', 'shield', 'speed', 'slowmo', 'magnet', 'bomb', 'rapid', 'double', 'ammo'],
                weights=[40, 12, 12, 8, 8, 5, 5, 5, 5]
            )[0]
            power_x = random.randint(50, SCREEN_WIDTH - 50)
            power_ups.append(PowerUp(power_x, -30, power_type))

        # Update and draw power-ups
        for power in power_ups[:]:
            power.update(current_diamond_speed)

            # Magnet effect
            if magnet_active > 0 and power.type == 'coin':
                dx = (player_x + 25) - power.x
                dy = (player_y + 25) - power.y
                dist = math.sqrt(dx*dx + dy*dy)
                if dist > 0 and dist < 200:
                    power.x += dx / dist * 5
                    power.y += dy / dist * 5

            if power.y > SCREEN_HEIGHT:
                power_ups.remove(power)
                continue

            power.draw(screen)

            # Check collision with player
            player_rect = pygame.Rect(player_x, player_y, 50, 50)
            if player_rect.colliderect(power.get_rect()):
                play_sound(sound_powerup)

                # Apply power-up effect
                if power.type == 'coin':
                    game_points += 5 * (1 + combo // 2)
                    for _ in range(10):
                        particles.append(Particle(power.x, power.y, YELLOW))
                elif power.type == 'shield':
                    if shields < max_shields:
                        shields += 1  # Add a shield (life), max 5
                    for _ in range(15):
                        particles.append(Particle(power.x, power.y, CYAN))
                elif power.type == 'speed':
                    speed_boost_active = PowerUp.TYPES['speed']['duration']
                    for _ in range(15):
                        particles.append(Particle(power.x, power.y, GREEN))
                elif power.type == 'slowmo':
                    slowmo_active = PowerUp.TYPES['slowmo']['duration']
                    for _ in range(15):
                        particles.append(Particle(power.x, power.y, PURPLE))
                elif power.type == 'magnet':
                    magnet_active = PowerUp.TYPES['magnet']['duration']
                    for _ in range(15):
                        particles.append(Particle(power.x, power.y, ORANGE))
                elif power.type == 'bomb':
                    # Clear all enemies on screen!
                    play_sound(sound_bomb)
                    trigger_screen_shake(20, 15)
                    for enemy in enemies:
                        explosions.append(Explosion(enemy.x, enemy.y))
                        game_points += 2
                        for _ in range(8):
                            particles.append(Particle(enemy.x, enemy.y, RED))
                    enemies_destroyed += len(enemies)
                    enemies.clear()
                    for _ in range(20):
                        particles.append(Particle(power.x, power.y, RED))
                elif power.type == 'rapid':
                    rapid_fire_active = PowerUp.TYPES['rapid']['duration']
                    for _ in range(15):
                        particles.append(Particle(power.x, power.y, (255, 100, 100)))
                elif power.type == 'double':
                    double_shot_active = PowerUp.TYPES['double']['duration']
                    for _ in range(15):
                        particles.append(Particle(power.x, power.y, (100, 100, 255)))
                elif power.type == 'ammo':
                    laser_ammo = min(max_ammo, laser_ammo + 10)
                    for _ in range(10):
                        particles.append(Particle(power.x, power.y, WHITE))

                power_ups.remove(power)

        # Check for collisions with enemies
        player_rect = pygame.Rect(player_x + 5, player_y + 5, 40, 40)  # Slightly smaller hitbox
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                if shields > 0:
                    # Shield blocks the hit - lose 1 life
                    shields -= 1
                    enemies.remove(enemy)
                    trigger_screen_shake(5, 5)
                    play_sound(sound_hit)
                    for _ in range(20):
                        particles.append(Particle(enemy.x, enemy.y, CYAN))
                else:
                    # No shields left - Game over
                    play_sound(sound_hit)
                    trigger_screen_shake(15, 20)

                    # Explosion particles
                    for _ in range(30):
                        particles.append(Particle(player_x + 25, player_y + 25, RED))

                    points += game_points
                    if game_points > high_score:
                        high_score = game_points
                    # Update best score for this level
                    if game_points > best_scores.get(level_name, 0):
                        best_scores[level_name] = game_points
                    save_progress()
                    await game_over(game_points, combo)
                    return

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.is_dead():
                particles.remove(particle)

        # Draw UI
        # Score panel
        pygame.draw.rect(screen, (0, 0, 0, 100), (5, 5, 200, 115), border_radius=10)
        pygame.draw.rect(screen, WHITE, (5, 5, 200, 115), 2, border_radius=10)
        draw_text(f"Score: {game_points}", FONT, WHITE, 15, 15)
        draw_text(f"Total: {points}", SMALL_FONT, (200, 200, 200), 15, 45)
        if combo > 0:
            draw_text(f"Combo: x{combo + 1}", SMALL_FONT, YELLOW, 15, 70)

        # Ammo display
        ammo_color = RED if laser_ammo <= 3 else (WHITE if laser_ammo < 10 else GREEN)
        draw_text(f"Ammo: {laser_ammo}/{max_ammo}", SMALL_FONT, ammo_color, 15, 95)

        # Destroyed counter
        draw_text(f"Destroyed: {enemies_destroyed}", SMALL_FONT, ORANGE, SCREEN_WIDTH - 150, SCREEN_HEIGHT - 30)

        # Shield/Lives display (prominent top center)
        lives_y = 10
        # Background box for lives
        lives_box_width = 180
        lives_box_x = (SCREEN_WIDTH - lives_box_width) // 2
        pygame.draw.rect(screen, (30, 30, 50), (lives_box_x, lives_y - 5, lives_box_width, 40), border_radius=10)
        pygame.draw.rect(screen, CYAN if shields > 0 else RED, (lives_box_x, lives_y - 5, lives_box_width, 40), 2, border_radius=10)

        # Draw shield/heart icons
        for i in range(max_shields):
            icon_x = lives_box_x + 20 + i * 32
            if i < shields:
                # Filled heart/shield icon
                pygame.draw.circle(screen, CYAN, (icon_x, lives_y + 15), 12)
                pygame.draw.circle(screen, WHITE, (icon_x, lives_y + 15), 8)
            else:
                # Empty heart/shield icon
                pygame.draw.circle(screen, (80, 80, 80), (icon_x, lives_y + 15), 12, 2)

        # Power-up status indicators
        status_x = SCREEN_WIDTH - 120
        status_y = 60  # Moved down to avoid pause button
        if speed_boost_active > 0:
            pygame.draw.rect(screen, GREEN, (status_x, status_y, 110, 25), border_radius=5)
            draw_text(f"Speed: {speed_boost_active // 60 + 1}s", SMALL_FONT, BLACK, status_x + 5, status_y + 3)
            status_y += 30
        if slowmo_active > 0:
            pygame.draw.rect(screen, PURPLE, (status_x, status_y, 110, 25), border_radius=5)
            draw_text(f"Slow: {slowmo_active // 60 + 1}s", SMALL_FONT, WHITE, status_x + 5, status_y + 3)
            status_y += 30
        if magnet_active > 0:
            pygame.draw.rect(screen, ORANGE, (status_x, status_y, 110, 25), border_radius=5)
            draw_text(f"Magnet: {magnet_active // 60 + 1}s", SMALL_FONT, BLACK, status_x + 5, status_y + 3)
            status_y += 30
        if rapid_fire_active > 0:
            pygame.draw.rect(screen, (255, 100, 100), (status_x, status_y, 110, 25), border_radius=5)
            draw_text(f"Rapid: {rapid_fire_active // 60 + 1}s", SMALL_FONT, WHITE, status_x + 5, status_y + 3)
            status_y += 30
        if double_shot_active > 0:
            pygame.draw.rect(screen, (100, 100, 255), (status_x, status_y, 110, 25), border_radius=5)
            draw_text(f"Double: {double_shot_active // 60 + 1}s", SMALL_FONT, WHITE, status_x + 5, status_y + 3)

        # Draw touch controls for mobile
        draw_touch_controls(screen)

        pygame.display.flip()

        # Handle pause button click
        pause_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                points += game_points
                # Update best score for this level
                if game_points > best_scores.get(level_name, 0):
                    best_scores[level_name] = game_points
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_clicked = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if TOUCH_BUTTONS["pause"].collidepoint(event.pos):
                    pause_clicked = True

        # Handle pause
        if pause_clicked:
            result = await pause_menu(game_points, level_name)
            if result == "quit":
                return

        # Get touch input
        touch = get_touch_input()

        # Handle player movement and shooting (keyboard + touch)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or touch["left"]) and player_x > 0:
            player_x -= player_speed
        if (keys[pygame.K_RIGHT] or touch["right"]) and player_x < SCREEN_WIDTH - 50:
            player_x += player_speed

        # Auto-shoot - automatically fires when cooldown is ready and has ammo
        if laser_cooldown <= 0 and laser_ammo > 0:
            play_sound(sound_laser)
            laser_ammo -= 1

            # Determine cooldown based on rapid fire
            if rapid_fire_active > 0:
                laser_cooldown = base_cooldown // 3
            else:
                laser_cooldown = base_cooldown

            # Create laser(s)
            laser_x = player_x + 25
            laser_y = player_y - 10

            if double_shot_active > 0:
                # Double shot - two lasers side by side
                lasers.append(Laser(laser_x - 15, laser_y, (255, 100, 100)))
                lasers.append(Laser(laser_x + 15, laser_y, (255, 100, 100)))
                # Double shot uses extra ammo
                if laser_ammo > 0:
                    laser_ammo -= 1
            else:
                lasers.append(Laser(laser_x, laser_y, RED))

        clock.tick(60)
        await asyncio.sleep(0)

async def game_over(score, max_combo):
    """Display the game over screen with stats."""
    global high_score

    # Load the game over image
    try:
        game_over_image = pygame.image.load("game_over.jpeg")
        game_over_image = pygame.transform.scale(game_over_image, (200, 200))
    except pygame.error:
        game_over_image = None

    animation_timer = 0

    while True:
        animation_timer += 1
        update_background()
        draw_background(screen, False)

        # Animated title
        title_scale = 1 + 0.05 * math.sin(animation_timer * 0.1)
        draw_text_centered("CAUGHT BY VEGETARIAN!", BIG_FONT, RED, 50)

        # Stats box
        box_y = 120
        pygame.draw.rect(screen, (240, 240, 255), (SCREEN_WIDTH // 2 - 150, box_y, 300, 150), border_radius=15)
        pygame.draw.rect(screen, BLUE, (SCREEN_WIDTH // 2 - 150, box_y, 300, 150), 3, border_radius=15)

        draw_text_centered(f"Score: {score}", FONT, BLACK, box_y + 20)
        draw_text_centered(f"Best Combo: x{max_combo + 1}", SMALL_FONT, PURPLE, box_y + 60)

        if score >= high_score and score > 0:
            # New high score animation
            if animation_timer % 30 < 15:
                draw_text_centered("NEW HIGH SCORE!", FONT, YELLOW, box_y + 100)
        else:
            draw_text_centered(f"High Score: {high_score}", SMALL_FONT, GREEN, box_y + 100)

        # Draw the game over image
        if game_over_image:
            img_x = (SCREEN_WIDTH - 200) // 2
            screen.blit(game_over_image, (img_x, 290))

        draw_text_centered("Press ENTER to continue", FONT, BLACK, SCREEN_HEIGHT - 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play_sound(sound_collect)
                    return

        await asyncio.sleep(0)
        clock.tick(60)

async def boss_game_loop():
    """BOSS MODE - Fight the FINAL VIRTUAL EMDR TEJECK BOSS!"""
    global points, high_score, screen_shake, shake_intensity, best_scores, current_level

    # Track current level for leaderboard
    current_level = "BOSS MODE"
    save_progress()  # Save that we're playing boss mode

    game_points = 0
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = SCREEN_HEIGHT - 100
    player_speed = 12  # Faster movement for boss fight
    enemies = []
    particles = []
    lasers = []
    fires = []  # Boss fire projectiles
    explosions = []

    # Create the boss
    boss = Boss()

    # Player states
    shields = 0  # Lives system: 0-5 shields
    max_shields = 5
    speed_boost_active = 0
    rapid_fire_active = 0
    double_shot_active = 0

    # Laser system - more ammo for boss fight
    laser_cooldown = 0
    base_cooldown = 12
    laser_ammo = 30
    max_ammo = 50

    # Animation
    player_bob = 0
    boss_defeated = False

    # Auto-save timer (save every 30 seconds = 1800 frames at 60fps)
    auto_save_timer = 0

    while True:
        # Auto-save progress periodically
        auto_save_timer += 1
        if auto_save_timer >= 1800:  # Every 30 seconds
            auto_save_timer = 0
            # Update best score for boss mode
            if game_points > best_scores.get("BOSS MODE", 0):
                best_scores["BOSS MODE"] = game_points
            save_progress()

        update_background()
        shake_x, shake_y = apply_screen_shake()

        # Limit list sizes to prevent memory issues
        while len(particles) > 100:
            particles.pop(0)
        while len(fires) > 50:
            fires.pop(0)
        while len(enemies) > 30:
            enemies.pop(0)
        while len(lasers) > 20:
            lasers.pop(0)
        while len(explosions) > 10:
            explosions.pop(0)

        # Dark red tinted background for boss fight
        for y in range(0, SCREEN_HEIGHT, 4):
            ratio = y / SCREEN_HEIGHT
            color = (int(80 + 40 * ratio), int(20 + 20 * ratio), int(40 + 30 * ratio))
            pygame.draw.rect(screen, color, (0, y, SCREEN_WIDTH, 4))

        # Update power-up timers (shields are permanent lives, not timed)
        if speed_boost_active > 0:
            speed_boost_active -= 1
        if rapid_fire_active > 0:
            rapid_fire_active -= 1
        if double_shot_active > 0:
            double_shot_active -= 1
        if laser_cooldown > 0:
            laser_cooldown -= 1

        current_speed = player_speed * 1.5 if speed_boost_active > 0 else player_speed

        # Player bobbing
        player_bob += 0.15
        bob_offset = math.sin(player_bob) * 3

        # Draw player
        player_image = shop_items[equipped_item]["image"]
        player_image = pygame.transform.scale(player_image, (50, 50))
        screen.blit(player_image, (player_x + shake_x, player_y + bob_offset + shake_y))

        # Draw shield effect (permanent shield aura when shields > 0)
        if shields > 0:
            pygame.draw.circle(screen, CYAN, (int(player_x + 25), int(player_y + 25 + bob_offset)), 35, 3)
            pulse = int(5 * math.sin(pygame.time.get_ticks() / 150))
            pygame.draw.circle(screen, CYAN, (int(player_x + 25), int(player_y + 25 + bob_offset)), 38 + pulse, 2)

        # Update and draw boss
        boss.update()
        boss.draw(screen)

        # Boss fires at player
        if boss.should_fire() and not boss_defeated:
            play_sound(sound_explosion)
            # Fire pattern based on phase
            if boss.phase == 1:
                fires.append(Fire(boss.x, boss.y + 75, player_x + 25, player_y + 25))
            elif boss.phase == 2:
                # Spread shot
                fires.append(Fire(boss.x - 30, boss.y + 75, player_x + 25, player_y + 25))
                fires.append(Fire(boss.x + 30, boss.y + 75, player_x + 25, player_y + 25))
            else:
                # Phase 3 - crazy fire
                for angle in [-30, 0, 30]:
                    target_x = player_x + 25 + angle * 5
                    fires.append(Fire(boss.x, boss.y + 75, target_x, player_y + 25, speed=10))

        # Update and draw fires
        for fire in fires[:]:
            fire.update()
            if fire.is_dead():
                fires.remove(fire)
                continue
            fire.draw(screen)

            # Check fire collision with player
            player_rect = pygame.Rect(player_x + 5, player_y + 5, 40, 40)
            if player_rect.colliderect(fire.get_rect()):
                if shields > 0:
                    # Shield blocks the hit - lose 1 life
                    shields -= 1
                    fires.remove(fire)
                    trigger_screen_shake(5, 5)
                    play_sound(sound_hit)
                    for _ in range(15):
                        particles.append(Particle(fire.x, fire.y, CYAN))
                else:
                    # No shields left - Game over
                    play_sound(sound_hit)
                    trigger_screen_shake(15, 20)
                    for _ in range(30):
                        particles.append(Particle(player_x + 25, player_y + 25, RED))
                    points += game_points
                    # Update best score for boss mode
                    if game_points > best_scores.get("BOSS MODE", 0):
                        best_scores["BOSS MODE"] = game_points
                    save_progress()
                    await game_over(game_points, 0)
                    return

        # Spawn smaller enemies occasionally
        if random.random() < 0.02:
            enemy_x = random.randint(50, SCREEN_WIDTH - 50)
            enemies.append(Enemy(enemy_x))

        # Update and draw enemies
        for enemy in enemies[:]:
            enemy.update(8)  # Fixed speed for boss mode
            if enemy.is_off_screen():
                enemies.remove(enemy)
                game_points += 1
            else:
                enemy.draw(screen, shake_x, shake_y)

        # Update and draw lasers
        for laser in lasers[:]:
            laser.update()
            if laser.is_off_screen():
                lasers.remove(laser)
                continue
            laser.draw(screen)

            # Check laser collision with boss
            if laser.get_rect().colliderect(boss.get_rect()):
                lasers.remove(laser)
                if boss.take_damage(2):
                    # Boss defeated!
                    boss_defeated = True
                    play_sound(sound_bomb)
                    trigger_screen_shake(30, 30)
                    # Big explosion
                    for _ in range(50):
                        particles.append(Particle(boss.x, boss.y, random.choice([RED, ORANGE, YELLOW])))
                    game_points += 10000  # Big reward for defeating the boss!
                    points += game_points
                    if game_points > high_score:
                        high_score = game_points
                    save_progress()
                    await victory_screen(game_points)
                    return
                else:
                    play_sound(sound_hit)
                    trigger_screen_shake(3, 3)
                    for _ in range(8):
                        particles.append(Particle(laser.x, laser.y, ORANGE))
                continue

            # Check laser collision with enemies (skip PowerUps)
            for enemy in enemies[:]:
                if isinstance(enemy, PowerUp):
                    continue  # Lasers pass through power-ups
                if laser.get_rect().colliderect(enemy.get_rect()):
                    enemies.remove(enemy)
                    if laser in lasers:
                        lasers.remove(laser)
                    game_points += 3
                    play_sound(sound_explosion)
                    for _ in range(10):
                        particles.append(Particle(enemy.x, enemy.y, ORANGE))
                    break

        # Check player collision with enemies and power-ups
        player_rect = pygame.Rect(player_x + 5, player_y + 5, 40, 40)
        for enemy in enemies[:]:
            if player_rect.colliderect(enemy.get_rect()):
                # Check if it's a power-up
                if isinstance(enemy, PowerUp):
                    enemies.remove(enemy)
                    play_sound(sound_powerup)
                    # Apply power-up effect
                    if enemy.type == 'shield':
                        if shields < max_shields:
                            shields += 1  # Add a shield (life), max 5
                    elif enemy.type == 'speed':
                        speed_boost_active = 300
                    elif enemy.type == 'rapid':
                        rapid_fire_active = 300
                    elif enemy.type == 'double':
                        double_shot_active = 400
                    elif enemy.type == 'ammo':
                        laser_ammo = min(max_ammo, laser_ammo + 10)
                    for _ in range(10):
                        particles.append(Particle(enemy.x, enemy.y, CYAN))
                elif shields > 0:
                    # Shield blocks the hit - lose 1 life
                    shields -= 1
                    enemies.remove(enemy)
                    trigger_screen_shake(5, 5)
                    play_sound(sound_hit)
                else:
                    # No shields left - Game over
                    play_sound(sound_hit)
                    trigger_screen_shake(15, 20)
                    for _ in range(30):
                        particles.append(Particle(player_x + 25, player_y + 25, RED))
                    points += game_points
                    # Update best score for boss mode
                    if game_points > best_scores.get("BOSS MODE", 0):
                        best_scores["BOSS MODE"] = game_points
                    save_progress()
                    await game_over(game_points, 0)
                    return

        # Spawn power-ups occasionally
        if random.random() < 0.015:
            power_type = random.choices(
                ['shield', 'speed', 'rapid', 'double', 'ammo'],
                weights=[20, 15, 20, 20, 25]
            )[0]
            power_x = random.randint(50, SCREEN_WIDTH - 50)
            # Create a simple power-up (reusing PowerUp class)
            power = PowerUp(power_x, -30, power_type)
            enemies.append(power)  # Using enemies list for simplicity

        # Update and draw particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.is_dead():
                particles.remove(particle)

        # Update explosions
        for explosion in explosions[:]:
            explosion.update()
            explosion.draw(screen)
            if not explosion.active:
                explosions.remove(explosion)

        # Draw UI
        pygame.draw.rect(screen, (30, 30, 30), (5, SCREEN_HEIGHT - 80, 200, 75), border_radius=10)
        draw_text(f"Score: {game_points}", FONT, WHITE, 15, SCREEN_HEIGHT - 75)
        ammo_color = RED if laser_ammo <= 5 else GREEN
        draw_text(f"Ammo: {laser_ammo}/{max_ammo}", SMALL_FONT, ammo_color, 15, SCREEN_HEIGHT - 45)

        # Lives/Shields display (bottom left, below score)
        lives_y = SCREEN_HEIGHT - 35
        lives_box_width = 180
        lives_box_x = 220  # Next to score panel
        pygame.draw.rect(screen, (30, 30, 50), (lives_box_x, lives_y - 10, lives_box_width, 35), border_radius=8)
        pygame.draw.rect(screen, CYAN if shields > 0 else RED, (lives_box_x, lives_y - 10, lives_box_width, 35), 2, border_radius=8)

        for i in range(max_shields):
            icon_x = lives_box_x + 20 + i * 32
            if i < shields:
                pygame.draw.circle(screen, CYAN, (icon_x, lives_y + 5), 10)
                pygame.draw.circle(screen, WHITE, (icon_x, lives_y + 5), 6)
            else:
                pygame.draw.circle(screen, (80, 80, 80), (icon_x, lives_y + 5), 10, 2)

        # Power-up indicators
        status_y = SCREEN_HEIGHT - 75
        if rapid_fire_active > 0:
            draw_text(f"Rapid!", SMALL_FONT, (255, 100, 100), 120, status_y)

        # Draw touch controls for mobile
        draw_touch_controls(screen)

        pygame.display.flip()

        # Event handling
        pause_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                points += game_points
                # Update best score for boss mode
                if game_points > best_scores.get("BOSS MODE", 0):
                    best_scores["BOSS MODE"] = game_points
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_clicked = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if TOUCH_BUTTONS["pause"].collidepoint(event.pos):
                    pause_clicked = True

        # Handle pause
        if pause_clicked:
            result = await pause_menu(game_points, "BOSS MODE")
            if result == "quit":
                return

        # Get touch input
        touch = get_touch_input()

        # Movement (keyboard + touch)
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or touch["left"]) and player_x > 0:
            player_x -= current_speed
        if (keys[pygame.K_RIGHT] or touch["right"]) and player_x < SCREEN_WIDTH - 50:
            player_x += current_speed

        # Auto-shoot - automatically fires when cooldown is ready and has ammo
        if laser_cooldown <= 0 and laser_ammo > 0:
            play_sound(sound_laser)
            laser_ammo -= 1
            laser_cooldown = base_cooldown // 3 if rapid_fire_active > 0 else base_cooldown

            laser_x = player_x + 25
            laser_y = player_y - 10

            if double_shot_active > 0:
                lasers.append(Laser(laser_x - 15, laser_y, (255, 100, 100)))
                lasers.append(Laser(laser_x + 15, laser_y, (255, 100, 100)))
                if laser_ammo > 0:
                    laser_ammo -= 1
            else:
                lasers.append(Laser(laser_x, laser_y, RED))

        clock.tick(60)
        await asyncio.sleep(0)

async def victory_screen(score):
    """Display victory screen after defeating the boss!"""
    animation_timer = 0

    while True:
        animation_timer += 1
        update_background()

        # Victory background - golden
        for y in range(0, SCREEN_HEIGHT, 4):
            ratio = y / SCREEN_HEIGHT
            r = int(255 - 50 * ratio)
            g = int(215 - 50 * ratio)
            b = int(0 + 50 * ratio)
            pygame.draw.rect(screen, (r, g, b), (0, y, SCREEN_WIDTH, 4))

        # Fireworks particles
        if animation_timer % 10 == 0:
            for _ in range(5):
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 200)
                color = random.choice([RED, YELLOW, GREEN, CYAN, PURPLE, ORANGE])
                # We'd need to maintain a particle list here, but for simplicity:
                pygame.draw.circle(screen, color, (x, y), random.randint(5, 15))

        # Victory text with animation
        scale = 1 + 0.1 * math.sin(animation_timer * 0.1)
        draw_text_centered("VICTORY!", BIG_FONT, YELLOW, 80)
        draw_text_centered("You defeated the", FONT, WHITE, 150)
        draw_text_centered("FINAL VIRTUAL EMDR TEJECK BOSS!", FONT, RED, 190)

        # Score box
        box_y = 260
        pygame.draw.rect(screen, (50, 50, 50), (SCREEN_WIDTH // 2 - 150, box_y, 300, 120), border_radius=15)
        pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH // 2 - 150, box_y, 300, 120), 3, border_radius=15)

        draw_text_centered(f"Final Score: {score}", FONT, WHITE, box_y + 20)
        draw_text_centered("BOSS DEFEATED!", FONT, GREEN, box_y + 60)

        # Animated stars
        for i in range(5):
            star_x = 150 + i * 120
            star_y = 450 + math.sin(animation_timer * 0.1 + i) * 10
            pygame.draw.polygon(screen, YELLOW, [
                (star_x, star_y - 20),
                (star_x + 7, star_y - 7),
                (star_x + 20, star_y - 7),
                (star_x + 10, star_y + 3),
                (star_x + 14, star_y + 20),
                (star_x, star_y + 10),
                (star_x - 14, star_y + 20),
                (star_x - 10, star_y + 3),
                (star_x - 20, star_y - 7),
                (star_x - 7, star_y - 7),
            ])

        draw_text_centered("Press ENTER to continue", FONT, WHITE, SCREEN_HEIGHT - 60)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play_sound(sound_powerup)
                    return

        await asyncio.sleep(0)
        clock.tick(60)

async def main():
    """Main entry point for the game."""
    # Load local leaderboard data first
    load_leaderboard()

    # Also load from cloud to get latest data
    if CLOUD_ENABLED:
        await load_leaderboard_from_cloud()

    # Show username entry screen
    await username_entry_screen()

    # Sync current user's data to cloud after login
    if CLOUD_ENABLED:
        await sync_to_cloud()

    # Now user is logged in, show main menu
    await main_menu()

if __name__ == "__main__":
    asyncio.run(main())
