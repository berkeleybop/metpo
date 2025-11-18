#!/usr/bin/env python3
"""
Generate OntoGPT feedback loop diagram for ICBO slides
"""
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

mpl.use("Agg")

fig, ax = plt.subplots(1, 1, figsize=(12, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis("off")

# Color scheme
color_input = "#E8F4F8"      # Light blue
color_process = "#FFF4E6"    # Light orange
color_decision = "#FFE6E6"   # Light red
color_output = "#E8F8E8"     # Light green
color_feedback = "#F0E6FF"   # Light purple

# Box style
box_style = "round,pad=0.1"

# 1. Literature Mining (top)
box1 = FancyBboxPatch((0.5, 8), 3, 1,
                       boxstyle=box_style,
                       facecolor=color_input,
                       edgecolor="#2E86AB",
                       linewidth=2)
ax.add_patch(box1)
ax.text(2, 8.5, "1. Literature Mining",
        ha="center", va="center", fontsize=12, fontweight="bold")
ax.text(2, 8.2, '"rod-shaped bacterium"',
        ha="center", va="center", fontsize=10, style="italic")

# Arrow down
arrow1 = FancyArrowPatch((2, 8), (2, 7),
                         arrowstyle="->",
                         mutation_scale=30,
                         linewidth=2,
                         color="#333")
ax.add_patch(arrow1)

# 2. OntoGPT Extraction
box2 = FancyBboxPatch((0.5, 6), 3, 1,
                       boxstyle=box_style,
                       facecolor=color_process,
                       edgecolor="#F18F01",
                       linewidth=2)
ax.add_patch(box2)
ax.text(2, 6.5, "2. OntoGPT Extraction",
        ha="center", va="center", fontsize=12, fontweight="bold")
ax.text(2, 6.2, "Attempts grounding",
        ha="center", va="center", fontsize=10)

# Arrow down
arrow2 = FancyArrowPatch((2, 6), (2, 5),
                         arrowstyle="->",
                         mutation_scale=30,
                         linewidth=2,
                         color="#333")
ax.add_patch(arrow2)

# 3. Decision: Term exists?
box3_x, box3_y = 0.5, 3.5
box3 = mpatches.FancyBboxPatch((box3_x, box3_y), 3, 1.5,
                                boxstyle="round,pad=0.1",
                                facecolor=color_decision,
                                edgecolor="#C1292E",
                                linewidth=2)
ax.add_patch(box3)
ax.text(2, 4.5, "3. Term in METPO?",
        ha="center", va="center", fontsize=12, fontweight="bold")
ax.text(2, 4.1, "Check ontology",
        ha="center", va="center", fontsize=10)

# NO path (left)
arrow_no = FancyArrowPatch((0.5, 4.25), (-1, 4.25),
                           arrowstyle="->",
                           mutation_scale=30,
                           linewidth=2,
                           color="#C1292E")
ax.add_patch(arrow_no)
ax.text(-0.3, 4.6, "NO", fontsize=11, fontweight="bold", color="#C1292E")

# 4. AUTO term generated (left branch)
box4 = FancyBboxPatch((-3.5, 3.5), 2.5, 1.5,
                       boxstyle=box_style,
                       facecolor="#FFE6E6",
                       edgecolor="#C1292E",
                       linewidth=2,
                       linestyle="--")
ax.add_patch(box4)
ax.text(-2.25, 4.5, "AUTO Term",
        ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(-2.25, 4.15, "AUTO:rod_shaped",
        ha="center", va="center", fontsize=9, family="monospace")
ax.text(-2.25, 3.85, "⚠️ Needs curation",
        ha="center", va="center", fontsize=9, style="italic")

# Arrow down to curation
arrow_curation = FancyArrowPatch((-2.25, 3.5), (-2.25, 2.5),
                                 arrowstyle="->",
                                 mutation_scale=30,
                                 linewidth=2,
                                 color="#C1292E")
ax.add_patch(arrow_curation)

# 5. Curation workflow
box5 = FancyBboxPatch((-3.5, 1), 2.5, 1.5,
                       boxstyle=box_style,
                       facecolor=color_feedback,
                       edgecolor="#6A4C93",
                       linewidth=2)
ax.add_patch(box5)
ax.text(-2.25, 2, "Curation Workflow",
        ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(-2.25, 1.65, "👤 Domain expert",
        ha="center", va="center", fontsize=9)
ax.text(-2.25, 1.35, "adds to METPO",
        ha="center", va="center", fontsize=9)

# Feedback arrow back to METPO
arrow_feedback = FancyArrowPatch((-1, 1.75), (2, 1.75),
                                 arrowstyle="->",
                                 mutation_scale=30,
                                 linewidth=3,
                                 color="#6A4C93",
                                 linestyle="-",
                                 connectionstyle="arc3,rad=.3")
ax.add_patch(arrow_feedback)
ax.text(0.5, 2.2, "Ontology updated",
        fontsize=9, style="italic", color="#6A4C93")

# YES path (right)
arrow_yes = FancyArrowPatch((3.5, 4.25), (6, 4.25),
                            arrowstyle="->",
                            mutation_scale=30,
                            linewidth=2,
                            color="#2E7D32")
ax.add_patch(arrow_yes)
ax.text(4.8, 4.6, "YES", fontsize=11, fontweight="bold", color="#2E7D32")

# 6. Successful grounding (right branch)
box6 = FancyBboxPatch((6, 3.5), 3, 1.5,
                       boxstyle=box_style,
                       facecolor=color_output,
                       edgecolor="#2E7D32",
                       linewidth=2)
ax.add_patch(box6)
ax.text(7.5, 4.5, "Grounded Term",
        ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(7.5, 4.1, "METPO:1000681",
        ha="center", va="center", fontsize=9, family="monospace")
ax.text(7.5, 3.8, '✓ "rod shaped"',
        ha="center", va="center", fontsize=9, style="italic")

# Arrow to KG
arrow_kg = FancyArrowPatch((7.5, 3.5), (7.5, 2.5),
                           arrowstyle="->",
                           mutation_scale=30,
                           linewidth=2,
                           color="#2E7D32")
ax.add_patch(arrow_kg)

# 7. Knowledge Graph
box7 = FancyBboxPatch((6, 1), 3, 1.5,
                       boxstyle=box_style,
                       facecolor="#E3F2FD",
                       edgecolor="#1976D2",
                       linewidth=2)
ax.add_patch(box7)
ax.text(7.5, 2, "Knowledge Graph",
        ha="center", va="center", fontsize=11, fontweight="bold")
ax.text(7.5, 1.65, "Semantic integration",
        ha="center", va="center", fontsize=9)
ax.text(7.5, 1.35, "with KG-Microbe",
        ha="center", va="center", fontsize=9)

# METPO ontology (center bottom) - the target of feedback
box_metpo = FancyBboxPatch((0.5, 0.5), 3, 1,
                           boxstyle=box_style,
                           facecolor="#FFF9C4",
                           edgecolor="#F57C00",
                           linewidth=3)
ax.add_patch(box_metpo)
ax.text(2, 1, "METPO Ontology",
        ha="center", va="center", fontsize=12, fontweight="bold")

# Arrow from METPO to OntoGPT (lookup during extraction)
arrow_lookup = FancyArrowPatch((3.5, 1), (5.5, 4.25),
                               arrowstyle="<-",
                               mutation_scale=30,
                               linewidth=2,
                               color="#666",
                               linestyle=":",
                               connectionstyle="arc3,rad=-.2")
ax.add_patch(arrow_lookup)
ax.text(4.3, 2.5, "Lookup", fontsize=8, style="italic", color="#666", rotation=50)

# Title
ax.text(5, 9.5, "OntoGPT ↔ METPO Feedback Loop",
        ha="center", va="center", fontsize=16, fontweight="bold")
ax.text(5, 9.1, "Data-driven ontology development through iterative refinement",
        ha="center", va="center", fontsize=11, style="italic", color="#555")

plt.tight_layout()
plt.savefig("/home/mark/gitrepos/metpo/ontogpt_icbo_demo/figures/ontogpt_feedback_loop.png",
            dpi=300, bbox_inches="tight", facecolor="white")
print("Generated: ontogpt_feedback_loop.png")
