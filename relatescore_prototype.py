import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions (simulating iPhone portrait)
WIDTH, HEIGHT = 375, 667
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("RelateScore Prototype")

# Colors from palette
CHARCOAL = (26, 26, 26)
WHITE = (255, 255, 255)
SOFT_GRAY = (245, 245, 245)
ACCENT_BLUE = (46, 106, 243)
MINT = (166, 227, 218)
ERROR_RED = (229, 70, 70)

# Fonts
font_large = pygame.font.SysFont('helvetica', 24, bold=True)
font_medium = pygame.font.SysFont('helvetica', 18)
font_small = pygame.font.SysFont('helvetica', 14)


class Button:
    """Reusable UI button"""
    def __init__(self, x, y, w, h, text, color=ACCENT_BLUE, text_color=WHITE):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=12)
        text_surf = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# Simulated data
assessment_progress = 0
questions = [
    "How often do you communicate openly?",
    "How do you handle conflict?",
    "Rate your empathy level.",
]
answers = [0] * len(questions)  # 1–5 scale
insights = [
    "Strength: Open Communication",
    "Blind Spot: Conflict Avoidance",
    "Pattern: Secure Attachment",
]
rgi_score = 75  # Simulated starting score

# Screens
current_screen = "onboarding1"


def draw_text(text, font, color, x, y, center=False):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)


def draw_rq_wheel(x, y, radius=80):
    """Simplified RQ Wheel as a circle with cross segments"""
    pygame.draw.circle(screen, CHARCOAL, (x, y), radius, 2)  # Outer circle
    # Sample segments
    pygame.draw.line(screen, MINT, (x, y - radius), (x, y + radius), 4)
    pygame.draw.line(screen, ACCENT_BLUE, (x - radius, y), (x + radius, y), 4)
    draw_text(f"RGI: {rgi_score}", font_medium, CHARCOAL, x, y + radius + 10, center=True)


# --------- Main loop ----------
while True:
    mouse_clicked = False
