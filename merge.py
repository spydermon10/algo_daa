from manim import *
import numpy as np

# Manim Community Edition


def clamp(x, a, b):
    return max(a, min(b, x))


class MergeSortExplanation(Scene):
    def construct(self):
        self.camera.background_color = "#0e1116"

        # --------------------
        # Safe-region layout constants
        # --------------------
        top_y = 3.15
        base_y = 1.05
        lower_y = -0.35
        out_y = -1.85

        title = Text("Merge sort", font_size=44, weight=BOLD)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # Values chosen to fit nicely
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

        def make_cell(val, color=BLUE_E):
            rect = RoundedRectangle(
                corner_radius=0.12,
                width=box_w,
                height=box_h,
                stroke_width=2.0,
                stroke_color=GRAY_B,
                fill_color=color,
                fill_opacity=0.35,
            )
            num = Text(str(val), font_size=32)
            num.move_to(rect.get_center())
            g = VGroup(rect, num)
            return g

        # Initial row
        cells = VGroup(*[make_cell(v) for v in values])
        for i, c in enumerate(cells):
            c.move_to([x_of(i), base_y, 0])

        self.play(
            LaggedStart(*[FadeIn(c, shift=0.15 * DOWN) for c in cells], lag_ratio=0.06),
            run_time=1.1,
        )
        self.wait(0.2)

        # --------------------
        # SPLIT (show before naming)
        # --------------------
        # Create a subtle divider that appears and then the array splits into two halves.
        split_line = Line([0, base_y + 0.65, 0], [0, base_y - 0.65, 0], color=GRAY_A, stroke_width=3)
        split_line.set_opacity(0.6)
        self.play(Create(split_line), run_time=0.45)

        left_half = VGroup(*cells[: n // 2])
        right_half = VGroup(*cells[n // 2 :])

        self.play(
            left_half.animate.shift(1.15 * LEFT),
            right_half.animate.shift(1.15 * RIGHT),
            run_time=0.7,
        )
        self.play(FadeOut(split_line), run_time=0.25)

        # Brief label after the split is visually clear
        label = Text("split", font_size=28)
        label.move_to([0, lower_y, 0])
        label.move_to([clamp(label.get_x(), -5.0, 5.0), label.get_y(), 0])
        self.play(FadeIn(label), run_time=0.35)
        self.wait(0.25)
        self.play(FadeOut(label), run_time=0.25)

        # Split again into quarters (visual recursion hint)
        q1 = VGroup(*cells[:2])
        q2 = VGroup(*cells[2:4])
        q3 = VGroup(*cells[4:6])
        q4 = VGroup(*cells[6:])

        # Add small vertical offsets to reduce crowding and keep inside safe frame
        self.play(
            q1.animate.shift(0.55 * UP + 0.50 * LEFT),
            q2.animate.shift(0.55 * UP + 0.50 * RIGHT),
            q3.animate.shift(0.55 * DOWN + 0.50 * LEFT),
            q4.animate.shift(0.55 * DOWN + 0.50 * RIGHT),
            run_time=0.8,
        )
        self.wait(0.15)

        # --------------------
        # MERGE (show a single merge in detail)
        # --------------------
        # We'll merge [7,2] and [1,8] into a sorted 4-list using an output row.
        # First, bring the top two quarters into a clean merge stage.
        stage_top = 0.95
        stage_mid = 0.15

        top_left = q1
        top_right = q2

        # Arrange them neatly
        def move_group_to_positions(group, xs, y):
            anims = []
            for mob, x in zip(group, xs):
                anims.append(mob.animate.move_to([x, y, 0]))
            return anims

        # Compute target x positions for two 2-lists centered
        tw = 2 * box_w + gap
        left_center_x = -1.85
        right_center_x = 1.85
        left_xs = [left_center_x - (box_w + gap) / 2, left_center_x + (box_w + gap) / 2]
        right_xs = [right_center_x - (box_w + gap) / 2, right_center_x + (box_w + gap) / 2]

        self.play(
            *move_group_to_positions(top_left, left_xs, stage_top),
            *move_group_to_positions(top_right, right_xs, stage_top),
            run_time=0.8,
        )

        # Dim the bottom quarters to focus attention
        dim_anims = []
        for mob in list(q3) + list(q4):
            dim_anims.append(mob[0].animate.set_fill(BLUE_E, 0.14))
        self.play(*dim_anims, run_time=0.4)

        # Create output slots (empty outlines) for 4 merged items
        out_total_w = 4 * box_w + 3 * gap
        out_start_x = -out_total_w / 2 + box_w / 2
        out_xs = [out_start_x + i * (box_w + gap) for i in range(4)]

        slots = VGroup()
        for x in out_xs:
            r = RoundedRectangle(
                corner_radius=0.12,
                width=box_w,
                height=box_h,
                stroke_width=2.0,
                stroke_color=GRAY_C,
                fill_opacity=0,
            ).move_to([x, stage_mid, 0])
            slots.add(r)

        self.play(FadeIn(slots), run_time=0.45)

        # Pointers above current heads (two triangles)
        pL = Triangle(color=GREEN_C, fill_opacity=1).scale(0.18).rotate(PI)
        pR = Triangle(color=RED_C, fill_opacity=1).scale(0.18).rotate(PI)
        pL.move_to(top_left[0].get_bottom() + 0.25 * DOWN)
        pR.move_to(top_right[0].get_bottom() + 0.25 * DOWN)

        # Shift to avoid overlap if close
        pL.shift(0.18 * LEFT)
        pR.shift(0.18 * RIGHT)

        self.play(FadeIn(pL, shift=0.1 * DOWN), FadeIn(pR, shift=0.1 * DOWN), run_time=0.5)

        # Helper to read current values from text
        def cell_value(cell):
            return int(cell[1].text)

        left_list = [top_left[0], top_left[1]]
        right_list = [top_right[0], top_right[1]]
        li = 0
        ri = 0
        out_index = 0

        def highlight_head(cell, color):
            return cell[0].animate.set_fill(color, 0.55)

        def unhighlight_cell(cell, base_opacity=0.35):
            return cell[0].animate.set_fill(BLUE_E, base_opacity)

        def move_pointer(pointer, cell):
            return pointer.animate.move_to(cell.get_bottom() + 0.25 * DOWN)

        # Perform merge by moving chosen cell into the next output slot.
        merged_cells = []

        while out_index < 4:
            left_avail = li < 2
            right_avail = ri < 2

            choose_left = False
            if left_avail and right_avail:
                choose_left = cell_value(left_list[li]) <= cell_value(right_list[ri])
            elif left_avail:
                choose_left = True
            else:
                choose_left = False

            if choose_left:
                chosen = left_list[li]
                head_anim = highlight_head(chosen, GREEN_D)
                other = right_list[ri] if right_avail else None
                other_anim = highlight_head(other, RED_D) if other is not None else None
                self.play(head_anim, *( [other_anim] if other_anim is not None else [] ), run_time=0.25)

                # Move chosen into slot
                target = slots[out_index].get_center()
                self.play(
                    chosen.animate.set_z_index(3).move_to(target + 0.35 * UP),
                    run_time=0.45,
                )
                self.play(chosen.animate.move_to(target), run_time=0.25)
                merged_cells.append(chosen)

                # Mark as placed
                self.play(chosen[0].animate.set_fill(GREEN_D, 0.42), run_time=0.18)

                # Advance left pointer
                li += 1
                if li < 2:
                    self.play(move_pointer(pL, left_list[li]).shift(0.18 * LEFT), run_time=0.25)
                else:
                    self.play(FadeOut(pL), run_time=0.2)

                # Clean highlights
                if other is not None:
                    self.play(unhighlight_cell(other, base_opacity=0.35), run_time=0.12)

            else:
                chosen = right_list[ri]
                head_anim = highlight_head(chosen, RED_D)
                other = left_list[li] if left_avail else None
                other_anim = highlight_head(other, GREEN_D) if other is not None else None
                self.play(head_anim, *( [other_anim] if other_anim is not None else [] ), run_time=0.25)

                target = slots[out_index].get_center()
                self.play(
                    chosen.animate.set_z_index(3).move_to(target + 0.35 * UP),
                    run_time=0.45,
                )
                self.play(chosen.animate.move_to(target), run_time=0.25)
                merged_cells.append(chosen)

                self.play(chosen[0].animate.set_fill(RED_D, 0.42), run_time=0.18)

                ri += 1
                if ri < 2:
                    self.play(move_pointer(pR, right_list[ri]).shift(0.18 * RIGHT), run_time=0.25)
                else:
                    self.play(FadeOut(pR), run_time=0.2)

                if other is not None:
                    self.play(unhighlight_cell(other, base_opacity=0.35), run_time=0.12)

            out_index += 1

        # Fade original input outlines (now moved) and keep only merged row
        self.play(FadeOut(slots), run_time=0.35)

        # Re-center the merged 4-list as a single group on the upper row
        merged_top = VGroup(*merged_cells)
        for i, mob in enumerate(merged_top):
            mob.set_z_index(0)
            mob[0].set_fill(BLUE_E, 0.35)
            mob.move_to([out_xs[i], stage_top, 0])

        # Show that the top half is now "merged"
        label = Text("merge", font_size=28)
        label.move_to([0, lower_y, 0])
        label.move_to([clamp(label.get_x(), -5.0, 5.0), label.get_y(), 0])
        self.play(FadeIn(label), run_time=0.35)
        self.wait(0.25)
        self.play(FadeOut(label), run_time=0.25)

        # --------------------
        # SHOW FINAL MERGE (fast, as motion)
        # --------------------
        # Build bottom merged 4-list quickly by sorting values visually (without extra text).
        bottom_cells = VGroup(*list(q3) + list(q4))

        # Bring bottom cells into two 2-lists, then into a 4-list below
        bottom_left = VGroup(bottom_cells[0], bottom_cells[1])
        bottom_right = VGroup(bottom_cells[2], bottom_cells[3])

        # Restore opacity for bottom cells
        self.play(*[c[0].animate.set_fill(BLUE_E, 0.35) for c in bottom_cells], run_time=0.3)

        # Arrange bottom inputs
        self.play(
            *move_group_to_positions(bottom_left, left_xs, out_y + 1.0),
            *move_group_to_positions(bottom_right, right_xs, out_y + 1.0),
            run_time=0.7,
        )

        # Create temporary slots for bottom merge
        slots2 = VGroup()
        for x in out_xs:
            r = RoundedRectangle(
                corner_radius=0.12,
                width=box_w,
                height=box_h,
                stroke_width=2.0,
                stroke_color=GRAY_C,
                fill_opacity=0,
            ).move_to([x, out_y, 0])
            slots2.add(r)
        self.play(FadeIn(slots2), run_time=0.3)

        # Actually compute bottom merge order (stable) and move accordingly
        bl = [bottom_left[0], bottom_left[1]]
        br = [bottom_right[0], bottom_right[1]]
        bl_sorted = sorted(bl, key=cell_value)
        br_sorted = sorted(br, key=cell_value)

        # Put them in sorted order within each pair (quick swap if needed)
        def maybe_swap_pair(pair_group, a, b):
            if cell_value(a) <= cell_value(b):
                return []
            pos_a = a.get_center()
            pos_b = b.get_center()
            return [
                a.animate.move_to(pos_b + 0.25 * UP),
                b.animate.move_to(pos_a + 0.25 * UP),
            ]

        # Swap within each 2-group if needed
        self.play(*maybe_swap_pair(bottom_left, bottom_left[0], bottom_left[1]), run_time=0.45)
        # refresh ordering visually by x positions
        bottom_left_arr = sorted([bottom_left[0], bottom_left[1]], key=lambda m: m.get_x())
        bottom_left = VGroup(*bottom_left_arr)

        self.play(*maybe_swap_pair(bottom_right, bottom_right[0], bottom_right[1]), run_time=0.45)
        bottom_right_arr = sorted([bottom_right[0], bottom_right[1]], key=lambda m: m.get_x())
        bottom_right = VGroup(*bottom_right_arr)

        # Merge these two sorted pairs into slots2 (fast)
        L = list(bottom_left)
        R = list(bottom_right)
        li2 = 0
        ri2 = 0
        out2 = []
        for k in range(4):
            choose_L = False
            if li2 < 2 and ri2 < 2:
                choose_L = cell_value(L[li2]) <= cell_value(R[ri2])
            elif li2 < 2:
                choose_L = True
            else:
                choose_L = False
            chosen = L[li2] if choose_L else R[ri2]
            if choose_L:
                li2 += 1
            else:
                ri2 += 1
            out2.append(chosen)

        self.play(
            LaggedStart(
                *[
                    out2[i].animate.set_z_index(3).move_to(slots2[i].get_center() + 0.25 * UP)
                    for i in range(4)
                ],
                lag_ratio=0.08,
            ),
            run_time=0.8,
        )
        self.play(
            LaggedStart(
                *[out2[i].animate.move_to(slots2[i].get_center()) for i in range(4)],
                lag_ratio=0.08,
            ),
            run_time=0.5,
        )
        self.play(FadeOut(slots2), run_time=0.3)

        bottom_merged = VGroup(*out2)
        for i, mob in enumerate(bottom_merged):
            mob.set_z_index(0)
            mob[0].set_fill(BLUE_E, 0.35)
            mob.move_to([out_xs[i], out_y + 1.0, 0])

        # --------------------
        # FINAL MERGE (8 -> 8)
        # --------------------
        # Create final output row at y = base_y (middle) and merge top_merged + bottom_merged down into it.
        final_y = -0.65
        final_total_w = n * box_w + (n - 1) * gap
        final_start_x = -final_total_w / 2 + box_w / 2
        final_xs = [final_start_x + i * (box_w + gap) for i in range(n)]

        slotsF = VGroup()
        for x in final_xs:
            r = RoundedRectangle(
                corner_radius=0.12,
                width=box_w,
                height=box_h,
                stroke_width=2.0,
                stroke_color=GRAY_C,
                fill_opacity=0,
            ).move_to([x, final_y, 0])
            slotsF.add(r)

        self.play(FadeIn(slotsF), run_time=0.35)

        # Prepare lists (already sorted 4 and 4, by construction above)
        top_sorted = list(merged_top)
        bot_sorted = list(bottom_merged)

        # Move them to be clearly two rows feeding into final
        self.play(
            *[m.animate.move_to([m.get_x(), 1.15, 0]) for m in top_sorted],
            *[m.animate.move_to([m.get_x(), -2.05, 0]) for m in bot_sorted],
            run_time=0.7,
        )

        # Two pointers for final merge
        pT = Triangle(color=GREEN_C, fill_opacity=1).scale(0.18).rotate(PI)
        pB = Triangle(color=RED_C, fill_opacity=1).scale(0.18).rotate(PI)
        pT.move_to(top_sorted[0].get_bottom() + 0.25 * DOWN).shift(0.18 * LEFT)
        pB.move_to(bot_sorted[0].get_top() + 0.25 * UP).shift(0.18 * LEFT)
        self.play(FadeIn(pT), FadeIn(pB), run_time=0.45)

        ti = 0
        bi = 0
        placed = []
        for k in range(n):
            choose_top = False
            if ti < 4 and bi < 4:
                choose_top = cell_value(top_sorted[ti]) <= cell_value(bot_sorted[bi])
            elif ti < 4:
                choose_top = True
            else:
                choose_top = False

            chosen = top_sorted[ti] if choose_top else bot_sorted[bi]
            other = bot_sorted[bi] if choose_top and bi < 4 else (top_sorted[ti] if (not choose_top and ti < 4) else None)

            # quick compare flash
            anims = [chosen[0].animate.set_fill(YELLOW_D, 0.55)]
            if other is not None:
                anims.append(other[0].animate.set_fill(GRAY_D, 0.40))
            self.play(*anims, run_time=0.18)

            target = slotsF[k].get_center()
            self.play(chosen.animate.set_z_index(4).move_to(target + 0.28 * UP), run_time=0.32)
            self.play(chosen.animate.move_to(target), run_time=0.20)
            chosen[0].set_fill(BLUE_E, 0.35)
            if other is not None:
                other[0].set_fill(BLUE_E, 0.35)

            placed.append(chosen)

            if choose_top:
                ti += 1
                if ti < 4:
                    self.play(pT.animate.move_to(top_sorted[ti].get_bottom() + 0.25 * DOWN).shift(0.18 * LEFT), run_time=0.18)
                else:
                    self.play(FadeOut(pT), run_time=0.18)
            else:
                bi += 1
                if bi < 4:
                    self.play(pB.animate.move_to(bot_sorted[bi].get_top() + 0.25 * UP).shift(0.18 * LEFT), run_time=0.18)
                else:
                    self.play(FadeOut(pB), run_time=0.18)

        self.play(FadeOut(slotsF), run_time=0.25)

        final_row = VGroup(*placed)
        for i, mob in enumerate(final_row):
            mob.set_z_index(0)
            mob.move_to([final_xs[i], final_y, 0])

        # Brief compact equation (late, brief)
        eq = MathTex("T(n)=2T(n/2)+\Theta(n)")
        eq.scale(0.9)
        eq.set_color(GRAY_A)
        eq.move_to([0, -2.85, 0])
        eq.move_to([clamp(eq.get_x(), -5.0, 5.0), eq.get_y(), 0])

        self.play(FadeIn(eq), run_time=0.6)
        self.wait(0.7)
        self.play(FadeOut(eq), run_time=0.45)

        # Final color sweep to emphasize sorted order
        for idx, mob in enumerate(final_row):
            hue = idx / max(1, n - 1)
            color = interpolate_color(BLUE_D, GREEN_D, hue)
            self.play(mob[0].animate.set_fill(color, 0.42), run_time=0.09)

        self.wait(0.6)
        self.play(FadeOut(VGroup(final_row, title)), run_time=0.9)
        self.wait(0.2)
