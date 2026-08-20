import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import client, { API_BASE_URL, getApiErrorMessage } from '../api/client';

export default function DonationDetail() {
  const { donationId } = useParams();
  const [data, setData] = useState(null);
  const [favorite, setFavorite] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    client.get(`/donations/${donationId}/detail`)
      .then((r) => setData(r.data))
      .catch((e) => setError(getApiErrorMessage(e, 'No se pudo cargar la publicación.')));
  }, [donationId]);

  const toggleFavorite = async () => {
    try {
      setError(null);
      const { data: result } = await client.post(`/donations/${data.donation.id}/favorite`);
      setFavorite(result.favorite);
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudo guardar la publicación como favorita.'));
    }
  };

  if (error && !data) return <div className="container"><div className="error" role="alert">{error}</div></div>;
  if (!data) return <div className="container">Cargando publicación...</div>;

  const d = data.donation;
  return <div className="container">
    <h2>{d.title}</h2>
    {error && <div className="error" role="alert">{error}</div>}
    <div className="card">
      <span className="badge">{d.status}</span>{d.is_urgent && <span> 🚨 Urgente</span>}
      <p>{d.description}</p>
      <p><b>Tipo:</b> {d.resource_type} · <b>Categoría:</b> {d.category}</p>
      <p><b>Cantidad:</b> {d.quantity} · <b>Estado:</b> {d.condition}</p>
      <p><b>Vencimiento:</b> {d.expiry_date ? new Date(d.expiry_date).toLocaleDateString() : 'No aplica'}</p>
      <p><b>Entrega:</b> {d.delivery_conditions}</p>
      {d.latitude != null && d.longitude != null && <a href={`https://www.google.com/maps/search/?api=1&query=${d.latitude},${d.longitude}`} target="_blank" rel="noreferrer">Ver ubicación aproximada en mapa</a>}
      <button style={{ marginLeft: 10 }} onClick={toggleFavorite}>{favorite ? '★ Guardada' : '☆ Guardar favorita'}</button>
    </div>
    <div className="card"><h3>Fotografías</h3><div className="photo-grid">{data.photos.map((p) => <img key={p.id} src={`${API_BASE_URL}${p.path}`} alt={d.title} />)}</div></div>
    <div className="card"><h3>Publicado por</h3><p>{data.donor.name} (@{data.donor.username})</p><p>Reputación: {data.donor.reputation_score}/5 ({data.donor.ratings_count} calificaciones)</p></div>
  </div>;
}
