import { useEffect, useState } from 'react';
import client, { getApiErrorMessage } from '../api/client';

export default function Dashboard() {
  const [d, setD] = useState(null), [n, setN] = useState([]), [error, setError] = useState(null);
  useEffect(() => {
    Promise.all([client.get('/dashboard'), client.get('/notifications')])
      .then(([a, b]) => { setD(a.data); setN(b.data.slice(0, 5)); })
      .catch((e) => setError(getApiErrorMessage(e, 'No se pudo cargar el dashboard.')));
  }, []);
  if (error && !d) return <div className="container"><div className="error" role="alert">{error}</div></div>;
  if (!d) return <div className="container">Cargando dashboard...</div>;
  return <div className="container"><h2>Dashboard personal</h2>{error && <div className="error" role="alert">{error}</div>}<div className="grid">{[['Donaciones activas', d.active_donations], ['Solicitudes abiertas', d.open_requests], ['Coincidencias', d.recommended_matches], ['Transacciones', d.recent_transactions], ['Reputación', `${d.reputation_score}/5`], ['Próximos a vencer', d.expiring_soon]].map(([a,b]) => <div className="card metric" key={a}><span>{a}</span><strong>{b}</strong></div>)}</div><div className="card"><h3>Mis estadísticas</h3><p>Solicitudes atendidas: {d.requests_attended}</p><p>Tasa de publicaciones/transacciones exitosas: {d.successful_rate}%</p><pre>{JSON.stringify(d.donations_by_category, null, 2)}</pre></div><div className="card"><h3>Notificaciones recientes</h3>{n.map(x => <p key={x.id}><b>{x.title}</b> — {x.message}</p>)}</div></div>;
}
