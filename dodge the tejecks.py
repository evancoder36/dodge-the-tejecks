import pygame
import random
import sys
import json

# Initialize Pygame
pygame.init()

# Screen dimensions for phone size
SCREEN_WIDTH = 798
SCREEN_HEIGHT = 640

# Fonts
FONT = pygame.font.Font(None, 30)
BIG_FONT = pygame.font.Font(None, 50)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dodge the Diamonds")

# Game variables
points = 0  # Initialize points to 0
shop_items = {
    "EMDRTejeck": {"cost": 0, "image": pygame.image.load("tejeck.jpeg"), "purchased": True},  # Tejeck is free
    "BabyTejeck": {"cost": 0, "image": pygame.image.load("babytejeck.jpeg"), "purchased": False},
    "Amelia": {"cost": 0, "image": pygame.image.load("amelia.jpeg"), "purchased": False},
    "Evan": {"cost": 0, "image": pygame.image.load("me.jpeg"), "purchased": False},
    "Mei": {"cost": 0, "image": pygame.image.load("babes.jpeg"), "purchased": False},
    "Alv": {"cost": 0, "image": pygame.image.load("alvin.jpeg"), "purchased": False},
}
equipped_item = "EMDRTejeck"  # Default equipped
selected_item = 0  # Track selected item in the shop

# Load diamond image
diamond_image = pygame.image.load("adeline.jpeg")
diamond_image = pygame.transform.scale(diamond_image, (40, 40))  # Scale the diamond image

# Clock for controlling FPS
clock = pygame.time.Clock()

# Load saved game progress (points and purchased items)
# Save game progress (total points and purchased items)
def save_progress():
    progress = {
        "points": points,  # Save total points
        "purchased_items": {item: data["purchased"] for item, data in shop_items.items()}
    }
    try:
        with open("save_progress.json", "w") as file:
            json.dump(progress, file)
    except IOError as e:
        print(f"Failed to save progress: {e}")

# Load saved game progress (total points and purchased items)
def load_progress():
    global points
    try:
        with open("save_progress.json", "r") as file:
            progress = json.load(file)
            points = progress.get("points", 0)  # Load total points
            for item in shop_items:
                shop_items[item]["purchased"] = progress["purchased_items"].get(item, False)
    except (FileNotFoundError, json.JSONDecodeError):
        # Default progress if save file doesn't exist or is invalid
        points = 0
        for item in shop_items:
            shop_items[item]["purchased"] = False


# Draw text on the screen
def draw_text(text, font, color, x, y):
    render = font.render(text, True, color)
    screen.blit(render, (x, y))

# Scale position based on screen resolution
def scale_position(x, y):
    return x * SCREEN_WIDTH // 360, y * SCREEN_HEIGHT // 640

# Scale size based on screen resolution
def scale_size(width, height):
    return width * SCREEN_WIDTH // 360, height * SCREEN_HEIGHT // 640

