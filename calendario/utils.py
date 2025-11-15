# calendario/utils.py
def create_or_update_event_for_medication(medication):
    """
    Implementa aquí la creación/actualización de eventos en tu calendario.
    medication es instancia de perfil_médico.models.Medication
    Debes mapear 'frequency' a reglas de repetición (RRULE) o crear eventos periódicos.
    """
    # Ejemplo conceptual: si frequency contiene "diaria" y preferred_time en profile,
    # crear evento en tu tabla Event con fecha = today @ profile.preferred_time y repetir diario.
    pass

def delete_event_for_medication(medication):
    # Busca evento asociado y borralo.
    pass
