
from reportlab.pdfgen import canvas

def test():
    c = canvas.Canvas("test.pdf")
    c.drawString(500,500,'yes')
    c.showPage()
    c.save()

test()