from manim import *
import numpy as np

# Manim Community Edition
# Single-scene, insight-first visualization of Prim's algorithm.


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


class PrimsAlgorithm(Scene):
    def construct(self):
        title = Text("Prim's algorithm", font_size=44)
        title.to_edge(UP)
        self.play(FadeIn(title, shift=0.2 * UP), run_time=0.8)

        # ---------------------------
        # Graph layout (kept well inside safe region)
        # ---------------------------
        pts = {
            "A": np.array([-4.2,  1.6, 0]),
            "B": np.array([-1.5,  2.2, 0]),
            "C": np.array([ 1.4,  1.7, 0]),
            "D": np.array([ 4.2,  0.8, 0]),
            "E": np.array([-3.2, -1.2, 0]),
            "F": np.array([ 0.0, -1.6, 0]),
            "G": np.array([ 3.4, -1.4, 0]),
        }

        # Undirected weighted edges
        edges = [
            ("A", "B", 2),
            ("A", "E", 4),
            ("B", "C", 3),
            ("B", "E", 2),
            ("B", "F", 5),
            ("C", "D", 2),
            ("C", "F", 3),
            ("D", "G", 3),
            ("F", "G", 2),
            ("E", "F", 1),
        ]

        # Visual style
        c_edge = GREY_B
        c_tree = YELLOW
        c_frontier = BLUE_C
        c_bad = RED_C

        # Build nodes
        nodes = {}
        labels = {}
        for name, p in pts.items():
            dot = Dot(p, radius=0.12, color=WHITE)
            dot.set_z_index(5)
            lab = Text(name, font_size=26, weight=BOLD)
            lab.set_color(BLACK)
            lab.move_to(dot.get_center())
            lab.set_z_index(6)
            nodes[name] = dot
            labels[name] = lab

        # Build edges and weight labels
        edge_mobs = {}
        wlabels = {}
        for u, v, w in edges:
            line = Line(pts[u], pts[v])
            line.set_stroke(c_edge, width=4)
            line.set_z_index(1)
            edge_mobs[(u, v)] = line
            edge_mobs[(v, u)] = line

            mid = (pts[u] + pts[v]) / 2
            # Slight normal offset so labels don't sit on the line
            vec = pts[v] - pts[u]
            n = np.array([-vec[1], vec[0], 0.0])
            if np.linalg.norm(n) > 1e-6:
                n = n / np.linalg.norm(n)
            offset = 0.18 * n

            wt = Text(str(w), font_size=22, weight=BOLD)
            wt.set_color(WHITE)
            wt.move_to(mid + offset)
            wt.set_z_index(4)

            bg = RoundedRectangle(width=wt.width + 0.18, height=wt.height + 0.10, corner_radius=0.08)
            bg.set_fill(BLACK, opacity=0.75)
            bg.set_stroke(width=0)
            bg.move_to(wt.get_center())
            bg.set_z_index(3)

            wlabels[(u, v)] = VGroup(bg, wt)
            wlabels[(v, u)] = wlabels[(u, v)]

        graph = VGroup(*{edge_mobs[(u, v)] for (u, v, _) in edges}, *wlabels.values(), *nodes.values(), *labels.values())
        clamp_to_safe(graph)

        # Introduce graph (no extra text)
        self.play(
            LaggedStart(
                *[Create(edge_mobs[(u, v)]) for (u, v, _) in edges],
                lag_ratio=0.04,
            ),
            run_time=1.2,
        )
        self.play(FadeIn(VGroup(*wlabels.values())), run_time=0.5)
        self.play(FadeIn(VGroup(*nodes.values()), scale=1.1), FadeIn(VGroup(*labels.values())), run_time=0.5)
        self.wait(0.25)

        # ---------------------------
        # Prim's algorithm (animated)
        # ---------------------------
        # Determine Prim order (deterministic tie-break)
        start = "A"
        in_tree = set([start])
        parent = {start: None}

        # helper: get weight
        w_lookup = {}
        for u, v, w in edges:
            w_lookup[(u, v)] = w
            w_lookup[(v, u)] = w

        def frontier_edges(in_set):
            out = []
            for u, v, w in edges:
                if (u in in_set) ^ (v in in_set):
                    a = u if u in in_set else v
                    b = v if u in in_set else u
                    out.append((a, b, w))
            # sort by weight, then lexicographic for stability
            out.sort(key=lambda t: (t[2], t[0], t[1]))
            return out

        # Start highlight
        start_ring = Circle(radius=0.22).move_to(nodes[start].get_center())
        start_ring.set_stroke(c_tree, width=6)
        start_ring.set_fill(opacity=0)
        start_ring.set_z_index(10)
        self.play(Create(start_ring), nodes[start].animate.set_color(c_tree), run_time=0.6)
        self.play(FadeOut(start_ring), run_time=0.25)
        self.wait(0.1)

        chosen_edges = []

        # Animation helpers
        def edge_key(u, v):
            return (u, v) if (u, v) in w_lookup else (v, u)

        def emphasize_edge(u, v, color, width=8):
            e = edge_mobs[(u, v)]
            return e.animate.set_stroke(color, width=width)

        def deemphasize_edge(u, v):
            e = edge_mobs[(u, v)]
            return e.animate.set_stroke(c_edge, width=4)

        def node_pulse(name, color, r0=0.18, r1=0.33):
            c = Circle(radius=r0).move_to(nodes[name].get_center())
            c.set_stroke(color, width=6)
            c.set_fill(opacity=0)
            c.set_z_index(9)
            return AnimationGroup(
                FadeIn(c),
                c.animate.scale(r1 / r0).set_opacity(0),
                lag_ratio=0.0,
                run_time=0.45,
            )

        # Grow MST
        while len(in_tree) < len(pts):
            fr = frontier_edges(in_tree)

            # Show the current best option: briefly color the lightest frontier edge
            u, v, w = fr[0]

            # Also briefly hint there are alternatives (a couple edges) without clutter
            alt_anims = []
            for (au, av, aw) in fr[1:3]:
                alt_anims.append(emphasize_edge(au, av, c_frontier, width=6))
            self.play(
                *alt_anims,
                emphasize_edge(u, v, c_tree, width=10),
                run_time=0.5,
            )

            # Commit: bring new node in, keep chosen edge yellow
            in_tree.add(v)
            parent[v] = u
            chosen_edges.append((u, v))

            self.play(
                nodes[v].animate.set_color(c_tree),
                node_pulse(v, c_tree),
                run_time=0.55,
            )

            # Reset alternative edges back to grey
            reset = []
            for (au, av, aw) in fr[1:3]:
                # If an alternative edge became internal after adding v, keep it grey anyway
                reset.append(deemphasize_edge(au, av))
            if reset:
                self.play(*reset, run_time=0.3)

            self.wait(0.1)

        # Dim non-tree edges to reveal the structure
        tree_set = set()
        for u, v in chosen_edges:
            tree_set.add(tuple(sorted((u, v))))

        dim_anims = []
        for (u, v, w) in edges:
            if tuple(sorted((u, v))) not in tree_set:
                dim_anims.append(edge_mobs[(u, v)].animate.set_stroke(GREY_D, width=3, opacity=0.25))
        self.play(*dim_anims, run_time=0.8)
        self.wait(0.25)

        # Compact equation appears late, briefly (single text block)
        mst = VGroup(*[edge_mobs[(u, v)] for (u, v) in chosen_edges], *nodes.values(), *labels.values())
        eq = MathTex(r"\min\ \text{total weight}")
        eq.scale(1.1)
        eq.next_to(mst, DOWN, buff=0.65)
        eq.move_to(np.array([0, eq.get_y(), 0]))
        if abs(eq.get_x()) > 5.0:
            eq.move_to(np.array([0, -2.85, 0]))
        if eq.get_bottom()[1] < -3.2:
            eq.shift(UP * (-3.2 - eq.get_bottom()[1] + 0.05))

        self.play(FadeIn(eq), run_time=0.5)
        self.wait(0.9)
        self.play(FadeOut(eq), run_time=0.4)

        self.wait(0.6)


# You are an expert mathematical animator using the Manim Community Edition (Python).
