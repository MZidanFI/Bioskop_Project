function downloadTicket(elementId, movieTitle) {
    const element = document.getElementById(elementId);
    
    const opt = {
        margin:       10,
        filename:     `Tiket-${movieTitle}.pdf`,
        image:        { 
            type: 'jpeg', 
            quality: 0.98 
        },
        html2canvas:  { 
            scale: 2
         },
        jsPDF:        { 
            unit: 'mm', 
            format: 'a6', 
            orientation: 'landscape' 
        }
    };

    html2pdf().set(opt).from(element).save();
}