const dropdownButton1 = document.getElementById('dropdownButton1');
const dropdownMenu1 = document.getElementById('dropdownMenu1');
dropdownMenu1.addEventListener('click', function (e) {
if (e.target.classList.contains('dropdown-item')) {
    e.preventDefault();
    const currentText = dropdownButton1.textContent.trim();
    const selectedText = e.target.textContent.trim();
    dropdownButton1.textContent = selectedText;
    e.target.textContent = currentText;
}
});
