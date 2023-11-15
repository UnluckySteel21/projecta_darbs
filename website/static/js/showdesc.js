function showDescription(button, descriptionId) {
    var descDiv = document.getElementById('desc-' + descriptionId);
    
    if (descDiv) {
        if (descDiv.style.display === 'none') {
            descDiv.style.display = 'block';
            button.textContent = 'Paslēpt aprakstu';
        } else {
            descDiv.style.display = 'none';
            button.textContent = 'Rādīt aprakstu';
        }
    }
}
