"""
Top-down RViz-style 2D robot localization visualization.

Shows a robot (blue circle) at the origin. A cloud of ~1000 red
particle-arrows (the classic particle-filter representation) starts
stacked on the robot, all move "forward" by 1 meter simultaneously,
and scatter into a messy cloud due to simulated wheel-slip noise.

To make the "how it became Gaussian" idea visible (not just narrated),
the scene then:
  1. Bins the particles' ACTUAL landing positions into a live histogram
     that grows up from the cloud.
  2. Morphs that histogram into a smooth bell curve fitted to the same
     data.
  3. Flies that exact curve up into a glowing yellow HUD panel in the
     top-right corner, so the payoff reads as "these dots -> this curve".

After that, the scene continues into Resampling ("the reality show roast"):
a laser beam hits a wall, particles are scored by how close they actually
landed to the true position, low-scoring ones dissolve like dust while
high-scoring ones get cloned to replace them, and the robot itself drives
up to meet the tight, converged cluster.

Run with:
    manim -pql robot_localization.py RobotLocalization      # quick draft
    manim -pqh robot_localization.py RobotLocalization      # high quality

NOTE ON PERFORMANCE
--------------------
Animating 1000 individual mobjects with `.animate.move_to()` in a single
`self.play(...)` call is faithful to the "1000 particles" brief but is
render-heavy on the Cairo renderer. For fast iteration, drop
NUM_PARTICLES down to ~200-300 (see the constant below), then bump it
back to 1000 for your final -qh render. You can also render with the
OpenGL renderer for a big speed boost:
    manim -pql --renderer=opengl robot_localization.py RobotLocalization
"""

import random
import numpy as np
from manim import *

config.frame_rate = 60
config.background_color = "#1a1a1a"

# ---------------------------------------------------------------------------
# Tunables
# ---------------------------------------------------------------------------
NUM_PARTICLES = 1000          # set to ~200-300 for fast draft renders
FORWARD_METERS = 1.0
UNITS_PER_METER = 1.6         # visual scale: 1 m -> 1.6 manim units
NOISE_STD = 0.16              # wheel-slip scatter std-dev (manim units)
SEED = 7

random.seed(SEED)
np.random.seed(SEED)

DARK_BG = "#1a1a1a"
GRID_CYAN = "#00e5ff"
ROBOT_BLUE = "#2fa4ff"
PARTICLE_RED = "#ff3b3b"
GLOW_YELLOW = "#ffe600"
WALL_COLOR = "#eafcff"
GOOD_GREEN = "#39ff6a"
BAD_GREY = "#7a4444"


