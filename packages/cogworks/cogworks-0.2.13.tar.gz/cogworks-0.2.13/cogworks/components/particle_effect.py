from cogworks import GameObject, Component
from cogworks.components.particle import Particle
from typing import Tuple
import random


class ParticleEffect(Component):
    """
    Particle system component for Cogworks.

    Supports looping, emission rate, bursts, world/local simulation,
    and per-particle customisation.
    """

    def __init__(
        self,
        sprite_path: str,
        emission_rate: float = 10.0,  # particles per second
        burst_count: int | None = None,
        looping: bool = True,
        duration: float = 3.0,
        start_delay: float = 0.0,
        max_particles: int = 100,
        simulation_space: str = "local",  # "local" or "world"
        min_x: float = 0,
        max_x: float = 50,
        min_y: float = 0,
        max_y: float = 50,
        min_rotation: float = -180,
        max_rotation: float = 180,
        min_scale: float = 0.4,
        max_scale: float = 0.8,
        move_speed: float = 500,
        gravity: float = 500,
        min_direction: Tuple[float, float] = (-1, -1),
        max_direction: Tuple[float, float] = (1, 1),
        lifetime: float = 1.5,
        end_scale: float | None = None,
        scale_with_lifetime: bool = False,
        rotate_over_lifetime: bool = False,
        fade_over_lifetime: bool = False,
    ):
        """
        Initialise a configurable particle effect similar to Unity's Particle System.

        Args:
            sprite_path (str): Path to the sprite used for each particle.
            emission_rate (float): Number of particles emitted per second.
            burst_count (int | None): Number of particles emitted instantly at the start (optional).
            looping (bool): Whether the effect restarts after its duration.
            duration (float): How long the effect emits particles before stopping or looping.
            start_delay (float): Time (in seconds) before emission begins.
            max_particles (int): Maximum number of active particles at once.
            simulation_space (str):
                "local" makes particles follow the parent object,
                "world" spawns them independently in the scene.
            min_x (float): Minimum horizontal offset for particle spawn position.
            max_x (float): Maximum horizontal offset for particle spawn position.
            min_y (float): Minimum vertical offset for particle spawn position.
            max_y (float): Maximum vertical offset for particle spawn position.
            min_rotation (float): Minimum initial rotation of a particle (degrees).
            max_rotation (float): Maximum initial rotation of a particle (degrees).
            min_scale (float): Minimum starting scale for a particle.
            max_scale (float): Maximum starting scale for a particle.
            move_speed (float): Base velocity magnitude for each particle.
            gravity (float): Gravity force applied to particles per second (negative = upward).
            min_direction (Tuple[float, float]): Minimum direction vector for randomised motion.
            max_direction (Tuple[float, float]): Maximum direction vector for randomised motion.
            lifetime (float): Lifetime of each particle (in seconds).
            end_scale (float | None): Optional final scale of the particle at the end of its life.
            scale_with_lifetime (bool): Whether particles grow/shrink over time.
            rotate_over_lifetime (bool): Whether particles continuously rotate over their lifetime.
            fade_over_lifetime (bool): Whether particles fade out gradually over time.
        """
        super().__init__()

        # Emission behaviour
        self.sprite_path = sprite_path
        self.emission_rate = emission_rate
        self.burst_count = burst_count
        self.looping = looping
        self.duration = duration
        self.start_delay = start_delay
        self.max_particles = max_particles
        self.simulation_space = simulation_space.lower()

        # Particle properties
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y
        self.min_rotation = min_rotation
        self.max_rotation = max_rotation
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.move_speed = move_speed
        self.gravity = gravity
        self.min_direction = min_direction
        self.max_direction = max_direction
        self.lifetime = lifetime
        self.end_scale = end_scale
        self.scale_with_lifetime = scale_with_lifetime
        self.rotate_over_lifetime = rotate_over_lifetime
        self.fade_over_lifetime = fade_over_lifetime

        # Internal runtime state
        self._time_since_last_emit = 0.0
        self._elapsed_time = 0.0
        self._active = False
        self._started = False

    def start(self) -> None:
        """Begin particle effect (with optional delay)."""
        if self.start_delay <= 0:
            self.play()
        else:
            self._started = True  # wait until delay finishes

    def play(self) -> None:
        """Start emitting particles."""
        self._elapsed_time = 0
        self._time_since_last_emit = 0
        self._active = True
        if self.burst_count:
            for _ in range(self.burst_count):
                self.spawn_particle()

    def stop(self) -> None:
        """Stop particle emission."""
        self._active = False

    def update(self, dt) -> None:
        """Update emission and timing logic each frame."""
        if self._started:
            self.start_delay -= dt
            if self.start_delay <= 0:
                self._started = False
                self.play()
            return

        if not self._active:
            return

        self._elapsed_time += dt
        if not self.looping and self._elapsed_time >= self.duration:
            self.stop()
            return

        # Emit particles according to emission rate
        if self.emission_rate > 0:
            self._time_since_last_emit += dt
            emit_interval = 1.0 / self.emission_rate
            while self._time_since_last_emit >= emit_interval:
                self._time_since_last_emit -= emit_interval
                self.spawn_particle()


    def spawn_particle(self) -> None:
        """Spawn a single particle instance."""
        if len(self.game_object.children) >= self.max_particles and self.simulation_space == "local":
            return  # Cap particles only in local mode

        particle = GameObject("Particle", z_index=5)
        particle_component = Particle(
            sprite_path=self.sprite_path,
            min_x=self.min_x,
            max_x=self.max_x,
            min_y=self.min_y,
            max_y=self.max_y,
            min_rotation=self.min_rotation,
            max_rotation=self.max_rotation,
            min_scale=self.min_scale,
            max_scale=self.max_scale,
            move_speed=self.move_speed * random.uniform(0.8, 1.2),
            gravity=self.gravity,
            min_direction=self.min_direction,
            max_direction=self.max_direction,
            lifetime=self.lifetime,
            end_scale=self.end_scale,
            scale_with_lifetime=self.scale_with_lifetime,
            rotate_over_lifetime=self.rotate_over_lifetime,
            fade_over_lifetime=self.fade_over_lifetime,
        )
        particle.add_component(particle_component)


        if self.simulation_space == "local":
            # Follows parent transform (e.g., a torch flame)
            self.game_object.add_child(particle)
        elif self.simulation_space == "world":
            # Spawns directly into the scene (e.g., explosion)
            self.game_object.scene.instantiate_game_object(particle)
            # Set world position to match emitter’s current position
            particle.transform.position = self.game_object.transform.world_position
        else:
            raise ValueError("simulation_space must be 'local' or 'world'")
