// JS Utility Functions for ERPConnect App

// ===================
// Chart Download Button
// ===================
function downloadChart(canvasId, filename) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return alert("Chart not found");
    const link = document.createElement("a");
    link.href = canvas.toDataURL("image/png");
    link.download = filename + ".png";
    link.click();
  }
  
  // ===================
  // Tag Preview Renderer (Optional)
  // ===================
  function previewTags(inputId, previewContainerId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewContainerId);
    if (!input || !preview) return;
  
    input.addEventListener("input", () => {
      const tags = input.value.split(',').map(t => t.trim()).filter(Boolean);
      preview.innerHTML = '';
      tags.forEach(tag => {
        const span = document.createElement("span");
        span.className = "badge bg-secondary me-1";
        span.textContent = tag.toLowerCase();
        preview.appendChild(span);
      });
    });
  }
  
  // ===================
  // Print Helper (optional override)
  // ===================
  function triggerPrint() {
    window.print();
  }
  