class RobotLocalization(Scene):
    def construct(self):
        self.camera.background_color = DARK_BG

        grid = self.build_grid()
        self.add(grid)

        robot = self.build_robot()
        self.play(FadeIn(robot, scale=0.6), run_time=0.6)

        # --- Particle cloud (particle filter) -----------------------------
        # Uniform distribution: "I could be anywhere on the map" -> scatter
        # particles randomly across the whole frame, NOT stacked on the robot.
        particles = VGroup(*[self.build_particle() for _ in range(NUM_PARTICLES)])
        margin = 0.4
        for p in particles:
            ux = random.uniform(-config.frame_width / 2 + margin, config.frame_width / 2 - margin)
            uy = random.uniform(-config.frame_height / 2 + margin, config.frame_height / 2 - margin)
            p.move_to([ux, uy, 0])
            p.rotate(random.uniform(0, TAU))  # random headings read as "uniform prior"
        self.add(particles)
        self.play(
            LaggedStart(*[FadeIn(p, scale=0.3) for p in particles], lag_ratio=0.0006),
            run_time=1.0,
        )
        self.wait(0.3)

        # Targets: forward 1 m + Gaussian slip noise
        forward_vec = UP * (FORWARD_METERS * UNITS_PER_METER)
        targets = []
        x_offsets = []  # raw lateral noise samples -> used to PROVE the shape later
        noise_mag = []  # full noise magnitude per particle -> used as a weight proxy later
        for _ in particles:
            nx = random.gauss(0, NOISE_STD)
            ny = random.gauss(0, NOISE_STD)
            targets.append(ORIGIN + forward_vec + np.array([nx, ny, 0]))
            x_offsets.append(nx)
            noise_mag.append(float(np.hypot(nx, ny)))

        move_anims = [
            particles[i].animate.move_to(targets[i]) for i in range(NUM_PARTICLES)
        ]
        self.play(*move_anims, run_time=2.2, rate_func=rate_functions.ease_out_cubic)
        self.wait(0.4)

        # --- Prove it: bin the ACTUAL scattered particles into a live       -
        # --- histogram, right under the cloud, then watch it melt into a    -
        # --- smooth bell curve. This is the "how it became Gaussian" beat.  -
        cloud_center_x = forward_vec[0]
        hist_base_y = forward_vec[1] - 0.85  # a clear strip below the cloud, above the robot
        hist_max_h = 0.55
        hist_x_range = 0.6

        bars, edges = self.build_histogram(
            x_offsets,
            base_y=hist_base_y,
            max_height=hist_max_h,
            x_range=hist_x_range,
            num_bins=13,
            center_x=cloud_center_x,
        )
        caption_anchor = robot.get_bottom() + DOWN * 0.55
        caption1 = Text("Where did the clones actually land?", font_size=24, color=GLOW_YELLOW)
        caption1.move_to(caption_anchor)
        self.play(FadeIn(caption1, shift=UP * 0.1), run_time=0.5)
        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.04),
            run_time=1.4,
        )
        self.wait(0.5)

        bell_curve = self.build_bell_curve_from_offsets(
            x_offsets,
            base_y=hist_base_y,
            max_height=hist_max_h,
            x_range=hist_x_range,
            center_x=cloud_center_x,
        )
        curve_glow = bell_curve.copy().set_stroke(width=9, opacity=0.25)

        caption2 = Text("...it's a bell curve.", font_size=24, color=GLOW_YELLOW)
        caption2.move_to(caption_anchor)

        self.play(
            ReplacementTransform(bars, VGroup(curve_glow, bell_curve)),
            ReplacementTransform(caption1, caption2),
            run_time=1.3,
        )
        self.wait(1.0)

        # --- Overhead glowing Gaussian probability panel -------------------
        # Fly the SAME curve we just derived from the particles up into the
        # HUD panel, so the payoff is literally "these dots became this graph".
        panel = self.build_gaussian_panel()
        panel.to_corner(UR, buff=0.35)
        panel_bg, panel_axes, panel_glow_layers, panel_curve, panel_label = panel

        self.play(
            FadeOut(caption2),
            FadeOut(curve_glow),
            FadeIn(panel_bg),
            FadeIn(panel_axes),
            ReplacementTransform(bell_curve, panel_curve),
            run_time=1.4,
        )
        self.play(FadeIn(panel_glow_layers), FadeIn(panel_label), run_time=0.6)
        self.wait(1.0)

        # ===================================================================
        # RESAMPLING ("The Reality Show Roast")
        # ===================================================================

        # --- 1. Laser scan hits a wall, angled off to the side so it clears
        # --- both the particle cloud and the HUD panel in the corner. -------
        beam_angle = 25 * DEGREES
        beam_dir = np.array([-np.sin(beam_angle), np.cos(beam_angle), 0])
        perp = np.array([beam_dir[1], -beam_dir[0], 0])
        beam_end = ORIGIN + beam_dir * (2 * UNITS_PER_METER)  # "2 meters away"

        wall = Line(
            beam_end - perp * 1.3, beam_end + perp * 1.3,
            color=WALL_COLOR, stroke_width=6,
        )
        beam = Line(ORIGIN, beam_end, color=WALL_COLOR, stroke_width=3)

        caption_wall = Text("Laser hits a wall — 2m away.", font_size=24, color=GLOW_YELLOW)
        caption_wall.move_to(caption_anchor)

        self.play(FadeIn(caption_wall, shift=UP * 0.1), run_time=0.5)
        self.play(Create(wall), run_time=0.5)
        self.play(
            Create(beam),
            Flash(beam_end, color=WALL_COLOR, flash_radius=0.35, line_length=0.25),
            run_time=0.6,
        )
        self.wait(0.3)

        # --- 2. Score every clone: a sonar-style pulse sweeps out from the --
        # --- robot while particles recolor by weight (how close they --------
        # --- actually landed to the true position = how well they'd --------
        # --- explain this laser reading). ------------------------------------
        weights = np.exp(-(np.array(noise_mag) ** 2) / (2 * (NOISE_STD * 1.4) ** 2))
        median_w = float(np.median(weights))
        good_mask = weights >= median_w

        recolor_anims = []
        for i, p in enumerate(particles):
            if good_mask[i]:
                recolor_anims.append(p.animate.set_fill(GOOD_GREEN, opacity=1))
            else:
                recolor_anims.append(p.animate.set_fill(BAD_GREY, opacity=0.4).scale(0.7))

        rings = VGroup(
            *[
                Circle(radius=0.05, stroke_color=WALL_COLOR, stroke_width=3, fill_opacity=0).move_to(ORIGIN)
                for _ in range(3)
            ]
        )
        ring_anims = [ring.animate.scale(9).set_stroke(opacity=0) for ring in rings]

        caption_score = Text("The sensor checks every clone's story.", font_size=24, color=GLOW_YELLOW)
        caption_score.move_to(caption_anchor)

        self.play(
            ReplacementTransform(caption_wall, caption_score),
            FadeOut(wall), FadeOut(beam),
            run_time=0.5,
        )
        self.add(rings)
        self.play(*ring_anims, *recolor_anims, run_time=1.2)
        self.remove(rings)
        self.wait(0.4)

        # --- 3. Resampling: bad clones dissolve like dust, good ones get ----
        # --- cloned to take their place ("Thanos snap"). --------------------
        good_indices = [i for i in range(NUM_PARTICLES) if good_mask[i]]
        bad_indices = [i for i in range(NUM_PARTICLES) if not good_mask[i]]
        good_particles = VGroup(*[particles[i] for i in good_indices])
        bad_particles = VGroup(*[particles[i] for i in bad_indices])

        caption_resample = Text("Bad clones vanish. Good ones get cloned.", font_size=24, color=GLOW_YELLOW)
        caption_resample.move_to(caption_anchor)
        self.play(ReplacementTransform(caption_score, caption_resample), run_time=0.4)

        dust_anims = [
            FadeOut(
                p, scale=0.15,
                shift=np.array([random.uniform(-0.5, 0.5), random.uniform(-0.2, 0.7), 0]),
            )
            for p in bad_particles
        ]
        self.play(LaggedStart(*dust_anims, lag_ratio=0.0025), run_time=1.6)
        self.wait(0.2)

        # Clone survivors near themselves to restore the cloud's density
        clones = VGroup()
        for _ in range(len(bad_indices)):
            src = random.choice(good_particles)
            clone = self.build_particle()
            clone.set_fill(GOOD_GREEN, opacity=1)
            clone.move_to(src.get_center() + np.array([random.gauss(0, 0.07), random.gauss(0, 0.07), 0]))
            clones.add(clone)
        self.play(
            LaggedStart(*[GrowFromCenter(c) for c in clones], lag_ratio=0.003),
            run_time=1.1,
        )
        self.wait(0.3)

        # --- 4. Final convergence: robot drives up to meet its own tight, ---
        # --- confident cluster of surviving/cloned particles. ---------------
        survivors = VGroup(*good_particles, *clones)
        final_targets = [
            forward_vec + np.array([random.gauss(0, 0.05), random.gauss(0, 0.05), 0])
            for _ in survivors
        ]

        caption_final = Text("Boom. It knows where it is.", font_size=24, color=GLOW_YELLOW)
        caption_final.move_to(caption_anchor)

        self.play(
            ReplacementTransform(caption_resample, caption_final),
            robot.animate.move_to(forward_vec),
            *[survivors[i].animate.move_to(final_targets[i]) for i in range(len(survivors))],
            run_time=1.6,
            rate_func=rate_functions.ease_in_out_cubic,
        )
        self.play(Flash(forward_vec, color=WHITE, flash_radius=0.7, line_length=0.35), run_time=0.5)
        self.wait(2)

    # -----------------------------------------------------------------
    # Builders
    # -----------------------------------------------------------------
    def build_grid(self):
        """Faint cyan grid over a full-frame dark background."""
        bg = Rectangle(
            width=config.frame_width,
            height=config.frame_height,
            fill_color=DARK_BG,
            fill_opacity=1,
            stroke_width=0,
        )

        spacing = 0.5
        lines = VGroup()
        x = -config.frame_width / 2
        while x <= config.frame_width / 2:
            lines.add(
                Line(
                    [x, -config.frame_height / 2, 0],
                    [x, config.frame_height / 2, 0],
                )
            )
            x += spacing
        y = -config.frame_height / 2
        while y <= config.frame_height / 2:
            lines.add(
                Line(
                    [-config.frame_width / 2, y, 0],
                    [config.frame_width / 2, y, 0],
                )
            )
            y += spacing

        lines.set_stroke(color=GRID_CYAN, width=0.6, opacity=0.12)
        return VGroup(bg, lines)

    def build_robot(self):
        """Bright blue circular robot icon with a heading tick and glow."""
        glow = VGroup(
            *[
                Circle(radius=0.3 + i * 0.12)
                .set_stroke(width=0)
                .set_fill(ROBOT_BLUE, opacity=0.10 - i * 0.02)
                for i in range(3)
            ]
        )
        body = Circle(radius=0.3, color=WHITE, stroke_width=2)
        body.set_fill(ROBOT_BLUE, opacity=1)
        heading = Triangle(fill_opacity=1, color=WHITE, stroke_width=0)
        heading.set_height(0.16)
        heading.move_to(body.get_top() + UP * 0.02)
        return VGroup(glow, body, heading)

    def build_particle(self):
        """A tiny red arrow (particle-filter sample), pointing 'forward' (+Y)."""
        arrow = Triangle(fill_opacity=0.9, color=PARTICLE_RED, stroke_width=0)
        arrow.set_height(0.09)
        arrow.set_fill(PARTICLE_RED, opacity=0.85)
        return arrow

    def build_histogram(self, x_offsets, base_y, max_height, x_range, num_bins, center_x=0.0):
        """
        Real histogram of the particles' actual lateral noise offsets.
        This is not a decorative curve -- the bar heights come straight
        from `x_offsets`, i.e. from where the 1000 particles really landed.
        """
        counts, edges = np.histogram(x_offsets, bins=num_bins, range=(-x_range, x_range))
        max_count = counts.max() if counts.max() > 0 else 1
        bin_width = edges[1] - edges[0]

        bars = VGroup()
        for i, c in enumerate(counts):
            h = max(c / max_count * max_height, 0.02)
            bar = Rectangle(
                width=bin_width * 0.82,
                height=h,
                stroke_width=0,
                fill_color=GLOW_YELLOW,
                fill_opacity=0.75,
            )
            bin_center = (edges[i] + edges[i + 1]) / 2
            bar.move_to([center_x + bin_center, base_y + h / 2, 0])
            bars.add(bar)
        return bars, edges

    def build_bell_curve_from_offsets(self, x_offsets, base_y, max_height, x_range, center_x=0.0):
        """
        Fits a Gaussian to the SAME data used for the histogram above, so the
        curve the audience sees is derived from the particle cloud itself.
        """
        std = float(np.std(x_offsets))
        if std < 1e-6:
            std = NOISE_STD

        def gaussian(x):
            return max_height * np.exp(-(x ** 2) / (2 * std ** 2))

        curve = ParametricFunction(
            lambda t: np.array([center_x + t, base_y + gaussian(t), 0]),
            t_range=[-x_range, x_range],
            color=GLOW_YELLOW,
        )
        curve.set_stroke(width=4)
        return curve

    def build_gaussian_panel(self):
        """Glowing yellow 2D Gaussian bell-curve, in a HUD-style panel."""
        panel_bg = RoundedRectangle(
            width=4.4, height=2.6, corner_radius=0.12,
            stroke_color=GRID_CYAN, stroke_width=1.5, stroke_opacity=0.6,
            fill_color="#0d0d0d", fill_opacity=0.75,
        )

        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[0, 1.1, 1],
            x_length=3.6,
            y_length=1.7,
            tips=False,
            axis_config={"stroke_color": GREY_B, "stroke_width": 1.5},
        )
        axes.move_to(panel_bg.get_center() + DOWN * 0.05)

        def gaussian(x, sigma=1.0):
            return np.exp(-(x ** 2) / (2 * sigma ** 2))

        curve = axes.plot(lambda x: gaussian(x, sigma=1.0), color=GLOW_YELLOW, stroke_width=3)

        # Glow: stacked, wider, more-transparent copies behind the curve
        glow_layers = VGroup()
        for i, (w, op) in enumerate([(10, 0.05), (7, 0.08), (4.5, 0.14)]):
            layer = axes.plot(lambda x: gaussian(x, sigma=1.0), color=GLOW_YELLOW)
            layer.set_stroke(width=w, opacity=op)
            glow_layers.add(layer)

        label = Text("P(x | z)", font_size=22, color=GLOW_YELLOW, weight=BOLD)
        label.next_to(panel_bg.get_top(), DOWN, buff=0.12)

        return VGroup(panel_bg, axes, glow_layers, curve, label)