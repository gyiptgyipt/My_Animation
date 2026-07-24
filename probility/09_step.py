from manim import *
import numpy as np


class DrunkWalkParticlesfilter(Scene):
    def construct(self):
        self.camera.background_color = "#07111E"

        title = Text("Drunk Walk + Particle Filter", font_size=34, weight=BOLD, color=YELLOW)
        title.to_edge(UP, buff=0.25)
        self.play(Write(title), run_time=0.7)
        self.wait(0.2)

        map_frame = RoundedRectangle(
            width=6.8,
            height=4.4,
            corner_radius=0.2,
            color=GRAY_B,
            fill_color="#16253A",
            fill_opacity=0.95,
        )
        map_frame.move_to(LEFT * 2.2)
        self.play(FadeIn(map_frame), run_time=0.6)

        walls = VGroup(
            Rectangle(width=0.8, height=1.6, color=WHITE, fill_color=WHITE, fill_opacity=0.8).move_to([0.0, -0.1, 0]),
            Rectangle(width=1.2, height=0.5, color=WHITE, fill_color=WHITE, fill_opacity=0.8).move_to([1.6, 0.9, 0]),
            Rectangle(width=0.6, height=1.2, color=WHITE, fill_color=WHITE, fill_opacity=0.8).move_to([-1.4, 0.6, 0]),
        )
        walls.move_to(map_frame.get_center())
        self.play(FadeIn(walls), run_time=0.5)

        def to_map(x, y):
            left = map_frame.get_left()[0] + 0.28
            right = map_frame.get_right()[0] - 0.28
            bottom = map_frame.get_bottom()[1] + 0.28
            top = map_frame.get_top()[1] - 0.28
            return np.array([left + (x / 6.0) * (right - left), bottom + (y / 4.0) * (top - bottom), 0.0])

        robot = self.make_robot()
        robot.scale(0.35)
        robot.move_to(to_map(1.0, 1.4))
        self.play(FadeIn(robot), run_time=0.6)

        particle_states = [(1.1 + 0.15 * i, 1.35 + 0.08 * (i % 3)) for i in range(16)]
        particles = VGroup(*[Dot(to_map(x, y), radius=0.04, color=BLUE_B).set_opacity(0.85) for x, y in particle_states])
        self.play(LaggedStart(*[FadeIn(p, scale=0.7) for p in particles], lag_ratio=0.06), run_time=0.8)

        caption = Text("The robot moves forward 1 meter.\nThe particles wobble with Gaussian noise.", font_size=20, color=WHITE)
        caption.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.6)

        robot_target = to_map(2.1, 1.4)
        new_particle_targets = []
        for x, y in particle_states:
            noisy_x = np.clip(x + np.random.normal(0.0, 0.3), 0.3, 5.7)
            noisy_y = np.clip(y + np.random.normal(0.0, 0.22), 0.25, 3.75)
            new_particle_targets.append(to_map(noisy_x, noisy_y))

        self.play(robot.animate.move_to(robot_target), run_time=0.8)
        self.play(LaggedStart(*[p.animate.move_to(new_particle_targets[i]) for i, p in enumerate(particles)], lag_ratio=0.03), run_time=1.2)
        self.wait(0.3)

        gaussian_curve = self.make_gaussian_curve(mu=2.0, sigma=0.42)
        gaussian_curve.move_to(RIGHT * 2.6 + DOWN * 1.2)
        gaussian_curve.set_stroke(TEAL_B, width=3)
        gaussian_label = Text("Gaussian spread", font_size=20, color=TEAL_B)
        gaussian_label.next_to(gaussian_curve, UP, buff=0.15)
        self.play(FadeIn(gaussian_curve), FadeIn(gaussian_label), run_time=0.8)
        self.wait(0.4)

        wall = Line([to_map(3.2, 0.0)[0], map_frame.get_bottom()[1] + 0.2, 0], [to_map(3.2, 0.0)[0], map_frame.get_top()[1] - 0.2, 0], color=YELLOW, stroke_width=4)
        wall_label = Text("wall", font_size=18, color=YELLOW)
        wall_label.next_to(wall, RIGHT, buff=0.1)
        laser = Line(robot.get_center(), wall.get_center() + RIGHT * 0.0, color=YELLOW, stroke_width=3)
        self.play(FadeIn(wall), FadeIn(wall_label), Create(laser), run_time=0.6)

        good = []
        bad = []
        for i, p in enumerate(particles):
            px, py = p.get_center()[0], p.get_center()[1]
            world = np.array([px, py, 0.0])
            world_x = (world[0] - map_frame.get_left()[0]) / (map_frame.get_width() - 0.56)
            if abs((world_x * 6.0) - 3.2) < 0.45:
                good.append(i)
            else:
                bad.append(i)

        surviving = VGroup(*[particles[i] for i in good])
        dying = VGroup(*[particles[i] for i in bad])
        self.play(
            LaggedStart(*[p.animate.set_color(GREEN_B).scale(1.2) for p in surviving], lag_ratio=0.05),
            LaggedStart(*[p.animate.set_color(RED).set_opacity(0.2) for p in dying], lag_ratio=0.04),
            run_time=0.9,
        )
        self.play(*[p.animate.set_opacity(0) for p in dying], run_time=0.6)
        self.play(*[p.animate.move_to(robot.get_center() + RIGHT * (0.15 * (i - len(good) / 2)) + UP * 0.1) for i, p in enumerate(surviving)], run_time=0.8)

        score_panel = self.score_panel()
        score_panel.to_edge(RIGHT, buff=0.3).shift(UP * 0.25)
        self.play(FadeIn(score_panel, shift=LEFT * 0.15), run_time=0.6)
        self.wait(0.4)

        kitchen = Rectangle(width=2.4, height=1.8, color=GRAY_B, fill_color="#1D2F3A", fill_opacity=0.9)
        kitchen.move_to(RIGHT * 2.7 + UP * 0.2)
        kitchen_label = Text("kitchen", font_size=18, color=WHITE)
        kitchen_label.next_to(kitchen, UP, buff=0.1)
        living_room = Rectangle(width=2.4, height=1.8, color=GRAY_B, fill_color="#1D2F3A", fill_opacity=0.9)
        living_room.move_to(LEFT * 2.7 + UP * 0.2)
        living_label = Text("living room", font_size=18, color=WHITE)
        living_label.next_to(living_room, UP, buff=0.1)
        self.play(FadeIn(kitchen), FadeIn(kitchen_label), FadeIn(living_room), FadeIn(living_label), run_time=0.7)

        kidnapped_note = Text("A human moves the robot to the kitchen.\nThe old particles stay behind.", font_size=20, color=RED)
        kidnapped_note.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(kidnapped_note, shift=UP * 0.1), run_time=0.6)
        self.play(robot.animate.move_to(kitchen.get_center() + DOWN * 0.1), run_time=0.8)
        self.play(LaggedStart(*[p.animate.move_to(living_room.get_center() + np.array([0.16 * (i - 5), 0.12, 0.0])) for i, p in enumerate(surviving)], lag_ratio=0.04), run_time=1.0)

        final_text = Text("The robot has been kidnapped.\nThe particle cloud is now wrong.", font_size=24, color=YELLOW, weight=BOLD)
        final_text.to_edge(DOWN, buff=0.2)
        self.play(FadeIn(final_text), run_time=0.7)
        self.wait(1.6)

    def make_robot(self):
        body = RoundedRectangle(corner_radius=0.12, width=0.8, height=0.5, color=BLUE_B, fill_color=BLUE_B, fill_opacity=0.9)
        head = RoundedRectangle(corner_radius=0.12, width=0.55, height=0.35, color=BLUE_E, fill_color=BLUE_E, fill_opacity=1)
        head.next_to(body, UP, buff=0.05)
        eye_l = Dot(head.get_center() + LEFT * 0.12, radius=0.04, color=WHITE)
        eye_r = Dot(head.get_center() + RIGHT * 0.12, radius=0.04, color=WHITE)
        wheels = VGroup(
            Circle(radius=0.1, color=WHITE, fill_color=WHITE, fill_opacity=0.8).move_to(body.get_center() + LEFT * 0.25 + DOWN * 0.32),
            Circle(radius=0.1, color=WHITE, fill_color=WHITE, fill_opacity=0.8).move_to(body.get_center() + RIGHT * 0.25 + DOWN * 0.32),
        )
        return VGroup(body, head, eye_l, eye_r, wheels)

    def make_gaussian_curve(self, mu, sigma):
        xs = np.linspace(0.0, 4.0, 120)
        ys = np.exp(-0.5 * ((xs - mu) / sigma) ** 2)
        points = []
        for x, y in zip(xs, ys):
            points.append(np.array([x * 0.6 - 1.2, 0.35 + 1.0 * y * 0.9, 0.0]))
        curve = VMobject()
        curve.set_points_smoothly(points)
        return curve

    def score_panel(self):
        title = Text("Measurement update", font_size=22, color=GREEN_B, weight=BOLD)
        line1 = Text("Good matches stay", font_size=18, color=WHITE)
        line2 = Text("Bad matches disappear", font_size=18, color=WHITE)
        body = VGroup(title, line1, line2).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        box = RoundedRectangle(width=3.1, height=1.5, corner_radius=0.12, color=GREEN_B, fill_color=BLACK, fill_opacity=0.45)
        body.move_to(box)
        return VGroup(box, body)
