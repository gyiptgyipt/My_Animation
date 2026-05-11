from manim import *

class TransformCoords(ThreeDScene):
    def construct(self):
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
        
        # Labels for the axes
        labels = axes.get_axis_labels(
            x_label="x", y_label="y", z_label="z"
        )

        # 2. Create a point and its coordinate lines
        point = Dot3D(point=axes.c2p(1, 1, 1), color=YELLOW)
        coords_text = MathTex("(1, 1, 1)").next_to(point, UR, buff=0.1).scale(0.8)
        
        # 3. Setup the initial camera angle
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)

        # --- ANIMATION SEQUENCE ---
        
        # Show axes and labels
        self.play(Create(axes), Write(labels))
        self.begin_ambient_camera_rotation(rate=0.1) # Slow rotation for 3D depth
        self.play(Create(point), Write(coords_text))
        self.wait(1)

        # 4. Transform to a new position
        new_point_coord = [2, -1, 2]
        new_point_pos = axes.c2p(*new_point_coord)
        new_text = MathTex("(2, -1, 2)").next_to(new_point_pos, UR, buff=0.1).scale(0.8)
        new_text.set_color(YELLOW)

        # The "Transform" happens here
        self.play(
            point.animate.move_to(new_point_pos),
            Transform(coords_text, new_text),
            run_time=2
        )
        
        self.wait(2)
        self.stop_ambient_camera_rotation()
