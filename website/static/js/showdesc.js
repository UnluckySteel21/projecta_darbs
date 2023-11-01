function showDescription(button, description) {
    var descDiv = document.getElementById('desc-' + description);
    if (descDiv.style.display === 'none') {
        descDiv.style.display = 'block';
        button.textContent = 'Paslēpt aprakstu'; 
    } else {
        descDiv.style.display = 'none';
        button.textContent = 'Rādīt aprakstu'; 
    }
}