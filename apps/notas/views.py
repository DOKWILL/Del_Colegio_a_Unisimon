@login_required_custom
def registrar_notas(request, asignacion_id):
    asignacion = get_object_or_404(Asignacion, pk=asignacion_id)
    
    # 1. Traer matriculados
    matriculas = Matricula.objects.filter(asignacion=asignacion, activa=True).select_related('estudiante')
    
    # 2. Traer notas existentes y organizarlas en un diccionario por el ID del estudiante
    notas_existentes = Nota.objects.filter(asignacion=asignacion)
    diccionario_notas = {nota.estudiante_id: nota for nota in notas_existentes}

    # 3. Emparejar estudiante con su nota (si existe)
    lista_estudiantes = []
    for matricula in matriculas:
        lista_estudiantes.append({
            'estudiante': matricula.estudiante,
            'nota': diccionario_notas.get(matricula.estudiante.id) # Puede ser None si es la primera vez
        })

    if request.method == 'POST':
        for item in lista_estudiantes:
            est_id = item['estudiante'].id
            
            # Capturar valores del form. Si viene vacío (''), lo convertimos a None
            p1_raw = request.POST.get(f'parcial1_{est_id}')
            p2_raw = request.POST.get(f'parcial2_{est_id}')
            p3_raw = request.POST.get(f'parcial3_{est_id}')
            
            p1 = float(p1_raw) if p1_raw else None
            p2 = float(p2_raw) if p2_raw else None
            p3 = float(p3_raw) if p3_raw else None

            # Guardar preservando lo que el profesor ingresó (o dejó vacío)
            Nota.objects.update_or_create(
                asignacion=asignacion,
                estudiante=item['estudiante'],
                defaults={
                    'parcial1': p1,
                    'parcial2': p2,
                    'parcial3': p3,
                }
            )
        messages.success(request, 'Calificaciones guardadas correctamente.')
        return redirect('notas:ver_notas', asignacion_id=asignacion.id)

    return render(request, 'notas/registrar_notas.html', {
        'asignacion': asignacion,
        'lista_estudiantes': lista_estudiantes
    })
