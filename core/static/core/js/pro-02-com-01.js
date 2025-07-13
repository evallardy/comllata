const dropdownButton2 = document.getElementById('dropdownButton2');
const dropdownMenu2 = document.getElementById('dropdownMenu2');
dropdownMenu2.addEventListener('click', function (e) {
if (e.target.classList.contains('dropdown-item')) {
    e.preventDefault();
    const currentText = dropdownButton2.textContent.trim();
    const selectedText = e.target.textContent.trim();
    dropdownButton2.textContent = selectedText;
    e.target.textContent = currentText;
}
});
