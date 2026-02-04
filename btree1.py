from manim import *
import numpy as np

# Manim Community Edition


def clamp(x, a, b):
    return max(a, min(b, x))


class BTreeExplanation(Scene):
    def construct(self):
        self.camera.background_color = "#0e1116"

        # Safe region guides (implicit): x in [-6,6], y in [-3.4,3.4]
        top_band_y = 3.15
        bottom_y = -2.9

        # --------------------
        # Helpers
        # --------------------
        def key_box(text, w=0.62, h=0.42, stroke=GRAY_B, fill=BLUE_E, fill_op=0.25):
            r = RoundedRectangle(width=w, height=h, corner_radius=0.08, stroke_width=2)
            r.set_stroke(stroke)
            r.set_fill(fill, opacity=fill_op)
            t = Text(str(text), font_size=22, weight=BOLD)
            g = VGroup(r, t)
            t.move_to(r.get_center())
            return g

        def node(keys, width=2.6):
            # A B-tree node is a box with multiple keys
            outer = RoundedRectangle(width=width, height=0.7, corner_radius=0.12, stroke_width=2)
            outer.set_stroke(GRAY_B)
            outer.set_fill(color="#111722", opacity=0.9)

            k = VGroup(*[key_box(x) for x in keys])
            k.arrange(RIGHT, buff=0.18)
            k.move_to(outer.get_center())
            g = VGroup(outer, k)
            return g

        def connectors(parent_mobj, child_mobjs):
            lines = VGroup()
            p = parent_mobj[0]  # outer box
            for ch in child_mobjs:
                c = ch[0]
                ln = Line(
                    p.get_bottom() + 0.05 * DOWN,
                    c.get_top() + 0.05 * UP,
                    stroke_width=3,
                    color=GRAY_C,
                )
                ln.set_opacity(0.75)
                lines.add(ln)
            return lines

        def search_dot():
            return Dot(radius=0.055, color=YELLOW_C)

        def glow(mobj, color=YELLOW_C, width=6, opacity=0.9):
            return mobj.copy().set_stroke(color, width=width, opacity=opacity).set_fill(opacity=0)

        # --------------------
        # Scene 1: "many keys per node" (show before naming)
        # --------------------
        root = node([10, 20], width=2.9).move_to([0, 1.8, 0])

        left = node([3, 6, 8], width=3.3).move_to([-3.6, -0.2, 0])
        mid = node([12, 16], width=2.6).move_to([0.0, -0.2, 0])
        right = node([22, 27, 30], width=3.3).move_to([3.6, -0.2, 0])
        children = VGroup(left, mid, right)

        edges = connectors(root, children)

        self.play(FadeIn(root, scale=0.95), run_time=0.6)
        self.play(Create(edges), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(ch, scale=0.95) for ch in children], lag_ratio=0.12), run_time=0.7)
        self.wait(0.2)

        # Briefly emphasize the "multiple keys" idea visually (no text)
        for n in [root, left, mid, right]:
            kgrp = n[1]
            self.play(*[k[0].animate.set_fill(BLUE_D, 0.45) for k in kgrp], run_time=0.18)
            self.play(*[k[0].animate.set_fill(BLUE_E, 0.25) for k in kgrp], run_time=0.18)

        # Now name it (single text block)
        title = Text("B-tree", font_size=46, weight=BOLD)
        title.to_edge(UP)
        title.set_y(top_band_y)
        self.play(FadeIn(title, shift=0.15 * UP), run_time=0.55)
        self.wait(0.35)
        self.play(FadeOut(title), run_time=0.3)

        # --------------------
        # Scene 2: Search motion (dot chooses a child by comparisons)
        # --------------------
        # Choose a target key (e.g. 16)
        target_key = 16

        dot = search_dot().move_to(root[0].get_top() + 0.35 * UP)
        self.play(FadeIn(dot), run_time=0.25)
        self.play(dot.animate.move_to(root[0].get_center()), run_time=0.45)

        # Highlight comparisons in root: 10 then 20
        root_keys = root[1]
        h = glow(root_keys[0][0])
        self.play(Create(h), run_time=0.18)
        self.play(FadeOut(h), run_time=0.12)
        h = glow(root_keys[1][0])
        self.play(Create(h), run_time=0.18)
        self.play(FadeOut(h), run_time=0.12)

        # Move along the middle edge (between 10 and 20)
        mid_edge = edges[1]
        self.play(MoveAlongPath(dot, mid_edge.copy().set_opacity(0)), run_time=0.65)
        self.play(dot.animate.move_to(mid[0].get_center()), run_time=0.35)

        # Highlight comparisons in mid: 12 then 16, stop at 16
        mid_keys = mid[1]
        h = glow(mid_keys[0][0])
        self.play(Create(h), run_time=0.18)
        self.play(FadeOut(h), run_time=0.12)
        h = glow(mid_keys[1][0])
        self.play(Create(h), run_time=0.2)
        self.play(mid_keys[1][0].animate.set_fill(YELLOW_D, 0.55), run_time=0.2)
        self.play(FadeOut(h), run_time=0.12)
        self.wait(0.2)
        self.play(mid_keys[1][0].animate.set_fill(BLUE_E, 0.25), run_time=0.25)

        self.play(FadeOut(dot), run_time=0.2)

        # Label (single text block, short)
        lbl = Text("search", font_size=30)
        lbl.move_to([0, bottom_y, 0])
        lbl.move_to([clamp(lbl.get_x(), -5.0, 5.0), lbl.get_y(), 0])
        self.play(FadeIn(lbl), run_time=0.35)
        self.wait(0.35)
        self.play(FadeOut(lbl), run_time=0.25)

        # --------------------
        # Scene 3: Insertion causes a split (core B-tree behavior)
        # --------------------
        # Insert 17 into the middle node -> overflow -> split
        new_key = key_box(17)
        new_key.scale(1.0)
        new_key.move_to(mid[0].get_center() + 1.35 * RIGHT)  # staged just inside the node
        self.play(FadeIn(new_key, scale=0.9), run_time=0.35)

        # Slide into the keys group and re-arrange visually
        mid_keys_with_new = VGroup(*[k.copy() for k in mid[1]], new_key)
        mid_keys_with_new.arrange(RIGHT, buff=0.18)
        mid_keys_with_new.move_to(mid[0].get_center())

        self.play(Transform(mid[1], mid_keys_with_new), run_time=0.55)
        self.wait(0.15)

        # Show "too full" by squeezing (no text)
        self.play(mid[0].animate.set_stroke(RED_C, 3), run_time=0.2)
        self.play(mid[0].animate.set_stroke(GRAY_B, 2), run_time=0.2)

        # Split: promote median 16 to root; left node gets 12, right gets 17
        # We'll morph the current mid node into two nodes and update root keys.
        promoted = mid[1][1]  # the '16' box within mid after transform

        promo_glow = glow(promoted[0], color=YELLOW_C, width=7)
        self.play(Create(promo_glow), run_time=0.2)

        # Create new nodes for split at the same location then separate
        mid_left = node([12], width=1.4).move_to(mid.get_center())
        mid_right = node([17], width=1.4).move_to(mid.get_center())

        # New root with promoted key inserted: [10,16,20]
        new_root = node([10, 16, 20], width=3.9).move_to(root.get_center())

        # Transform root while we "lift" promoted key upward
        lift = promoted.copy()
        self.add(lift)
        self.play(lift.animate.move_to(root[0].get_center() + 0.15 * UP), run_time=0.35)

        self.play(
            FadeOut(promo_glow),
            Transform(root, new_root),
            run_time=0.55,
        )
        self.remove(lift)

        # Replace mid with two nodes, spread them horizontally a bit
        self.play(FadeOut(mid), run_time=0.25)
        self.add(mid_left, mid_right)
        self.play(
            mid_left.animate.shift(1.0 * LEFT),
            mid_right.animate.shift(1.0 * RIGHT),
            run_time=0.55,
        )

        # Update children group: left, mid_left, mid_right, right
        new_children = VGroup(left, mid_left, mid_right, right)

        # Redraw connectors cleanly
        self.play(FadeOut(edges), run_time=0.25)
        edges = connectors(root, new_children)
        self.play(Create(edges), run_time=0.7)

        # Quick balance cue: flash all leaves
        leaf_flash = [left, mid_left, mid_right, right]
        self.play(*[n[0].animate.set_fill(TEAL_E, 0.25) for n in leaf_flash], run_time=0.25)
        self.play(*[n[0].animate.set_fill("#111722", 0.9) for n in leaf_flash], run_time=0.25)

        lbl = Text("split", font_size=30)
        lbl.move_to([0, bottom_y, 0])
        lbl.move_to([clamp(lbl.get_x(), -5.0, 5.0), lbl.get_y(), 0])
        self.play(FadeIn(lbl), run_time=0.35)
        self.wait(0.4)
        self.play(FadeOut(lbl), run_time=0.25)

        # --------------------
        # Late, compact formalism: height ~ log n
        # --------------------
        eq = MathTex(r"\text{height}\sim\log n")
        eq.set_color(GRAY_A)
        eq.move_to([0, bottom_y, 0])
        eq.move_to([clamp(eq.get_x(), -5.0, 5.0), eq.get_y(), 0])

        # Visual hint: compress vertically and show that only few levels exist
        all_nodes = VGroup(root, new_children)
        all_edges = edges
        self.play(all_nodes.animate.scale(0.92).shift(0.1 * DOWN), all_edges.animate.set_opacity(0.65), run_time=0.5)
        self.play(FadeIn(eq), run_time=0.6)
        self.wait(0.8)
        self.play(FadeOut(eq), run_time=0.4)

        self.play(FadeOut(VGroup(all_nodes, all_edges)), run_time=0.8)
        self.wait(0.15)
