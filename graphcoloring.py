from manim import *
import numpy as np

# Manim Community Edition
# Insight-first visualization: Greedy graph coloring.


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


class GraphColoringGreedy(Scene):
    def construct(self):
        title = Text("Graph coloring", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # Graph layout kept well inside safe region under the title
        pts = {
            0: np.array([-3.2,  0.9, 0.0]),
            1: np.array([-0.8,  1.5, 0.0]),
            2: np.array([ 1.8,  0.9, 0.0]),
            3: np.array([ 2.8, -0.8, 0.0]),
            4: np.array([ 0.2, -1.6, 0.0]),
            5: np.array([-2.6, -1.0, 0.0]),
        }

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),  # outer cycle
            (1, 4), (2, 4), (0, 4)  # chords
        ]

        # Palette as hex strings (hashable), converted to Manim colors when used.
        palette_hex = ["#58C4DD", "#FF9F1C", "#83C167", "#9B59B6", "#2EC4B6"]

        # Build vertices
        r = 0.22
        verts = {}
        for i, p in pts.items():
            v = Circle(radius=r, stroke_width=4, stroke_color=GREY_B, fill_opacity=1.0, fill_color=GREY_E)
            v.move_to(p)
            v.set_z_index(3)
            verts[i] = v

        # Build edges
        edge_mobs = {}
        edge_group = VGroup()
        for a, b in edges:
            ln = Line(pts[a], pts[b], stroke_width=4, color=GREY_B)
            ln.set_z_index(1)
            edge_mobs[(a, b)] = ln
            edge_mobs[(b, a)] = ln
            edge_group.add(ln)

        graph = VGroup(edge_group, *verts.values())
        graph.shift(DOWN * 0.2)
        clamp_to_safe(graph)

        self.play(Create(edge_group), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(verts[i], scale=1.1) for i in verts], lag_ratio=0.12), run_time=0.9)
        self.wait(0.2)

        # Moving focus ring
        focus = Circle(radius=r + 0.08, stroke_width=6, stroke_color=YELLOW)
        focus.set_z_index(6)
        focus.move_to(verts[0].get_center())
        self.play(FadeIn(focus), run_time=0.3)

        def neighbors(v_idx):
            return sorted({b for a, b in edges if a == v_idx} | {a for a, b in edges if b == v_idx})

        # Neighbor highlight overlay
        def neighbor_rings(v_idx, color=RED_C):
            rings = VGroup()
            for u in neighbors(v_idx):
                ring = Circle(radius=r + 0.06, stroke_width=5, stroke_color=color)
                ring.move_to(verts[u].get_center())
                ring.set_z_index(5)
                rings.add(ring)
            return rings

        # Coloring state stores hex strings (hashable)
        color_of = {i: None for i in verts}

        def available_color_hex(v_idx):
            used = {color_of[u] for u in neighbors(v_idx) if color_of[u] is not None}
            for hx in palette_hex:
                if hx not in used:
                    return hx
            return palette_hex[-1]

        # Greedy order
        order = [1, 4, 0, 2, 5, 3]

        # Single short label, then remove
        label = Text("Greedy", font_size=34)
        label.next_to(graph, DOWN, buff=0.65)
        label.move_to([0, label.get_y(), 0])
        if label.get_bottom()[1] < -3.2:
            label.shift(UP * (-3.2 - label.get_bottom()[1] + 0.05))
        self.play(FadeIn(label), run_time=0.45)
        self.wait(0.25)
        self.play(FadeOut(label), run_time=0.35)

        # Animate coloring
        for v in order:
            self.play(focus.animate.move_to(verts[v].get_center()), run_time=0.45)

            rings = neighbor_rings(v)
            self.play(FadeIn(rings), run_time=0.25)

            chosen_hx = available_color_hex(v)

            # Tint edges to already-colored neighbors (shows which colors are blocked)
            to_tint_anims = []
            for u in neighbors(v):
                if color_of[u] is not None:
                    to_tint_anims.append(edge_mobs[(v, u)].animate.set_color(color_of[u]).set_stroke(width=6))
            if to_tint_anims:
                self.play(*to_tint_anims, run_time=0.25)

            self.play(
                verts[v].animate.set_fill(chosen_hx, opacity=1.0).set_stroke(color=WHITE, width=4),
                run_time=0.35,
            )
            color_of[v] = chosen_hx

            # Restore edges
            if to_tint_anims:
                self.play(
                    *[edge_mobs[(v, u)].animate.set_color(GREY_B).set_stroke(width=4) for u in neighbors(v)],
                    run_time=0.25,
                )

            self.play(FadeOut(rings), run_time=0.2)
            self.wait(0.05)

        self.wait(0.25)

        # Correctness check: sweep along edges
        sweep = VGroup()
        for a, b in edges:
            ln = edge_mobs[(a, b)].copy()
            ln.set_stroke(color=YELLOW, width=7, opacity=0.9)
            ln.set_z_index(4)
            sweep.add(ln)
        self.play(LaggedStart(*[ShowPassingFlash(m, time_width=0.5) for m in sweep], lag_ratio=0.08), run_time=1.4)
        self.wait(0.2)

        # Final compact summary equation
        eq = MathTex(r"\chi_G\le\Delta+1")
        eq.scale(1.05)
        eq.next_to(graph, DOWN, buff=0.65)
        eq.move_to([0, eq.get_y(), 0])
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))
        self.play(FadeIn(eq), run_time=0.55)
        self.wait(0.75)
        self.play(FadeOut(eq), run_time=0.35)

        # End beat: pulse each color class (no text)
        distinct_hex = [hx for hx in palette_hex if hx in {c for c in color_of.values() if c is not None}]
        grow_anims = []
        shrink_anims = []
        for hx in distinct_hex:
            group = VGroup(*[verts[i] for i in verts if color_of[i] == hx])
            grow_anims.append(group.animate.scale(1.06))
            shrink_anims.append(group.animate.scale(1 / 1.06))
        if grow_anims:
            self.play(*grow_anims, run_time=0.25)
            self.play(*shrink_anims, run_time=0.25)
        self.wait(0.4)


# You are an expert mathematical animator using the Manim Community Edition (Python).
