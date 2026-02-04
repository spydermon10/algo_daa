from manim import *
import numpy as np


class RedBlackTreeInsertion(Scene):
    def construct(self):
        # ---------------------------
        # Visual constants / safety
        # ---------------------------
        title = Text("RB-tree insert", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # Layout anchors (kept within safe region)
        tree_center = np.array([0.0, 0.35, 0.0])
        tree_top_y = 2.2
        level_y = [tree_top_y, 1.05, -0.05]  # 3 levels
        level_dx = [0.0, 2.7, 1.55]          # horizontal spacing per depth

        # Colors
        col_red = RED_C
        col_black = GREY_B
        edge_col = GREY_A
        highlight_col = YELLOW

        # Node geometry
        node_r = 0.34
        stroke_w = 3

        def node_mob(value, color=col_red):
            circ = Circle(radius=node_r)
            circ.set_fill(color, opacity=1.0)
            circ.set_stroke(WHITE, width=stroke_w)
            txt = Text(str(value), font_size=28, weight=BOLD)
            txt.set_color(WHITE)
            g = VGroup(circ, txt)
            txt.move_to(circ.get_center())
            g.circ = circ
            g.txt = txt
            g.value = value
            g.color = color
            return g

        def edge_mob(p, c):
            ln = Line(p, c)
            ln.set_stroke(edge_col, width=4)
            ln.set_z_index(0)
            return ln

        def place_at_depth(index, depth):
            # index: horizontal index among that depth's potential slots
            # depth 0 has index 0; depth 1 indices -1, +1; depth 2 indices -2,-0,+0,+2 conceptual
            if depth == 0:
                x = 0
            elif depth == 1:
                x = index * level_dx[1]
            else:
                x = index * level_dx[2]
            return tree_center + np.array([x, level_y[depth], 0])

        # ---------------------------
        # Build initial tree (classic insertion-fix demo)
        #            10(B)
        #          /      \
        #       5(R)     15(R)
        #
        # Insert 1 -> parent red & uncle red: recolor
        # then insert 0 -> parent red & uncle black: rotate + recolor
        # ---------------------------

        n10 = node_mob(10, color=col_black).move_to(place_at_depth(0, 0))
        n5 = node_mob(5, color=col_red).move_to(place_at_depth(-1, 1))
        n15 = node_mob(15, color=col_red).move_to(place_at_depth(+1, 1))

        e10_5 = edge_mob(n10.get_center(), n5.get_center())
        e10_15 = edge_mob(n10.get_center(), n15.get_center())

        tree = VGroup(e10_5, e10_15, n10, n5, n15)
        self.play(LaggedStart(FadeIn(n10), FadeIn(e10_5), FadeIn(n5), FadeIn(e10_15), FadeIn(n15), lag_ratio=0.12), run_time=1.2)
        self.wait(0.2)

        # ---------------------------
        # Insert 1 (as BST insert)
        # ---------------------------
        insert1 = node_mob(1, color=col_red)
        insert1.to_edge(LEFT)
        insert1.shift(DOWN * 0.9)
        # ensure inside safe region
        if insert1.get_left()[0] < -5.8:
            insert1.shift(RIGHT * (-5.8 - insert1.get_left()[0]))
        if insert1.get_bottom()[1] < -3.2:
            insert1.shift(UP * (-3.2 - insert1.get_bottom()[1] + 0.05))

        self.play(FadeIn(insert1, shift=0.3 * RIGHT), run_time=0.6)

        target_pos_1 = place_at_depth(-2, 2)  # left-left of 10
        # animate down the tree path with a moving dot
        tracer = Dot(n10.get_center(), radius=0.06, color=highlight_col)
        tracer.set_z_index(8)
        self.play(FadeIn(tracer), run_time=0.2)
        self.play(tracer.animate.move_to(n5.get_center()), run_time=0.5)
        self.play(tracer.animate.move_to(target_pos_1 + np.array([0, 0.35, 0])), run_time=0.5)
        self.play(FadeOut(tracer), run_time=0.2)

        e5_1 = edge_mob(n5.get_center(), target_pos_1)
        insert1.generate_target()
        insert1.target.move_to(target_pos_1)
        self.play(Create(e5_1), MoveToTarget(insert1), run_time=0.8)
        self.wait(0.2)

        # fix-up: parent red (5), uncle red (15) -> recolor
        # show trio highlight (no text)
        glow_p = Circle(radius=node_r * 1.18).move_to(n5.get_center()).set_stroke(highlight_col, width=6)
        glow_u = Circle(radius=node_r * 1.18).move_to(n15.get_center()).set_stroke(highlight_col, width=6)
        glow_g = Circle(radius=node_r * 1.18).move_to(n10.get_center()).set_stroke(highlight_col, width=6)
        for g in (glow_p, glow_u, glow_g):
            g.set_fill(opacity=0)
            g.set_z_index(9)

        self.play(LaggedStart(Create(glow_p), Create(glow_u), Create(glow_g), lag_ratio=0.12), run_time=0.7)
        self.wait(0.15)

        # recolor animation
        self.play(
            n5.circ.animate.set_fill(col_black, opacity=1),
            n15.circ.animate.set_fill(col_black, opacity=1),
            n10.circ.animate.set_fill(col_red, opacity=1),
            run_time=0.7,
        )
        self.wait(0.15)
        self.play(FadeOut(glow_p), FadeOut(glow_u), FadeOut(glow_g), run_time=0.35)

        # root must be black
        self.play(n10.circ.animate.set_fill(col_black, opacity=1), run_time=0.45)
        self.wait(0.3)

        # ---------------------------
        # Insert 0 (to trigger rotation)
        # ---------------------------
        insert0 = node_mob(0, color=col_red)
        insert0.to_edge(LEFT)
        insert0.shift(DOWN * 2.2)
        if insert0.get_left()[0] < -5.8:
            insert0.shift(RIGHT * (-5.8 - insert0.get_left()[0]))
        if insert0.get_bottom()[1] < -3.2:
            insert0.shift(UP * (-3.2 - insert0.get_bottom()[1] + 0.05))

        self.play(FadeIn(insert0, shift=0.3 * RIGHT), run_time=0.6)

        target_pos_0 = place_at_depth(-3, 2)  # left of 1 (deeper visually same depth for simplicity)
        # Keep within safe frame: clamp x
        target_pos_0 = np.array([max(-5.2, target_pos_0[0]), target_pos_0[1], 0.0])

        tracer2 = Dot(n10.get_center(), radius=0.06, color=highlight_col)
        tracer2.set_z_index(8)
        self.play(FadeIn(tracer2), run_time=0.2)
        self.play(tracer2.animate.move_to(n5.get_center()), run_time=0.45)
        self.play(tracer2.animate.move_to(insert1.get_center()), run_time=0.45)
        self.play(tracer2.animate.move_to(target_pos_0 + np.array([0, 0.35, 0])), run_time=0.45)
        self.play(FadeOut(tracer2), run_time=0.2)

        e1_0 = edge_mob(insert1.get_center(), target_pos_0)
        insert0.generate_target()
        insert0.target.move_to(target_pos_0)
        self.play(Create(e1_0), MoveToTarget(insert0), run_time=0.8)
        self.wait(0.2)

        # Now fix-up: parent (1) red, uncle (right child of 5) is NIL (black) -> rotate
        # We'll do a RIGHT rotation at 5 around 1? Actually configuration is LL (0 under 1 under 5).
        # Standard fix: rotate right at grandparent (5), recolor (1 becomes black, 5 becomes red).

        # Highlight local subtree
        glow_gp = Circle(radius=node_r * 1.18).move_to(n5.get_center()).set_stroke(highlight_col, width=6)
        glow_p2 = Circle(radius=node_r * 1.18).move_to(insert1.get_center()).set_stroke(highlight_col, width=6)
        for g in (glow_gp, glow_p2):
            g.set_fill(opacity=0)
            g.set_z_index(9)
        self.play(LaggedStart(Create(glow_gp), Create(glow_p2), lag_ratio=0.15), run_time=0.6)
        self.wait(0.15)

        # Compute post-rotation positions (subtree rooted at n5)
        # Before: 5 is left child of 10; 1 is left child of 5; 0 is left child of 1.
        # After right-rotate at 5: 1 becomes left child of 10, 5 becomes right child of 1.

        pos_1_new = place_at_depth(-1, 1)  # where 5 used to be
        pos_5_new = place_at_depth(0, 2)   # right child position of 1 (approx)
        pos_0_new = place_at_depth(-2, 2)  # keep 0 as left child of 1 (approx)

        # Clamp to safe region a bit
        for p in (pos_1_new, pos_5_new, pos_0_new):
            pass

        # Animate node moves
        self.play(
            insert1.animate.move_to(pos_1_new),
            n5.animate.move_to(pos_5_new),
            insert0.animate.move_to(pos_0_new),
            run_time=1.0,
        )

        # Update edges: remove old edges and create new ones (clean transform)
        new_e10_left = edge_mob(n10.get_center(), insert1.get_center())
        new_e1_5 = edge_mob(insert1.get_center(), n5.get_center())
        new_e1_0 = edge_mob(insert1.get_center(), insert0.get_center())

        self.play(
            FadeOut(e10_5),
            FadeOut(e5_1),
            FadeOut(e1_0),
            run_time=0.25,
        )
        self.add(new_e10_left, new_e1_5, new_e1_0)
        self.play(FadeIn(new_e10_left), FadeIn(new_e1_5), FadeIn(new_e1_0), run_time=0.25)

        # Recolor parent/grandparent
        self.play(
            insert1.circ.animate.set_fill(col_black, opacity=1),
            n5.circ.animate.set_fill(col_red, opacity=1),
            run_time=0.6,
        )
        self.wait(0.15)
        self.play(FadeOut(glow_gp), FadeOut(glow_p2), run_time=0.35)

        # Root stays black (already)
        self.wait(0.4)

        # ---------------------------
        # Brief equation summary (single MathTex block)
        # ---------------------------
        eq = MathTex("\text{rotate + recolor}")
        eq.scale(0.95)
        eq.next_to(tree, DOWN, buff=0.65)
        eq.move_to(np.array([0, eq.get_y(), 0]))
        if abs(eq.get_x()) > 5:
            eq.move_to(np.array([0, -2.9, 0]))
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))

        self.play(FadeIn(eq), run_time=0.5)
        self.wait(0.7)
        self.play(FadeOut(eq), run_time=0.4)

        # End with the fixed tree held briefly
        self.wait(0.8)


# You are an expert mathematical animator using the Manim Community Edition (Python).
