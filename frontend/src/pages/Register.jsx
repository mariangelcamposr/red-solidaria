import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getApiErrorMessage } from '../api/client';

const roles = [
  ['particular', 'Particular'], ['rescatista', 'Rescatista'], ['hogar_transito', 'Hogar de tránsito'],
  ['ong', 'ONG'], ['veterinaria', 'Clínica veterinaria'], ['comercio', 'Comercio/Tienda']
];

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [step, setStep] = useState(1);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    username: '', email: '', password: '', first_name: '', last_name: '', phone: '', address: '',
    city: '', state: '', country: 'Venezuela', postal_code: '', role: 'particular', latitude: '',
    longitude: '', terms_accepted: false, privacy_accepted: false
  });

  const set = (key) => (e) => setForm({
    ...form,
    [key]: e.target.type === 'checkbox' ? e.target.checked : e.target.value
  });

  const next = () => {
    setError(null);
    if (step === 1 && (!form.first_name || !form.last_name || !form.email || !form.phone || !form.username || !form.password)) {
      setError('Completa todos los datos personales.'); return;
    }
    if (step === 2 && (!form.address || !form.city || !form.state || !form.country)) {
      setError('Completa la ubicación.'); return;
    }
    if (step === 2) {
      const hasLat = form.latitude !== '';
      const hasLon = form.longitude !== '';
      if (hasLat !== hasLon) {
        setError('Si deseas registrar coordenadas, debes completar latitud y longitud. También puedes dejar ambas vacías.'); return;
      }
      if (hasLat && (Number(form.latitude) < -90 || Number(form.latitude) > 90)) {
        setError('La latitud debe estar entre -90 y 90.'); return;
      }
      if (hasLon && (Number(form.longitude) < -180 || Number(form.longitude) > 180)) {
        setError('La longitud debe estar entre -180 y 180.'); return;
      }
    }
    setStep(Math.min(4, step + 1));
  };

  const submit = async () => {
    setError(null);
    if (!form.terms_accepted || !form.privacy_accepted) {
      setError('Debes aceptar Términos y Privacidad.'); return;
    }
    setSubmitting(true);
    try {
      const payload = {
        ...form,
        postal_code: form.postal_code || null,
        latitude: form.latitude === '' ? null : Number(form.latitude),
        longitude: form.longitude === '' ? null : Number(form.longitude),
      };
      await register(payload);
      nav('/dashboard');
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudo registrar.'));
    } finally {
      setSubmitting(false);
    }
  };

  return <div className="container" style={{ maxWidth: 700 }}>
    <h2>Crear cuenta</h2>
    <div className="progress">Paso {step} de 4 — {step * 25}%</div>
    {error && <div className="error" role="alert">{error}</div>}

    {step === 1 && <div className="card"><h3>Datos personales</h3>
      <div className="row"><input placeholder="Nombre" value={form.first_name} onChange={set('first_name')} /><input placeholder="Apellido" value={form.last_name} onChange={set('last_name')} /></div>
      <input placeholder="Usuario" value={form.username} onChange={set('username')} />
      <input type="email" placeholder="Correo" value={form.email} onChange={set('email')} />
      <input placeholder="Teléfono" value={form.phone} onChange={set('phone')} />
      <input type="password" placeholder="Contraseña (mín. 6)" value={form.password} onChange={set('password')} />
    </div>}

    {step === 2 && <div className="card"><h3>Ubicación</h3>
      <input placeholder="Dirección" value={form.address} onChange={set('address')} />
      <div className="row"><input placeholder="Ciudad" value={form.city} onChange={set('city')} /><input placeholder="Estado/Provincia" value={form.state} onChange={set('state')} /></div>
      <div className="row"><input placeholder="País" value={form.country} onChange={set('country')} /><input placeholder="Código postal" value={form.postal_code} onChange={set('postal_code')} /></div>
      <div className="row"><input type="number" step="any" placeholder="Latitud (opcional)" value={form.latitude} onChange={set('latitude')} /><input type="number" step="any" placeholder="Longitud (opcional)" value={form.longitude} onChange={set('longitude')} /></div>
      <p className="muted">Las coordenadas son opcionales. Puedes dejar ambas vacías.</p>
    </div>}

    {step === 3 && <div className="card"><h3>Tipo de usuario</h3>{roles.map(([v, l]) => <label key={v} className="choice"><input type="radio" name="role" value={v} checked={form.role === v} onChange={set('role')} />{l}</label>)}</div>}

    {step === 4 && <div className="card"><h3>Confirmación y privacidad</h3>
      <label className="choice"><input type="checkbox" checked={form.terms_accepted} onChange={set('terms_accepted')} />Acepto Términos y Condiciones.</label>
      <label className="choice"><input type="checkbox" checked={form.privacy_accepted} onChange={set('privacy_accepted')} />Acepto Política de Privacidad y tratamiento de datos.</label>
      <p className="muted">En esta entrega académica la verificación de correo queda simulada/local para no depender de un proveedor externo.</p>
    </div>}

    <div className="row">
      <button type="button" className="secondary" disabled={step === 1 || submitting} onClick={() => { setError(null); setStep(step - 1); }}>Anterior</button>
      {step < 4 ? <button type="button" onClick={next}>Siguiente</button> : <button type="button" disabled={submitting} onClick={submit}>{submitting ? 'Creando cuenta...' : 'Crear cuenta'}</button>}
    </div>
    <p className="muted">¿Ya tienes cuenta? <Link to="/login">Inicia sesión</Link></p>
  </div>;
}
