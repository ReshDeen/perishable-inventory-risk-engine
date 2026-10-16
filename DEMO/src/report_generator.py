"""
P.I.R.E. Audit Report Generation Module
Generates professional executive PDF reports via ReportLab and CSV audit streams.
Includes dataset summaries, food safety alerts, financial valuations, and model metrics.
"""

from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import REPORTS_DIR


class NumberedCanvas(canvas.Canvas):
    """Custom canvas that tracks total pages and prints running header/footer."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages: int):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(54, letter[1] - 36, "P.I.R.E. — Perishable Inventory Risk Evaluation System")
            self.drawRightString(letter[0] - 54, letter[1] - 36, "CONFIDENTIAL & PROPRIETARY AUDIT REPORT")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, letter[1] - 42, letter[0] - 54, letter[1] - 42)

        # Running footer
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 36, page_str)
        self.drawString(54, 36, "P.I.R.E. Inventory Decision Engine • Built with XGBoost & Streamlit")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 46, letter[0] - 54, 46)

        self.restoreState()


class ReportGenerator:
    """Produces publication-grade audit PDF reports and standardized CSV exports."""

    @classmethod
    def generate_pdf_report(
        cls,
        df: pd.DataFrame,
        financial_summary: Dict[str, Any],
        model_metrics: Optional[Dict[str, Any]] = None,
        dataset_origin: str = "Synthetic Demonstration Dataset",
        output_path: Optional[Path] = None
    ) -> bytes:
        """
        Builds a comprehensive PDF audit report.
        Returns PDF bytes and optionally writes to output_path.
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            leftMargin=54,
            rightMargin=54,
            topMargin=54,
            bottomMargin=54
        )

        styles = getSampleStyleSheet()

        # Custom Typography Styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0F172A"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#475569"),
            spaceAfter=12
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1E3A8A"),
            spaceBefore=14,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#1E293B")
        )
        alert_style = ParagraphStyle(
            "AlertText",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#991B1B")
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=body_style,
            fontName="Helvetica-Bold"
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("P.I.R.E. INVENTORY RISK & CLEARANCE AUDIT REPORT", title_style))
        gen_time = datetime.now().strftime("%B %d, %Y • %I:%M %p")
        story.append(Paragraph(f"Generated: {gen_time} | Data Origin: <b>{dataset_origin}</b>", subtitle_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=12))

        # 2. Executive Financial & Risk Summary
        story.append(Paragraph("1. Executive Portfolio Risk Summary", h2_style))

        total_prods = len(df)
        expired_count = int((df.get("final_risk") == "EXPIRED").sum()) if "final_risk" in df.columns else 0
        critical_count = int((df.get("final_risk") == "CRITICAL").sum()) if "final_risk" in df.columns else 0
        high_count = int((df.get("final_risk") == "HIGH").sum()) if "final_risk" in df.columns else 0
        med_count = int((df.get("final_risk") == "MEDIUM").sum()) if "final_risk" in df.columns else 0
        low_count = int((df.get("final_risk") == "LOW").sum()) if "final_risk" in df.columns else 0

        summary_data = [
            [
                Paragraph("<b>Total SKU Records Audited:</b>", body_style),
                Paragraph(str(total_prods), body_style),
                Paragraph("<b>Total Stock Value:</b>", body_style),
                Paragraph(f"₹{financial_summary.get('total_inventory_cost', 0):,.2f}", body_style)
            ],
            [
                Paragraph("<b>Expired Products (0% Sale):</b>", body_style),
                Paragraph(f"<font color='#DC2626'><b>{expired_count}</b></font>", body_style),
                Paragraph("<b>Inventory Value at Risk:</b>", body_style),
                Paragraph(f"<font color='#B45309'><b>₹{financial_summary.get('total_value_at_risk', 0):,.2f}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Critical & High Urgency:</b>", body_style),
                Paragraph(f"{critical_count + high_count}", body_style),
                Paragraph("<b>Est. Recoverable Value:</b>", body_style),
                Paragraph(f"<font color='#047857'><b>₹{financial_summary.get('total_potential_recovery', 0):,.2f}</b></font>", body_style)
            ],
            [
                Paragraph("<b>Medium & Low Risk:</b>", body_style),
                Paragraph(f"{med_count + low_count}", body_style),
                Paragraph("<b>Expired Write-Off Loss:</b>", body_style),
                Paragraph(f"<font color='#DC2626'><b>₹{financial_summary.get('expired_writeoff_loss', 0):,.2f}</b></font>", body_style)
            ]
        ]

        summary_table = Table(summary_data, colWidths=[150, 90, 150, 114])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 10))

        # 3. Mandatory Food Safety Warning Banner
        if expired_count > 0:
            alert_box = [
                [
                    Paragraph(
                        f"⚠️ <b>MANDATORY FOOD SAFETY DIRECTIVE:</b> {expired_count} product(s) have exceeded their expiry date. "
                        "Retail food-safety regulations strictly forbid selling, remarketing, or discounting expired perishable items. "
                        "These products must be quarantined immediately and removed for safe disposal.",
                        alert_style
                    )
                ]
            ]
            alert_table = Table(alert_box, colWidths=[504])
            alert_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FEF2F2")),
                ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#DC2626")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]))
            story.append(alert_table)
            story.append(Spacer(1, 10))

        # 4. Model Training and Evaluation Metrics
        if model_metrics and "metrics" in model_metrics:
            story.append(Paragraph("2. Machine Learning (XGBoost) Model Validation", h2_style))
            m = model_metrics.get("metrics", {})
            ml_data = [
                [
                    Paragraph("<b>Classifier Architecture:</b>", body_style),
                    Paragraph("XGBoost Multi-Class Gradient Boosting", body_style),
                    Paragraph("<b>Accuracy Score:</b>", body_style),
                    Paragraph(f"{m.get('accuracy', 0)*100:.1f}%", body_style)
                ],
                [
                    Paragraph("<b>Weighted Precision:</b>", body_style),
                    Paragraph(f"{m.get('precision', 0)*100:.1f}%", body_style),
                    Paragraph("<b>Weighted Recall:</b>", body_style),
                    Paragraph(f"{m.get('recall', 0)*100:.1f}%", body_style)
                ],
                [
                    Paragraph("<b>Weighted F1-Score:</b>", body_style),
                    Paragraph(f"{m.get('f1_score', 0)*100:.1f}%", body_style),
                    Paragraph("<b>Training Samples:</b>", body_style),
                    Paragraph(f"{model_metrics.get('train_samples', 0)} train / {model_metrics.get('test_samples', 0)} test", body_style)
                ]
            ]
            ml_table = Table(ml_data, colWidths=[140, 110, 130, 124])
            ml_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EFF6FF")),
                ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#93C5FD")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BFDBFE")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(ml_table)
            story.append(Spacer(1, 10))

        # 5. Top Priority Action Items Table (Expired, Critical, and High Risk)
        story.append(Paragraph("3. Priority Action Inventory Schedule", h2_style))
        story.append(Paragraph("Key inventory records requiring immediate store manager attention:", body_style))
        story.append(Spacer(1, 4))

        # Filter top urgent items (up to 20 items for readability)
        priority_mask = df["final_risk"].isin(["EXPIRED", "CRITICAL", "HIGH"]) if "final_risk" in df.columns else pd.Series(True, index=df.index)
        priority_df = df[priority_mask].head(25) if not df.empty else df

        if priority_df.empty:
            story.append(Paragraph("<i>No critical or expired items detected. Inventory health is optimal.</i>", body_style))
        else:
            table_headers = ["Product ID / Name", "Category", "Days Left", "Risk Tier", "Price", "Action / Rec."]
            rows_data = [[Paragraph(f"<b>{h}</b>", cell_bold) for h in table_headers]]

            for _, r in priority_df.iterrows():
                p_name = f"{r.get('prod_id', '')} - {r.get('prod_name', '')[:20]}"
                cat = str(r.get("category", "N/A"))
                days = str(r.get("days_remaining", "N/A"))
                risk = str(r.get("final_risk", "N/A"))
                price = f"₹{float(r.get('prod_price', 0)):.1f}"

                # Highlight risk text color
                if risk == "EXPIRED":
                    risk_txt = f"<font color='#DC2626'><b>{risk}</b></font>"
                elif risk == "CRITICAL":
                    risk_txt = f"<font color='#EA580C'><b>{risk}</b></font>"
                else:
                    risk_txt = f"<font color='#B45309'><b>{risk}</b></font>"

                disc_pct = r.get("recommended_discount_pct", 0)
                if risk == "EXPIRED":
                    act = "<font color='#DC2626'>Remove from Sale</font>"
                elif disc_pct > 0:
                    act = f"Discount {disc_pct}% (₹{float(r.get('recommended_selling_price', 0)):.1f})"
                else:
                    act = "Monitor"

                rows_data.append([
                    Paragraph(p_name, body_style),
                    Paragraph(cat, body_style),
                    Paragraph(days, body_style),
                    Paragraph(risk_txt, body_style),
                    Paragraph(price, body_style),
                    Paragraph(act, body_style)
                ])

            p_table = Table(rows_data, colWidths=[140, 80, 50, 60, 50, 124])
            p_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            story.append(p_table)

        # 6. Operational Methodology & Disclaimer Note
        story.append(Spacer(1, 14))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94A3B8"), spaceAfter=8))
        disclaimer_text = (
            "<b>Audit Compliance Note:</b> This report is generated by the P.I.R.E. Decision Support System. "
            "Model predictions are generated via an XGBoost multi-class classifier using temporal and cold-chain features. "
            "Estimated recoverable values represent potential revenue assuming 100% clearance of discount-eligible quantities "
            "and do not constitute guaranteed revenue. Perishable items past their stated expiration date are automatically "
            "condemned in strict alignment with retail food safety standards."
        )
        story.append(Paragraph(disclaimer_text, body_style))

        # Build document with custom canvas
        doc.build(story, canvasmaker=NumberedCanvas)

        pdf_bytes = buffer.getvalue()
        buffer.close()

        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "wb") as f:
                f.write(pdf_bytes)

        return pdf_bytes

    @classmethod
    def generate_csv_bytes(cls, df: pd.DataFrame) -> bytes:
        """Converts DataFrame to UTF-8 encoded CSV byte stream."""
        return df.to_csv(index=False).encode("utf-8")
