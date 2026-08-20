import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import client, { getApiErrorMessage } from '../api/client';

export default function Matches() {
  const [matches, setMatches] = useState([]);
  const [donationsById, setDonationsById] = useState({});
  const [error, setError] = useState(null);
  const { user } = useAuth();

  const load = async () => {
    try {
      const { data } = await client.get('/matches/me');
      setMatches(data);
      const donationIds = [...new Set(data.map((m) => m.donation_id))];
      const donationEntries = await Promise.all(
        donationIds.map((id) => client.get(`/donations/${id}`).then((r) => [id, r.data]))
      );
      setDonationsById(Object.fromEntries(donationEntries));
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudieron cargar las coincidencias.'));
    }
  };

  useEffect(() => { load(); }, []);

  const contact = async (id) => {
    try {
      setError(null);
      await client.post(`/matches/${id}/contact`);
      await load();
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudo contactar al donante.'));
    }
  };

  return <div className="container">
    <h2>Mis coincidencias</h2>
    {error && <div className="error" role="alert">{error}</div>}
    <p className="muted">El sistema analiza tus solicitudes activas y te muestra las donaciones más compatibles, ordenadas por puntaje.</p>
    {matches.length === 0 && <p className="muted">Todavía no tenés coincidencias.</p>}
    {matches.map((m) => {
      const donation = donationsById[m.donation_id];
      // Una coincidencia entre una solicitud y una donación del mismo usuario no es válida.
      if (!donation || (user && donation.donor_id === user.id)) return null;
      return <div className="card" key={m.id}>
        <span className={`badge ${m.status}`}>{m.status}</span>
        <h3>{donation ? donation.title : `Donación #${m.donation_id}`}</h3>
        {donation && <p>{donation.description}</p>}
        {donation && <p className="muted">{donation.category} · {donation.location}</p>}
        <p className="muted">Puntaje de compatibilidad: {(m.score * 100).toFixed(0)}%</p>
        <div className="row" style={{ maxWidth: 320 }}>
          {m.status === 'notificada' || m.status === 'visualizada' ?
            <button onClick={() => contact(m.id)}>Contactar donante</button> :
            <Link to={`/coincidencias/${m.id}`}><button>Abrir conversación</button></Link>}
        </div>
      </div>;
    })}
  </div>;
}
