from math import sqrt

from manim import *
import numpy as np


class ProbabilityAnimation(Scene):
    def construct(self):
        true_pose = np.array([3.2, 2.4])
        x_candidates = np.array([2.6, 2.9, 3.2, 3.5, 3.8])
        y_candidates = np.array([1.8, 2.1, 2.4, 2.7, 3.0])
        motion_prediction = np.array([3.05, 2.15])
        sensor_measurement = np.array([3.25, 2.35])
        motion_sigma_x = 0.42
        motion_sigma_y = 0.36
        sigma_x = 0.32
        sigma_y = 0.28

        x_motion_prior = self.gaussian_likelihood(x_candidates, motion_prediction[0], motion_sigma_x)
        y_motion_prior = self.gaussian_likelihood(y_candidates, motion_prediction[1], motion_sigma_y)
        x_sensor_likelihood = self.gaussian_likelihood(x_candidates, sensor_measurement[0], sigma_x)
        y_sensor_likelihood = self.gaussian_likelihood(y_candidates, sensor_measurement[1], sigma_y)
        x_posterior_scores = x_motion_prior * x_sensor_likelihood
        y_posterior_scores = y_motion_prior * y_sensor_likelihood
        x_probabilities = x_posterior_scores / np.sum(x_posterior_scores)
        y_probabilities = y_posterior_scores / np.sum(y_posterior_scores)
        best_x = float(x_candidates[np.argmax(x_probabilities)])
        best_y = float(y_candidates[np.argmax(y_probabilities)])
        chosen_pose = np.array([best_x, best_y])

        title = Text("Robot Localization: Choose X and Y by Probability", font_size=32, weight=BOLD)
        title.to_edge(UP, buff=0.3)
        self.play(Write(title), run_time=0.8)

        inputs = self.make_input_view(
            motion_prediction,
            sensor_measurement,
            motion_sigma_x,
            motion_sigma_y,
            sigma_x,
            sigma_y,
        )
        self.play(FadeIn(inputs, shift=UP * 0.12), run_time=1.0)
        self.wait(2.5)
        self.play(FadeOut(inputs), run_time=0.7)

        x_section = self.make_probability_axis(
            "X possibility",
            x_candidates,
            x_probabilities,
            sensor_measurement[0],
            best_x,
            BLUE,
        )
        x_section.to_edge(LEFT, buff=0.65).shift(UP * 0.35)

        y_section = self.make_probability_axis(
            "Y possibility",
            y_candidates,
            y_probabilities,
            sensor_measurement[1],
            best_y,
            GREEN,
        )
        y_section.to_edge(RIGHT, buff=0.65).shift(UP * 0.35)

        self.play(FadeIn(x_section[0]), Create(x_section[1]), run_time=0.9)
        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in x_section[2]], lag_ratio=0.1),
            FadeIn(x_section[3], shift=UP * 0.1),
            run_time=1.0,
        )
        self.play(FadeIn(x_section[4], shift=UP * 0.1), run_time=0.7)

        self.play(FadeIn(y_section[0]), Create(y_section[1]), run_time=0.9)
        self.play(
            LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in y_section[2]], lag_ratio=0.1),
            FadeIn(y_section[3], shift=UP * 0.1),
            run_time=1.0,
        )
        self.play(FadeIn(y_section[4], shift=UP * 0.1), run_time=0.7)

        chosen_text = Text(
            f"Choose position = ({best_x:.1f}, {best_y:.1f}) m",
            font_size=30,
            color=YELLOW,
            weight=BOLD,
        )
        chosen_text.to_edge(DOWN, buff=0.35)
        self.play(FadeIn(chosen_text, shift=UP * 0.1), run_time=0.8)
        self.wait(1.2)

        self.play(
            FadeOut(x_section),
            FadeOut(y_section),
            FadeOut(chosen_text),
            run_time=0.8,
        )

        calculation = self.make_calculation_view(
            x_candidates,
            x_motion_prior,
            x_sensor_likelihood,
            x_posterior_scores,
            x_probabilities,
            y_candidates,
            y_motion_prior,
            y_sensor_likelihood,
            y_posterior_scores,
            y_probabilities,
            motion_prediction,
            sensor_measurement,
            motion_sigma_x,
            motion_sigma_y,
            sigma_x,
            sigma_y,
            chosen_pose,
        )
        title.generate_target()
        title.target.become(Text("Why This Position Wins", font_size=32, weight=BOLD))
        title.target.to_edge(UP, buff=0.3)
        self.play(MoveToTarget(title), FadeIn(calculation, shift=UP * 0.12), run_time=1.0)
        self.wait(4)
        self.play(FadeOut(calculation), run_time=0.8)

        self.show_rviz_view(
            title,
            true_pose,
            motion_prediction,
            sensor_measurement,
            chosen_pose,
            sigma_x,
            sigma_y,
        )

    def gaussian_likelihood(self, candidates, measurement, sigma):
        return np.exp(-0.5 * ((candidates - measurement) / sigma) ** 2)

    def normal_weights(self, candidates, mean, sigma):
        weights = self.gaussian_likelihood(candidates, mean, sigma)
        return weights / np.sum(weights)

    def make_input_view(
        self,
        motion_prediction,
        sensor_measurement,
        motion_sigma_x,
        motion_sigma_y,
        sensor_sigma_x,
        sensor_sigma_y,
    ):
        motion_card = self.make_input_card(
            "Motion model input",
            [
                "previous pose + wheel odometry",
                f"predicted pose = ({motion_prediction[0]:.2f}, {motion_prediction[1]:.2f})",
                f"motion noise = ({motion_sigma_x:.2f}, {motion_sigma_y:.2f})",
            ],
            RED,
        )
        sensor_card = self.make_input_card(
            "Sensor model input",
            [
                "landmark / scan matching measurement",
                f"measured pose = ({sensor_measurement[0]:.2f}, {sensor_measurement[1]:.2f})",
                f"sensor noise = ({sensor_sigma_x:.2f}, {sensor_sigma_y:.2f})",
            ],
            YELLOW,
        )
        arrow = Arrow(LEFT * 1.0, RIGHT * 1.0, color=GRAY_A, stroke_width=5)
        output = self.make_input_card(
            "Localization output",
            [
                "posterior = motion prior x sensor likelihood",
                "choose max posterior probability",
                "then draw chosen pose in RViz",
            ],
            BLUE,
        )
        group = VGroup(motion_card, sensor_card, arrow, output).arrange(RIGHT, buff=0.38)
        group.scale(0.92)
        group.move_to(DOWN * 0.15)
        return group

    def make_input_card(self, title, lines, color):
        heading = Text(title, font_size=24, color=color, weight=BOLD)
        body = VGroup(*[Text(line, font_size=18, color=WHITE) for line in lines])
        body.arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        content = VGroup(heading, body).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        box = RoundedRectangle(
            width=3.65,
            height=2.15,
            corner_radius=0.08,
            color=color,
            fill_color=BLACK,
            fill_opacity=0.35,
            stroke_width=2,
        )
        content.move_to(box)
        return VGroup(box, content)

    def make_calculation_view(
        self,
        x_candidates,
        x_motion_prior,
        x_sensor_likelihood,
        x_posterior_scores,
        x_probabilities,
        y_candidates,
        y_motion_prior,
        y_sensor_likelihood,
        y_posterior_scores,
        y_probabilities,
        motion_prediction,
        sensor_measurement,
        motion_sigma_x,
        motion_sigma_y,
        sigma_x,
        sigma_y,
        chosen_pose,
    ):
        formula = VGroup(
            Text("Localization combines motion prediction and sensor measurement.", font_size=23, color=GRAY_A),
            MathTex(
                r"\text{posterior}(p_i)=\text{motion prior}(p_i)\times\text{sensor likelihood}(p_i)",
                font_size=34,
                color=WHITE,
            ),
            MathTex(
                r"P(p_i)=\frac{\text{posterior}(p_i)}{\sum \text{posterior}(p)}",
                font_size=34,
                color=WHITE,
            ),
        ).arrange(DOWN, buff=0.18)
        formula.to_edge(UP, buff=1.05)

        x_table = self.make_calculation_table(
            "X calculation",
            "x",
            x_candidates,
            motion_prediction[0],
            sensor_measurement[0],
            motion_sigma_x,
            sigma_x,
            x_motion_prior,
            x_sensor_likelihood,
            x_posterior_scores,
            x_probabilities,
            BLUE,
        )
        x_table.to_edge(LEFT, buff=0.55).shift(DOWN * 0.55)

        y_table = self.make_calculation_table(
            "Y calculation",
            "y",
            y_candidates,
            motion_prediction[1],
            sensor_measurement[1],
            motion_sigma_y,
            sigma_y,
            y_motion_prior,
            y_sensor_likelihood,
            y_posterior_scores,
            y_probabilities,
            GREEN,
        )
        y_table.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.55)

        result = Text(
            f"Highest probabilities: x = {chosen_pose[0]:.1f} m, y = {chosen_pose[1]:.1f} m",
            font_size=27,
            color=YELLOW,
            weight=BOLD,
        )
        result.to_edge(DOWN, buff=0.35)

        return VGroup(formula, x_table, y_table, result)

    def make_calculation_table(
        self,
        title,
        axis_name,
        candidates,
        motion_value,
        measurement,
        motion_sigma,
        sigma,
        motion_prior,
        sensor_likelihood,
        posterior_scores,
        probabilities,
        color,
    ):
        heading = Text(
            f"{title}: motion {axis_name}={motion_value:.2f}, sensor {axis_name}={measurement:.2f}",
            font_size=18,
            color=color,
            weight=BOLD,
        )

        headers = VGroup(
            Text(axis_name, font_size=17, color=GRAY_A),
            Text("prior", font_size=17, color=GRAY_A),
            Text("sensor", font_size=17, color=GRAY_A),
            Text("post.", font_size=17, color=GRAY_A),
            Text("prob.", font_size=17, color=GRAY_A),
        ).arrange(RIGHT, buff=0.26)

        rows = VGroup()
        best_index = int(np.argmax(probabilities))
        for index, (candidate, prior, likelihood, posterior, probability) in enumerate(
            zip(candidates, motion_prior, sensor_likelihood, posterior_scores, probabilities)
        ):
            row_color = YELLOW if index == best_index else WHITE
            row = VGroup(
                Text(f"{candidate:.1f}", font_size=17, color=row_color),
                Text(f"{prior:.2f}", font_size=17, color=row_color),
                Text(f"{likelihood:.2f}", font_size=17, color=row_color),
                Text(f"{posterior:.2f}", font_size=17, color=row_color),
                Text(f"{probability * 100:.1f}%", font_size=17, color=row_color),
            ).arrange(RIGHT, buff=0.31)
            rows.add(row)

        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        headers.next_to(heading, DOWN, aligned_edge=LEFT, buff=0.22)
        rows.next_to(headers, DOWN, aligned_edge=LEFT, buff=0.15)

        box = RoundedRectangle(
            width=5.15,
            height=2.55,
            corner_radius=0.08,
            color=color,
            fill_color=BLACK,
            fill_opacity=0.35,
            stroke_width=2,
        )
        content = VGroup(heading, headers, rows)
        content.move_to(box)
        return VGroup(box, content)

    def make_probability_axis(self, heading, candidates, probabilities, measurement, chosen, color):
        axis = NumberLine(
            x_range=[float(candidates[0]) - 0.3, float(candidates[-1]) + 0.3, 0.3],
            length=4.7,
            include_numbers=True,
            font_size=18,
            color=GRAY_B,
        )

        label = Text(heading, font_size=25, color=color, weight=BOLD)
        label.next_to(axis, UP, buff=0.35)

        bars = VGroup()
        bar_labels = VGroup()
        for value, probability in zip(candidates, probabilities):
            bar = Rectangle(
                width=0.34,
                height=2.4 * float(probability),
                color=color,
                fill_color=color,
                fill_opacity=0.55,
                stroke_width=2,
            )
            bar.next_to(axis.n2p(float(value)), UP, buff=0)
            bars.add(bar)

            percent = Text(f"{probability * 100:.0f}%", font_size=15, color=WHITE)
            percent.next_to(bar, UP, buff=0.05)
            bar_labels.add(percent)

        measurement_marker = Triangle(
            color=YELLOW,
            fill_color=YELLOW,
            fill_opacity=0.9,
            stroke_width=0,
        ).scale(0.12)
        measurement_marker.rotate(PI)
        measurement_marker.next_to(axis.n2p(float(measurement)), DOWN, buff=0.08)
        measurement_label = Text(
            f"sensor = {measurement:.2f}",
            font_size=18,
            color=YELLOW,
        )
        measurement_label.next_to(measurement_marker, DOWN, buff=0.05)
        measurement_group = VGroup(measurement_marker, measurement_label)

        chosen_highlight = SurroundingRectangle(
            bars[int(np.argmax(probabilities))],
            color=YELLOW,
            buff=0.06,
            stroke_width=4,
        )
        chosen_label = Text(
            f"choose {chosen:.1f} m",
            font_size=20,
            color=YELLOW,
            weight=BOLD,
        )
        chosen_label.next_to(chosen_highlight, UP, buff=0.32)
        chosen_group = VGroup(chosen_highlight, chosen_label)

        return VGroup(label, axis, bars, VGroup(bar_labels, measurement_group), chosen_group)

    def show_rviz_view(
        self,
        title,
        true_pose,
        motion_prediction,
        sensor_measurement,
        chosen_pose,
        sigma_x,
        sigma_y,
    ):
        title.generate_target()
        title.target.become(Text("RViz View: Put the Chosen Position on the Map", font_size=32, weight=BOLD))
        title.target.to_edge(UP, buff=0.3)

        map_group, map_to_point = self.make_rviz_map()
        map_group.to_edge(LEFT, buff=0.6).shift(DOWN * 0.15)

        true_robot = self.make_robot_marker(GREEN).move_to(map_to_point(*true_pose))
        true_label = Text("true robot", font_size=18, color=GREEN)
        true_label.next_to(true_robot, UP, buff=0.08)

        motion_dot = Dot(map_to_point(*motion_prediction), radius=0.08, color=RED)
        motion_label = Text("motion prediction", font_size=18, color=RED)
        motion_label.next_to(motion_dot, LEFT, buff=0.08)

        sensor_dot = Dot(map_to_point(*sensor_measurement), radius=0.08, color=YELLOW)
        sensor_label = Text("sensor reading", font_size=18, color=YELLOW)
        sensor_label.next_to(sensor_dot, DOWN, buff=0.08)

        chosen_robot = self.make_robot_marker(BLUE).move_to(map_to_point(*chosen_pose))
        chosen_label = Text("chosen estimate", font_size=18, color=BLUE)
        chosen_label.next_to(chosen_robot, UP, buff=0.08)

        uncertainty = Ellipse(
            width=4 * sigma_x * self.map_scale(map_to_point),
            height=4 * sigma_y * self.map_scale(map_to_point),
            color=BLUE,
            fill_color=BLUE,
            fill_opacity=0.14,
            stroke_width=3,
        )
        uncertainty.move_to(map_to_point(*chosen_pose))

        x_line = DashedLine(
            map_to_point(chosen_pose[0], 0),
            map_to_point(chosen_pose[0], chosen_pose[1]),
            color=BLUE,
            stroke_width=3,
        )
        y_line = DashedLine(
            map_to_point(0, chosen_pose[1]),
            map_to_point(chosen_pose[0], chosen_pose[1]),
            color=GREEN,
            stroke_width=3,
        )

        panel = self.make_result_panel(
            true_pose,
            motion_prediction,
            sensor_measurement,
            chosen_pose,
            sigma_x,
            sigma_y,
        )
        panel.to_edge(RIGHT, buff=0.55).shift(DOWN * 0.15)

        self.play(MoveToTarget(title), FadeIn(map_group), run_time=1.0)
        self.play(FadeIn(true_robot), FadeIn(true_label), run_time=0.6)
        self.play(FadeIn(motion_dot, scale=0.8), FadeIn(motion_label), run_time=0.7)
        self.play(FadeIn(sensor_dot, scale=0.8), FadeIn(sensor_label), run_time=0.7)
        self.play(Create(x_line), Create(y_line), run_time=0.7)
        self.play(
            FadeIn(uncertainty),
            FadeIn(chosen_robot, scale=0.85),
            FadeIn(chosen_label),
            FadeIn(panel, shift=LEFT * 0.15),
            run_time=1.0,
        )
        self.wait(3)

    def make_rviz_map(self):
        world_width = 6.0
        world_height = 4.5
        scale = 1.18
        map_width = world_width * scale
        map_height = world_height * scale

        frame = Rectangle(
            width=map_width,
            height=map_height,
            color=GRAY_B,
            fill_color=GRAY_E,
            fill_opacity=0.55,
            stroke_width=3,
        )

        def map_to_point(x, y):
            return frame.get_corner(DL) + RIGHT * (x * scale) + UP * (y * scale)

        grid = VGroup()
        for x in np.arange(0.5, world_width, 0.5):
            grid.add(Line(map_to_point(x, 0), map_to_point(x, world_height), color=GRAY_D, stroke_width=1))
        for y in np.arange(0.5, world_height, 0.5):
            grid.add(Line(map_to_point(0, y), map_to_point(world_width, y), color=GRAY_D, stroke_width=1))

        obstacles = VGroup(
            Rectangle(width=0.45, height=1.7, color=WHITE, fill_color=WHITE, fill_opacity=0.72)
            .move_to(map_to_point(1.45, 2.2)),
            Rectangle(width=1.45, height=0.38, color=WHITE, fill_color=WHITE, fill_opacity=0.72)
            .move_to(map_to_point(4.65, 1.35)),
            Rectangle(width=0.95, height=0.42, color=WHITE, fill_color=WHITE, fill_opacity=0.72)
            .move_to(map_to_point(4.35, 3.35)),
        )

        axes = VGroup(
            Arrow(map_to_point(0.25, 0.25), map_to_point(1.0, 0.25), buff=0, color=RED, stroke_width=4),
            Arrow(map_to_point(0.25, 0.25), map_to_point(0.25, 1.0), buff=0, color=GREEN, stroke_width=4),
            Text("x", font_size=16, color=RED).next_to(map_to_point(1.0, 0.25), RIGHT, buff=0.03),
            Text("y", font_size=16, color=GREEN).next_to(map_to_point(0.25, 1.0), UP, buff=0.03),
        )

        label = Text("/map", font_size=22, color=GRAY_A, weight=BOLD)
        label.next_to(frame, UP, buff=0.12)

        return VGroup(frame, grid, obstacles, axes, label), map_to_point

    def map_scale(self, map_to_point):
        return np.linalg.norm(map_to_point(1, 0) - map_to_point(0, 0))

    def make_robot_marker(self, color):
        body = Triangle(color=color, fill_color=color, fill_opacity=0.9, stroke_width=2)
        body.scale(0.18)
        body.rotate(-PI / 2)
        center = Dot(radius=0.045, color=WHITE)
        return VGroup(body, center)

    def make_result_panel(
        self,
        true_pose,
        motion_prediction,
        sensor_measurement,
        chosen_pose,
        sigma_x,
        sigma_y,
    ):
        error = np.linalg.norm(chosen_pose - true_pose)
        heading = Text("Chosen pose", font_size=25, color=BLUE, weight=BOLD)
        lines = VGroup(
            Text(f"motion: ({motion_prediction[0]:.2f}, {motion_prediction[1]:.2f})", font_size=20, color=RED),
            Text(f"sensor: ({sensor_measurement[0]:.2f}, {sensor_measurement[1]:.2f})", font_size=20, color=YELLOW),
            Text(f"x choose: {chosen_pose[0]:.1f} m", font_size=21, color=BLUE),
            Text(f"y choose: {chosen_pose[1]:.1f} m", font_size=21, color=GREEN),
            Text(f"sigma x: {sigma_x:.2f} m", font_size=19, color=GRAY_A),
            Text(f"sigma y: {sigma_y:.2f} m", font_size=19, color=GRAY_A),
            Text(f"error from true: {error:.2f} m", font_size=21, color=WHITE, weight=BOLD),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)

        panel = RoundedRectangle(
            width=4.1,
            height=2.85,
            corner_radius=0.08,
            color=GRAY_B,
            fill_color=BLACK,
            fill_opacity=0.45,
            stroke_width=2,
        )
        content = VGroup(heading, lines).arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        content.move_to(panel).shift(LEFT * 0.05)
        return VGroup(panel, content)
