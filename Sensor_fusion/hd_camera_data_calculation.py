from manim import *
import time


config.frame_rate = 60
config.pixel_width = 1920
config.pixel_height = 1080


class HDCameraDataCalculation(Scene):
    def construct(self):
        width = 1920
        height = 1080
        rgb_channels = 3
        fps = 30
        cameras = 3

        pixels_per_frame = width * height
        bytes_per_frame = pixels_per_frame * rgb_channels
        bytes_per_second = bytes_per_frame * fps
        robot_bytes_per_second = bytes_per_second * cameras
        robot_gbps = robot_bytes_per_second * 8 / 1_000_000_000

        title = Text("HD camera data", font_size=30, weight=BOLD)
        title.to_corner(UL, buff=0.4)

        camera = self.make_camera()
        camera.scale(1.15).to_edge(LEFT, buff=0.8).shift(UP * 0.42)

        hd_frame = self.make_hd_frame(width, height)
        hd_frame.next_to(camera, RIGHT, buff=0.7)

        pixel_count = VGroup(
            Text("One HD image", font_size=28, color=BLUE_B),
            Text("1920 x 1080", font_size=34, weight=BOLD),
            Text("2,073,600 pixels", font_size=30, color=GRAY_A),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        pixel_count.next_to(hd_frame, RIGHT, buff=0.55)
        
        time.sleep(8) # me added

        self.play(FadeIn(title, shift=DOWN * 0.12), run_time=0.8, rate_func=smooth)
        self.play(
            FadeIn(camera, shift=RIGHT * 0.15),
            Create(hd_frame),
            run_time=1.35,
            rate_func=smooth,
        )
        self.play(FadeIn(pixel_count, shift=UP * 0.15), run_time=1.0, rate_func=smooth)
        self.wait(0.25)

        pixel_sample = self.make_pixel_sample()
        pixel_sample.move_to(LEFT * 4.0 + DOWN * 1.65)

        rgb_formula = VGroup(
            Text("RGB: 3 values per pixel", font_size=28, color=GREEN_B),
            Text("2,073,600 x 3", font_size=31, weight=BOLD),
            Text("6,220,800 bytes per frame", font_size=30, weight=BOLD),
            Text("about 6.22 MB raw", font_size=24, color=GRAY_B),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        rgb_formula.next_to(pixel_sample, RIGHT, buff=0.7)

        time.sleep(8) # me added

        self.play(FadeIn(pixel_sample, scale=0.92), run_time=0.9, rate_func=smooth)
        self.play(FadeIn(rgb_formula, shift=RIGHT * 0.12), run_time=1.15, rate_func=smooth)
        self.wait(0.25)

        fps_group = self.make_stream(
            "30 FPS",
            "6,220,800 bytes/frame x 30 FPS",
            "186,624,000 bytes/second",
            "186.6 MB/s from one camera",
            YELLOW,
        )
        fps_group.to_edge(DOWN, buff=0.35).shift(LEFT * 3.15)

        robot_group = self.make_stream(
            "Robot: 3 cameras",
            "186,624,000 bytes/s x 3",
            "559,872,000 bytes/second",
            f"559.9 MB/s  =  {robot_gbps:.2f} Gbps raw data",
            ORANGE,
        )
        robot_group.to_edge(DOWN, buff=0.35).shift(RIGHT * 3.15)

        self.play(
            FadeOut(pixel_count, shift=UP * 0.15),
            FadeOut(rgb_formula, shift=DOWN * 0.15),
            FadeOut(pixel_sample, shift=DOWN * 0.15),
            hd_frame.animate.scale(0.68).to_edge(UP, buff=1.2).shift(RIGHT * 0.9),
            camera.animate.scale(0.74).next_to(hd_frame, LEFT, buff=0.35),
            run_time=1.1,
            rate_func=smooth,
        )
        self.play(FadeIn(fps_group[0], shift=UP * 0.12), run_time=0.45, rate_func=smooth)
        self.play(
            LaggedStart(*[FadeIn(frame, shift=RIGHT * 0.15) for frame in fps_group[1]], lag_ratio=0.08),
            FadeIn(fps_group[2][0], shift=UP * 0.08),
            FadeIn(fps_group[2][1], shift=UP * 0.08),
            run_time=1.25,
            rate_func=smooth,
        )
        self.play(FadeIn(fps_group[2][2], shift=UP * 0.1), run_time=0.65, rate_func=smooth)
        self.wait(0.25)

        self.play(FadeIn(robot_group[0], shift=UP * 0.12), run_time=0.45, rate_func=smooth)
        self.play(
            LaggedStart(*[FadeIn(cam, shift=UP * 0.15) for cam in robot_group[1]], lag_ratio=0.12),
            FadeIn(robot_group[2][0], shift=UP * 0.08),
            FadeIn(robot_group[2][1], shift=UP * 0.08),
            run_time=1.25,
            rate_func=smooth,
        )
        self.play(FadeIn(robot_group[2][2], shift=UP * 0.1), run_time=0.75, rate_func=smooth)
        self.wait(0.3)

        final_panel = RoundedRectangle(
            width=11.9,
            height=1.1,
            corner_radius=0.08,
            color=TEAL_B,
            fill_color=TEAL_E,
            fill_opacity=0.35,
            stroke_width=3,
        )
        final_text = Text(
            "Raw 3-camera HD vision at 30 FPS needs about 560 MB/s before compression.",
            font_size=16,
            weight=BOLD,
            color=WHITE,
        )
        final_note = Text(
            "That is why robots use compression, region-of-interest processing, or dedicated vision hardware.",
            font_size=14,
            color=GRAY_A,
        )
        final = VGroup(final_panel, VGroup(final_text, final_note).arrange(DOWN, buff=0.12))
        final[1].move_to(final_panel)
        final.to_edge(DOWN, buff=0.3)

        self.play(
            FadeOut(fps_group, shift=DOWN * 0.2),
            FadeOut(robot_group, shift=DOWN * 0.2),
            run_time=0.8,
            rate_func=smooth,
        )
        self.play(FadeIn(final, shift=UP * 0.2), run_time=1, rate_func=smooth)
        self.wait(3)

    def make_camera(self):
        body = RoundedRectangle(
            width=1.8,
            height=1.1,
            corner_radius=0.08,
            color=BLUE_B,
            fill_color=BLUE_E,
            fill_opacity=0.75,
            stroke_width=3,
        )
        lens_outer = Circle(radius=0.34, color=WHITE, stroke_width=3)
        lens_inner = Circle(radius=0.18, color=BLUE_A, fill_color=BLUE_A, fill_opacity=0.8)
        lens = VGroup(lens_outer, lens_inner).move_to(body)
        mount = Rectangle(width=0.72, height=0.18, color=BLUE_B, fill_opacity=0.8)
        mount.next_to(body, DOWN, buff=0)
        label = Text("HD", font_size=24, weight=BOLD, color=WHITE)
        label.next_to(lens, UP, buff=0.08)
        return VGroup(body, lens, mount, label)

    def make_hd_frame(self, width, height):
        frame = RoundedRectangle(
            width=3.7,
            height=2.08,
            corner_radius=0.08,
            color=BLUE_B,
            fill_color=BLUE_E,
            fill_opacity=0.18,
            stroke_width=3,
        )
        label = Text(f"{width} x {height}", font_size=30, weight=BOLD, color=WHITE)
        label.move_to(frame)
        pixels = VGroup()
        for row in range(5):
            for col in range(9):
                dot = Dot(radius=0.018, color=BLUE_A)
                dot.move_to(frame.get_corner(UL) + RIGHT * (0.35 + col * 0.36) + DOWN * (0.35 + row * 0.31))
                pixels.add(dot)
        return VGroup(frame, pixels, label)

    def make_pixel_sample(self):
        pixel = Square(side_length=0.95, color=WHITE, fill_color=GRAY_E, fill_opacity=0.6)
        channel_r = Rectangle(width=0.34, height=1.1, color=RED, fill_color=RED, fill_opacity=0.85)
        channel_g = Rectangle(width=0.34, height=1.1, color=GREEN, fill_color=GREEN, fill_opacity=0.85)
        channel_b = Rectangle(width=0.34, height=1.1, color=BLUE, fill_color=BLUE, fill_opacity=0.85)
        channels = VGroup(channel_r, channel_g, channel_b).arrange(RIGHT, buff=0.05)
        channels.next_to(pixel, RIGHT, buff=0.35)

        label = Text("pixel", font_size=21, color=WHITE)
        label.next_to(pixel, DOWN, buff=0.18)
        rgb = Text("R + G + B", font_size=22, color=WHITE)
        rgb.next_to(channels, DOWN, buff=0.18)
        arrow = Arrow(pixel.get_right(), channels.get_left(), buff=0.08, color=GRAY_A)
        return VGroup(pixel, channels, label, rgb, arrow)

    def make_stream(self, heading, line_1, line_2, line_3, color):
        title = Text(heading, font_size=28, color=color, weight=BOLD)

        if "cameras" in heading:
            visuals = VGroup(self.small_camera(), self.small_camera(), self.small_camera()).arrange(RIGHT, buff=0.32)
            visuals.scale(1.45)
        else:
            visuals = VGroup(*[self.small_frame(i) for i in range(6)]).arrange(RIGHT, buff=0.1)

        formula = VGroup(
            Text(line_1, font_size=23, color=GRAY_B),
            Text(line_2, font_size=27, color=WHITE, weight=BOLD),
            Text(line_3, font_size=24, color=color, weight=BOLD),
        ).arrange(DOWN, buff=0.13)

        group = VGroup(title, visuals, formula).arrange(DOWN, buff=0.22)
        return group

    def small_frame(self, index):
        color = interpolate_color(BLUE_B, TEAL_B, index / 5)
        rect = RoundedRectangle(
            width=0.44,
            height=0.25,
            corner_radius=0.03,
            color=color,
            fill_color=color,
            fill_opacity=0.35,
            stroke_width=2,
        )
        return rect

    def small_camera(self):
        body = RoundedRectangle(
            width=0.7,
            height=0.42,
            corner_radius=0.04,
            color=ORANGE,
            fill_color=ORANGE,
            fill_opacity=0.25,
            stroke_width=2,
        )
        lens = Circle(radius=0.12, color=WHITE, stroke_width=2).move_to(body)
        return VGroup(body, lens)
