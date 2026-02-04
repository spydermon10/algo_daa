from manim import *
import numpy as np


class EightQueens(Scene):
    def construct(self):
        # ---------------------------
        # Visual constants / safety
        # ---------------------------
        board_side = 5.2  # keeps everything comfortably within [-6,6]x[-3.4,3.4]
        cell = board_side / 8
        board_center = np.array([0.0, -0.15, 0.0])

        dark = GREY_E
        light = GREY_B
        queen_color = GOLD
        threat_color = RED
        ok_color = GREEN

        # Title (only text on screen at start)
        title = Text("8 queens", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # ---------------------------
        # Build chessboard
        # ---------------------------
        squares = VGroup()
        for r in range(8):
            for c in range(8):
                sq = Square(side_length=cell)
                sq.set_stroke(color=BLACK, width=1)
                sq.set_fill(light if (r + c) % 2 == 0 else dark, opacity=1)
                # map (r,c) with r=0 top to y positive
                x = (c - 3.5) * cell
                y = (3.5 - r) * cell
                sq.move_to(board_center + np.array([x, y, 0]))
                squares.add(sq)

        board = squares
        self.play(FadeIn(board), run_time=1.0)
        self.wait(0.2)

        # Helper: get center of a cell
        def cell_center(r, c):
            x = (c - 3.5) * cell
            y = (3.5 - r) * cell
            return board_center + np.array([x, y, 0])

        # Helper: queen mobject
        def make_queen(scale=1.0):
            q = Text("♛", font_size=56, color=queen_color)
            q.scale(0.72 * scale)
            q.set_stroke(BLACK, width=1, opacity=0.6)
            return q

        # Helper: highlight threatened squares for a queen at (r,c)
        def threat_overlays(r, c, opacity=0.35):
            overlays = VGroup()
            coords = set()
            # row and col
            for cc in range(8):
                if cc != c:
                    coords.add((r, cc))
            for rr in range(8):
                if rr != r:
                    coords.add((rr, c))
            # diagonals
            for k in range(1, 8):
                for rr, cc in [(r + k, c + k), (r + k, c - k), (r - k, c + k), (r - k, c - k)]:
                    if 0 <= rr < 8 and 0 <= cc < 8:
                        coords.add((rr, cc))
            # build overlay squares
            for (rr, cc) in coords:
                o = Square(side_length=cell)
                o.set_stroke(width=0)
                o.set_fill(threat_color, opacity=opacity)
                o.move_to(cell_center(rr, cc))
                overlays.add(o)
            overlays.set_z_index(5)
            return overlays

        # ---------------------------
        # Show what a queen attacks (no extra text)
        # ---------------------------
        demo_q = make_queen()
        demo_pos = (3, 3)
        demo_q.move_to(cell_center(*demo_pos))
        self.play(FadeIn(demo_q, scale=0.9), run_time=0.6)

        demo_threat = threat_overlays(*demo_pos, opacity=0.28)
        self.play(FadeIn(demo_threat), run_time=0.6)
        self.wait(0.4)

        # Move queen to show threats move with it
        new_pos = (1, 6)
        new_threat = threat_overlays(*new_pos, opacity=0.28)
        self.play(
            demo_q.animate.move_to(cell_center(*new_pos)),
            Transform(demo_threat, new_threat),
            run_time=1.0,
        )
        self.wait(0.3)

        # Clear demo
        self.play(FadeOut(demo_threat), FadeOut(demo_q), run_time=0.6)
        self.wait(0.2)

        # ---------------------------
        # Place queens: show conflicts first
        # ---------------------------
        # A deliberately conflicting placement (two queens in same row, then diagonal)
        q1 = make_queen(); q2 = make_queen(); q3 = make_queen()
        p1 = (6, 1)
        p2 = (6, 5)  # same row conflict with p1
        p3 = (4, 3)  # diagonal conflict with p2 (after we move)

        q1.move_to(cell_center(*p1))
        self.play(FadeIn(q1, scale=0.9), run_time=0.5)
        th1 = threat_overlays(*p1, opacity=0.22)
        self.play(FadeIn(th1), run_time=0.4)

        q2.move_to(cell_center(*p2))
        self.play(FadeIn(q2, scale=0.9), run_time=0.5)

        # show conflict flash on the attacked square (q2 position is attacked by q1)
        conflict_sq = Square(side_length=cell).set_stroke(threat_color, width=6)
        conflict_sq.set_fill(threat_color, opacity=0.0)
        conflict_sq.move_to(cell_center(*p2))
        conflict_sq.set_z_index(10)
        self.play(Create(conflict_sq), run_time=0.25)
        self.play(FadeOut(conflict_sq), run_time=0.25)
        self.wait(0.2)

        # Fix by moving q2 to a safe-looking spot (still not final)
        fixed_p2 = (3, 5)
        th2 = threat_overlays(*fixed_p2, opacity=0.22)
        self.play(q2.animate.move_to(cell_center(*fixed_p2)), run_time=0.7)
        self.play(Transform(th1, threat_overlays(*p1, opacity=0.22)), FadeIn(th2), run_time=0.4)
        self.wait(0.2)

        # Add q3 to create a diagonal conflict with q2
        q3.move_to(cell_center(*p3))
        self.play(FadeIn(q3, scale=0.9), run_time=0.5)

        # Flash conflict on whichever is attacked: q3 is attacked by q2 if diagonal matches
        # Check diagonal between fixed_p2 and p3
        if abs(fixed_p2[0] - p3[0]) == abs(fixed_p2[1] - p3[1]):
            flash_pos = p3
        else:
            flash_pos = fixed_p2
        conflict_sq2 = Square(side_length=cell).set_stroke(threat_color, width=6)
        conflict_sq2.set_fill(threat_color, opacity=0.0)
        conflict_sq2.move_to(cell_center(*flash_pos))
        conflict_sq2.set_z_index(10)
        self.play(Create(conflict_sq2), run_time=0.25)
        self.play(FadeOut(conflict_sq2), run_time=0.25)
        self.wait(0.2)

        # Clear this small attempt
        self.play(FadeOut(th1), FadeOut(th2), FadeOut(q1), FadeOut(q2), FadeOut(q3), run_time=0.7)
        self.wait(0.2)

        # ---------------------------
        # Build a full solution (one queen per row), placing row-by-row
        # ---------------------------
        # Known 8-queens solution as columns for rows 0..7
        sol_cols = [0, 4, 7, 5, 2, 6, 1, 3]

        queens = VGroup()
        all_threats = VGroup()

        # A small, minimal label appears only after the visual idea is underway
        label = Text("one per row", font_size=28)
        label.next_to(board, DOWN, buff=0.6)
        label.move_to(np.array([0, label.get_y(), 0]))
        if abs(label.get_x()) > 5:
            label.move_to(np.array([0, -2.9, 0]))
        self.play(FadeIn(label), run_time=0.5)

        # Place queens with brief threat overlays that fade, keeping screen uncluttered
        for r, c in enumerate(sol_cols):
            q = make_queen(scale=0.98)
            q.move_to(cell_center(r, c))
            queens.add(q)
            self.play(FadeIn(q, scale=0.9), run_time=0.28)

            th = threat_overlays(r, c, opacity=0.14)
            all_threats.add(th)
            self.play(FadeIn(th), run_time=0.18)
            self.play(FadeOut(th), run_time=0.18)

        self.play(FadeOut(label), run_time=0.4)

        # Show that no queens attack each other: quick sweep with green rings
        rings = VGroup()
        for q in queens:
            ring = Circle(radius=0.33 * cell * 1.7)
            ring.set_stroke(ok_color, width=5)
            ring.set_fill(opacity=0)
            ring.move_to(q.get_center())
            ring.set_z_index(12)
            rings.add(ring)

        self.play(LaggedStart(*[Create(r) for r in rings], lag_ratio=0.08), run_time=1.0)
        self.play(FadeOut(rings), run_time=0.4)
        self.wait(0.2)

        # ---------------------------
        # Brief equation summary (single MathTex block)
        # ---------------------------
        eq = MathTex("\text{No shared row, col, diagonal}")
        eq.scale(0.9)
        eq.next_to(board, DOWN, buff=0.65)
        eq.move_to(np.array([0, eq.get_y(), 0]))
        if abs(eq.get_x()) > 5:
            eq.move_to(np.array([0, -2.9, 0]))

        # Ensure it stays above y=-3.2
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))

        self.play(FadeIn(eq), run_time=0.6)
        self.wait(0.8)
        self.play(FadeOut(eq), run_time=0.5)

        # Keep final configuration on screen briefly
        self.wait(0.8)


# You are an expert mathematical animator using the Manim Community Edition (Python).
