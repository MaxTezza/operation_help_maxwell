"""
PDF generation utility for design presentations
"""
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class TezzaWorksPDFGenerator:
    """Generate professional PDF presentations for design options"""

    def __init__(self, output_dir='static/pdfs'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Body style
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))

    def _create_header_footer(self, canvas_obj, doc):
        """Add header and footer to each page"""
        canvas_obj.saveState()

        # Header
        canvas_obj.setFont('Helvetica-Bold', 16)
        canvas_obj.setFillColor(colors.HexColor('#2C3E50'))
        canvas_obj.drawString(inch, letter[1] - 0.5 * inch, "TezzaWorks")
        canvas_obj.setFont('Helvetica', 10)
        canvas_obj.drawString(inch, letter[1] - 0.7 * inch, "Custom Design Presentation")

        # Footer
        canvas_obj.setFont('Helvetica', 9)
        canvas_obj.setFillColor(colors.HexColor('#7F8C8D'))
        canvas_obj.drawString(inch, 0.5 * inch, f"Generated on {datetime.now().strftime('%B %d, %Y')}")
        canvas_obj.drawRightString(letter[0] - inch, 0.5 * inch, f"Page {doc.page}")

        canvas_obj.restoreState()

    def generate_presentation(self, request, designs, output_filename=None):
        """
        Generate a professional PDF presentation

        Args:
            request: DesignRequest model instance
            designs: List of Design model instances
            output_filename: Optional custom filename

        Returns:
            Path to generated PDF file
        """
        if output_filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_filename = f"presentation_{request.company_name}_{timestamp}.pdf"

        output_path = os.path.join(self.output_dir, output_filename)

        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )

        # Container for PDF elements
        story = []

        # Cover Page
        story.append(Spacer(1, 2 * inch))
        story.append(Paragraph("Custom Design Presentation", self.styles['CustomTitle']))
        story.append(Spacer(1, 0.3 * inch))
        story.append(Paragraph(f"Prepared for: {request.company_name}", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2 * inch))
        story.append(Paragraph("TezzaWorks Design Team", self.styles['CustomBody']))
        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph(datetime.now().strftime('%B %d, %Y'), self.styles['CustomBody']))

        story.append(PageBreak())

        # Brand Overview Page
        story.append(Paragraph("Your Brand Profile", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2 * inch))

        # Brand Keywords
        story.append(Paragraph("<b>Brand Keywords:</b>", self.styles['CustomBody']))
        story.append(Paragraph(request.brand_keywords, self.styles['CustomBody']))
        story.append(Spacer(1, 0.2 * inch))

        # Brand Colors (if provided)
        if request.brand_colors:
            story.append(Paragraph("<b>Brand Colors:</b>", self.styles['CustomBody']))
            story.append(Paragraph(request.brand_colors, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2 * inch))

        # Target Audience (if provided)
        if request.target_audience:
            story.append(Paragraph("<b>Target Audience:</b>", self.styles['CustomBody']))
            story.append(Paragraph(request.target_audience, self.styles['CustomBody']))
            story.append(Spacer(1, 0.2 * inch))

        story.append(PageBreak())

        # Design Options
        story.append(Paragraph("Design Options", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.3 * inch))

        for idx, design in enumerate(designs, 1):
            # Design title
            title = design.title or f"Design Option {idx}"
            story.append(Paragraph(f"<b>{title}</b>", self.styles['CustomSubtitle']))
            story.append(Spacer(1, 0.2 * inch))

            # Design image
            try:
                img_path = os.path.join('static/uploads', design.filename)
                if os.path.exists(img_path):
                    img = Image(img_path, width=5 * inch, height=5 * inch, kind='proportional')
                    story.append(img)
                    story.append(Spacer(1, 0.2 * inch))
            except Exception as e:
                print(f"Error loading image {design.filename}: {e}")

            # Design description
            if design.description:
                story.append(Paragraph(design.description, self.styles['CustomBody']))

            story.append(Spacer(1, 0.3 * inch))

            # Page break between designs (except last one)
            if idx < len(designs):
                story.append(PageBreak())

        # Next Steps Page
        story.append(PageBreak())
        story.append(Paragraph("Next Steps", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.2 * inch))

        next_steps_text = """
        <b>1. Review Designs</b><br/>
        Take your time to review each design option. Consider how they align with your brand values and target audience.<br/><br/>

        <b>2. Provide Feedback</b><br/>
        Use the online gallery to select your favorite designs and provide any feedback or suggestions.<br/><br/>

        <b>3. Refinement</b><br/>
        Based on your selections, we'll refine the chosen design(s) and prepare final production files.<br/><br/>

        <b>4. Production</b><br/>
        Once approved, we'll move forward with production of your custom corporate gifts.<br/><br/>

        <b>Questions?</b><br/>
        Contact us at: info@tezzaworks.com<br/>
        Phone: (555) 123-4567
        """

        story.append(Paragraph(next_steps_text, self.styles['CustomBody']))

        # Build PDF
        doc.build(story, onFirstPage=self._create_header_footer, onLaterPages=self._create_header_footer)

        return output_path


def generate_design_pdf(request, designs):
    """
    Convenience function to generate a PDF presentation

    Args:
        request: DesignRequest model instance
        designs: List of Design model instances

    Returns:
        Path to generated PDF file
    """
    generator = TezzaWorksPDFGenerator()
    return generator.generate_presentation(request, designs)
