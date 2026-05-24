from manim import *

config.frame_rate = 24
config.pixel_width = 854
config.pixel_height = 480


class SensorFusionDemo(Scene):
    def construct(self):
        title = Text("Sensor Fusion: Wheel + IMU + LiDAR + GPS", font_size=30)
        title.to_edge(UP)

        road = NumberLine(
            x_range=[0, 16, 2],
            length=9.5,
            include_numbers=True,
            font_size=22,
            color=GRAY_B,
        )
        road.shift(DOWN * 2.2)
        road_label = Text("position on road (meters)", font_size=22, color=GRAY_A)
        road_label.next_to(road, DOWN, buff=0.25)

        car = self.make_car()
        car.move_to(road.n2p(10) + UP * 0.45)
        car_label = Text("last known x = 10.0 m", font_size=22, color=YELLOW)
        car_label.next_to(car, UP, buff=0.25).shift(LEFT * 0.8)

        wall = VGroup(
            Rectangle(width=0.18, height=1.1, color=TEAL, fill_opacity=0.7),
            Text("wall", font_size=18, color=TEAL_B).next_to(ORIGIN, UP, buff=0.1),
        )
        wall[0].move_to(road.n2p(15) + UP * 0.55)
        wall[1].next_to(wall[0], UP, buff=0.08)

        self.play(Write(title), run_time=1)
        self.play(Create(road), Write(road_label), FadeIn(wall), run_time=1.2)
        self.play(FadeIn(car), Write(car_label), run_time=1)
        self.wait(0.7)

        prediction = VGroup(
            Text("1) Predict with motion sensors", font_size=25, color=BLUE_B),
            MathTex(r"x_{\text{wheel}} = 10.0 + 2.0 = 12.0\text{ m}"),
            MathTex(r"x_{\text{IMU}} = 12.0 + 0.2 = 12.2\text{ m}"),
        )
        prediction.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        prediction.scale(0.75)
        prediction.to_corner(UL, buff=0.55).shift(DOWN * 0.35)

        wheel_arrow = Arrow(
            start=road.n2p(10) + UP * 0.15,
            end=road.n2p(12) + UP * 0.15,
            buff=0,
            color=BLUE,
            stroke_width=6,
        )
        wheel_dot = Dot(road.n2p(12) + UP * 0.45, color=BLUE)
        wheel_tag = Text("wheel: 12.0", font_size=20, color=BLUE_B)
        wheel_tag.next_to(wheel_dot, UP, buff=0.12)

        imu_dot = Dot(road.n2p(12.2) + UP * 0.75, color=PURPLE_B)
        imu_tag = Text("IMU: 12.2", font_size=20, color=PURPLE_B)
        imu_tag.next_to(imu_dot, UP, buff=0.12)

        self.play(Write(prediction[0]), run_time=0.7)
        self.play(GrowArrow(wheel_arrow), Write(prediction[1]), run_time=1.1)
        self.play(FadeIn(wheel_dot), Write(wheel_tag), run_time=0.7)
        self.play(FadeIn(imu_dot), Write(imu_tag), Write(prediction[2]), run_time=1.1)
        self.wait(0.8)

        correction = VGroup(
            Text("2) Correct with outside-world sensors", font_size=25, color=GREEN_B),
            MathTex(r"x_{\text{LiDAR}} = 15.0 - 2.6 = 12.4\text{ m}"),
            MathTex(r"x_{\text{GPS}} = 12.9\text{ m}"),
        )
        correction.arrange(DOWN, aligned_edge=LEFT, buff=0.22)
        correction.scale(0.75)
        correction.next_to(prediction, DOWN, aligned_edge=LEFT, buff=0.35)

        lidar_beam = DashedLine(
            start=road.n2p(12.4) + UP * 0.55,
            end=wall[0].get_left(),
            color=TEAL_B,
            stroke_width=4,
        )
        lidar_dot = Dot(road.n2p(12.4) + UP * 1.05, color=TEAL_B)
        lidar_tag = Text("LiDAR: 12.4", font_size=20, color=TEAL_B)
        lidar_tag.next_to(lidar_dot, UP, buff=0.12)

        gps_dot = Dot(road.n2p(12.9) + UP * 1.35, color=ORANGE)
        gps_ring = Circle(radius=0.22, color=ORANGE).move_to(gps_dot)
        gps_tag = Text("GPS: 12.9", font_size=20, color=ORANGE)
        gps_tag.next_to(gps_dot, UP, buff=0.12)

        self.play(Write(correction[0]), run_time=0.7)
        self.play(Create(lidar_beam), FadeIn(lidar_dot), Write(lidar_tag), Write(correction[1]), run_time=1.4)
        self.play(Create(gps_ring), FadeIn(gps_dot), Write(gps_tag), Write(correction[2]), run_time=1.1)
        self.wait(0.8)

        trust_title = Text("Trust each sensor by how reliable it is now", font_size=24, color=WHITE)
        trust_title.to_corner(UR, buff=0.55).shift(DOWN * 0.35)

        sensor_cards = VGroup(
            self.sensor_card("Wheel", "12.0 m", "35%", BLUE),
            self.sensor_card("IMU", "12.2 m", "15%", PURPLE_B),
            self.sensor_card("LiDAR", "12.4 m", "30%", TEAL_B),
            self.sensor_card("GPS", "12.9 m", "20%", ORANGE),
        )
        sensor_cards.arrange(DOWN, buff=0.13)
        sensor_cards.next_to(trust_title, DOWN, aligned_edge=LEFT, buff=0.2)

        self.play(Write(trust_title), run_time=0.7)
        for card in sensor_cards:
            self.play(FadeIn(card, shift=LEFT * 0.2), run_time=0.35)
        self.wait(0.6)

        formula = VGroup(
            MathTex(
                r"x_{\text{fused}} =",
                r"0.35(12.0)",
                r"+0.15(12.2)",
                r"+0.30(12.4)",
                r"+0.20(12.9)",
            ),
            MathTex(r"x_{\text{fused}} = 12.33\text{ m} \approx 12.3\text{ m}"),
        )
        formula.arrange(DOWN, aligned_edge=LEFT, buff=0.25)
        formula.scale(0.68)
        formula.to_edge(DOWN, buff=0.35)

        self.play(
            FadeOut(road_label),
            FadeOut(car_label),
            FadeOut(prediction),
            FadeOut(correction),
            run_time=0.5,
        )
        self.play(Write(formula[0]), run_time=1.6)
        self.play(Write(formula[1]), run_time=1.1)

        fused_dot = Dot(road.n2p(12.33) + UP * 0.45, color=GREEN, radius=0.09)
        fused_line = Line(
            start=road.n2p(12.33) + DOWN * 0.25,
            end=road.n2p(12.33) + UP * 1.65,
            color=GREEN,
            stroke_width=5,
        )
        fused_tag = Text("best estimate: 12.3 m", font_size=24, color=GREEN_B)
        fused_tag.next_to(fused_line, UP, buff=0.14)

        self.play(Create(fused_line), FadeIn(fused_dot), Write(fused_tag), run_time=1)
        self.play(car.animate.move_to(road.n2p(12.33) + UP * 0.45), run_time=1.3)
        self.wait(0.7)

        beginner_takeaway = VGroup(
            Text("Beginner idea:", font_size=28, color=YELLOW),
            Text("Fusion is not magic. It is a careful vote.", font_size=25),
            Text("Each sensor gets a weight, then the robot averages the guesses.", font_size=24),
        )
        beginner_takeaway.arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        beginner_takeaway.to_edge(LEFT, buff=0.65).shift(UP * 1.35)

        self.play(FadeOut(trust_title), FadeOut(sensor_cards), run_time=0.5)
        self.play(Write(beginner_takeaway), run_time=1.5)
        self.wait(3)

    def make_car(self):
        body = RoundedRectangle(
            width=1.05,
            height=0.42,
            corner_radius=0.08,
            color=YELLOW,
            fill_opacity=0.85,
        )
        roof = Polygon(
            LEFT * 0.33 + UP * 0.21,
            RIGHT * 0.28 + UP * 0.21,
            RIGHT * 0.12 + UP * 0.5,
            LEFT * 0.18 + UP * 0.5,
            color=YELLOW,
            fill_opacity=0.85,
        )
        wheel_1 = Circle(radius=0.11, color=WHITE, fill_opacity=1).shift(LEFT * 0.32 + DOWN * 0.22)
        wheel_2 = Circle(radius=0.11, color=WHITE, fill_opacity=1).shift(RIGHT * 0.32 + DOWN * 0.22)
        return VGroup(body, roof, wheel_1, wheel_2)

    def sensor_card(self, name, value, weight, color):
        box = RoundedRectangle(
            width=3.2,
            height=0.54,
            corner_radius=0.08,
            color=color,
            fill_color=color,
            fill_opacity=0.12,
            stroke_width=2,
        )
        label = Text(name, font_size=18, color=color)
        reading = Text(value, font_size=18, color=WHITE)
        trust = Text(weight, font_size=18, color=YELLOW)
        row = VGroup(label, reading, trust).arrange(RIGHT, buff=0.4)
        row.move_to(box)
        return VGroup(box, row)
