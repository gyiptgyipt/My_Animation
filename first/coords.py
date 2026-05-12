from manim import *
import random

config.frame_rate = 60

class TransformCoords(ThreeDScene):
    def construct(self):
        random.seed(7)
        demo_coord = [
            round(random.uniform(-2.2, 2.2), 1),
            round(random.uniform(-2.2, 2.2), 1),
            round(random.uniform(0.6, 2.4), 1),
        ]

        # 1. Initialize 3D Axes
        axes = ThreeDAxes(
            x_range=[-3, 3, 1],
            y_range=[-3, 3, 1],
            z_range=[-3, 3, 1],
            x_length=5,
            y_length=5,
            z_length=5,
            axis_config={"include_tip": True, "color": BLUE_D}
        )
        
        # Labels for the axes, placed manually so z stays visible.
        labels = VGroup(
            MathTex("x").move_to(axes.c2p(3.35, 0, 0)),
            MathTex("y").move_to(axes.c2p(0, 3.35, 0)),
            MathTex("z").move_to(axes.c2p(0, 0, 3.35)),
        )
        labels.set_color(BLUE_B)

        def vector_magnitude(coords):
            return sum(value ** 2 for value in coords) ** 0.5

        def vector_label(coords, position):
            label = MathTex(
                rf"\vec{{v}}=\langle {coords[0]}, {coords[1]}, {coords[2]} \rangle"
            )
            label.move_to(position)
            label.scale(0.65)
            label.set_color(YELLOW)
            return label

        def scalar_label(coords):
            magnitude = vector_magnitude(coords)
            label = MathTex(
                rf"|\vec{{v}}|=\sqrt{{{coords[0] ** 2:.2f}+{coords[1] ** 2:.2f}+{coords[2] ** 2:.2f}}}"
                rf"\approx {magnitude:.2f}"
            )
            label.to_corner(UL)
            label.scale(0.75)
            label.set_color(GREEN)
            return label

        def vector_arrow(start, end):
            return Arrow(
                start=start,
                end=end,
                buff=0,
                color=ORANGE,
                stroke_width=6,
                max_tip_length_to_length_ratio=0.15,
            )

        # 2. Create a vector, point, and scalar value.
        origin = axes.c2p(0, 0, 0)
        point_pos = axes.c2p(*demo_coord)
        point = Dot(point=point_pos, color=YELLOW, radius=0.08)
        vector = vector_arrow(origin, point_pos)
        coords_text = vector_label(demo_coord, axes.c2p(demo_coord[0] + 0.5, demo_coord[1] + 0.45, demo_coord[2] + 0.35))
        scalar_text = scalar_label(demo_coord)
        
        # 3. Setup the initial camera angle
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=1)

        # --- ANIMATION SEQUENCE ---
        
        # Show axes and labels
        self.add_fixed_orientation_mobjects(labels, coords_text)
        self.add_fixed_in_frame_mobjects(scalar_text)
        self.play(Create(axes), Write(labels))
        self.play(Create(point))
        self.wait(5)

        self.play(Create(vector), Write(coords_text), Write(scalar_text))
        self.wait(5)
