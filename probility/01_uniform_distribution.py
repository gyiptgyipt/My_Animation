"""
Uniform Distribution Animation (Myanmar) — real 8x8 Grid Map version
======================================================================
Run with:
    manim -pqh uniform_distribution.py UniformDistribution

Requires the "Noto Sans Myanmar" font to be installed on your system
so Manim's Pango-based Text renderer can shape the Burmese script correctly.

    Ubuntu/Debian:  sudo apt-get install fonts-noto-core fonts-noto-unhinted
    macOS:          brew install --cask font-noto-sans-myanmar
    Windows:        download & install from Google Fonts (Noto Sans Myanmar)

This version draws a REAL 8x8 grid (64 individually-drawn cells, addressed
by (x, y) in [0..7]) instead of pretending at a much larger grid. At the
end, the grid cells physically morph (Transform) into a 64-bar bar chart
to show the uniform distribution — no color-heatmap ending, no particle
scatter.
"""

from manim import *
import numpy as np

MM_FONT = "Noto Sans Myanmar"

# ---- color palette -----------------------------------------------------
BG_COLOR = "#0F1117"
CELL_COLOR = "#2B2F3A"
CELL_STROKE = "#4A90E2"
ROBOT_BODY = "#4A90E2"
ROBOT_EYE = "#FFFFFF"
BAR_COLOR = "#4A90E2"
HIGHLIGHT = "#F5A623"
TEXT_COLOR = "#FFFFFF"
VO_COLOR = "#B8C4D9"

GRID_N = 8            # real 8 x 8 grid = 64 cells
GRID_SIZE = 5.4        # on-screen width/height of the grid (Manim units)
GRID_CENTER = np.array([0, -0.25, 0])
N_CELLS = GRID_N * GRID_N  # 64


def mm_text(text, size=32, color=TEXT_COLOR, weight=NORMAL):
    return Text(text, font=MM_FONT, font_size=size, color=color, weight=weight)


def grid_to_point(gx, gy, n=GRID_N, size=GRID_SIZE, center=GRID_CENTER):
    """Map a grid cell index (gx, gy), each in [0, n-1], to a scene point."""
    cell = size / n
    x = center[0] - size / 2 + (gx + 0.5) * cell
    y = center[1] - size / 2 + (gy + 0.5) * cell
    return np.array([x, y, 0])


