document.addEventListener('DOMContentLoaded', function() {
    let detalleContainer = document.getElementById('detalle-container');
    let addButton = document.getElementById('add-detalle');
    
    // Estas son las tallas y colores dinámicos que vienen del backend
    let tallas = JSON.parse('{{ tallas|safe }}');
    let colores = JSON.parse('{{ colores|safe }}');

    addButton.addEventListener('click', function() {
        let index = detalleContainer.children.length;
        let newField = document.createElement('div');
        newField.classList.add('form-row', 'mb-2');
        
        let tallasOptions = '';
        tallas.forEach(talla => {
            tallasOptions += `<option value="${talla[0]}">${talla[1]}</option>`;
        });
        
        let coloresOptions = '';
        colores.forEach(color => {
            coloresOptions += `<option value="${color[0]}">${color[1]}</option>`;
        });

        newField.innerHTML = `
            <div class="col">
                <label>Talla:</label>
                <select class="form-control" name="detalle[${index}][talla]">
                    ${tallasOptions}
                </select>
            </div>
            <div class="col">
                <label>Color:</label>
                <select class="form-control" name="detalle[${index}][color]">
                    ${coloresOptions}
                </select>
            </div>
            <div class="col">
                <label>Cantidad:</label>
                <input type="number" class="form-control" name="detalle[${index}][cantidad]" min="1">
            </div>
            <div class="col-auto">
                <button type="button" class="btn btn-danger mt-4 remove-detalle">Eliminar</button>
            </div>
        `;
        
        detalleContainer.appendChild(newField);

        // Añadir funcionalidad de eliminar
        newField.querySelector('.remove-detalle').addEventListener('click', function() {
            newField.remove();
        });
    });
});
