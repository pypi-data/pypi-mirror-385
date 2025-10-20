import weakref
import pygame
from cogworks.pygame_wrappers.window import Window

from cogworks.component import Component
from cogworks.components.camera import Camera
from cogworks.components.audio_source import AudioSource


class AudioListener(Component):
    """
    Represents an audio listener component that processes audio sources
    relative to the active camera's position.

    This component keeps track of all active `AudioSource` instances,
    updates their perceived position based on the listener's location
    (typically tied to the camera), and handles registration and cleanup.
    """

    def __init__(self, target_transform=None):
        """
        Args:
            target_transform (Transform, optional):
                A Transform to use as the listener’s position target.
                If not provided, the camera’s centre position is used.
        """
        super().__init__()
        self._sources = set()
        self._target_transform_ref = weakref.ref(target_transform) if target_transform else None
        self.debug = False

    def register_source(self, source: AudioSource) -> None:
        """
        Register an AudioSource to be managed by this listener.

        This links the source with the listener, allowing positional
        audio updates based on the listener's location.

        Args:
            source (AudioSource): The audio source to register.
        """
        self._sources.add(source)
        source._listener = self

    def unregister_source(self, source: AudioSource) -> None:
        """
        Unregister an AudioSource from this listener.

        Removes the source from tracking and clears its listener reference.

        Args:
            source (AudioSource): The audio source to unregister.
        """
        self._sources.discard(source)
        source._listener = None

    def clear_sources(self) -> None:
        """
        Stop and remove all registered audio sources.

        This is typically called when the listener is destroyed or reset.
        Ensures all associated sources are stopped and detached safely.
        """
        for source in list(self._sources):
            source.stop()
            source._listener = None
        self._sources.clear()

    def _get_listener_position(self) -> tuple[float, float] | None:
        """
        Determine the current listener position in world coordinates.

        If a target transform is set and valid, that transform’s position
        is used. Otherwise, the listener defaults to the camera’s centre.
        """
        # If a target transform was provided, use its world position
        if self._target_transform_ref:
            target = self._target_transform_ref()
            if target and target.exists():
                x, y = target.get_world_position()
                return (x, y)

        # Otherwise, fall back to the camera’s centre
        cam = self.game_object.get_component(Camera)
        if not cam:
            return None

        sw, sh = Window.get_instance().get_size()
        return (
            cam.offset_x + (sw / 2) / cam.zoom,
            cam.offset_y + (sh / 2) / cam.zoom
        )

    def set_target_transform(self, target_transform):
        self._target_transform_ref = weakref.ref(target_transform) if target_transform else None

    def update(self, dt: float) -> None:
        """
        Update all registered audio sources with the current listener position.

        The listener’s position is derived from the attached `Camera` component
        unless a target transform has been provided, ensuring spatial audio
        behaves correctly relative to the listener’s view or focus.
        """
        listener_pos = self._get_listener_position()
        if not listener_pos:
            return

        # Update all registered audio sources
        for source in list(self._sources):
            source.set_listener_position(listener_pos)

    def render(self, surface) -> None:
        if not self.debug:
            return

        cam = self.game_object.get_component(Camera)
        if not cam:
            return

        listener_pos = self._get_listener_position()
        if not listener_pos:
            return

        lx, ly = cam.world_to_screen(*listener_pos)
        lx, ly = int(lx), int(ly)

        # Draw marker
        pygame.draw.circle(surface, (0, 255, 0), (lx, ly), 6)
        pygame.draw.line(surface, (0, 255, 0), (lx - 8, ly), (lx + 8, ly), 1)
        pygame.draw.line(surface, (0, 255, 0), (lx, ly - 8), (lx, ly + 8), 1)

        # Display debug position text
        font = pygame.font.Font(None, 20)
        text_surface = font.render(f"Listener: ({int(listener_pos[0])}, {int(listener_pos[1])})", True, (0, 255, 0))
        surface.blit(text_surface, (lx + 10, ly - 10))
