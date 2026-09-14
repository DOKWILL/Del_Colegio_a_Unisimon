from django.contrib import admin
from .models import Asistencia

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    # 1. Columnas que se mostrarán en la tabla
    list_display = (
        'id', 
        'estudiante', 
        'asignacion', 
        'fecha', 
        'encuentro', 
        'estado', 
        'observaciones'
    )
    
    # 2. ¡La magia de la edición rápida! Convierte estas columnas en campos editables
    list_editable = ('estado', 'observaciones')
    
    # 3. Filtros laterales (Vitales para cargar solo la lista de una clase específica)
    list_filter = ('asignacion', 'fecha', 'encuentro')
    
    # 4. Buscador conectado al campo nombre_apellido del modelo Estudiante
    search_fields = ('estudiante__nombre_apellido',)
    
    # 5. Paginación amplia para que quepa todo el salón en una sola vista
    list_per_page = 50
    
    # Evita que se pueda editar el ID o el estudiante por error
    readonly_fields = ('fecha', 'hora')