def main_menu():
    """Display the main menu."""
    while True:
        screen.fill((255, 255, 255))  # White background
        draw_text("Dodge the Tejecks", BIG_FONT, (0, 0, 0), *scale_position(60, 50))  # Black text
        draw_text("1. PLAY", FONT, (0, 0, 0), *scale_position(50, 200))
        draw_text("2. SHOP", FONT, (0, 0, 0), *scale_position(50, 250))
        draw_text("3. QUIT", FONT, (0, 0, 0), *scale_position(50, 300))
        draw_text("4. INSTRUCTIONS", FONT, (0, 0, 0), *scale_position(50, 350))
        draw_text("5. CHANGELOG", FONT, (0, 0, 0), *scale_position(50, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()  # Save progress on exit
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    choose_difficulty()
                elif event.key == pygame.K_2:
                    shop()
                elif event.key == pygame.K_3:
                    save_progress()  # Save progress before quitting
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_4:
                    instructions_screen()
                elif event.key == pygame.K_5:
                    changelog_screen()



def instructions_screen():
    """Display the instructions screen."""
    while True:
        screen.fill((255, 255, 255))  # White background
        draw_text("Instructions", BIG_FONT, (0, 0, 0), *scale_position(100, 50))  # Black text
        draw_text("1. Move with LEFT and RIGHT arrows.", FONT, (0, 0, 0), *scale_position(20, 150))
        draw_text("2. Avoid the falling diamonds.", FONT, (0, 0, 0), *scale_position(20, 200))
        draw_text("3. Earn points by dodging diamonds.", FONT, (0, 0, 0), *scale_position(20, 250))
        draw_text("4. Use points to buy new colors in the shop.", FONT, (0, 0, 0), *scale_position(20, 300))
        draw_text("5. Press UP/DOWN in the shop to select items.", FONT, (0, 0, 0), *scale_position(20, 350))
        draw_text("Press B to return to the Main Menu", FONT, (0, 0, 0), *scale_position(60, SCREEN_HEIGHT - 100))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    return

def changelog_screen():
    """Display the changelog screen."""
    updates = [
        "Version 1.0:",
        "- Added Main Menu with play, shop, and quit options.",
        "- Implemented difficulty levels: Easy, Medium, Hard.",
        "- Introduced diamonds for dodging and scoring.",
        "",
        "Version 1.1:",
        "- More Items in Shop.",
        "- New Difficulty Levels added",
        "- Implemented saving purchased items.",
        "- Added equipped status for purchased items.",
        "- Bugs fixed. ",
        "- Tejeck Characters added"
        "",
    ]

    while True:
        screen.fill((255, 255, 255))  # White background
        draw_text("Changelog", BIG_FONT, (0, 0, 0), *scale_position(100, 50))  # Black text
        y_offset = 150
        for line in updates:
            draw_text(line, FONT, (0, 0, 0), *scale_position(20, y_offset))
            y_offset += 30  # Spacing between lines

        draw_text("Press B to return to the Main Menu", FONT, (0, 0, 0), *scale_position(60, SCREEN_HEIGHT - 100))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    return

def choose_difficulty():
    """Choose difficulty screen."""
    while True:
        screen.fill((255, 255, 255))  # White background
        draw_text("Choose Difficulty", BIG_FONT, (0, 0, 0), *scale_position(80, 50))  # Black text
        draw_text("1. Easy", FONT, (0, 0, 0), *scale_position(50, 200))
        draw_text("2. Medium", FONT, (0, 0, 0), *scale_position(50, 250))
        draw_text("3. Hard", FONT, (0, 0, 0), *scale_position(50, 300))
        draw_text("4. Impossible", FONT, (0, 0, 0), *scale_position(50, 350))
        draw_text("5. God Mode", FONT, (0, 0, 0), *scale_position(50, 400))
        draw_text("6. Creator Mode", FONT, (0, 0, 0), *scale_position(50, 450))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_loop(5)
                elif event.key == pygame.K_2:
                    game_loop(10)
                elif event.key == pygame.K_3:
                    game_loop(15)
                elif event.key == pygame.K_4:
                    game_loop(30)
                elif event.key == pygame.K_5:
                    game_loop(100)
                elif event.key == pygame.K_6:
                    game_loop(150)
                elif event.key == pygame.K_b:
                    return

def shop():
    """Shop screen."""
    global points, equipped_item, selected_item

    while True:
        screen.fill((255, 255, 255))  # White background
        draw_text("Shop", BIG_FONT, (0, 0, 0), *scale_position(120, 50))  # Black text
        draw_text(f"Points: {points}", FONT, (0, 0, 0), *scale_position(10, 10))
        draw_text(f"Equipped: {equipped_item}", FONT, (0, 0, 0), *scale_position(10, 50))

        y_offset = 150  # Start the items a bit lower to make space
        for idx, (item_name, item_data) in enumerate(shop_items.items()):
            image = item_data["image"]
            purchased = item_data["purchased"]
            cost = item_data["cost"]
            status = "Equipped" if equipped_item == item_name else ("Purchased" if purchased else f"{cost} Points")

            # Highlight the selected item
            if idx == selected_item:
                pygame.draw.rect(screen, (200, 200, 200), (40, y_offset - 10, SCREEN_WIDTH - 80, 40))

            # Display item image
            scaled_image = pygame.transform.scale(image, (40, 40))
            screen.blit(scaled_image, (50, y_offset))

            # Display text
            draw_text(f"{item_name}: {status}", FONT, (0, 0, 0), *scale_position(100, y_offset + 5))

            # Display "Not enough points" message if player can't afford item
            if not purchased and points < cost:
                draw_text("Not enough points", FONT, (255, 0, 0), *scale_position(100, y_offset + 35))

            y_offset += 50  # Space out the items

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(shop_items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(shop_items)
                elif event.key == pygame.K_RETURN:
                    selected_item_name = list(shop_items.keys())[selected_item]
                    selected_item_data = shop_items[selected_item_name]
                    if not selected_item_data["purchased"] and points >= selected_item_data["cost"]:
                        points -= selected_item_data["cost"]
                        selected_item_data["purchased"] = True
                    if selected_item_data["purchased"]:
                        equipped_item = selected_item_name
                    save_progress()  # Save progress after purchase
                elif event.key == pygame.K_b:
                    return

def game_loop(difficulty):
    """Main game loop."""
    global points
    game_points = 0  # Session-specific points
    player_x = SCREEN_WIDTH // 2 - 25
    player_y = SCREEN_HEIGHT - 100
    player_speed = 10
    diamond_speed = difficulty
    diamonds = []

    while True:
        screen.fill((255, 255, 255))  # White background

        # Load the equipped player's image
        player_image = shop_items[equipped_item]["image"]
        player_image = pygame.transform.scale(player_image, (50, 50))  # Scale to fit player size
        screen.blit(player_image, (player_x, player_y))  # Draw the equipped player image

        # Update and draw the diamonds
        for diamond in diamonds[:]:
            diamond[1] += diamond_speed
            if diamond[1] > SCREEN_HEIGHT:
                diamonds.remove(diamond)
                game_points += 1  # Add session-specific points
            screen.blit(diamond_image, (diamond[0] - 20, diamond[1] - 20))  # Draw diamond

        # Spawn new diamonds randomly
        if random.random() < 0.05:
            diamond_x = random.randint(50, SCREEN_WIDTH - 50)
            diamonds.append([diamond_x, -20])  # Spawn above the screen

        # Check for collisions
        for diamond in diamonds:
            if player_x < diamond[0] < player_x + 50 and player_y < diamond[1] < player_y + 50:
                points += game_points  # Add session-specific points to total
                save_progress()  # Save progress
                game_over(game_points)  # Pass session score to game over screen
                return

        # Display scores
        draw_text(f"Points This Game: {game_points}", FONT, (0, 0, 0), *scale_position(10, 10))
        draw_text(f"Total Points: {points}", FONT, (0, 0, 0), *scale_position(10, 50))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                points += game_points  # Add session points before quitting
                save_progress()  # Save progress
                pygame.quit()
                sys.exit()

        # Handle player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - 50:
            player_x += player_speed

        clock.tick(60)  # 60 FPS




def game_over(score):
    """Display the game over screen."""
    # Load the game over image
    try:
        game_over_image = pygame.image.load("game_over.jpeg")
        game_over_image = pygame.transform.scale(game_over_image, (300, 300))  # Resize if needed
    except pygame.error as e:
        print(f"Error loading image: {e}")
        game_over_image = None

    while True:
        screen.fill((255, 255, 255))  # White background
        draw_text("CAUGHT BY VEGETARIAN!", BIG_FONT, (255, 0, 0), *scale_position(50, 50))  # Red "GAME OVER"
        draw_text(f"Your Score: {score}", FONT, (0, 0, 0), *scale_position(50, 150))  # Display score

        # Draw the image if loaded successfully
        if game_over_image:
            screen.blit(game_over_image, scale_position(50, 200))  # Adjust position as needed

        draw_text("Press ENTER to return to the main menu", FONT, (0, 0, 0), *scale_position(50, 550))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_progress()  # Save progress before quitting
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return  # Return to the main menu



# Load saved progress before starting the game
load_progress()

# Start the game by showing the main menu
main_menu()