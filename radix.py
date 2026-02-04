from manim import *
import numpy as np

# Manim Community Edition


def clamp(x, a, b):
    return max(a, min(b, x))


class RadixSortExplanation(Scene):
    def construct(self):
        self.camera.background_color = "#0e1116"

        # Safe region guides (implicit): x in [-6,6], y in [-3.4,3.4]
        top_band_y = 3.15
        bottom_y = -2.9

        # --------------------
        # Layout constants
        # --------------------
        base = 10
        bin_w, bin_h = 0.9, 0.7
        bins_y = -0.55
        arr_y = 2.0
        out_y = 0.95

        # --------------------
        # Helpers
        # --------------------
        def number_card(n, w=1.05, h=0.62):
            r = RoundedRectangle(width=w, height=h, corner_radius=0.12, stroke_width=2)
            r.set_stroke(GRAY_B)
            r.set_fill(color="#111722", opacity=0.95)
            t = Text(str(n), font_size=26, weight=BOLD)
            t.move_to(r.get_center())
            g = VGroup(r, t)
            return g

        def digit_marker(char, color=YELLOW_C):
            # Small highlight behind a digit character
            rect = RoundedRectangle(width=0.34, height=0.44, corner_radius=0.08, stroke_width=0)
            rect.set_fill(color, opacity=0.35)
            txt = Text(str(char), font_size=28, weight=BOLD, color=WHITE)
            txt.move_to(rect.get_center())
            return VGroup(rect, txt)

        def make_bin(i):
            box = RoundedRectangle(width=bin_w, height=bin_h, corner_radius=0.12, stroke_width=2)
            box.set_stroke(GRAY_C)
            box.set_fill(color="#0b1220", opacity=0.9)
            lab = Text(str(i), font_size=20, color=GRAY_A)
            lab.move_to(box.get_top() + 0.18 * DOWN)
            g = VGroup(box, lab)
            return g

        def get_digit(n, place):
            # place=0 ones, 1 tens
            return (n // (10 ** place)) % 10

        def stable_brace(mobj):
            b = Brace(mobj, DOWN, color=GRAY_A)
            t = Text("stable", font_size=26, color=GRAY_A)
            t.next_to(b, DOWN, buff=0.15)
            return VGroup(b, t)

        # --------------------
        # Scene 1: Show array (no text first)
        # --------------------
        nums = [170, 45, 75, 90, 802, 24, 2, 66]
        cards = VGroup(*[number_card(n) for n in nums]).arrange(RIGHT, buff=0.18)
        if cards.width > 11.2:
            cards.scale_to_fit_width(11.2)
        cards.move_to([0, arr_y, 0])

        self.play(LaggedStart(*[FadeIn(c, shift=0.15 * UP) for c in cards], lag_ratio=0.08), run_time=0.8)
        self.wait(0.25)

        # Brief label after the visual appears
        title = Text("radix sort", font_size=44, weight=BOLD)
        title.to_edge(UP)
        title.set_y(top_band_y)
        self.play(FadeIn(title, shift=0.12 * UP), run_time=0.55)
        self.wait(0.35)
        self.play(FadeOut(title), run_time=0.25)

        # --------------------
        # Create bins 0..9
        # --------------------
        bins = VGroup(*[make_bin(i) for i in range(base)]).arrange(RIGHT, buff=0.14)
        if bins.width > 11.4:
            bins.scale_to_fit_width(11.4)
        bins.move_to([0, bins_y, 0])

        self.play(FadeIn(bins, shift=0.1 * DOWN), run_time=0.6)
        self.wait(0.2)

        # Output row placeholder (where we collect after each pass)
        out_row = VGroup(*[c.copy() for c in cards]).arrange(RIGHT, buff=0.18)
        out_row.set_opacity(0)
        if out_row.width > 11.2:
            out_row.scale_to_fit_width(11.2)
        out_row.move_to([0, out_y, 0])
        self.add(out_row)

        # --------------------
        # Pass animation function
        # --------------------
        def run_pass(place, label_text):
            # Single text block label, below main visual
            lbl = Text(label_text, font_size=30, color=GRAY_A)
            lbl.move_to([0, bottom_y, 0])
            lbl.move_to([clamp(lbl.get_x(), -5.0, 5.0), lbl.get_y(), 0])

            self.play(FadeIn(lbl), run_time=0.35)
            self.wait(0.1)
            self.play(FadeOut(lbl), run_time=0.2)

            # Buckets: list of lists of card mobjects (we'll move copies for clarity)
            buckets = [[] for _ in range(base)]

            # Working copies that will move into bins
            moving = VGroup(*[c.copy() for c in cards])
            for m, c in zip(moving, cards):
                m.move_to(c.get_center())
            self.add(moving)

            # For each number, highlight digit and drop into bin
            for idx, (n, mob) in enumerate(zip(nums, moving)):
                d = get_digit(n, place)

                # Digit highlight marker near the card (right side)
                s = str(n)
                # pick digit char from the right
                ch = s[-(place + 1)] if len(s) > place else "0"
                dm = digit_marker(ch)
                dm.scale(0.85)
                dm.next_to(mob, DOWN, buff=0.08)
                # keep within safe region by nudging slightly up if near bottom
                if dm.get_bottom()[1] < -3.2:
                    dm.shift(0.25 * UP)

                self.play(FadeIn(dm, scale=0.95), run_time=0.12)

                # Compute target stack position in bin
                bin_box = bins[d][0]
                stack_level = len(buckets[d])
                target = bin_box.get_bottom() + 0.18 * UP + stack_level * 0.58 * UP

                # If stack goes too high, slightly compress spacing (won't happen for small demo)
                if target[1] > 1.35:
                    target = bin_box.get_bottom() + 0.18 * UP + stack_level * 0.48 * UP

                path = ArcBetweenPoints(mob.get_center(), target, angle=-TAU / 8)
                self.play(MoveAlongPath(mob, path), run_time=0.28)
                self.play(FadeOut(dm), run_time=0.08)
                buckets[d].append(mob)

            self.wait(0.15)

            # Collect back in order 0..9 into output row (stable by construction)
            collected = []
            for d in range(base):
                collected += buckets[d]

            targets = VGroup(*[m.copy() for m in collected]).arrange(RIGHT, buff=0.18)
            if targets.width > 11.2:
                targets.scale_to_fit_width(11.2)
            targets.move_to([0, out_y, 0])

            # Move the actual mobjects to their new output positions
            self.play(*[m.animate.move_to(t.get_center()) for m, t in zip(collected, targets)], run_time=0.7)

            # Update cards order & nums order to match collected
            new_cards = VGroup(*collected)
            # Replace original cards on top row by transforming positions (keep top row as current array)
            top_targets = VGroup(*[m.copy() for m in collected]).arrange(RIGHT, buff=0.18)
            if top_targets.width > 11.2:
                top_targets.scale_to_fit_width(11.2)
            top_targets.move_to([0, arr_y, 0])

            self.play(*[m.animate.move_to(tt.get_center()) for m, tt in zip(collected, top_targets)], run_time=0.7)

            # Rewrite global order
            new_nums = [int(c[1].text) for c in collected]

            # Clear and set
            self.remove(cards)
            return new_nums, new_cards

        # --------------------
        # Pass 1: ones
        # --------------------
        nums, cards = run_pass(place=0, label_text="ones")

        # Show stability cue briefly (single text block: brace+text is one group, still only one text)
        brace = stable_brace(cards)
        brace.move_to([0, -2.55, 0])
        if brace.get_bottom()[1] < -3.2:
            brace.shift(0.25 * UP)
        self.play(FadeIn(brace), run_time=0.45)
        self.wait(0.35)
        self.play(FadeOut(brace), run_time=0.25)

        # --------------------
        # Pass 2: tens
        # --------------------
        nums, cards = run_pass(place=1, label_text="tens")

        # --------------------
        # Pass 3: hundreds
        # --------------------
        nums, cards = run_pass(place=2, label_text="hundreds")

        # --------------------
        # Late compact formalism
        # --------------------
        self.play(FadeOut(bins), run_time=0.4)
        eq = MathTex(r"k\ \text{passes} \Rightarrow O(k\,n)")
        eq.set_color(GRAY_A)
        eq.move_to([0, bottom_y, 0])
        eq.move_to([clamp(eq.get_x(), -5.0, 5.0), eq.get_y(), 0])

        self.play(FadeIn(eq), run_time=0.6)
        self.wait(0.9)
        self.play(FadeOut(eq), run_time=0.35)

        self.play(FadeOut(cards), run_time=0.8)
        self.wait(0.15)
