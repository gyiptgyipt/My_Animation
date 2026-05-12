from manim import *

config.frame_rate = 24
config.pixel_width = 854
config.pixel_height = 480


class RotationMatrixDemo(Scene):
    def construct(self):
        theta = 45 * DEGREES
        start_vector = [1, 1, 0]
        rotated_vector = [0, 2 ** 0.5, 0]

        title = Text("2D Rotation Matrix", font_size=38).to_edge(UP)

        axes = Axes(
            x_range=[-1, 3, 1],
            y_range=[-1, 3, 1],
            x_length=5.2,
            y_length=5.2,
            axis_config={"include_tip": True, "color": BLUE_D},
        ).to_edge(LEFT, buff=0.65).shift(DOWN * 0.25)
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        start_arrow = Vector(
            axes.c2p(*start_vector) - axes.c2p(0, 0),
            color=YELLOW,
        ).shift(axes.c2p(0, 0))
        start_label = MathTex(r"\vec{v}=\begin{bmatrix}1\\1\end{bmatrix}")
        start_label.next_to(start_arrow.get_end(), RIGHT, buff=0.15)
        start_label.set_color(YELLOW)

        rotated_label = MathTex(r"\vec{v}'=\begin{bmatrix}0\\\sqrt{2}\end{bmatrix}")
        rotated_label.next_to(axes.c2p(*rotated_vector), LEFT, buff=0.15)
        rotated_label.set_color(GREEN)

        angle_arc = Arc(
            radius=0.75,
            start_angle=45 * DEGREES,
            angle=theta,
            color=ORANGE,
            arc_center=axes.c2p(0, 0),
        )
        angle_label = MathTex(r"45^\circ", color=ORANGE).scale(0.8)
        angle_label.move_to(axes.c2p(0.45, 1.0, 0))

        steps = VGroup(
            MathTex(
                r"R(\theta)=\begin{bmatrix}\cos\theta&-\sin\theta\\\sin\theta&\cos\theta\end{bmatrix}",
            ),
            MathTex(
                r"R(45^\circ)\vec{v}=\begin{bmatrix}\cos45^\circ&-\sin45^\circ\\\sin45^\circ&\cos45^\circ\end{bmatrix}\begin{bmatrix}1\\1\end{bmatrix}",
            ),
            MathTex(
                r"=\begin{bmatrix}\frac{\sqrt{2}}{2}&-\frac{\sqrt{2}}{2}\\\frac{\sqrt{2}}{2}&\frac{\sqrt{2}}{2}\end{bmatrix}\begin{bmatrix}1\\1\end{bmatrix}",
            ),
            MathTex(
                r"=\begin{bmatrix}\frac{\sqrt{2}}{2}-\frac{\sqrt{2}}{2}\\\frac{\sqrt{2}}{2}+\frac{\sqrt{2}}{2}\end{bmatrix}",
            ),
            MathTex(
                r"=\begin{bmatrix}0\\\sqrt{2}\end{bmatrix}",
            ),
        )
        steps.arrange(DOWN, aligned_edge=LEFT, buff=0.35)
        steps.scale(0.72)
        steps.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.2)

        self.play(Write(title), run_time=1)
        self.play(Create(axes), Write(axes_labels), run_time=1)
        self.play(GrowArrow(start_arrow), Write(start_label), run_time=1.5)
        self.wait(1)

        for step in steps:
            self.play(Write(step), run_time=1.5)
            self.wait(0.5)

        self.play(Create(angle_arc), Write(angle_label), run_time=1.5)
        self.play(
            Rotate(start_arrow, angle=theta, about_point=axes.c2p(0, 0)),
            Transform(start_label, rotated_label),
            run_time=3,
            rate_func=linear,
        )
        start_arrow.set_color(GREEN)
        self.wait(3)
