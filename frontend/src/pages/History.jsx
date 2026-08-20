import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client, { getApiErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function History() {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      const { data } = await client.get("/transactions/me", { params: { _refresh: Date.now() } });
      setTransactions(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "No se pudo cargar el historial."));
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    const refresh = () => load();
    window.addEventListener('focus', refresh);
    return () => { clearInterval(interval); window.removeEventListener('focus', refresh); };
  }, [load]);

  return <div className="container">
    <h2>Historial</h2>
    {error && <p className="error" role="alert">{error}</p>}
    {user && <p className="muted">Tu reputación actual: <span className="stars">{"★".repeat(Math.round(user.reputation_score))}</span> ({user.reputation_score} / 5, {user.ratings_count} calificaciones)</p>}
    {transactions.length === 0 && !error && <p className="muted">Todavía no tenés transacciones.</p>}
    {transactions.map((t) => <div className="card" key={t.id}>
      <span className={`badge ${t.status}`}>{t.status}</span>
      <h3>Transacción #{t.id}</h3>
      <p className="muted">{t.delivery_details}</p>
      <p>Confirmación del donante: {t.donor_confirmed ? "✅ confirmada" : "⏳ pendiente"}<br />Confirmación del solicitante: {t.requester_confirmed ? "✅ confirmada" : "⏳ pendiente"}</p>
      <Link to={`/transacciones/${t.id}`}><button className="secondary">Ver detalle</button></Link>
    </div>)}
  </div>;
}
