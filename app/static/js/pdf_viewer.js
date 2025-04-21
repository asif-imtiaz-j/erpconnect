// === PDF Viewer Integration (PDF.js) ===

const pdfjsLib = window['pdfjs-dist/build/pdf'];
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

function embedCanvasFromPDF(pdfUrl, containerId = 'pdfViewer') {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Clear previous
  container.innerHTML = '';

  pdfjsLib.getDocument(pdfUrl).promise.then((pdfDoc) => {
    for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
      pdfDoc.getPage(pageNum).then((page) => {
        const canvas = document.createElement("canvas");
        const context = canvas.getContext("2d");
        const viewport = page.getViewport({ scale: 1.2 });

        canvas.height = viewport.height;
        canvas.width = viewport.width;
        container.appendChild(canvas);

        page.render({ canvasContext: context, viewport: viewport });
      });
    }
  });
}
