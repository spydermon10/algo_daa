from manim import *
import numpy as np


# Manim Community Edition
# Single-scene, insight-first visualization of B-tree insertion.


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


class BTreeInsertion(Scene):
    def construct(self):
        # ---------------------------
        # Visual constants / safety
        # ---------------------------
        title = Text("B-tree insert", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # Board area for the tree (kept well below title band)
        tree_anchor = np.array([0.0, 0.35, 0.0])

        # Colors
        key_col = GREY_E
        node_fill = GREY_D
        node_stroke = GREY_B
        edge_col = GREY_B
        hi = YELLOW
        promote_col = BLUE_B
        split_col = RED_C

        # Geometry
        key_w = 0.62
        key_h = 0.48
        pad = 0.12
        node_stroke_w = 3

        def key_box(val, fill=key_col):
            r = RoundedRectangle(corner_radius=0.08, width=key_w, height=key_h)
            r.set_fill(fill, opacity=1)
            r.set_stroke(WHITE, width=2)
            t = Text(str(val), font_size=24, weight=BOLD)
            t.set_color(WHITE)
            g = VGroup(r, t)
            t.move_to(r.get_center())
            g.rect = r
            g.text = t
            g.val = val
            return g

        def make_node(keys):
            # keys: list of ints
            boxes = VGroup(*[key_box(k) for k in keys])
            boxes.arrange(RIGHT, buff=pad)
            bg = RoundedRectangle(
                corner_radius=0.12,
                width=boxes.width + 0.30,
                height=boxes.height + 0.22,
            )
            bg.set_fill(node_fill, opacity=1)
            bg.set_stroke(node_stroke, width=node_stroke_w)
            g = VGroup(bg, boxes)
            boxes.move_to(bg.get_center())
            g.bg = bg
            g.boxes = boxes
            g.keys = list(keys)
            return g

        def update_node_keys(node, new_keys):
            new = make_node(new_keys)
            new.move_to(node.get_center())
            return new

        def edge(parent, child):
            # connect from bottom of parent bg to top of child bg
            p = parent.bg.get_bottom() + np.array([0, 0.02, 0])
            c = child.bg.get_top() + np.array([0, -0.02, 0])
            ln = Line(p, c)
            ln.set_stroke(edge_col, width=4)
            ln.set_z_index(0)
            return ln

        # ---------------------------
        # Start with a single root node (order 3 / max 2 keys)
        # ---------------------------
        root = make_node([10, 20]).move_to(tree_anchor + np.array([0, 1.25, 0]))
        clamp_to_safe(root)
        self.play(FadeIn(root, shift=0.15 * UP), run_time=0.8)
        self.wait(0.25)

        # Incoming key 30
        incoming = key_box(30)
        incoming.to_edge(LEFT)
        incoming.shift(DOWN * 1.2)
        clamp_to_safe(incoming)
        self.play(FadeIn(incoming, shift=0.25 * RIGHT), run_time=0.6)

        # Move key into the root (visual insert)
        glow = SurroundingRectangle(root.bg, corner_radius=0.14)
        glow.set_stroke(hi, width=5)
        glow.set_fill(opacity=0)
        glow.set_z_index(6)
        self.play(Create(glow), run_time=0.35)

        # Insert by morphing root to have 3 keys (overflow)
        root_over = update_node_keys(root, [10, 20, 30])
        self.play(incoming.animate.move_to(root_over.boxes[-1].get_center()), run_time=0.7)
        self.play(Transform(root, root_over), FadeOut(incoming), run_time=0.6)
        self.wait(0.15)

        # Show overflow as a red outline
        overflow = SurroundingRectangle(root.bg, corner_radius=0.14)
        overflow.set_stroke(split_col, width=6)
        overflow.set_fill(opacity=0)
        overflow.set_z_index(7)
        self.play(Transform(glow, overflow), run_time=0.45)
        self.wait(0.2)

        # ---------------------------
        # Split the root: promote middle key
        # ---------------------------
        # Prepare new nodes positions
        y_root = root.get_y()
        new_root_pos = np.array([0.0, y_root + 0.95, 0.0])
        left_pos = np.array([-2.2, y_root - 0.95, 0.0])
        right_pos = np.array([+2.2, y_root - 0.95, 0.0])

        # Create the two children and the new root
        left = make_node([10]).move_to(root.get_center())
        right = make_node([30]).move_to(root.get_center())
        new_root = make_node([20]).move_to(root.get_center())

        # Middle key highlight (promotion)
        mid_box = root.boxes[1]
        promote_ring = SurroundingRectangle(mid_box, corner_radius=0.10)
        promote_ring.set_stroke(promote_col, width=5)
        promote_ring.set_fill(opacity=0)
        promote_ring.set_z_index(8)

        self.play(Create(promote_ring), run_time=0.35)

        # Replace root with a promoted key, and spawn children from the old root
        self.play(
            Transform(root, new_root),
            FadeOut(glow),
            run_time=0.55,
        )
        self.add(left, right)

        # Animate split: children slide down and apart; root rises
        self.play(
            root.animate.move_to(new_root_pos),
            left.animate.move_to(left_pos),
            right.animate.move_to(right_pos),
            FadeOut(promote_ring),
            run_time=1.0,
        )

        # Edges
        eL = edge(root, left)
        eR = edge(root, right)
        self.play(Create(eL), Create(eR), run_time=0.5)
        self.wait(0.35)

        # ---------------------------
        # Now show insertion into a leaf without splitting
        # Insert key 25 -> goes to right child [30] -> becomes [25,30]
        # ---------------------------
        incoming2 = key_box(25)
        incoming2.to_edge(LEFT)
        incoming2.shift(DOWN * 2.2)
        clamp_to_safe(incoming2)
        self.play(FadeIn(incoming2, shift=0.25 * RIGHT), run_time=0.6)

        # Tracer dot down to right child
        tracer = Dot(root.get_center(), radius=0.06, color=hi)
        tracer.set_z_index(9)
        self.play(FadeIn(tracer), run_time=0.2)
        self.play(tracer.animate.move_to(right.get_center()), run_time=0.65)
        self.play(FadeOut(tracer), run_time=0.2)

        right_glow = SurroundingRectangle(right.bg, corner_radius=0.14)
        right_glow.set_stroke(hi, width=5)
        right_glow.set_fill(opacity=0)
        right_glow.set_z_index(6)
        self.play(Create(right_glow), run_time=0.3)

        right_new = update_node_keys(right, [25, 30])
        # place incoming to the left slot visually
        self.play(incoming2.animate.move_to(right_new.boxes[0].get_center()), run_time=0.7)
        self.play(Transform(right, right_new), FadeOut(incoming2), run_time=0.6)
        self.play(FadeOut(right_glow), run_time=0.25)
        self.wait(0.35)

        # ---------------------------
        # Brief compact summary (single MathTex)
        # ---------------------------
        eq = MathTex(r"\text{insert} \;\to\; \text{split} \;\to\; \text{promote}")
        eq.scale(0.95)

        main_visual = VGroup(root, left, right, eL, eR)
        eq.next_to(main_visual, DOWN, buff=0.65)
        eq.move_to(np.array([0, eq.get_y(), 0]))
        if abs(eq.get_x()) > 5.0:
            eq.move_to(np.array([0, -2.85, 0]))
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))

        self.play(FadeIn(eq), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(eq), run_time=0.4)

        self.wait(0.7)


# You are an expert mathematical animator using the Manim Community Edition (Python).
