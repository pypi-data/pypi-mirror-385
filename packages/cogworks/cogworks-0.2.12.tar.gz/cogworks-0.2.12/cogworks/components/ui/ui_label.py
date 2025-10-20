import pygame
from cogworks.components.ui.ui_transform import UITransform
from cogworks.components.ui.ui_renderer import UIRenderer


class UILabel(UIRenderer):
    """
    UILabel is a simple UI element for displaying text on the screen.

    Features:
        - Renders text with alignment (anchor) relative to the UITransform's rect.
        - Supports custom font size, text colour, and optional background colour.
        - Can update text dynamically at runtime via `set_text`.
        - Supports optional rounded corners for the background.
        - Anchor options: 'center', 'topleft', 'topright', 'bottomleft', 'bottomright',
                          'midtop', 'midbottom', 'midleft', 'midright'.
        - Supports alpha transparency and fade-in/fade-out animations.
    """

    def __init__(
        self,
        text: str,
        font_size: int = 24,
        color: tuple[int, int, int] = (255, 255, 255),
        bg_color: tuple[int, int, int] | None = None,
        border_radius: int = 0,
        anchor: str = "center",
    ):
        """
        Initialise a UILabel component.

        Args:
            text (str): The text displayed by the label.
            font_size (int, optional): Font size (default: 24).
            color (tuple[int,int,int], optional): Text colour (default: white).
            bg_color (tuple[int,int,int] | None, optional): Background colour.
            border_radius (int, optional): Rounded corner radius for background (default: 0).
            anchor (str, optional): Text alignment anchor (default: 'center').
                                    Options include:
                                    'center', 'topleft', 'topright', 'bottomleft', 'bottomright',
                                    'midtop', 'midbottom', 'midleft', 'midright'.
        """
        super().__init__()
        self.start_text = text
        self.text = self.start_text
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.bg_color = bg_color
        self.border_radius = border_radius
        self.anchor = anchor.lower().strip()

        # Alpha (transparency) support
        self.alpha = 255  # Fully visible by default
        self.fade_speed = 0  # How much alpha changes per frame
        self.fading_in = False
        self.fading_out = False

    def start(self):
        self.text = self.start_text

    def set_text(self, new_text: str) -> None:
        """Update the label's text."""
        self.text = new_text

    def fade_in(self, speed: int = 5) -> None:
        """Start fading the label in (increasing alpha)."""
        self.fade_speed = abs(speed)
        self.fading_in = True
        self.fading_out = False

    def fade_out(self, speed: int = 5) -> None:
        """Start fading the label out (decreasing alpha)."""
        self.fade_speed = abs(speed)
        self.fading_out = True
        self.fading_in = False

    def update(self, dt: float) -> None:
        """
        Update label fade animations.
        Should be called every frame (dt = delta time).
        """
        if self.fading_in:
            self.alpha = min(255, self.alpha + self.fade_speed)
            if self.alpha >= 255:
                self.fading_in = False
        elif self.fading_out:
            self.alpha = max(0, self.alpha - self.fade_speed)
            if self.alpha <= 0:
                self.fading_out = False

    def render(self, surface) -> None:
        rect = self.game_object.get_component(UITransform).rect
        text_surf = self.font.render(self.text, True, self.color)

        # Apply alpha transparency
        text_surf.set_alpha(self.alpha)

        # Draw background if needed
        if self.bg_color:
            bg_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            bg_color_with_alpha = (*self.bg_color, self.alpha)
            pygame.draw.rect(bg_surf, bg_color_with_alpha, bg_surf.get_rect(), border_radius=self.border_radius)
            surface.blit(bg_surf, rect)

        # Get the text rect and position based on the chosen anchor
        text_rect = text_surf.get_rect()

        # Map anchor keywords to rect attributes dynamically
        if hasattr(rect, self.anchor):
            setattr(text_rect, self.anchor, getattr(rect, self.anchor))
        else:
            # Default fallback to center if anchor is invalid
            text_rect.center = rect.center

        # Blit text at anchored position
        surface.blit(text_surf, text_rect)
