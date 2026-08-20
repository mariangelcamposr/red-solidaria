import json
from datetime import datetime

def analyze_publication(title,description,resource_type,expiry_date=None):
    text=f'{title} {description}'.lower(); warnings=[]
    if any(x in text for x in ['vencido','caducado','expired']): warnings.append('posible producto vencido')
    if resource_type.lower() in ('medicamento','medicina') and not expiry_date: warnings.append('medicamento sin fecha de vencimiento')
    keywords=[w for w in ('medicamento','alimento','accesorio','higiene','perro','gato') if w in text]
    return json.dumps({'modo':'reglas_fase_2','confianza':0.85 if not warnings else 0.55,'keywords':keywords,'alertas':warnings,'analizado_en':datetime.utcnow().isoformat()},ensure_ascii=False)

def assistant_answer(message):
    q=message.lower()
    if 'registro' in q or 'registr' in q: return 'Para registrarte completa tus datos personales, ubicación, tipo de usuario y acepta términos y privacidad. En esta versión la verificación es local mediante enlace.'
    if 'donación' in q or 'donacion' in q: return 'Podés publicar medicamentos, alimentos, accesorios, higiene u otros insumos. El sistema valida los datos y busca coincidencias automáticamente.'
    if 'solicitud' in q: return 'Una solicitud indica el recurso, cantidad, justificación, ubicación y prioridad. Las solicitudes activas participan en el matching.'
    if 'coincidencia' in q or 'matching' in q: return 'El matching considera tipo, categoría, ubicación/distancia, cantidad, vencimiento, prioridad y urgencia.'
    if 'estado' in q: return 'Podés consultar tus publicaciones, coincidencias y transacciones desde el dashboard e historial.'
    if 'ayuda' in q or 'soporte' in q: return 'Si no puedo resolver tu consulta, podés crear un ticket de soporte desde el asistente.'
    return 'Puedo ayudarte con registro, donaciones, solicitudes, coincidencias, entregas, calificaciones y funcionamiento de la plataforma.'
