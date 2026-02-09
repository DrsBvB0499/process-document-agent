"""
Process Flow Diagram Generator
================================
Generates professional AS-IS process flow diagrams with swimlanes,
decision points, and exception paths using Pillow.

Part of the Process Analysis Agent toolkit.
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


class FlowchartGenerator:
    """
    Generates process flow diagrams from structured process data.
    
    The generator creates swimlane-based flowcharts with:
    - Process steps (rounded rectangles)
    - Decision points (diamonds)
    - Exception paths (red)
    - Start/End terminals (pill shapes)
    - Loop-back arrows
    - Legend with pain points
    """

    # ── Default Colors ──
    COLORS = {
        "start":     "#2980B9",
        "process":   "#2C3E50",
        "decision":  "#E67E22",
        "exception": "#C0392B",
        "end":       "#27AE60",
        "arrow":     "#5D6D7E",
        "text_w":    "#FFFFFF",
        "text_d":    "#2C3E50",
        "bg_swim":   "#F0F4F8",
        "bg_swim2":  "#E8EDF2",
        "border":    "#BDC3C7",
        "label_bg":  "#F9E79F",
        "title_bg":  "#1B4F72",
    }

    def __init__(self, width=2400, height=3200):
        self.W = width
        self.H = height
        self.img = None
        self.draw = None
        self._load_fonts()

    def _load_fonts(self):
        """Load fonts with fallback to defaults."""
        font_paths = {
            "bold": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "normal": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        }
        try:
            self.font_title = ImageFont.truetype(font_paths["bold"], 32)
            self.font_subtitle = ImageFont.truetype(font_paths["normal"], 18)
            self.font_bold = ImageFont.truetype(font_paths["bold"], 16)
            self.font_normal = ImageFont.truetype(font_paths["normal"], 15)
            self.font_small = ImageFont.truetype(font_paths["normal"], 13)
            self.font_label = ImageFont.truetype(font_paths["bold"], 13)
            self.font_legend = ImageFont.truetype(font_paths["normal"], 14)
        except OSError:
            default = ImageFont.load_default()
            self.font_title = default
            self.font_subtitle = default
            self.font_bold = default
            self.font_normal = default
            self.font_small = default
            self.font_label = default
            self.font_legend = default

    # ──────────────────────────────────────────────
    # Drawing primitives
    # ──────────────────────────────────────────────

    def _rounded_rect(self, x, y, w, h, r, fill, outline=None):
        self.draw.rounded_rectangle(
            [x, y, x + w, y + h], radius=r,
            fill=fill, outline=outline or fill, width=2
        )

    def _draw_box(self, cx, cy, w, h, text, fill, text_color="#FFFFFF", lines=None):
        """Draw a process step box centered at (cx, cy)."""
        x, y = cx - w // 2, cy - h // 2
        self._rounded_rect(x, y, w, h, 10, fill, outline="#1A1A2E")
        if lines:
            total_h = len(lines) * 20
            start_y = cy - total_h // 2
            for i, line in enumerate(lines):
                bbox = self.draw.textbbox((0, 0), line, font=self.font_normal)
                tw = bbox[2] - bbox[0]
                self.draw.text((cx - tw // 2, start_y + i * 20), line,
                               fill=text_color, font=self.font_normal)
        else:
            bbox = self.draw.textbbox((0, 0), text, font=self.font_normal)
            tw = bbox[2] - bbox[0]
            self.draw.text((cx - tw // 2, cy - 8), text,
                           fill=text_color, font=self.font_normal)

    def _draw_diamond(self, cx, cy, w, h, text, fill):
        """Draw a decision diamond centered at (cx, cy)."""
        points = [(cx, cy - h // 2), (cx + w // 2, cy),
                  (cx, cy + h // 2), (cx - w // 2, cy)]
        self.draw.polygon(points, fill=fill, outline="#1A1A2E", width=2)
        words = text.split()
        if len(words) > 3:
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            for i, line in enumerate([line1, line2]):
                bbox = self.draw.textbbox((0, 0), line, font=self.font_small)
                tw = bbox[2] - bbox[0]
                self.draw.text((cx - tw // 2, cy - 14 + i * 18), line,
                               fill="#FFFFFF", font=self.font_small)
        else:
            bbox = self.draw.textbbox((0, 0), text, font=self.font_small)
            tw = bbox[2] - bbox[0]
            self.draw.text((cx - tw // 2, cy - 7), text,
                           fill="#FFFFFF", font=self.font_small)

    def _draw_terminal(self, cx, cy, w, h, text, fill):
        """Draw a start/end terminal (pill shape)."""
        x, y = cx - w // 2, cy - h // 2
        self.draw.rounded_rectangle([x, y, x + w, y + h], radius=h // 2,
                                     fill=fill, outline="#1A1A2E", width=2)
        bbox = self.draw.textbbox((0, 0), text, font=self.font_bold)
        tw = bbox[2] - bbox[0]
        self.draw.text((cx - tw // 2, cy - 9), text,
                       fill="#FFFFFF", font=self.font_bold)

    def _arrowhead(self, x, y, angle, size=10):
        """Draw an arrowhead at (x, y) pointing in direction angle."""
        self.draw.polygon([
            (x, y),
            (x - size * math.cos(angle - 0.4), y - size * math.sin(angle - 0.4)),
            (x - size * math.cos(angle + 0.4), y - size * math.sin(angle + 0.4)),
        ], fill=self.COLORS["arrow"])

    def _arrow(self, x1, y1, x2, y2, label=None, label_side="right"):
        """Draw a straight arrow with optional label."""
        self.draw.line([(x1, y1), (x2, y2)], fill=self.COLORS["arrow"], width=2)
        angle = math.atan2(y2 - y1, x2 - x1)
        self._arrowhead(x2, y2, angle)
        if label:
            self._draw_label(label, x1, y1, x2, y2, label_side)

    def _draw_label(self, label, x1, y1, x2, y2, side):
        """Draw a label near the midpoint of a line."""
        lx, ly = (x1 + x2) // 2, (y1 + y2) // 2
        bbox = self.draw.textbbox((0, 0), label, font=self.font_label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if side == "right":
            self.draw.rounded_rectangle(
                [lx + 6, ly - th // 2 - 3, lx + tw + 14, ly + th // 2 + 3],
                radius=4, fill=self.COLORS["label_bg"])
            self.draw.text((lx + 10, ly - th // 2 - 1), label,
                           fill=self.COLORS["text_d"], font=self.font_label)
        elif side == "left":
            self.draw.rounded_rectangle(
                [lx - tw - 14, ly - th // 2 - 3, lx - 6, ly + th // 2 + 3],
                radius=4, fill=self.COLORS["label_bg"])
            self.draw.text((lx - tw - 10, ly - th // 2 - 1), label,
                           fill=self.COLORS["text_d"], font=self.font_label)
        elif side == "above":
            self.draw.rounded_rectangle(
                [lx - tw // 2 - 4, ly - th - 8, lx + tw // 2 + 4, ly - 4],
                radius=4, fill=self.COLORS["label_bg"])
            self.draw.text((lx - tw // 2, ly - th - 6), label,
                           fill=self.COLORS["text_d"], font=self.font_label)

    def _arrow_right_then_down(self, x1, y1, x2, y2, label=None):
        """Draw an L-shaped arrow: right then down."""
        self.draw.line([(x1, y1), (x2, y1)], fill=self.COLORS["arrow"], width=2)
        self.draw.line([(x2, y1), (x2, y2)], fill=self.COLORS["arrow"], width=2)
        self._arrowhead(x2, y2, math.pi / 2)
        if label:
            bbox = self.draw.textbbox((0, 0), label, font=self.font_label)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            mx = (x1 + x2) // 2
            self.draw.rounded_rectangle(
                [mx - tw // 2 - 4, y1 - th - 8, mx + tw // 2 + 4, y1 - 4],
                radius=4, fill=self.COLORS["label_bg"])
            self.draw.text((mx - tw // 2, y1 - th - 6), label,
                           fill=self.COLORS["text_d"], font=self.font_label)

    # ──────────────────────────────────────────────
    # High-level diagram generation
    # ──────────────────────────────────────────────

    def generate(self, process_data: dict, output_path: str) -> str:
        """
        Generate a process flow diagram from structured process data.

        Args:
            process_data: Dictionary containing:
                - title: Process name
                - subtitle: Additional context line
                - swimlanes: List of swimlane names (left to right)
                - steps: List of step dicts with keys:
                    - type: "start", "process", "decision", "exception", "end"
                    - text: Display text (or list of lines)
                    - lane: Which swimlane (0-indexed)
                    - connections: List of connection dicts
                - pain_points: List of pain point strings for legend
            output_path: Where to save the PNG

        Returns:
            The output file path
        """
        self.img = Image.new("RGB", (self.W, self.H), "#FFFFFF")
        self.draw = ImageDraw.Draw(self.img)

        self._draw_title(process_data.get("title", "Process Flow"),
                         process_data.get("subtitle", ""))
        self._draw_swimlanes(process_data.get("swimlanes", ["System", "Employee"]))
        self._draw_steps(process_data)
        self._draw_legend(process_data.get("pain_points", []))

        self.img.save(output_path, "PNG", quality=95)
        return output_path

    def generate_generic(self, output_path: str, process_name: str) -> str:
        """
        Generate a generic process flow diagram for any process.
        This creates a simple visual representation when detailed
        layout data is not available.
        
        Args:
            output_path: Where to save the PNG
            process_name: Name of the process for the title
            
        Returns:
            The output file path
        """
        self.img = Image.new("RGB", (self.W, self.H), "#FFFFFF")
        self.draw = ImageDraw.Draw(self.img)
        C = self.COLORS

        # ── Title ──
        self.draw.rectangle([0, 0, self.W, 90], fill=C["title_bg"])
        title = f"AS-IS PROCESS FLOW: {process_name.upper()}"
        bbox = self.draw.textbbox((0, 0), title, font=self.font_title)
        self.draw.text((self.W // 2 - (bbox[2] - bbox[0]) // 2, 16), title,
                       fill="#FFFFFF", font=self.font_title)
        sub = "Process Analysis  |  Standardization Checkpoint"
        bbox = self.draw.textbbox((0, 0), sub, font=self.font_subtitle)
        self.draw.text((self.W // 2 - (bbox[2] - bbox[0]) // 2, 56), sub,
                       fill="#AED6F1", font=self.font_subtitle)

        # ── Swimlanes ──
        LANE_TOP = 110
        LANE_H = 2800
        
        # Two standard swimlanes
        self.draw.rectangle([40, LANE_TOP, 1200, LANE_TOP + LANE_H],
                            fill=C["bg_swim"], outline=C["border"], width=1)
        self.draw.rectangle([1200, LANE_TOP, self.W - 40, LANE_TOP + LANE_H],
                            fill=C["bg_swim2"], outline=C["border"], width=1)

        self.draw.rectangle([40, LANE_TOP, 1200, LANE_TOP + 50], fill="#2C3E50")
        self.draw.text((520, LANE_TOP + 14), "SYSTEM / AUTOMATION", 
                       fill="#FFFFFF", font=self.font_bold)
        self.draw.rectangle([1200, LANE_TOP, self.W - 40, LANE_TOP + 50], fill="#2C3E50")
        self.draw.text((1600, LANE_TOP + 14), "TEAM / MANUAL WORK",
                       fill="#FFFFFF", font=self.font_bold)

        # ── Generic Process Flow ──
        SYS_X = 620
        EMP_X = 1700
        BOX_W = 400
        BOX_H = 60
        Y_START = 240
        Y_GAP = 160
        
        y = [Y_START + i * Y_GAP for i in range(15)]

        # START
        self._draw_terminal(SYS_X, y[0], 350, 50, "Process Trigger", C["start"])

        # Input received
        self._draw_box(SYS_X, y[1], BOX_W, BOX_H, "", C["process"],
                       lines=["Input received", "from suppliers"])
        self._arrow(SYS_X, y[0] + 25, SYS_X, y[1] - BOX_H // 2)

        # Initial validation
        self._draw_box(EMP_X, y[2], BOX_W, BOX_H, "", C["process"],
                       lines=["Initial review", "and validation"])
        self._arrow(SYS_X, y[1] + BOX_H // 2, SYS_X, y[1] + BOX_H // 2 + 30)
        self._arrow_right_then_down(SYS_X, y[1] + BOX_H // 2 + 30,
                                     EMP_X, y[2] - BOX_H // 2)

        # Process work
        self._draw_box(EMP_X, y[3], BOX_W, BOX_H, "", C["process"],
                       lines=["Core process", "activities"])
        self._arrow(EMP_X, y[2] + BOX_H // 2, EMP_X, y[3] - BOX_H // 2)

        # Decision point
        DIA_W = 300
        DIA_H = 90
        self._draw_diamond(EMP_X, y[4] + 10, DIA_W, DIA_H, 
                          "Validation check", C["decision"])
        self._arrow(EMP_X, y[3] + BOX_H // 2, EMP_X, y[4] + 10 - DIA_H // 2)

        # Success path
        self._draw_box(EMP_X, y[5], BOX_W, BOX_H, "", C["process"],
                       lines=["Finalize and", "prepare output"])
        self._arrow(EMP_X, y[4] + 10 + DIA_H // 2, EMP_X, y[5] - BOX_H // 2,
                    label="Pass", label_side="left")

        # Exception path
        EXCEPT_X = EMP_X + 500
        self._draw_box(EXCEPT_X, y[4] + 10, 320, BOX_H, "", C["exception"],
                       lines=["Exception handling", "or rework"])
        self._arrow(EMP_X + DIA_W // 2, y[4] + 10, EXCEPT_X - 160, y[4] + 10,
                    label="Fail")
        
        # Loop back from exception
        self._arrow(EXCEPT_X, y[4] + 10 + BOX_H // 2, EXCEPT_X, y[5] + 30)
        self.draw.line([(EXCEPT_X, y[5] + 30), (EMP_X, y[5] + 30)],
                       fill=C["arrow"], width=2)

        # System output
        self._draw_box(SYS_X, y[6], BOX_W, BOX_H, "", C["process"],
                       lines=["System generates", "final output"])
        self._arrow(EMP_X, y[5] + BOX_H // 2, EMP_X, y[5] + BOX_H // 2 + 30)
        self.draw.line([(EMP_X, y[5] + BOX_H // 2 + 30), 
                       (SYS_X, y[5] + BOX_H // 2 + 30)],
                       fill=C["arrow"], width=2)
        self._arrow(SYS_X, y[5] + BOX_H // 2 + 30, SYS_X, y[6] - BOX_H // 2)

        # Delivery
        self._draw_box(SYS_X, y[7], BOX_W, BOX_H, "", C["process"],
                       lines=["Output delivered", "to customers"])
        self._arrow(SYS_X, y[6] + BOX_H // 2, SYS_X, y[7] - BOX_H // 2)

        # END
        self._draw_terminal(SYS_X, y[8] + 10, 360, 50,
                            "Process Complete", C["end"])
        self._arrow(SYS_X, y[7] + BOX_H // 2, SYS_X, y[8] + 10 - 25)

        # ── Legend ──
        pain_points = [
            "See documentation for details",
            "Process analysis complete",
        ]
        self._draw_legend_generic(pain_points)

        self.img.save(output_path, "PNG", quality=95)
        return output_path

    def _draw_title(self, title, subtitle):
        self.draw.rectangle([0, 0, self.W, 90], fill=self.COLORS["title_bg"])
        bbox = self.draw.textbbox((0, 0), title, font=self.font_title)
        self.draw.text((self.W // 2 - (bbox[2] - bbox[0]) // 2, 16), title,
                       fill="#FFFFFF", font=self.font_title)
        if subtitle:
            bbox = self.draw.textbbox((0, 0), subtitle, font=self.font_subtitle)
            self.draw.text((self.W // 2 - (bbox[2] - bbox[0]) // 2, 56), subtitle,
                           fill="#AED6F1", font=self.font_subtitle)

    def _draw_swimlanes(self, lanes):
        LANE_TOP = 110
        LANE_H = 3020
        lane_w = (self.W - 80) // len(lanes)
        colors = [self.COLORS["bg_swim"], self.COLORS["bg_swim2"]]
        for i, lane in enumerate(lanes):
            x1 = 40 + i * lane_w
            x2 = x1 + lane_w
            self.draw.rectangle([x1, LANE_TOP, x2, LANE_TOP + LANE_H],
                                fill=colors[i % 2], outline=self.COLORS["border"], width=1)
            self.draw.rectangle([x1, LANE_TOP, x2, LANE_TOP + 50], fill="#2C3E50")
            bbox = self.draw.textbbox((0, 0), lane.upper(), font=self.font_bold)
            tw = bbox[2] - bbox[0]
            self.draw.text(((x1 + x2) // 2 - tw // 2, LANE_TOP + 14), lane.upper(),
                           fill="#FFFFFF", font=self.font_bold)

    def _draw_steps(self, process_data):
        """Override this for custom process layouts."""
        pass

    def _draw_legend(self, pain_points):
        self._draw_legend_generic(pain_points)

    def _draw_legend_generic(self, pain_points):
        C = self.COLORS
        LX = 60
        LY = self.H - 130
        self.draw.rectangle([LX, LY, self.W - 40, self.H - 20],
                            fill="#FFFFFF", outline=C["border"], width=1)
        self.draw.text((LX + 20, LY + 10), "LEGEND", fill=C["text_d"], font=self.font_bold)

        items = [
            (C["start"], "Start / System trigger"),
            (C["process"], "Process step"),
            (C["decision"], "Decision point"),
            (C["exception"], "Exception path"),
            (C["end"], "End"),
        ]
        for i, (color, label) in enumerate(items):
            bx = LX + 20 + i * 440
            by = LY + 45
            self._rounded_rect(bx, by, 30, 22, 5, color)
            self.draw.text((bx + 40, by + 2), label, fill=C["text_d"], font=self.font_legend)

        self.draw.text((LX + 20, LY + 80), "Pain points:",
                       fill=C["text_d"], font=self.font_bold)
        for i, p in enumerate(pain_points):
            self.draw.text((LX + 140 + i * 480, LY + 80), f"⚠ {p}",
                           fill=C["exception"], font=self.font_legend)


if __name__ == "__main__":
    print("FlowchartGenerator class ready for use.")
    print("Use session_to_document.py to generate diagrams from session files.")