class UniformDistribution(Scene):
    def construct(self):
        self.camera.background_color = BG_COLOR

        # =====================================================
        # 0. TITLE
        # =====================================================
        title = mm_text(
            'Uniform Distribution: "ငါ ဘာမှမသိဘူး" အဆင့် — 8×8 Grid Map',
            size=36,
            color=HIGHLIGHT,
            weight=BOLD,
        )
        title.to_edge(UP, buff=0.5)

        self.play(Write(title))
        self.wait(0.5)

        # =====================================================
        # 1. BUILD A REAL 8x8 GRID (64 individually-drawn cells)
        # =====================================================
        cell_side = GRID_SIZE / GRID_N
        cells = VGroup()
        cell_index = {}  # (gx, gy) -> index in `cells`
        for gy in range(GRID_N):
            for gx in range(GRID_N):
                sq = Square(side_length=cell_side)
                sq.set_fill(CELL_COLOR, opacity=1)
                sq.set_stroke(CELL_STROKE, width=1.5)
                sq.move_to(grid_to_point(gx, gy))
                idx = gy * GRID_N + gx
                cell_index[(gx, gy)] = idx
                cells.add(sq)

        # axis ticks 0..7 along the bottom and left of the grid
        x_ticks = VGroup(*[
            mm_text(str(v), size=18, color=VO_COLOR)
            .next_to(grid_to_point(v, 0), DOWN, buff=0.2)
            for v in range(GRID_N)
        ])
        y_ticks = VGroup(*[
            mm_text(str(v), size=18, color=VO_COLOR)
            .next_to(grid_to_point(0, v), LEFT, buff=0.2)
            for v in range(GRID_N)
        ])
        x_axis_label = mm_text("x", size=22, color=VO_COLOR).next_to(x_ticks, DOWN, buff=0.15)
        y_axis_label = mm_text("y", size=22, color=VO_COLOR).next_to(y_ticks, LEFT, buff=0.15)

        self.play(
            LaggedStart(*[FadeIn(c, scale=0.7) for c in cells], lag_ratio=0.015),
            run_time=1.4,
        )
        self.play(
            LaggedStart(*[FadeIn(t) for t in (*x_ticks, *y_ticks)], lag_ratio=0.03),
            FadeIn(x_axis_label), FadeIn(y_axis_label),
        )
        self.wait(0.3)

        # =====================================================
        # 2. ROBOT DROPPED ONTO ONE CELL, EYES CLOSED
        # =====================================================
        start_gx, start_gy = 5, 3
        robot = self.make_robot(eyes_closed=True)
        robot.scale(0.45)
        robot.move_to(grid_to_point(start_gx, start_gy))

        self.play(FadeIn(robot, shift=DOWN * 1.0), run_time=0.8)
        self.wait(0.3)

        # question marks floating over the robot
        q_marks = VGroup(*[
            mm_text("?", size=28, color=HIGHLIGHT).move_to(
                robot.get_center() + np.array([np.random.uniform(-0.45, 0.45),
                                                np.random.uniform(0.55, 1.05), 0])
            )
            for _ in range(4)
        ])
        self.play(LaggedStart(*[FadeIn(q, scale=1.4) for q in q_marks], lag_ratio=0.25))
        self.play(
            *[q.animate.shift(UP * 0.2).set_opacity(0) for q in q_marks],
            run_time=1.0,
        )
        self.remove(q_marks)

        # =====================================================
        # 3. VO CAPTION: robot asks about its (x, y) position
        # =====================================================
        vo1 = mm_text('"ငါ ဘယ် (x, y) position မှာ ရှိနေလဲ"', size=28, color=HIGHLIGHT)
        vo1.to_edge(DOWN, buff=1.3)
        bubble = SurroundingRectangle(vo1, color=HIGHLIGHT, buff=0.25, corner_radius=0.15)

        coord_tag = mm_text("(x=?, y=?)", size=20, color=HIGHLIGHT)
        coord_tag.next_to(robot, RIGHT, buff=0.2)

        self.play(FadeIn(bubble), Write(vo1), FadeIn(coord_tag, shift=UP * 0.1))
        self.wait(1.0)
        self.play(FadeOut(bubble), FadeOut(vo1))

        # =====================================================
        # 4. SHOW UNIFORM PROBABILITY OVER ALL 64 CELLS
        # =====================================================
        prob_label = mm_text("P(x, y) = 1 / 64", size=34, color=HIGHLIGHT, weight=BOLD)
        prob_label.move_to(cells.get_top() + UP * 0.5)

        # a quick equal-weight ripple across every cell (no color wash, no particles)
        self.play(
            LaggedStart(*[
                Indicate(c, color=HIGHLIGHT, scale_factor=1.12)
                for c in cells
            ], lag_ratio=0.01),
            FadeIn(prob_label, scale=1.2),
            run_time=1.4,
        )
        self.wait(0.3)

        vo2 = mm_text(
            "ဘာသတင်းအချက်အလက်မှ မရှိသေးလို့ … ကွက် 64 ကွက်လုံး ဖြစ်နိုင်ခြေ 1/64 စီပဲ",
            size=25, color=VO_COLOR,
        )
        vo2.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(vo2, shift=UP * 0.2))
        self.wait(1.6)
        self.play(FadeOut(vo2), FadeOut(prob_label))

        # =====================================================
        # 5. MORPH THE 64 GRID CELLS INTO A 64-BAR BAR CHART
        # =====================================================
        self.play(
            FadeOut(robot), FadeOut(coord_tag),
            FadeOut(x_ticks), FadeOut(y_ticks),
            FadeOut(x_axis_label), FadeOut(y_axis_label),
            run_time=0.7,
        )

        CHART_WIDTH = 10.5
        CHART_HEIGHT = 3.4
        baseline_y = -1.4
        base_x = -CHART_WIDTH / 2
        bar_unit = CHART_WIDTH / N_CELLS
        bar_w = bar_unit * 0.82
        bar_h = CHART_HEIGHT * 0.62  # uniform target height for every bar

        baseline = Line(
            [base_x - 0.15, baseline_y, 0], [base_x + CHART_WIDTH + 0.15, baseline_y, 0],
            color=GREY_B, stroke_width=2,
        )

        # zero-height "seed" bars positioned on the baseline, ordered to match `cells`
        seed_bars = VGroup()
        target_bars = VGroup()
        for gy in range(GRID_N):
            for gx in range(GRID_N):
                idx = cell_index[(gx, gy)]
                x_center = base_x + (idx + 0.5) * bar_unit

                seed = Rectangle(width=bar_w, height=0.001,
                                  fill_color=BAR_COLOR, fill_opacity=1, stroke_width=0)
                seed.move_to([x_center, baseline_y, 0], aligned_edge=DOWN)
                seed_bars.add(seed)

                tgt = Rectangle(width=bar_w, height=bar_h,
                                 fill_color=BAR_COLOR, fill_opacity=1, stroke_width=0)
                tgt.move_to([x_center, baseline_y, 0], aligned_edge=DOWN)
                target_bars.add(tgt)

        # a few x-axis reference ticks under the bar chart (linear cell index 0..63)
        idx_ticks_vals = [0, 16, 32, 48, 63]
        idx_ticks = VGroup(*[
            mm_text(str(v), size=16, color=VO_COLOR)
            .next_to([base_x + (v + 0.5) * bar_unit, baseline_y, 0], DOWN, buff=0.2)
            for v in idx_ticks_vals
        ])
        idx_axis_label = mm_text("cell index (gy×8 + gx)", size=18, color=VO_COLOR)
        idx_axis_label.next_to(idx_ticks, DOWN, buff=0.15)

        self.play(
            Transform(cells, seed_bars),
            FadeIn(baseline),
            run_time=1.0,
        )
        self.remove(cells)
        self.add(seed_bars, baseline)

        self.play(
            Transform(seed_bars, target_bars),
            LaggedStart(*[FadeIn(t) for t in idx_ticks], lag_ratio=0.1),
            FadeIn(idx_axis_label),
            run_time=1.3,
            rate_func=rate_functions.ease_out_cubic,
        )

        bar_val_label = mm_text("1/64", size=26, color=HIGHLIGHT, weight=BOLD)
        bar_val_label.next_to(seed_bars, UP, buff=0.25)
        level_line = DashedLine(
            [base_x - 0.15, baseline_y + bar_h, 0],
            [base_x + CHART_WIDTH + 0.15, baseline_y + bar_h, 0],
            color=HIGHLIGHT, stroke_width=1.5, dash_length=0.1,
        )
        self.play(FadeIn(level_line), FadeIn(bar_val_label, shift=UP * 0.15))
        self.wait(0.5)

        # =====================================================
        # 6. FINAL EXPLANATION
        # =====================================================
        chart_title = mm_text(
            "ဘားအားလုံး အမြင့်ချင်းတူ = ဖြစ်နိုင်ခြေအားလုံး ညီတူညီမျှ = Uniform Distribution",
            size=27, color=HIGHLIGHT, weight=BOLD,
        )
        chart_title.to_edge(UP, buff=0.6)
        self.play(Write(chart_title))
        self.wait(0.5)

        closing = mm_text(
            '"ငါ ဘာမှမသိသေးဘူး" — ဒါက ကျွန်တော်တို့ရဲ့ ပထမဆုံး ဖြစ်တန်စွမ်း ခြေလှမ်းပါ',
            size=25, color=VO_COLOR,
        )
        closing.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(closing, shift=UP * 0.2))
        self.wait(2.5)

        self.play(*[FadeOut(m) for m in self.mobjects])
        self.wait(0.5)

    # ---------------------------------------------------------------
    def make_robot(self, eyes_closed=False):
        """A very simple, cute box-robot made of manim shapes."""
        head = RoundedRectangle(
            corner_radius=0.15, width=1.4, height=1.1,
            fill_color=ROBOT_BODY, fill_opacity=1, stroke_color=WHITE, stroke_width=2,
        )
        antenna_stem = Line(head.get_top(), head.get_top() + UP * 0.3, color=WHITE, stroke_width=3)
        antenna_ball = Dot(antenna_stem.get_end(), radius=0.07, color=HIGHLIGHT)

        if eyes_closed:
            eye_l = Line(LEFT * 0.05, RIGHT * 0.05, color=ROBOT_EYE, stroke_width=3).move_to(
                head.get_center() + LEFT * 0.28 + UP * 0.05)
            eye_r = Line(LEFT * 0.05, RIGHT * 0.05, color=ROBOT_EYE, stroke_width=3).move_to(
                head.get_center() + RIGHT * 0.28 + UP * 0.05)
        else:
            eye_l = Dot(head.get_center() + LEFT * 0.28 + UP * 0.05, radius=0.09, color=ROBOT_EYE)
            eye_r = Dot(head.get_center() + RIGHT * 0.28 + UP * 0.05, radius=0.09, color=ROBOT_EYE)

        mouth = Line(LEFT * 0.18, RIGHT * 0.18, color=ROBOT_EYE, stroke_width=3)
        mouth.move_to(head.get_center() + DOWN * 0.25)

        body = RoundedRectangle(
            corner_radius=0.1, width=1.0, height=0.7,
            fill_color=ROBOT_BODY, fill_opacity=1, stroke_color=WHITE, stroke_width=2,
        )
        body.next_to(head, DOWN, buff=0.05)

        leg_l = Rectangle(width=0.18, height=0.35, fill_color=ROBOT_BODY,
                           fill_opacity=1, stroke_color=WHITE, stroke_width=2)
        leg_r = leg_l.copy()
        leg_l.next_to(body, DOWN, buff=0.0).shift(LEFT * 0.25)
        leg_r.next_to(body, DOWN, buff=0.0).shift(RIGHT * 0.25)

        robot = VGroup(leg_l, leg_r, body, head, antenna_stem, antenna_ball,
                        eye_l, eye_r, mouth)
        return robot