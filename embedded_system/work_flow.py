from manim import *


# Render with: manim -pqh embedded_system/work_flow.py RobotControlLoop
class RobotControlLoop(Scene):
    """A visual walkthrough of the embedded velocity-control loop in a mobile robot."""

    BG = "#0B1020"
    PANEL = "#151E34"
    PANEL_DIM = "#10182A"
    TEXT_MUTED = "#9DACCC"
    CYAN = "#36D1DC"
    BLUE = "#5B8CFF"
    YELLOW = "#FFD166"
    GREEN = "#5EE6A8"
    PINK = "#F970A7"

    def construct(self):
        self.camera.background_color = self.BG

        title = Text("What happens when a robot hears…", font_size=29,
                     color=self.TEXT_MUTED)
        title.move_to(UP * 3.5)
        command = Text('“GO FORWARD”', font_size=39, weight=BOLD, color=self.YELLOW)
        command.next_to(title, DOWN, buff=0.08)
        command_box = SurroundingRectangle(command, color=self.YELLOW, buff=0.16,
                                            corner_radius=0.12, stroke_width=2)

        road = Line(LEFT * 6.6 + UP * 2.27, RIGHT * 6.6 + UP * 2.27,
                    color="#405070", stroke_width=3)
        dashes = VGroup(*[
            Line(LEFT * 0.35, RIGHT * 0.35, color="#5E7097", stroke_width=3)
            .move_to([x, 2.27, 0]) for x in np.arange(-5.7, 6.1, 1.5)
        ])
        robot = self.make_robot().move_to(LEFT * 4.9 + UP * 2.65)
        # Keeping the robot unlabelled here leaves the opening uncluttered.
        motion_arrow = Arrow(LEFT * 3.5 + UP * 2.65, LEFT * 2.35 + UP * 2.65,
                             buff=0.08, color=self.GREEN, stroke_width=5)

        self.play(FadeIn(title, shift=DOWN * 0.15),
                  FadeIn(command, shift=DOWN * 0.15), Create(command_box), run_time=1.0)
        self.play(Create(road), FadeIn(dashes), FadeIn(robot, shift=RIGHT * 0.3),
                  GrowArrow(motion_arrow), run_time=1.0)

        cards = [
            self.card("1", "Navigation", "target velocity", self.BLUE),
            self.card("2", "ROS", "velocity command", self.CYAN),
            self.card("3", "Motor controller", "speed control", self.YELLOW, width=3.35),
            self.card("4", "Microcontroller", "PWM signals", self.PINK, width=3.35),
            self.card("5", "Motor", "spins wheels", self.GREEN),
            self.card("6", "Encoder", "measures motion", self.CYAN),
        ]
        # A serpentine layout makes the signal direction and return path readable.
        for card, point in zip(cards, [
            [-4.25, 0.42, 0], [0, 0.42, 0], [4.25, 0.42, 0],
            [4.25, -1.32, 0], [0, -1.32, 0], [-4.25, -1.32, 0],
        ]):
            card.scale(0.90).move_to(point)

        arrows = VGroup(
            self.arrow_between(cards[0], cards[1], self.TEXT_MUTED),
            self.arrow_between(cards[1], cards[2], self.TEXT_MUTED),
        )
        controller_to_mcu = Arrow(cards[2].get_bottom(), cards[3].get_top(), buff=.12,
                                  color=self.TEXT_MUTED, stroke_width=3, tip_length=.14)
        controller_to_ros = CurvedArrow(cards[2].get_top() + UP * .12 + LEFT * .18,
                                       cards[1].get_top() + UP * .10 + RIGHT * .18,
                                       angle=TAU / 2.8, color=self.CYAN,
                                       stroke_width=3, tip_length=0.14)
        mcu_to_motor = Arrow(cards[3].get_left(), cards[4].get_right(), buff=.08,
                             color=self.TEXT_MUTED, stroke_width=3, tip_length=.13)
        motor_to_encoder = Arrow(cards[4].get_left(), cards[5].get_right(), buff=.08,
                                 color=self.TEXT_MUTED, stroke_width=3, tip_length=.13)
        feedback = CurvedArrow(cards[5].get_bottom() + DOWN * .08,
                               cards[2].get_bottom() + DOWN * .10,
                               angle=-TAU / 2.8, color=self.CYAN,
                               stroke_width=3, tip_length=0.14)
        feedback_label = Text("actual speed feedback", font_size=16, color=self.CYAN)
        feedback_label.move_to(DOWN * 2.48 + RIGHT * 0.65)
        ros_feedback_label = Text("status feedback", font_size=16, color=self.CYAN)
        ros_feedback_label.move_to(UP * 1.82 + RIGHT * 1.2)

        workflow_label = Text("THE CLOSED-LOOP WORKFLOW", font_size=18,
                              weight=BOLD, color=self.TEXT_MUTED)
        workflow_label.to_edge(LEFT, buff=.45).move_to(UP * 1.15 + LEFT * 4.55)
        caption = Text("A simple instruction starts a fast control loop.", font_size=25,
                       color=WHITE)
        caption.move_to(DOWN * 3.27)

        self.play(Write(workflow_label), *[FadeIn(c, shift=UP * .16) for c in cards],
                  run_time=1.4)
        self.play(Create(arrows), Create(controller_to_mcu), Create(controller_to_ros),
                  Create(mcu_to_motor), Create(motor_to_encoder),
                  Create(feedback), FadeIn(feedback_label), FadeIn(ros_feedback_label),
                  FadeIn(caption), run_time=1.2)

        stages = [
            (cards[0], "Navigation calculates a target velocity.", self.BLUE),
            (cards[1], "ROS sends the velocity command.", self.CYAN),
            (cards[2], "The motor controller compares and controls speed.", self.YELLOW),
            (cards[3], "A microcontroller turns that into PWM signals.", self.PINK),
            (cards[4], "The motor spins — and the robot moves forward.", self.GREEN),
            (cards[5], "An encoder measures what really happened.", self.CYAN),
        ]

        for index, (active, words, color) in enumerate(stages):
            new_caption = Text(words, font_size=25, color=WHITE).move_to(caption)
            self.play(Transform(caption, new_caption), self.highlight(active, color), run_time=.55)
            if index < 2:
                self.play(self.pulse_on(arrows[index], color), run_time=.55)
            elif index == 2:
                self.wait(.35)
            elif index == 3:
                self.play(self.pulse_on(controller_to_mcu, color), run_time=.55)
            elif index == 4:
                self.play(self.pulse_on(mcu_to_motor, color),
                          robot.animate.shift(RIGHT * 2.45),
                          motion_arrow.animate.shift(RIGHT * 2.45), run_time=1.1)
            else:
                self.play(self.pulse_on(motor_to_encoder, color), run_time=.65)

        loop_caption = Text("Desired speed  ↔  actual speed  →  adjust motor output",
                            font_size=28, weight=BOLD, color=self.YELLOW).move_to(caption)
        loop_ring = SurroundingRectangle(cards[2], color=self.YELLOW, buff=.10,
                                         corner_radius=.12, stroke_width=4)
        self.play(Transform(caption, loop_caption), Create(loop_ring),
                  Indicate(cards[2], color=self.YELLOW, scale_factor=1.05), run_time=1.2)
        self.play(self.pulse_on(feedback, self.CYAN),
                  self.pulse_on(controller_to_ros, self.CYAN),
                  self.pulse_on(controller_to_mcu, self.PINK), run_time=1.25)
        final = Text("Embedded engineering makes this loop happen continuously very fast.",
                     font_size=25, color=self.GREEN).move_to(caption)
        self.play(Transform(caption, final), Flash(cards[2].get_center(), color=self.YELLOW,
                                                   flash_radius=.7, line_length=.15), run_time=1)
        self.wait(2)

    def card(self, number, title, detail, color, width=2.67):
        box = RoundedRectangle(width=width, height=1.02, corner_radius=.14,
                               stroke_color="#334563", stroke_width=2,
                               fill_color=self.PANEL, fill_opacity=1)
        box.set_z_index(1)
        badge = Circle(radius=.19, color=color, fill_color=color, fill_opacity=1,
                       stroke_width=0).move_to(box.get_left() + RIGHT * .32 + UP * .22)
        badge.set_z_index(3)
        num = Text(number, font_size=16, color=self.BG, weight=BOLD).move_to(badge)
        num.set_z_index(4)
        heading = Text(title, font_size=20, weight=BOLD, color=WHITE)
        heading.next_to(badge, RIGHT, buff=.13).align_to(badge, UP)
        heading.set_z_index(3)
        sub = Text(detail, font_size=15, color=self.TEXT_MUTED)
        sub.move_to(box.get_center() + DOWN * .24)
        sub.set_z_index(3)
        return VGroup(box, badge, num, heading, sub)

    def arrow_between(self, left, right, color):
        return Arrow(left.get_right() + RIGHT * .03, right.get_left() + LEFT * .03,
                     buff=0.07, color=color, stroke_width=3, tip_length=.13)

    def highlight(self, card, color):
        return AnimationGroup(
            *[c[0].animate.set_fill(self.PANEL_DIM, opacity=1).set_stroke("#263652", width=2)
              for c in self.current_cards_except(card)],
            card[0].animate.set_fill("#24314D", opacity=1).set_stroke(color, width=4),
            lag_ratio=0,
        )

    def current_cards_except(self, active):
        # All card groups currently on screen except the active one.
        return [m for m in self.mobjects if isinstance(m, VGroup) and len(m) == 5 and m is not active]

    def pulse_on(self, path, color):
        dot = Dot(color=color, radius=.075).move_to(path.get_start())
        return Succession(FadeIn(dot, scale=.5), MoveAlongPath(dot, path), FadeOut(dot, scale=.5))

    def make_robot(self):
        body = RoundedRectangle(width=1.25, height=.66, corner_radius=.16,
                                color=self.CYAN, fill_color="#1D3F5C", fill_opacity=1.0,
                                stroke_width=3)
        wheel_l = Circle(radius=.19, color="#1B2437", fill_color="#1B2437", fill_opacity=1)
        wheel_r = wheel_l.copy()
        wheel_l.move_to(body.get_bottom() + LEFT * .38 + DOWN * .06)
        wheel_r.move_to(body.get_bottom() + RIGHT * .38 + DOWN * .06)
        sensor = RoundedRectangle(width=.26, height=.18, corner_radius=.04, color=self.YELLOW,
                                 fill_color=self.YELLOW, fill_opacity=1, stroke_width=0)
        sensor.move_to(body.get_right() + LEFT * .09)
        antenna = Line(body.get_top() + LEFT * .26, body.get_top() + LEFT * .38 + UP * .27,
                       color=self.CYAN, stroke_width=3)
        antenna_dot = Dot(antenna.get_end(), radius=.045, color=self.CYAN)
        return VGroup(wheel_l, wheel_r, body, sensor, antenna, antenna_dot)
