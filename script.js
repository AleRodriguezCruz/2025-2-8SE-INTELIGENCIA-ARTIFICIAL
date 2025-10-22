// Cargar estadísticas al iniciar
document.addEventListener('DOMContentLoaded', function() {
    cargarEstadisticas();
    cargarColumnas();
});

async function cargarEstadisticas() {
    try {
        const response = await fetch('/excel/negocio/estadisticas');
        const data = await response.json();
        
        if (response.ok) {
            mostrarEstadisticas(data.estadisticas);
        } else {
            mostrarError('Error al cargar estadísticas');
        }
    } catch (error) {
        mostrarError('Error de conexión: ' + error.message);
    }
}

async function cargarDatos() {
    const limite = document.getElementById('limite').value;
    try {
        const response = await fetch(`/excel/negocio/datos?limite=${limite}`);
        const data = await response.json();
        
        if (response.ok) {
            mostrarDatos(data.datos);
        } else {
            mostrarError('Error al cargar datos');
        }
    } catch (error) {
        mostrarError('Error de conexión: ' + error.message);
    }
}

async function filtrarDatos() {
    const columna = document.getElementById('columna').value;
    const valor = document.getElementById('valor').value;
    
    if (!columna || !valor) {
        alert('Por favor, selecciona columna y ingresa un valor');
        return;
    }
    
    try {
        const response = await fetch(`/excel/negocio/filtrar?columna=${columna}&valor=${valor}`);
        const data = await response.json();
        
        if (response.ok) {
            mostrarFiltrosResultado(data.datos_filtrados);
        } else {
            mostrarError('Error al filtrar datos');
        }
    } catch (error) {
        mostrarError('Error de conexión: ' + error.message);
    }
}

async function analizarDatos() {
    const tipoAnalisis = document.getElementById('tipo-analisis').value;
    
    try {
        const response = await fetch(`/excel/negocio/analizar?tipo_analisis=${tipoAnalisis}`);
        const data = await response.json();
        
        if (response.ok) {
            mostrarAnalisisResultado(data.analisis);
        } else {
            mostrarError('Error en el análisis');
        }
    } catch (error) {
        mostrarError('Error de conexión: ' + error.message);
    }
}

// Funciones de utilidad para mostrar datos
function mostrarEstadisticas(stats) {
    const container = document.getElementById('estadisticas');
    container.innerHTML = `
        <div class="stat-item">
            <strong>Total Registros</strong>
            <div>${stats.total_registros}</div>
        </div>
        <div class="stat-item">
            <strong>Columnas</strong>
            <div>${stats.columnas ? stats.columnas.length : 0}</div>
        </div>
    `;
}

function mostrarDatos(datos) {
    const container = document.getElementById('datos-container');
    if (datos.length === 0) {
        container.innerHTML = '<p>No hay datos disponibles</p>';
        return;
    }
    
    const headers = Object.keys(datos[0]);
    const html = `
        <table>
            <thead>
                <tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr>
            </thead>
            <tbody>
                ${datos.map(row => `
                    <tr>${headers.map(h => `<td>${row[h]}</td>`).join('')}</tr>
                `).join('')}
            </tbody>
        </table>
    `;
    container.innerHTML = html;
}

function mostrarError(mensaje) {
    console.error(mensaje);
    // Puedes mostrar el error en un div específico o con alert
    alert(mensaje);
}
