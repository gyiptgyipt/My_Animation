from manim import *


MYANMAR_FONT = "Noto Sans Myanmar"


class EncoderCountCalculation(Scene):
    def construct(self):
        self.camera.background_color = "#0b1020"

        title = Text(
            "Motor Encoder Count Calculation",
            font_size=42,
            weight=BOLD,
            color=WHITE,
        )
        subtitle = Text(
            "Pulse ပေါင်း 2,000 ထွက်တဲ့ Motor တစ်ခု ဆိုပါစို့",
            font=MYANMAR_FONT,
            font_size=26,
            color=BLUE_B,
        )
        header = VGroup(title, subtitle).arrange(DOWN, buff=0.12)
        header.to_edge(UP, buff=0.35)

        ground = Line(LEFT * 5.65 + DOWN * 1.7, RIGHT * 4.9 + DOWN * 1.7, color=GRAY_B, stroke_width=5)
        ruler = self.make_ruler(ground)
        wheel_radius = 0.75
        start_x = ground.get_start()[0] + 0.45
        goal_x = ground.get_end()[0] - 0.45
        wheel_start = np.array([start_x, ground.get_y() + wheel_radius, 0])
        wheel_goal = np.array([goal_x, ground.get_y() + wheel_radius, 0])

        wheel_group = self.make_wheel()
        wheel_group.move_to(wheel_start)

        pulse_panel = self.make_pulse_panel()
        pulse_panel.to_edge(RIGHT, buff=0.55).shift(UP * 0.6)

        formula_panel = self.make_formula_panel()
        formula_panel.to_edge(LEFT, buff=0.55).shift(UP * 0.45)

        distance_panel = self.make_distance_panel()
        distance_panel.to_edge(DOWN, buff=0.35)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.12), run_time=1.2)
        self.play(Create(ground), FadeIn(ruler), FadeIn(wheel_group), run_time=1.1)
        self.wait(0.4)

        self.play(FadeIn(pulse_panel, shift=LEFT * 0.25), run_time=0.8)
        self.emit_pulses(wheel_group, pulse_panel)

        self.play(FadeIn(formula_panel, shift=RIGHT * 0.25), run_time=0.9)
        self.wait(0.7)

        tick_tracker = ValueTracker(0)
        distance_tracker = ValueTracker(0)
        tick_number = DecimalNumber(0, num_decimal_places=0, group_with_commas=True, font_size=35, color=YELLOW)
        tick_number.add_updater(lambda m: m.set_value(tick_tracker.get_value()))
        dist_number = DecimalNumber(0, num_decimal_places=2, font_size=35, color=GREEN_B)
        dist_number.add_updater(lambda m: m.set_value(distance_tracker.get_value()))

        live_row = VGroup(
            Text("Ticks ဖတ်ရသော အရေအတွက် =", font=MYANMAR_FONT, font_size=25, color=WHITE),
            tick_number,
        ).arrange(RIGHT, buff=0.2)
        live_row.next_to(distance_panel, UP, buff=0.18)

        meter_row = VGroup(
            Text("Distance =", font_size=27, color=WHITE),
            dist_number,
            Text("m", font_size=27, color=GREEN_B),
        ).arrange(RIGHT, buff=0.14)
        meter_row.next_to(live_row, DOWN, buff=0.16)

        self.play(FadeIn(live_row), FadeIn(meter_row), run_time=0.7)

        roll_tracker = ValueTracker(0)
        wheel_body = wheel_group[0]
        wheel_label = wheel_group[1]
        base_wheel_body = wheel_body.copy().move_to(ORIGIN)

        def update_wheel(body):
            progress = roll_tracker.get_value()
            center = interpolate(wheel_start, wheel_goal, progress)
            travel = (goal_x - start_x) * progress
            body.become(base_wheel_body.copy().rotate(-travel / wheel_radius).move_to(center))
            wheel_label.next_to(body, DOWN, buff=0.2)

        wheel_body.add_updater(update_wheel)
        self.play(
            roll_tracker.animate.set_value(1),
            tick_tracker.animate.set_value(100000),
            distance_tracker.animate.set_value(15.7),
            run_time=5,
            rate_func=linear,
        )
        wheel_body.clear_updaters()
        tick_number.clear_updaters()
        dist_number.clear_updaters()

        final_answer = Text(
            "Tick 100,000 ဖတ်ရရင် -> 15.7 မီတာ လျှောက်ခဲ့တာပေါ့!",
            font=MYANMAR_FONT,
            font_size=31,
            weight=BOLD,
            color=YELLOW,
        )
        final_answer.to_edge(DOWN, buff=0.42)
        self.play(Transform(distance_panel, final_answer), run_time=0.9)
        self.play(Circumscribe(final_answer, color=YELLOW, fade_out=True), run_time=1.1)
        self.wait(2.5)

    def make_wheel(self):
        tire = Circle(radius=0.75, color=BLUE_B, stroke_width=8)
        hub = Circle(radius=0.13, color=YELLOW, fill_color=YELLOW, fill_opacity=1)
        spokes = VGroup()
        for angle in [0, PI / 3, 2 * PI / 3, PI, 4 * PI / 3, 5 * PI / 3]:
            spokes.add(Line(ORIGIN, 0.66 * np.array([np.cos(angle), np.sin(angle), 0]), color=WHITE, stroke_width=3))
        tick_marks = VGroup()
        for angle in np.linspace(0, TAU, 24, endpoint=False):
            outer = 0.83 * np.array([np.cos(angle), np.sin(angle), 0])
            inner = 0.72 * np.array([np.cos(angle), np.sin(angle), 0])
            tick_marks.add(Line(inner, outer, color=TEAL_B, stroke_width=2))
        diameter = Line(LEFT * 0.75, RIGHT * 0.75, color=YELLOW, stroke_width=4)
        body = VGroup(tire, spokes, hub, tick_marks, diameter)
        label = Text("10 cm", font_size=22, color=YELLOW).next_to(body, DOWN, buff=0.2)
        return VGroup(body, label)

    def make_ruler(self, ground):
        marks = VGroup()
        for i in range(9):
            x = interpolate(ground.get_start()[0] + 0.45, ground.get_end()[0] - 0.45, i / 8)
            mark = Line([x, -1.62, 0], [x, -1.86, 0], color=GRAY_A, stroke_width=2)
            marks.add(mark)
        start = Text("start", font_size=18, color=GRAY_A).next_to(marks[0], DOWN, buff=0.08)
        end = Text("15.7 m", font_size=18, color=GREEN_B).next_to(marks[-1], DOWN, buff=0.08)
        return VGroup(marks, start, end)

    def make_pulse_panel(self):
        title = Text("Encoder pulses", font_size=18, weight=BOLD, color=WHITE)
        motor = RoundedRectangle(
            width=1.25,
            height=0.45,
            corner_radius=0.08,
            color=BLUE_B,
            fill_color="#101b38",
            fill_opacity=0.9,
        )
        motor_text = Text("Motor", font_size=15, color=BLUE_B).move_to(motor)
        sensor = VGroup(
            Rectangle(width=0.32, height=0.65, color=YELLOW, fill_color="#302700", fill_opacity=0.85),
            Text("A/B", font_size=12, color=YELLOW),
        )
        sensor[1].move_to(sensor[0])
        sensor.next_to(motor, RIGHT, buff=0.1)
        pulse_note = Text("2,000 ticks / rev", font_size=15, color=YELLOW)
        body = VGroup(VGroup(motor, motor_text, sensor), pulse_note).arrange(DOWN, buff=0.14)
        panel = self.panel(width=2.25, height=1.38)
        VGroup(title, body).arrange(DOWN, buff=0.12).move_to(panel)
        return VGroup(panel, title, body)

    def make_formula_panel(self):
        lines = VGroup(
            Text("Formula", font_size=28, weight=BOLD, color=WHITE),
            Text("Distance per Tick", font_size=25, color=BLUE_B),
            Text("= (pi x ဘီးအချင်း) / Tick အရေအတွက်", font=MYANMAR_FONT, font_size=22, color=WHITE),
            Text("= (3.14 x 10 cm) / 2,000", font_size=23, color=GRAY_A),
            Text("= 0.0157 cm / tick", font_size=27, weight=BOLD, color=GREEN_B),
        )
        lines.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        panel = self.panel(width=5.45, height=2.75)
        lines.move_to(panel)
        return VGroup(panel, lines)

    def make_distance_panel(self):
        panel = self.panel(width=6.7, height=0.82)
        text = Text(
            "Distance = Tick Count x Distance per Tick",
            font_size=27,
            color=WHITE,
        ).move_to(panel)
        return VGroup(panel, text)

    def panel(self, width, height):
        return RoundedRectangle(
            width=width,
            height=height,
            corner_radius=0.08,
            color=GRAY_B,
            fill_color="#111827",
            fill_opacity=0.88,
            stroke_width=2,
        )

    def emit_pulses(self, wheel_group, pulse_panel):
        origin = wheel_group.get_right() + RIGHT * 0.08 + UP * 0.38
        target = pulse_panel.get_left() + LEFT * 0.08 + DOWN * 0.15
        pulse_dots = VGroup()
        pulse_lines = VGroup()
        for i in range(12):
            y_offset = ((i % 4) - 1.5) * 0.16
            dot = Dot(origin + UP * y_offset, radius=0.045, color=YELLOW)
            pulse_dots.add(dot)
            if i % 2 == 0:
                pulse_lines.add(Line(origin + UP * y_offset, target + UP * y_offset, color=YELLOW, stroke_width=1.5, stroke_opacity=0.4))
        self.play(Create(pulse_lines), run_time=0.5)
        self.play(
            LaggedStart(
                *[
                    dot.animate.move_to(target + UP * (((i % 4) - 1.5) * 0.16))
                    for i, dot in enumerate(pulse_dots)
                ],
                lag_ratio=0.08,
            ),
            run_time=1.7,
        )
        self.play(FadeOut(pulse_dots), FadeOut(pulse_lines), run_time=0.35)
