from reportlab.pdfgen import canvas

class FooterCanvas(canvas.Canvas):

    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self.pages = []

    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        page_count = len(self.pages)
        for page in self.pages:
            self.__dict__.update(page)
            self.draw_canvas(page_count)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_canvas(self, page_count):
        page =  str(self._pageNumber) + " de " + str(page_count)
        self.saveState()
        self.setStrokeColorRGB(0, 0, 0)
        self.setLineWidth(0.5)
        self.line(30, 38, 550, 38)
        self.setFont('Helvetica', 10)
        self.drawString(500, 25, page)
        self.drawImage("static/topomenunegro.png", 25,760, width=80, height=60, mask='auto')
        self.drawImage("static/teavilogograndecontacto.jpg",425,755, width=131, height=60, mask='auto')
        self.line(30, 750, 550, 750)
        self.restoreState()