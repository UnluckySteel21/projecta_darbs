function showDescription(button) {
    var row = button.parentNode; // Get the parent <td> element
    var descDiv = row.querySelector('.description'); // Find the corresponding description element

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