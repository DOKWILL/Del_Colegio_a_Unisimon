/**
 * Funcionalidad principal del sistema.
 * - Sidebar toggle para responsive
 * - Auto-dismiss de alertas
 * - Confirmación antes de eliminar
 * - Cálculo de notas en tiempo real
 */
document.addEventListener('DOMContentLoaded', function() {

    // === SIDEBAR TOGGLE (Responsive) ===
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            if (overlay) overlay.classList.toggle('show');
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // === AUTO-DISMISS ALERTS ===
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function() { alert.remove(); }, 500);
        }, 5000);
    });

    // === CONFIRM DELETE ===
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    deleteButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const name = btn.getAttribute('data-confirm-delete');
            if (!confirm('¿Está seguro que desea eliminar "' + name + '"? Esta acción no se puede deshacer.')) {
                e.preventDefault();
            }
        });
    });

    // === REAL-TIME GRADE CALCULATION ===
    const gradeInputs = document.querySelectorAll('.grade-input');
    gradeInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const row = input.closest('tr');
            if (!row) return;

            const p1 = parseFloat(row.querySelector('.parcial1')?.value) || 0;
            const p2 = parseFloat(row.querySelector('.parcial2')?.value) || 0;
            const p3 = parseFloat(row.querySelector('.parcial3')?.value) || 0;

            const definitiva = (p1 * 0.30 + p2 * 0.30 + p3 * 0.40).toFixed(2);
            const defCell = row.querySelector('.definitiva-preview');
            if (defCell) {
                defCell.textContent = definitiva;
                defCell.style.fontWeight = '700';
                defCell.style.color = parseFloat(definitiva) >= 3.0 ? '#10b981' : '#ef4444';
            }
        });
    });

    // === ANIMATE ELEMENTS ON SCROLL ===
    const animateElements = document.querySelectorAll('.animate-in');
    animateElements.forEach(function(el, i) {
        el.style.animationDelay = (i * 0.05) + 's';
    });
});
