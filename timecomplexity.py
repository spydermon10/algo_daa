from manim import *
import numpy as np

# Manim Community Edition
# Single-scene, insight-first visualization of time complexity growth.


def clamp_to_safe(mob, x_min=-5.8, x_max=5.8, y_min=-3.2, y_max=3.2):
    dx = 0
    dy = 0
    if mob.get_left()[0] < x_min:
        dx = x_min - mob.get_left()[0]
    if mob.get_right()[0] > x_max:
        dx = x_max - mob.get_right()[0]
    if mob.get_bottom()[1] < y_min:
        dy = y_min - mob.get_bottom()[1]
    if mob.get_top()[1] > y_max:
        dy = y_max - mob.get_top()[1]
    mob.shift(np.array([dx, dy, 0]))
    return mob


class TimeComplexityGraphDAA(Scene):
    def construct(self):
        title = Text("Time complexity", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # Axes: keep comfortably inside safe region under title
        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[0, 10, 2],
            x_length=10.6,
            y_length=5.4,
            axis_config={"stroke_width": 3, "include_ticks": True, "tick_size": 0.06},
        )
        axes.shift(DOWN * 0.35)
        clamp_to_safe(axes)

        x_lab = Text("n", font_size=28)
        y_lab = Text("work", font_size=28)
        x_lab.next_to(axes.x_axis, RIGHT, buff=0.15)
        y_lab.next_to(axes.y_axis, UP, buff=0.10)
        if y_lab.get_top()[1] > 3.2:
            y_lab.shift(DOWN * (y_lab.get_top()[1] - 3.2 + 0.05))
        for t in (x_lab, y_lab):
            t.set_z_index(10)

        self.play(Create(axes), FadeIn(x_lab), FadeIn(y_lab), run_time=1.2)
        self.wait(0.25)

        # Curves (kept within the axes region)
        c_log = TEAL_C
        c_lin = BLUE_C
        c_nlogn = GREEN_C
        c_quad = ORANGE
        c_exp = RED_C

        def f_log(x):
            return np.log2(x + 1)

        def f_lin(x):
            return x

        def f_nlogn(x):
            return x * np.log2(x + 1)

        def f_quad(x):
            return x**2

        def f_exp(x):
            return 2**x

        # Normalize to y in [0,10] so everything fits and comparisons are visual
        xs = np.linspace(0, 10, 400)
        vals = {
            "log": f_log(xs),
            "lin": f_lin(xs),
            "nlogn": f_nlogn(xs),
            "quad": f_quad(xs),
            "exp": f_exp(xs),
        }
        max_at_10 = {
            k: float(v[-1]) for k, v in vals.items()
        }

        def scaled_graph(func, color, key, stroke_width=6):
            scale = 10.0 / max_at_10[key]
            return axes.plot(lambda x: func(x) * scale, x_range=[0, 10], color=color, stroke_width=stroke_width)

        g_log = scaled_graph(f_log, c_log, "log", stroke_width=5)
        g_lin = scaled_graph(f_lin, c_lin, "lin", stroke_width=5)
        g_nlogn = scaled_graph(f_nlogn, c_nlogn, "nlogn", stroke_width=5)
        g_quad = scaled_graph(f_quad, c_quad, "quad", stroke_width=5)
        g_exp = scaled_graph(f_exp, c_exp, "exp", stroke_width=5)

        # A moving dot at a chosen n; it will slide right to show relative growth.
        n_tracker = ValueTracker(2.0)

        def dot_on(graph, color):
            d = Dot(color=color, radius=0.08)
            d.set_z_index(6)

            def upd(m):
                x = float(n_tracker.get_value())
                m.move_to(graph.get_point_from_function(x))

            d.add_updater(upd)
            return d

        d_log = dot_on(g_log, c_log)
        d_lin = dot_on(g_lin, c_lin)
        d_nlogn = dot_on(g_nlogn, c_nlogn)
        d_quad = dot_on(g_quad, c_quad)
        d_exp = dot_on(g_exp, c_exp)

        # Draw curves one by one (show before naming)
        self.play(Create(g_log), FadeIn(d_log), run_time=0.8)
        self.play(Create(g_lin), FadeIn(d_lin), run_time=0.8)
        self.play(Create(g_nlogn), FadeIn(d_nlogn), run_time=0.8)
        self.play(Create(g_quad), FadeIn(d_quad), run_time=0.8)
        self.play(Create(g_exp), FadeIn(d_exp), run_time=0.9)
        self.wait(0.2)

        # Slide n to the right: motion is the explanation
        self.play(n_tracker.animate.set_value(9.6), run_time=2.2, rate_func=linear)
        self.wait(0.2)

        # Fade dots (reduce clutter) and briefly label the family names as a single equation block
        self.play(
            FadeOut(VGroup(d_log, d_lin, d_nlogn, d_quad, d_exp)),
            run_time=0.45,
        )

        # One MathTex block only, placed below the axes
        eq = MathTex(r"O(\log n)\;<\;O(n)\;<\;O(n\log n)\;<\;O(n^2)\;<\;O(2^n)")
        eq.scale(0.95)
        eq.next_to(axes, DOWN, buff=0.65)
        eq.move_to(np.array([0, eq.get_y(), 0]))
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))
        if abs(eq.get_x()) > 5.0:
            eq.move_to(np.array([0, -2.85, 0]))

        self.play(FadeIn(eq), run_time=0.6)
        self.wait(1.1)
        self.play(FadeOut(eq), run_time=0.45)

        # Dim everything except a "good" vs "bad" visual split without extra text
        good = VGroup(g_log, g_lin, g_nlogn).copy()
        bad = VGroup(g_quad, g_exp).copy()
        for m in good:
            m.set_stroke(opacity=1.0)
        for m in bad:
            m.set_stroke(opacity=1.0)

        # Soft highlight regions by tinting curves
        self.play(
            g_log.animate.set_stroke(c_log, width=6, opacity=1),
            g_lin.animate.set_stroke(c_lin, width=6, opacity=1),
            g_nlogn.animate.set_stroke(c_nlogn, width=6, opacity=1),
            g_quad.animate.set_stroke(GREY_C, width=4, opacity=0.35),
            g_exp.animate.set_stroke(GREY_C, width=4, opacity=0.35),
            run_time=0.7,
        )
        self.wait(0.5)
        self.play(
            g_quad.animate.set_stroke(c_quad, width=6, opacity=1),
            g_exp.animate.set_stroke(c_exp, width=6, opacity=1),
            g_log.animate.set_stroke(GREY_C, width=4, opacity=0.35),
            g_lin.animate.set_stroke(GREY_C, width=4, opacity=0.35),
            g_nlogn.animate.set_stroke(GREY_C, width=4, opacity=0.35),
            run_time=0.7,
        )
        self.wait(0.6)

        # Reset all
        self.play(
            g_log.animate.set_stroke(c_log, width=5, opacity=1),
            g_lin.animate.set_stroke(c_lin, width=5, opacity=1),
            g_nlogn.animate.set_stroke(c_nlogn, width=5, opacity=1),
            g_quad.animate.set_stroke(c_quad, width=5, opacity=1),
            g_exp.animate.set_stroke(c_exp, width=5, opacity=1),
            run_time=0.6,
        )
        self.wait(0.6)


# You are an expert mathematical animator using the Manim Community Edition (Python).
