from manim import *


MYANMAR_FONT = "Noto Sans Myanmar"


class MotionModelSamplingTime(Scene):
    def construct(self):
        self.camera.background_color = "#0b1020"

        title = Text(
            "Sampling time (Δt) တိုင်းမှာ Computer က ဘာတွက်လဲ?",
            font=MYANMAR_FONT,
            font_size=29,
            weight=BOLD,
            color=WHITE,
        )
        subtitle = Text(
            "Differential Drive Odometry Motion Model",
            font_size=20,
            color=BLUE_B,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.08)
        header.to_edge(UP, buff=0.22)

        map_panel, axes, grid, path, robot, old_pose, new_pose = self.make_world_map()
        map_group = VGroup(map_panel, axes, grid, path, robot, old_pose, new_pose)
        map_group.to_edge(LEFT, buff=0.32).shift(DOWN * 0.12)

        speed_panel = self.make_speed_panel()
        speed_panel.to_edge(RIGHT, buff=0.34).shift(UP * 1.2)

        delta_panel = self.make_delta_panel()
        delta_panel.next_to(speed_panel, DOWN, buff=0.16)

        update_panel = self.make_update_panel()
        update_panel.next_to(delta_panel, DOWN, buff=0.16)

        computer = self.make_computer()
        computer.move_to(RIGHT * 0.82 + DOWN * 2.0)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.1), run_time=1.2)
        self.play(FadeIn(map_panel), Create(grid), Create(axes), run_time=1)
        self.play(FadeIn(old_pose), FadeIn(robot), run_time=0.9)
        self.wait(0.3)

        self.play(FadeIn(speed_panel, shift=LEFT * 0.25), FadeIn(computer, shift=UP * 0.15), run_time=0.9)
        self.animate_wheel_readings(speed_panel, computer)

        self.play(Circumscribe(speed_panel[2], color=GREEN_B, fade_out=True), run_time=0.9)
        self.play(FadeIn(delta_panel, shift=LEFT * 0.25), run_time=0.8)
        self.play(Circumscribe(delta_panel[1], color=YELLOW, fade_out=True), run_time=0.9)

        delta_s_arrow, delta_theta_arc = self.make_motion_marks(axes)
        self.play(Create(delta_s_arrow), Create(delta_theta_arc), run_time=1.1)
        self.play(FadeIn(update_panel, shift=LEFT * 0.25), run_time=0.8)
        self.play(Circumscribe(update_panel[1][0], color=YELLOW, fade_out=True), run_time=0.8)
        self.play(Create(path), run_time=0.9)

        robot_tracker = ValueTracker(0)
        start_pose = np.array([-1.2, -0.55, 0])
        end_pose = np.array([1.55, 0.82, 0])
        start_angle = 12 * DEGREES
        end_angle = 48 * DEGREES
        base_robot = self.make_robot_body().move_to(ORIGIN)

        def update_robot(mob):
            t = robot_tracker.get_value()
            pos = axes.c2p(
                interpolate(start_pose[0], end_pose[0], t),
                interpolate(start_pose[1], end_pose[1], t),
                0,
            )
            angle = interpolate(start_angle, end_angle, t)
            mob.become(base_robot.copy().rotate(angle).move_to(pos))

        robot.add_updater(update_robot)
        trace = VMobject(color=GREEN_B, stroke_width=6)
        trace.set_points_as_corners([axes.c2p(start_pose[0], start_pose[1], 0), axes.c2p(start_pose[0], start_pose[1], 0)])

        def update_trace(mob):
            t = robot_tracker.get_value()
            pts = []
            for alpha in np.linspace(0, t, 35):
                x = interpolate(start_pose[0], end_pose[0], alpha)
                y = interpolate(start_pose[1], end_pose[1], alpha) + 0.15 * np.sin(alpha * PI)
                pts.append(axes.c2p(x, y, 0))
            if len(pts) > 1:
                mob.set_points_smoothly(pts)

        trace.add_updater(update_trace)
        self.add(trace)
        self.play(
            robot_tracker.animate.set_value(1),
            run_time=4.0,
            rate_func=smooth,
        )
        robot.clear_updaters()
        trace.clear_updaters()

        new_pose.move_to(axes.c2p(-1.1, 1.35, 0))
        self.play(FadeIn(new_pose, shift=UP * 0.1), run_time=0.6)
        self.play(Circumscribe(update_panel[1][1], color=GREEN_B, fade_out=True), run_time=0.9)

        final_note = Text(
            "ဒါကြောင့် Δt တစ်ကြိမ်တိုင်းမှာ pose အသစ် (x, y, θ) ကို update လုပ်ပါတယ်။",
            font=MYANMAR_FONT,
            font_size=22,
            weight=BOLD,
            color=YELLOW,
        )
        final_note.to_edge(DOWN, buff=0.28)
        self.play(FadeIn(final_note, shift=UP * 0.2), run_time=0.9)
        self.wait(2.2)

    def make_world_map(self):
        panel = self.panel(width=6.2, height=4.25)
        axes = Axes(
            x_range=[-2.5, 2.8, 1],
            y_range=[-1.8, 1.8, 1],
            x_length=5.45,
            y_length=3.2,
            tips=True,
            axis_config={"color": BLUE_D, "stroke_width": 3},
        ).move_to(panel).shift(DOWN * 0.1)
        grid = VGroup()
        for x in np.arange(-2, 3, 1):
            grid.add(Line(axes.c2p(x, -1.6, 0), axes.c2p(x, 1.6, 0), color=GRAY_D, stroke_width=1))
        for y in np.arange(-1, 2, 1):
            grid.add(Line(axes.c2p(-2.35, y, 0), axes.c2p(2.55, y, 0), color=GRAY_D, stroke_width=1))

        start = axes.c2p(-1.2, -0.55, 0)
        end = axes.c2p(1.55, 1.24, 0)
        path = DashedVMobject(
            VMobject().set_points_smoothly([start, axes.c2p(0.0, -0.18, 0), axes.c2p(0.85, 0.45, 0), end]),
            num_dashes=18,
            color=GREEN_B,
            stroke_width=4,
        )
        robot = self.make_robot_body().rotate(12 * DEGREES).move_to(start)
        old_pose = Text("(x_old, y_old, θ_old)", font_size=15, color=GRAY_A).next_to(robot, DOWN, buff=0.14)
        new_pose = Text("(x_new, y_new, θ_new)", font_size=15, color=GREEN_B)
        return panel, axes, grid, path, robot, old_pose, new_pose

    def make_robot_body(self):
        body = RoundedRectangle(
            width=0.72,
            height=0.46,
            corner_radius=0.08,
            color=BLUE_B,
            fill_color="#102a4c",
            fill_opacity=0.95,
            stroke_width=3,
        )
        nose = Triangle(color=YELLOW, fill_color=YELLOW, fill_opacity=1).scale(0.13)
        nose.rotate(-PI / 2).next_to(body, RIGHT, buff=-0.02)
        left_wheel = Rectangle(width=0.12, height=0.58, color=TEAL_B, fill_color=TEAL_B, fill_opacity=1)
        right_wheel = left_wheel.copy()
        left_wheel.next_to(body, UP, buff=0.02)
        right_wheel.next_to(body, DOWN, buff=0.02)
        center = Dot(radius=0.055, color=WHITE)
        return VGroup(body, nose, left_wheel, right_wheel, center)

    def make_speed_panel(self):
        title = Text("1) Wheel speed မှ robot speed", font=MYANMAR_FONT, font_size=17, weight=BOLD, color=WHITE)
        left = self.value_row("v_L", "0.40 m/s", TEAL_B)
        right = self.value_row("v_R", "0.70 m/s", YELLOW)
        formulas = VGroup(
            Text("v = (v_R + v_L) / 2", font_size=20, color=GREEN_B),
            Text("ω = (v_R - v_L) / b", font_size=20, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.09)
        body = VGroup(title, left, right, formulas).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        panel = self.panel(width=4.62, height=1.72)
        self.fit_inside(body, panel)
        return VGroup(panel, title, formulas, body)

    def make_delta_panel(self):
        title = Text("2) Sampling time နဲ့မြှောက်", font=MYANMAR_FONT, font_size=17, weight=BOLD, color=WHITE)
        formulas = VGroup(
            Text("Δs = v * Δt", font_size=20, color=GREEN_B),
            Text("Δθ = ω * Δt", font_size=20, color=ORANGE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        note = Text("Δt = 0.1 s ဆိုပါစို့", font=MYANMAR_FONT, font_size=16, color=BLUE_B)
        body = VGroup(title, note, formulas).arrange(DOWN, aligned_edge=LEFT, buff=0.1)
        panel = self.panel(width=4.62, height=1.35)
        self.fit_inside(body, panel)
        return VGroup(panel, formulas, body)

    def make_update_panel(self):
        title = Text("3) World map ပေါ်မှာ pose update", font=MYANMAR_FONT, font_size=16, weight=BOLD, color=WHITE)
        x_formula = VGroup(
            Text("X_new = X_old + Δs *", font_size=15, color=GREEN_B),
            Text("cos(θ_old + Δθ / 2)", font_size=15, color=GREEN_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.03)
        y_formula = VGroup(
            Text("Y_new = Y_old + Δs *", font_size=15, color=GREEN_B),
            Text("sin(θ_old + Δθ / 2)", font_size=15, color=GREEN_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.03)
        formulas = VGroup(
            Text("θ_new = θ_old + Δθ", font_size=16, color=ORANGE),
            x_formula,
            y_formula,
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.07)
        body = VGroup(title, formulas).arrange(DOWN, aligned_edge=LEFT, buff=0.11)
        panel = self.panel(width=4.62, height=1.88)
        self.fit_inside(body, panel)
        return VGroup(panel, formulas, body)

    def make_computer(self):
        screen = RoundedRectangle(
            width=1.36,
            height=0.82,
            corner_radius=0.08,
            color=GRAY_B,
            fill_color="#111827",
            fill_opacity=0.95,
            stroke_width=2,
        )
        label = Text("Computer", font_size=15, color=WHITE).move_to(screen).shift(UP * 0.13)
        dt = Text("Δt", font_size=15, color=YELLOW).next_to(label, DOWN, buff=0.06)
        stand = VGroup(
            Line(DOWN * 0.41, DOWN * 0.66, color=GRAY_B, stroke_width=4),
            Line(LEFT * 0.32 + DOWN * 0.66, RIGHT * 0.32 + DOWN * 0.66, color=GRAY_B, stroke_width=4),
        )
        return VGroup(screen, label, dt, stand)

    def make_motion_marks(self, axes):
        delta_s_arrow = Arrow(
            axes.c2p(-1.2, -0.55, 0),
            axes.c2p(-0.25, -0.2, 0),
            color=GREEN_B,
            buff=0,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.18,
        )
        ds_label = Text("Δs", font_size=16, color=GREEN_B).next_to(delta_s_arrow, UP, buff=0.08)
        delta_theta_arc = Arc(
            radius=0.48,
            start_angle=12 * DEGREES,
            angle=36 * DEGREES,
            arc_center=axes.c2p(-0.18, -0.19, 0),
            color=ORANGE,
            stroke_width=5,
        )
        dtheta_label = Text("Δθ", font_size=15, color=ORANGE).next_to(delta_theta_arc, RIGHT, buff=0.06)
        return VGroup(delta_s_arrow, ds_label), VGroup(delta_theta_arc, dtheta_label)

    def animate_wheel_readings(self, speed_panel, computer):
        dots = VGroup()
        start_left = speed_panel.get_left() + LEFT * 0.1 + DOWN * 0.15
        target = computer.get_top() + UP * 0.05
        for i in range(10):
            color = TEAL_B if i % 2 == 0 else YELLOW
            dots.add(Dot(start_left + DOWN * (i * 0.03), radius=0.04, color=color))
        self.play(
            LaggedStart(
                *[
                    dot.animate.move_to(target + RIGHT * ((i - 4.5) * 0.08))
                    for i, dot in enumerate(dots)
                ],
                lag_ratio=0.08,
            ),
            run_time=1.4,
        )
        self.play(FadeOut(dots), run_time=0.25)

    def value_row(self, label, value, color):
        return VGroup(
            Text(label, font_size=20, color=color),
            Text("=", font_size=18, color=GRAY_A),
            Text(value, font_size=18, color=WHITE),
        ).arrange(RIGHT, buff=0.12)

    def fit_inside(self, body, panel, padding=0.24):
        max_width = panel.width - padding
        max_height = panel.height - padding
        scale = min(max_width / body.width, max_height / body.height, 1)
        body.scale(scale)
        body.move_to(panel)

    def panel(self, width, height):
        return RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.08,
            color=GRAY_B,
            fill_color="#111827",
            fill_opacity=0.9,
            stroke_width=2,
        )
