from manim import *

class MathOverlay(Scene):
    def construct(self):
        # Create a math equation
        formula = MathTex(r"e^{i\pi} + 1 = 0")
        formula.scale(2)
        formula.set_color(YELLOW) # Bright colors look best on overlays
        
        # Simple animation
        self.play(Write(formula))
        self.wait(2)
        self.play(Unwrite(formula))
