from manim import *
import numpy as np

# Manim Community Edition


def clamp(x, a, b):
    return max(a, min(b, x))


class QuickSortExplanation(Scene):
    def construct(self):
        self.camera.background_color = "#0e1116"

        # --------------------
        # Layout constants (safe region)
        # --------------------
        top_y = 3.15
        base_y = -0.55
        arrow_y = 1.25
        label_y = 2.05
        
        # Keep everything well inside [-6, 6] x [-3.4, 3.4]
        
        title = Text("Quick sort", font_size=44, weight=BOLD)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # Array values (small enough to fit)
        values = [7, 2, 1, 8, 6, 3, 5, 4]
        n = len(values)

        # Box geometry
        box_w = 1.05
        box_h = 0.75
        gap = 0.12
        total_w = n * box_w + (n - 1) * gap
        start_x = -total_w / 2 + box_w / 2

        def x_of(i):
            return start_x + i * (box_w + gap)

        def make_cell(i, val, color=BLUE_E):
            rect = RoundedRectangle(
                corner_radius=0.12,
                width=box_w,
                height=box_h,
                stroke_width=2.0,
                stroke_color=GRAY_B,
                fill_color=color,
                fill_opacity=0.35,
            )
            rect.move_to([x_of(i), base_y, 0])
            num = Text(str(val), font_size=32)
            num.move_to(rect.get_center())
            return VGroup(rect, num)

        cells = VGroup(*[make_cell(i, v) for i, v in enumerate(values)])
        self.play(LaggedStart(*[FadeIn(c, shift=0.15 * DOWN) for c in cells], lag_ratio=0.06), run_time=1.1)

        # Minimal label (only one text block at once)
        label = Text("pivot", font_size=28)
        label.move_to([0, label_y, 0])

        # Choose pivot: last element
        pivot_i = n - 1
        pivot_cell = cells[pivot_i]
        pivot_rect = pivot_cell[0]

        pivot_glow = SurroundingRectangle(
            pivot_rect,
            color=YELLOW,
            buff=0.08,
            stroke_width=4,
        )

        pivot_arrow = Arrow(
            start=[x_of(pivot_i), arrow_y, 0],
            end=[x_of(pivot_i), base_y + box_h / 2 + 0.08, 0],
            buff=0,
            stroke_width=6,
            max_tip_length_to_length_ratio=0.22,
            color=YELLOW,
        )

        self.play(Create(pivot_arrow), FadeIn(pivot_glow), run_time=0.7)
        self.play(FadeIn(label, shift=0.1 * UP), run_time=0.5)
        self.wait(0.25)

        # --------------------
        # Partition visualization
        # --------------------
        # We'll do Lomuto partition around pivot value.
        pivot_val = values[pivot_i]

        # Two regions: < pivot and >= pivot (shown by subtle bands)
        left_band = Rectangle(
            width=3.9,
            height=0.98,
            stroke_width=0,
            fill_color=GREEN,
            fill_opacity=0.10,
        ).move_to([-2.05, base_y, 0])

        right_band = Rectangle(
            width=3.9,
            height=0.98,
            stroke_width=0,
            fill_color=RED,
            fill_opacity=0.08,
        ).move_to([2.05, base_y, 0])

        # Place bands behind cells
        bands = VGroup(left_band, right_band)
        self.play(FadeIn(bands), run_time=0.5)
        self.wait(0.15)

        # Remove label (text) before any other text appears later
        self.play(FadeOut(label), run_time=0.35)

        # Pointer i and scan j
        i = -1
        j = 0

        i_marker = Triangle(color=GREEN_C, fill_opacity=1).scale(0.18)
        i_marker.rotate(PI)
        i_marker.move_to([x_of(0), base_y - 0.58, 0])

        j_marker = Triangle(color=TEAL_A, fill_opacity=1).scale(0.18)
        j_marker.rotate(PI)
        j_marker.move_to([x_of(0), base_y - 0.58, 0])

        # Slight horizontal offsets so markers don't overlap
        i_marker.shift(0.18 * LEFT)
        j_marker.shift(0.18 * RIGHT)

        self.play(FadeIn(i_marker, shift=0.15 * DOWN), FadeIn(j_marker, shift=0.15 * DOWN), run_time=0.6)

        def highlight_cell(idx, color, opacity=0.55):
            rect = cells[idx][0]
            return rect.animate.set_fill(color, opacity)

        def unhighlight_cell(idx):
            rect = cells[idx][0]
            return rect.animate.set_fill(BLUE_E, 0.35)

        def move_marker_to(marker, idx, side_shift=0):
            return marker.animate.move_to([x_of(idx), base_y - 0.58, 0]).shift(side_shift * RIGHT)

        # Partition loop for j = 0..n-2
        for j in range(0, n - 1):
            # Move scan marker
            self.play(move_marker_to(j_marker, j, side_shift=0.18), run_time=0.35)

            # Compare visually by flashing cell vs pivot
            self.play(
                highlight_cell(j, TEAL_D, 0.55),
                pivot_rect.animate.set_fill(YELLOW_D, 0.50),
                run_time=0.25,
            )
            self.play(
                pivot_rect.animate.set_fill(BLUE_E, 0.35),
                run_time=0.15,
            )

            if values[j] < pivot_val:
                i += 1

                # Move i marker
                self.play(move_marker_to(i_marker, i, side_shift=-0.18), run_time=0.35)

                # If i != j, swap elements (animate swapping the cell groups)
                if i != j:
                    # Swap animation: cells[i] and cells[j] exchange positions
                    ci = cells[i]
                    cj = cells[j]
                    pos_i = ci.get_center()
                    pos_j = cj.get_center()

                    # Bring forward for clarity
                    self.play(ci.animate.set_z_index(2), cj.animate.set_z_index(2), run_time=0.1)

                    self.play(
                        ci.animate.move_to(pos_j + 0.35 * UP),
                        cj.animate.move_to(pos_i + 0.35 * UP),
                        run_time=0.45,
                    )
                    self.play(
                        ci.animate.move_to(pos_j),
                        cj.animate.move_to(pos_i),
                        run_time=0.35,
                    )

                    # Swap in data and in VGroup ordering
                    values[i], values[j] = values[j], values[i]
                    cells[i], cells[j] = cells[j], cells[i]

                    # Restore z-index
                    cells[i].set_z_index(0)
                    cells[j].set_z_index(0)

                # Mark left side as "good": brief green tint
                self.play(cells[i][0].animate.set_fill(GREEN_D, 0.42), run_time=0.2)

            # Unhighlight scan cell
            self.play(unhighlight_cell(j), run_time=0.2)

        # Place pivot to its final spot (swap i+1 with pivot)
        pivot_final = i + 1

        # Move markers to show boundary
        if pivot_final < n:
            self.play(move_marker_to(i_marker, clamp(pivot_final - 1, 0, n - 1), side_shift=-0.18), run_time=0.35)

        # Highlight pivot again
        self.play(
            Create(pivot_arrow),
            FadeIn(pivot_glow),
            pivot_rect.animate.set_fill(YELLOW_D, 0.50),
            run_time=0.5,
        )

        if pivot_final != pivot_i:
            cp = cells[pivot_i]
            ck = cells[pivot_final]
            pos_p = cp.get_center()
            pos_k = ck.get_center()

            self.play(cp.animate.set_z_index(3), ck.animate.set_z_index(3), run_time=0.1)
            self.play(
                cp.animate.move_to(pos_k + 0.45 * UP),
                ck.animate.move_to(pos_p + 0.45 * UP),
                run_time=0.55,
            )
            self.play(
                cp.animate.move_to(pos_k),
                ck.animate.move_to(pos_p),
                run_time=0.35,
            )

            values[pivot_i], values[pivot_final] = values[pivot_final], values[pivot_i]
            cells[pivot_i], cells[pivot_final] = cells[pivot_final], cells[pivot_i]

            cells[pivot_i].set_z_index(0)
            cells[pivot_final].set_z_index(0)

        # Pivot is now fixed
        pivot_rect_final = cells[pivot_final][0]
        pivot_lock = SurroundingRectangle(pivot_rect_final, color=YELLOW, buff=0.08, stroke_width=4)
        self.play(
            FadeOut(pivot_glow),
            FadeOut(pivot_arrow),
            pivot_rect_final.animate.set_fill(YELLOW_D, 0.50),
            Create(pivot_lock),
            run_time=0.6,
        )

        # Clean up markers and bands
        self.play(FadeOut(i_marker), FadeOut(j_marker), FadeOut(bands), run_time=0.5)

        # --------------------
        # Recurse visually: show two subarrays
        # --------------------
        # Dim everything then spotlight left and right ranges.
        dim_anims = []
        for idx in range(n):
            if idx == pivot_final:
                continue
            dim_anims.append(cells[idx][0].animate.set_fill(BLUE_E, 0.18))
        self.play(*dim_anims, run_time=0.5)

        # Brace left part
        left_len = pivot_final
        right_len = n - pivot_final - 1

        left_brace = None
        right_brace = None

        if left_len >= 2:
            left_group = VGroup(*[cells[k] for k in range(0, pivot_final)])
            left_brace = Brace(left_group, DOWN, buff=0.12)
        if right_len >= 2:
            right_group = VGroup(*[cells[k] for k in range(pivot_final + 1, n)])
            right_brace = Brace(right_group, DOWN, buff=0.12)

        # One short text at a time
        if left_brace is not None:
            t = Text("left", font_size=28)
            t.next_to(left_brace, DOWN, buff=0.15)
            t.move_to([t.get_x(), max(t.get_y(), -3.05), 0])
            self.play(GrowFromCenter(left_brace), FadeIn(t), run_time=0.6)
            self.wait(0.25)
            self.play(FadeOut(t), run_time=0.3)

        if right_brace is not None:
            t = Text("right", font_size=28)
            t.next_to(right_brace, DOWN, buff=0.15)
            t.move_to([t.get_x(), max(t.get_y(), -3.05), 0])
            self.play(GrowFromCenter(right_brace), FadeIn(t), run_time=0.6)
            self.wait(0.25)
            self.play(FadeOut(t), run_time=0.3)

        # Collapse to a smaller overview and show recursion as repeated partitioning strokes
        # (No more text; just motion.)
        all_group = VGroup(*cells, pivot_lock, title)
        self.play(all_group.animate.scale(0.92).shift(0.10 * UP), run_time=0.6)

        # Simple recursive indication: quickly "fix" a pivot in left and right by flashing
        def flash_fixed(idx, color=YELLOW):
            r = SurroundingRectangle(cells[idx][0], color=color, buff=0.07, stroke_width=3)
            return r

        # Choose representative pivots (not actual full recursion), to communicate idea
        flashes = VGroup()
        if left_len >= 2:
            idx = 1
            flashes.add(flash_fixed(idx))
        if right_len >= 2:
            idx = pivot_final + 2 if pivot_final + 2 < n else n - 1
            flashes.add(flash_fixed(idx))

        if len(flashes) > 0:
            self.play(LaggedStart(*[Create(f) for f in flashes], lag_ratio=0.25), run_time=0.9)
            self.play(LaggedStart(*[FadeOut(f) for f in flashes], lag_ratio=0.2), run_time=0.6)

        # Final compact equation (brief)
        eq = MathTex("T(n)=T(k)+T(n-k-1)+\Theta(n)")
        eq.scale(0.9)
        eq.move_to([0, -2.75, 0])
        eq.set_color(GRAY_A)
        # ensure safe x
        eq.move_to([clamp(eq.get_x(), -5.0, 5.0), eq.get_y(), 0])

        self.play(FadeIn(eq), run_time=0.6)
        self.wait(0.9)
        self.play(FadeOut(eq), run_time=0.5)

        # Fade out braces if they exist
        outs = []
        if left_brace is not None:
            outs.append(FadeOut(left_brace))
        if right_brace is not None:
            outs.append(FadeOut(right_brace))
        if outs:
            self.play(*outs, run_time=0.4)

        # End: emphasize sorted structure by gradient fill left->right
        for idx in range(n):
            hue = idx / max(1, n - 1)
            color = interpolate_color(BLUE_D, GREEN_D, hue)
            self.play(cells[idx][0].animate.set_fill(color, 0.40), run_time=0.10)
        self.wait(0.6)

        self.play(FadeOut(VGroup(*cells, pivot_lock)), FadeOut(title), run_time=0.8)
        self.wait(0.2)
