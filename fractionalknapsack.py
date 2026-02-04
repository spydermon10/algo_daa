from manim import *
import numpy as np

# Manim Community Edition
# Single-scene, insight-first visualization of Fractional Knapsack.


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


class FractionalKnapsack(Scene):
    def construct(self):
        # ---------------------------
        # Title (single text at a time rule respected)
        # ---------------------------
        title = Text("Fractional knapsack", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # ---------------------------
        # Layout anchors
        # ---------------------------
        left_x = -3.9
        right_x = 3.6
        top_y = 1.9
        row_dy = 1.15

        # Colors
        c_item = GREY_D
        c_item_stroke = GREY_B
        c_fill = BLUE_C
        c_fill2 = GREEN_C
        c_cap = YELLOW
        c_bad = RED_C
        c_ratio = TEAL_A

        # ---------------------------
        # Data: (value, weight)
        # Chosen so ratios differ clearly and fractional step is visible
        # ---------------------------
        items = [
            {"name": "A", "v": 60, "w": 10},  # ratio 6
            {"name": "B", "v": 100, "w": 20},  # ratio 5
            {"name": "C", "v": 120, "w": 30},  # ratio 4
        ]
        cap = 50

        # ---------------------------
        # Item card helper
        # ---------------------------
        def item_card(it):
            card = RoundedRectangle(width=3.2, height=0.78, corner_radius=0.12)
            card.set_fill(c_item, opacity=1)
            card.set_stroke(c_item_stroke, width=2)

            # Ultra-short text on card; not a separate explanatory paragraph
            t = Text(f"{it['name']}  v={it['v']}  w={it['w']}", font_size=26, weight=BOLD)
            t.set_color(WHITE)
            t.move_to(card.get_center())

            # Ratio chip (small, still same card)
            ratio = it["v"] / it["w"]
            chip = RoundedRectangle(width=1.0, height=0.36, corner_radius=0.10)
            chip.set_fill(c_ratio, opacity=1)
            chip.set_stroke(WHITE, width=1)
            chip_t = Text(f"{ratio:.1f}", font_size=22, weight=BOLD)
            chip_t.set_color(BLACK)
            chip_g = VGroup(chip, chip_t)
            chip_t.move_to(chip.get_center())
            chip_g.next_to(card, RIGHT, buff=0.2)

            g = VGroup(card, t, chip_g)
            g.card = card
            g.text = t
            g.chip = chip_g
            g.it = it
            return g

        # Build initial unsorted list on left
        cards = VGroup(*[item_card(it) for it in items])
        cards.arrange(DOWN, buff=0.35)
        cards.move_to(np.array([left_x, top_y - 0.55, 0]))
        for c in cards:
            clamp_to_safe(c)

        self.play(LaggedStart(*[FadeIn(c, shift=0.2 * RIGHT) for c in cards], lag_ratio=0.15), run_time=0.9)
        self.wait(0.25)

        # ---------------------------
        # Visualize sorting by value/weight: reorder cards by moving
        # ---------------------------
        sorted_items = sorted(items, key=lambda d: d["v"] / d["w"], reverse=True)
        order = {it["name"]: i for i, it in enumerate(sorted_items)}
        targets = []
        for c in cards:
            i = order[c.it["name"]]
            t = c.copy()
            t.move_to(np.array([left_x, (top_y - 0.55) - i * row_dy, 0]))
            targets.append(t)

        self.play(*[c.animate.move_to(t.get_center()) for c, t in zip(cards, targets)], run_time=0.9)
        self.wait(0.25)

        # ---------------------------
        # Knapsack container on right
        # ---------------------------
        bag_w = 2.6
        bag_h = 3.2
        bag = RoundedRectangle(width=bag_w, height=bag_h, corner_radius=0.18)
        bag.set_fill(GREY_E, opacity=1)
        bag.set_stroke(WHITE, width=2)
        bag.move_to(np.array([right_x, 0.15, 0]))

        fill = Rectangle(width=bag_w - 0.18, height=0.01)
        fill.set_fill(c_fill, opacity=1)
        fill.set_stroke(width=0)
        fill.align_to(bag, DOWN)
        fill.shift(UP * 0.09)

        cap_line = Line(bag.get_left() + 0.08 * RIGHT, bag.get_right() + 0.08 * LEFT)
        cap_line.set_stroke(c_cap, width=4)
        cap_line.move_to(bag.get_top() + 0.08 * DOWN)
        cap_line.set_opacity(0.0)

        clamp_to_safe(VGroup(bag, fill))
        self.play(FadeIn(bag), run_time=0.6)
        self.play(FadeIn(fill), run_time=0.2)

        # Capacity label (single text at a time: title already present, but title is allowed.
        # We'll keep title only; no extra label.)

        # Tracker for fill fraction by weight
        cur_w = 0
        cur_v = 0

        def set_fill_fraction(frac, color=None):
            frac = np.clip(frac, 0, 1)
            new_h = (bag_h - 0.18) * frac
            if new_h < 0.02:
                new_h = 0.02
            new_fill = Rectangle(width=bag_w - 0.18, height=new_h)
            new_fill.set_stroke(width=0)
            new_fill.set_fill(color or c_fill, opacity=1)
            new_fill.align_to(bag, DOWN)
            new_fill.shift(UP * 0.09)
            return new_fill

        # ---------------------------
        # Pack items in greedy order: full, full, then fraction
        # ---------------------------
        main_visual = VGroup(cards, bag, fill)

        for idx, it in enumerate(sorted_items):
            # Highlight the current card
            card = [c for c in cards if c.it["name"] == it["name"]][0]
            ring = SurroundingRectangle(card.card, corner_radius=0.14)
            ring.set_stroke(WHITE, width=4)
            ring.set_fill(opacity=0)
            ring.set_z_index(10)
            self.play(Create(ring), run_time=0.25)

            remaining = cap - cur_w
            if it["w"] <= remaining:
                # Take full item: animate a mini-block into bag and fill rises
                token = RoundedRectangle(width=0.9, height=0.42, corner_radius=0.12)
                token.set_fill(c_fill, opacity=1)
                token.set_stroke(WHITE, width=1)
                token.move_to(card.get_right() + 0.7 * RIGHT)
                clamp_to_safe(token)
                self.play(FadeIn(token, shift=0.15 * RIGHT), run_time=0.25)

                # Move token into bag
                target_pt = bag.get_center() + np.array([0, -0.9 + 0.7 * idx, 0])
                target_pt[1] = np.clip(target_pt[1], bag.get_bottom()[1] + 0.35, bag.get_top()[1] - 0.35)
                self.play(token.animate.move_to(target_pt).scale(0.9), run_time=0.6)
                self.play(FadeOut(token), run_time=0.15)

                cur_w += it["w"]
                cur_v += it["v"]

                new_fill = set_fill_fraction(cur_w / cap, color=c_fill)
                self.play(Transform(fill, new_fill), run_time=0.55)
            else:
                # Take fraction: show partial token sliced, fill to the top
                frac = remaining / it["w"] if it["w"] > 0 else 0

                token_full = RoundedRectangle(width=0.9, height=0.42, corner_radius=0.12)
                token_full.set_fill(c_fill2, opacity=1)
                token_full.set_stroke(WHITE, width=1)
                token_full.move_to(card.get_right() + 0.7 * RIGHT)
                clamp_to_safe(token_full)

                # Slice indicator (masked by scaling about left)
                token_part = token_full.copy()
                token_part.set_fill(c_fill2, opacity=1)
                token_part.stretch_to_fit_width(0.9 * frac)
                token_part.move_to(token_full.get_left() + (0.9 * frac) / 2 * RIGHT)

                self.play(FadeIn(token_full, shift=0.15 * RIGHT), run_time=0.25)
                self.play(Transform(token_full, token_part), run_time=0.5)

                # Move fraction into bag and fill to cap
                self.play(token_full.animate.move_to(bag.get_center()), run_time=0.6)
                self.play(FadeOut(token_full), run_time=0.15)

                cur_w += remaining
                cur_v += it["v"] * frac

                new_fill = set_fill_fraction(1.0, color=c_fill2)
                self.play(Transform(fill, new_fill), FadeIn(cap_line.set_opacity(1.0)), run_time=0.55)
                break

            self.play(FadeOut(ring), run_time=0.2)
            self.wait(0.1)

        # ---------------------------
        # Compact equation appears late, briefly
        # ---------------------------
        # Remove cap line gently to reduce clutter before equation
        self.play(cap_line.animate.set_opacity(0.0), run_time=0.25)

        eq = MathTex(r"\text{pick max }\frac{v}{w}")
        eq.scale(1.05)
        eq.next_to(VGroup(bag, cards), DOWN, buff=0.65)
        eq.move_to(np.array([0, eq.get_y(), 0]))
        if abs(eq.get_x()) > 5.0:
            eq.move_to(np.array([0, -2.85, 0]))
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))

        self.play(FadeIn(eq), run_time=0.5)
        self.wait(0.9)
        self.play(FadeOut(eq), run_time=0.4)

        # End hold
        self.wait(0.6)


# You are an expert mathematical animator using the Manim Community Edition (Python).
