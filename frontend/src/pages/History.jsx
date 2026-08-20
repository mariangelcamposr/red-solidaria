import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import client from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function History() {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);

  useEffect(() => {
    client.get("/transactions/me").then(({ data }) => setTransactions(data));
  }, []);

  return (
    <div className="container">
      <h2>Historial</h2>
      {user && (
        <p className="muted">
          Tu reputación actual: <span className="stars">{"★".repeat(Math.round(user.reputation_score))}</span>{" "}
          ({user.reputation_score} / 5, {user.ratings_count} calificaciones)
        </p>
      )}
      {transactions.length === 0 && <p className="muted">Todavía no tenés transacciones.</p>}
      {transactions.map((t) => (
        <div className="card" key={t.id}>
          <span className={`badge ${t.status}`}>{t.status}</span>
          <h3>Transacción #{t.id}</h3>
          <p className="muted">{t.delivery_details}</p>
          <Link to={`/transacciones/${t.id}`}>
            <button className="secondary">Ver detalle</button>
          </Link>
        </div>
      ))}
    </div>
  );
}
