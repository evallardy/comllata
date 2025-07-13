const numberFormat2 = new Intl.NumberFormat('en-MX', { style: 'decimal', 'fraction': '00' });
function valideKey(evt) {
    var code = (evt.which) ? evt.which : evt.keyCode;
    var value = evt.target.value;
    var hasDecimal = (value.indexOf('.') !== -1);
    if ((code >= 48 && code <= 57) || (code == 46 && !hasDecimal)) {
        return true;
    } else {
        return false;
    }
}
function valideKeySinPunto(evt){
    var code = (evt.which) ? evt.which : evt.keyCode;
    if(code>=48 && code<=57) {
        return true;
    } else{
        return false;
    }
}
function reformatear(obj) {
    let valor = $('#' + obj).val().replace(/,/g, '');  // Eliminar comas del valor del campo
    $('#' + obj).val(numberFormat2.format(valor));  // Aplicar formato al valor sin comas
//    objeto = "#" + obj;
//    valor = $(objeto).val().replaceAll(",", "").replaceAll(",", "");
//    $(objeto).val(numberFormat2.format(valor));
}
//function reformatear(obj) {
//    objeto = "#" + obj;
//    valor = $(objeto).val().replaceAll(",", "").replaceAll(",", "");
//    $(objeto).val(numberFormat2.format(valor));
//}
function validaNumeros(e) {
    if (e.keyCode >= 48 && e.keyCode <= 57) {
        return true;
    } else {
        return false;
    }
}
function formatoDecimal(cadena, e, d ) {
    contador = 0;
    decimales = 0;
    enteros = 0;
    sw = 0;
    for(var i = 0; i < cadena.length; i++) {
        if (cadena[i] == ".") {
            contador ++
            sw = 1;
        } else {
            if (sw == 1) {
                if (contador == 1) {
                    decimales ++;
                    if (decimales > 2) {
                        return false;
                    }
                }
            } else {
                enteros ++;
                if (enteros > 2) {
                    return false;
                }
            }
        }
    }
    if (contador > 1) {
        return false;
    } else {
        return true;
    }
}
