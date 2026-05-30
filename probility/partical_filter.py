import copy
import math
import random

import numpy as np
from manim import *


class ParticleFilterRoboticsAnimation(Scene):
    def construct(self):
        random.seed(12)
        np.random.seed(12)

        title = Text("Particle Filter Localization", font_size=38, weight=BOLD)
        subtitle = Text("AMCL-style robot pose estimate: x, y, theta", font_size=24, color=GRAY_A)
        VGroup(title, subtitle).arrange(DOWN, buff=0.12).to_edge(UP, buff=0.25)

        map_group, to_map = self.make_map()
        map_group.to_edge(LEFT, buff=0.55).shift(DOWN * 0.35)

        sensor_panel = self.make_sensor_panel()
        sensor_panel.to_edge(RIGHT, buff=0.55).shift(UP * 0.2)

        step_bar = self.make_step_bar()
        step_bar.to_edge(DOWN, buff=0.28)

        self.play(Write(title), FadeIn(subtitle, shift=UP * 0.1), run_time=1)
        self.play(FadeIn(map_group), FadeIn(sensor_panel), FadeIn(step_bar), run_time=1.1)

        particles = self.initial_particles()
        particle_dots = self.particle_mobjects(particles, to_map, BLUE_B)
        unknown_note = self.note("Robot initially has no idea where it is.", YELLOW)
        unknown_note.next_to(map_group, UP, buff=0.16)

        self.activate_step(step_bar, 0)
        self.play(
            LaggedStart(*[FadeIn(dot, scale=0.4) for dot in particle_dots], lag_ratio=0.01),
            FadeIn(unknown_note, shift=UP * 0.1),
            run_time=1.8,
        )
        self.wait(0.6)

        true_pose = np.array([4.25, 2.6, 0.22])
        predicted_particles = self.predict_particles(particles, distance=0.9, rotation=0.18)
        predicted_dots = self.particle_mobjects(predicted_particles, to_map, BLUE)
        motion_formula = self.motion_formula()
        motion_formula.next_to(sensor_panel, DOWN, buff=0.25)

        self.activate_step(step_bar, 1)
        self.play(FadeOut(unknown_note), FadeIn(motion_formula, shift=LEFT * 0.1), run_time=0.6)
        self.play(
            Transform(particle_dots, predicted_dots),
            *self.motion_arrows(particles, predicted_particles, to_map),
            run_time=1.8,
        )
        self.wait(0.6)

        robot = self.robot_marker(GREEN).move_to(to_map(true_pose[0], true_pose[1]))
        true_label = Text("real robot", font_size=18, color=GREEN)
        true_label.next_to(robot, UP, buff=0.07)
        real_scan = self.scan_lines(to_map, true_pose, [2.05, 1.05, 2.6], GREEN, solid=True)

        good_particle = np.array([4.1, 2.45, 0.18])
        bad_particle = np.array([1.45, 3.15, -0.55])
        good_scan = self.scan_lines(to_map, good_particle, [1.95, 1.12, 2.48], GREEN_B, solid=False)
        bad_scan = self.scan_lines(to_map, bad_particle, [0.8, 2.4, 1.15], RED, solid=False)
        compare_panel = self.sensor_comparison_panel()
        compare_panel.move_to(sensor_panel)

        self.activate_step(step_bar, 2)
        self.play(
            FadeOut(sensor_panel),
            FadeOut(motion_formula),
            FadeIn(robot, scale=0.8),
            FadeIn(true_label),
            FadeIn(compare_panel, shift=LEFT * 0.1),
            run_time=0.8,
        )
        self.play(Create(real_scan), run_time=0.9)
        self.play(Create(good_scan), run_time=0.8)
        self.play(Create(bad_scan), run_time=0.8)

        weighted_particles = self.weight_particles(predicted_particles, target=true_pose[:2])
        weighted_dots = self.particle_mobjects(weighted_particles, to_map, BLUE, use_weights=True)
        weight_formula = self.weight_formula()
        weight_formula.next_to(compare_panel, DOWN, buff=0.24)
        self.play(FadeIn(weight_formula, shift=UP * 0.08), Transform(particle_dots, weighted_dots), run_time=1.1)
        self.wait(0.7)

        normalized_panel = self.normalization_panel(weighted_particles)
        normalized_panel.next_to(compare_panel, DOWN, buff=0.24)
        self.activate_step(step_bar, 3)
        self.play(FadeOut(weight_formula), FadeIn(normalized_panel, shift=UP * 0.08), run_time=0.8)
        self.wait(0.7)

        resampled_particles = self.resample_particles(weighted_particles, count=len(weighted_particles))
        resampled_dots = self.particle_mobjects(resampled_particles, to_map, TEAL_B)
        cluster_ring = Circle(radius=0.72, color=YELLOW, stroke_width=4).move_to(to_map(true_pose[0], true_pose[1]))
        resample_note = self.note("Good guesses clone. Bad guesses disappear.", TEAL_B)
        resample_note.next_to(map_group, UP, buff=0.16)

        self.activate_step(step_bar, 4)
        self.play(FadeOut(normalized_panel), FadeIn(resample_note, shift=UP * 0.08), run_time=0.5)
        self.play(Transform(particle_dots, resampled_dots), Create(cluster_ring), run_time=1.6)
        self.wait(0.6)

        estimate = self.estimate_pose(resampled_particles)
        estimate_robot = self.robot_marker(YELLOW).move_to(to_map(estimate[0], estimate[1]))
        estimate_label = Text(f"estimate = ({estimate[0]:.2f}, {estimate[1]:.2f}, theta)", font_size=21, color=YELLOW)
        estimate_label.next_to(estimate_robot, DOWN, buff=0.1)
        loop_panel = self.loop_panel()
        loop_panel.move_to(compare_panel)

        self.activate_step(step_bar, 5)
        self.play(
            FadeOut(compare_panel),
            FadeOut(good_scan),
            FadeOut(bad_scan),
            FadeOut(real_scan),
            FadeOut(resample_note),
            FadeIn(loop_panel, shift=LEFT * 0.1),
            FadeIn(estimate_robot, scale=0.8),
            FadeIn(estimate_label),
            run_time=1.0,
        )
        self.wait(1.0)

        data_flow = self.data_flow_panel()
        data_flow.move_to(loop_panel)
        final_line = Text(
            "Many robots compete to explain reality. Good guesses survive.",
            font_size=28,
            color=YELLOW,
            weight=BOLD,
        )
        final_line.to_edge(DOWN, buff=0.33)
        self.play(FadeOut(loop_panel), FadeIn(data_flow, shift=UP * 0.1), FadeOut(step_bar), FadeIn(final_line), run_time=1)
        self.wait(3)

    def make_map(self):
        world_width = 6.0
        world_height = 4.2
        scale = 1.08
        frame = Rectangle(
            width=world_width * scale,
            height=world_height * scale,
            color=GRAY_B,
            fill_color=GRAY_E,
            fill_opacity=0.5,
            stroke_width=3,
        )

        def to_map(x, y):
            return frame.get_corner(DL) + RIGHT * (x * scale) + UP * (y * scale)

        grid = VGroup()
        for x in np.arange(0.5, world_width, 0.5):
            grid.add(Line(to_map(x, 0), to_map(x, world_height), color=GRAY_D, stroke_width=1))
        for y in np.arange(0.5, world_height, 0.5):
            grid.add(Line(to_map(0, y), to_map(world_width, y), color=GRAY_D, stroke_width=1))

        obstacles = VGroup(
            Rectangle(width=0.42, height=1.55, color=WHITE, fill_color=WHITE, fill_opacity=0.72).move_to(to_map(1.5, 2.45)),
            Rectangle(width=1.35, height=0.36, color=WHITE, fill_color=WHITE, fill_opacity=0.72).move_to(to_map(4.55, 1.25)),
            Rectangle(width=1.05, height=0.38, color=WHITE, fill_color=WHITE, fill_opacity=0.72).move_to(to_map(4.4, 3.35)),
            Rectangle(width=0.35, height=0.9, color=WHITE, fill_color=WHITE, fill_opacity=0.72).move_to(to_map(2.9, 0.95)),
        )

        axes = VGroup(
            Arrow(to_map(0.28, 0.28), to_map(1.0, 0.28), buff=0, color=RED, stroke_width=4),
            Arrow(to_map(0.28, 0.28), to_map(0.28, 1.0), buff=0, color=GREEN, stroke_width=4),
            Text("x", font_size=16, color=RED).next_to(to_map(1.0, 0.28), RIGHT, buff=0.04),
            Text("y", font_size=16, color=GREEN).next_to(to_map(0.28, 1.0), UP, buff=0.04),
        )
        label = Text("Occupancy map + particles", font_size=22, color=WHITE)
        label.next_to(frame, DOWN, buff=0.14)
        return VGroup(frame, grid, obstacles, axes, label), to_map

    def make_sensor_panel(self):
        lines = [
            ("map", "/map occupancy grid", BLUE_B),
            ("odometry", "/odom wheel motion", RED_B),
            ("LiDAR", "/scan laser ranges", GREEN_B),
        ]
        title = Text("Robot Inputs", font_size=26, color=WHITE, weight=BOLD)
        rows = VGroup()
        for name, detail, color in lines:
            dot = Dot(radius=0.07, color=color)
            left = Text(name, font_size=20, color=color)
            right = Text(detail, font_size=18, color=GRAY_A)
            row = VGroup(dot, left, right).arrange(RIGHT, buff=0.18)
            rows.add(row)
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        body = VGroup(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        box = RoundedRectangle(width=4.35, height=2.3, corner_radius=0.08, color=GRAY_B, fill_color=BLACK, fill_opacity=0.42)
        body.move_to(box)
        return VGroup(box, body)

    def make_step_bar(self):
        labels = ["Init", "Prediction", "Measurement", "Normalize", "Resample", "Estimate"]
        chips = VGroup()
        for label in labels:
            box = RoundedRectangle(width=1.72, height=0.42, corner_radius=0.07, color=GRAY_C, fill_color=BLACK, fill_opacity=0.35)
            text = Text(label, font_size=16, color=GRAY_A)
            text.move_to(box)
            chips.add(VGroup(box, text))
        chips.arrange(RIGHT, buff=0.1)
        return chips

    def activate_step(self, step_bar, index):
        animations = []
        for i, chip in enumerate(step_bar):
            color = YELLOW if i == index else GRAY_C
            fill = "#2a2410" if i == index else BLACK
            text_color = YELLOW if i == index else GRAY_A
            animations.append(chip[0].animate.set_color(color).set_fill(fill, opacity=0.55 if i == index else 0.35))
            animations.append(chip[1].animate.set_color(text_color))
        self.play(*animations, run_time=0.35)

    def initial_particles(self):
        particles = []
        for _ in range(95):
            particles.append(
                {
                    "x": random.uniform(0.35, 5.65),
                    "y": random.uniform(0.35, 3.85),
                    "theta": random.uniform(-math.pi, math.pi),
                    "weight": 1 / 95,
                }
            )
        return particles

    def predict_particles(self, particles, distance, rotation):
        moved = []
        for p in particles:
            new_p = copy.deepcopy(p)
            noisy_distance = distance + random.gauss(0, 0.11)
            noisy_rotation = rotation + random.gauss(0, 0.05)
            new_p["x"] = min(5.75, max(0.25, new_p["x"] + noisy_distance * math.cos(new_p["theta"])))
            new_p["y"] = min(3.95, max(0.25, new_p["y"] + noisy_distance * math.sin(new_p["theta"])))
            new_p["theta"] += noisy_rotation
            moved.append(new_p)
        return moved

    def weight_particles(self, particles, target):
        sigma = 0.78
        total = 0
        weighted = []
        for p in particles:
            new_p = copy.deepcopy(p)
            error = math.hypot(new_p["x"] - target[0], new_p["y"] - target[1])
            scan_error = error * 2.1
            new_p["weight"] = math.exp(-(scan_error**2) / (2 * sigma**2))
            total += new_p["weight"]
            weighted.append(new_p)
        for p in weighted:
            p["weight"] /= total
        return weighted

    def resample_particles(self, particles, count):
        weights = [p["weight"] for p in particles]
        chosen = random.choices(particles, weights=weights, k=count)
        resampled = []
        for p in chosen:
            new_p = copy.deepcopy(p)
            new_p["x"] += random.gauss(0, 0.08)
            new_p["y"] += random.gauss(0, 0.08)
            new_p["theta"] += random.gauss(0, 0.03)
            new_p["weight"] = 1 / count
            resampled.append(new_p)
        return resampled

    def estimate_pose(self, particles):
        weights = np.array([p["weight"] for p in particles])
        xs = np.array([p["x"] for p in particles])
        ys = np.array([p["y"] for p in particles])
        return np.array([float(np.sum(weights * xs)), float(np.sum(weights * ys))])

    def particle_mobjects(self, particles, to_map, color, use_weights=False):
        dots = VGroup()
        for p in particles:
            radius = 0.035
            opacity = 0.65
            dot_color = color
            if use_weights:
                radius = 0.025 + min(0.11, p["weight"] * 2.8)
                opacity = 0.25 + min(0.75, p["weight"] * 12)
                dot_color = interpolate_color(BLUE_E, YELLOW, min(1, p["weight"] * 18))
            dots.add(Dot(to_map(p["x"], p["y"]), radius=radius, color=dot_color).set_opacity(opacity))
        return dots

    def motion_arrows(self, before, after, to_map):
        arrows = []
        for start, end in zip(before[::16], after[::16]):
            arrows.append(
                GrowArrow(
                    Arrow(
                        to_map(start["x"], start["y"]),
                        to_map(end["x"], end["y"]),
                        buff=0,
                        color=RED_B,
                        stroke_width=3,
                        max_tip_length_to_length_ratio=0.25,
                    )
                )
            )
        return arrows

    def scan_lines(self, to_map, pose, ranges, color, solid):
        angles = [0, math.pi / 2, -math.pi / 4]
        rays = VGroup()
        start = to_map(pose[0], pose[1])
        for angle, distance in zip(angles, ranges):
            end = to_map(pose[0] + distance * math.cos(pose[2] + angle), pose[1] + distance * math.sin(pose[2] + angle))
            line_class = Line if solid else DashedLine
            rays.add(line_class(start, end, color=color, stroke_width=4))
        return rays

    def robot_marker(self, color):
        body = Triangle(color=color, fill_color=color, fill_opacity=0.85, stroke_width=2).scale(0.18)
        body.rotate(-PI / 2)
        ring = Circle(radius=0.22, color=color, stroke_width=2)
        return VGroup(ring, body)

    def note(self, text, color):
        return Text(text, font_size=22, color=color, weight=BOLD)

    def motion_formula(self):
        lines = VGroup(
            Text("Prediction: move every particle with odometry + noise", font_size=21, color=RED_B, weight=BOLD),
            Text("x' = x + d cos(theta) + N(0, sigma_x)", font_size=18, color=WHITE),
            Text("y' = y + d sin(theta) + N(0, sigma_y)", font_size=18, color=WHITE),
            Text("theta' = theta + delta theta + N(0, sigma_theta)", font_size=18, color=WHITE),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = RoundedRectangle(width=4.55, height=1.55, corner_radius=0.08, color=RED_B, fill_color=BLACK, fill_opacity=0.4)
        lines.move_to(box)
        return VGroup(box, lines)

    def sensor_comparison_panel(self):
        title = Text("Measurement Update", font_size=25, color=GREEN_B, weight=BOLD)
        rows = VGroup(
            Text("1. Pretend robot is at each particle", font_size=18, color=WHITE),
            Text("2. Ray-cast a predicted LiDAR scan", font_size=18, color=WHITE),
            Text("3. Compare predicted scan to real scan", font_size=18, color=WHITE),
            Text("green = good match, red = bad match", font_size=18, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        body = VGroup(title, rows).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        box = RoundedRectangle(width=4.55, height=2.45, corner_radius=0.08, color=GREEN_B, fill_color=BLACK, fill_opacity=0.42)
        body.move_to(box)
        return VGroup(box, body)

    def weight_formula(self):
        body = VGroup(
            Text("Weight calculation", font_size=21, color=YELLOW, weight=BOLD),
            Text("error = sum |real_scan - predicted_scan|", font_size=17, color=WHITE),
            Text("w = exp(-(error^2) / (2 sigma^2))", font_size=17, color=WHITE),
            Text("smaller error -> larger weight", font_size=17, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.11)
        box = RoundedRectangle(width=4.55, height=1.48, corner_radius=0.08, color=YELLOW, fill_color=BLACK, fill_opacity=0.4)
        body.move_to(box)
        return VGroup(box, body)

    def normalization_panel(self, particles):
        top = sorted([p["weight"] for p in particles], reverse=True)[:3]
        body = VGroup(
            Text("Normalize weights", font_size=22, color=YELLOW, weight=BOLD),
            Text("sum of all weights = 1.0", font_size=18, color=WHITE),
            Text(f"top weights: {top[0]:.3f}, {top[1]:.3f}, {top[2]:.3f}", font_size=18, color=GRAY_A),
            Text("Now they can be sampled like probabilities.", font_size=17, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        box = RoundedRectangle(width=4.55, height=1.48, corner_radius=0.08, color=YELLOW, fill_color=BLACK, fill_opacity=0.4)
        body.move_to(box)
        return VGroup(box, body)

    def loop_panel(self):
        title = Text("Continuous Robotics Loop", font_size=24, color=TEAL_B, weight=BOLD)
        steps = VGroup(
            Text("prediction()", font_size=18, color=RED_B),
            Text("measurement_update()", font_size=18, color=GREEN_B),
            Text("normalize()", font_size=18, color=YELLOW),
            Text("resample()", font_size=18, color=TEAL_B),
            Text("estimate_pose()", font_size=18, color=BLUE_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.13)
        body = VGroup(title, steps).arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        box = RoundedRectangle(width=4.55, height=2.35, corner_radius=0.08, color=TEAL_B, fill_color=BLACK, fill_opacity=0.42)
        body.move_to(box)
        return VGroup(box, body)

    def data_flow_panel(self):
        blocks = VGroup(
            self.flow_block("Wheel Encoder", "Odometry", RED_B),
            self.flow_block("LiDAR Scan", "Measurement", GREEN_B),
            self.flow_block("Map", "Ray casting", BLUE_B),
            self.flow_block("AMCL", "Pose estimate", YELLOW),
        ).arrange(DOWN, buff=0.18)
        title = Text("ROS2 / AMCL Data Flow", font_size=25, color=WHITE, weight=BOLD)
        title.next_to(blocks, UP, buff=0.22)
        return VGroup(title, blocks)

    def flow_block(self, top, bottom, color):
        box = RoundedRectangle(width=4.35, height=0.62, corner_radius=0.08, color=color, fill_color=color, fill_opacity=0.12)
        label = VGroup(Text(top, font_size=18, color=color), Text(bottom, font_size=16, color=WHITE)).arrange(RIGHT, buff=0.35)
        label.move_to(box)
        return VGroup(box, label)
