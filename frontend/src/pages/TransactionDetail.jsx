import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import client, { getApiErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function TransactionDetail() {
  const { transactionId } = useParams();
  const { user } = useAuth();

  const [tx, setTx] = useState(null);
  const [score, setScore] = useState(5);
  const [comment, setComment] = useState("");
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);

  const load = async () => {
    const { data } = await client.get("/transactions/me");
    const found = data.find((t) => String(t.id) === transactionId);
    setTx(found || null);
  };

  useEffect(() => {
    load();
  }, [transactionId]);

  const confirm = async () => {
    setError(null);
    try {
      const { data } = await client.post(`/transactions/${transactionId}/confirm`);
      setTx(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "No se pudo confirmar"));
    }
  };

  const submitRating = async (e) => {
    e.preventDefault();
    setError(null);
    setNotice(null);
    try {
      await client.post(`/transactions/${transactionId}/ratings`, { score: Number(score), comment });
      setNotice("¡Gracias! Tu calificación fue registrada y actualizó la reputación del usuario.");
      setComment("");
    } catch (err) {
      setError(getApiErrorMessage(err, "No se pudo calificar"));
    }
  };

  if (!tx) return <div className="container">Cargando transacción...</div>;

  const myConfirmation = user?.id === tx.donor_id ? tx.donor_confirmed : tx.requester_confirmed;

  return (
    <div className="container">
      <h2>Transacción #{tx.id}</h2>
      {error && <p className="error">{error}</p>}
      {notice && <p style={{ color: "#16a34a" }}>{notice}</p>}

      <div className="card">
        <span className={`badge ${tx.status}`}>{tx.status}</span>
        <p className="muted">Detalles de entrega: {tx.delivery_details}</p>
        <p>
          Confirmación del donante: {tx.donor_confirmed ? "✅" : "⏳ pendiente"}
          <br />
          Confirmación del solicitante: {tx.requester_confirmed ? "✅" : "⏳ pendiente"}
        </p>

        {tx.status === "pendiente_confirmacion" && !myConfirmation && (
          <button onClick={confirm}>Confirmar que la entrega fue exitosa</button>
        )}
        {tx.status === "pendiente_confirmacion" && myConfirmation && (
          <p className="muted">Ya confirmaste. Esperando confirmación de la otra parte.</p>
        )}
      </div>

      {tx.status === "completada" && (
        <div className="card">
          <h3>Calificar experiencia</h3>
          <form onSubmit={submitRating}>
            <select value={score} onChange={(e) => setScore(e.target.value)}>
              {[5, 4, 3, 2, 1].map((n) => (
                <option key={n} value={n}>
                  {"★".repeat(n)} ({n})
                </option>
              ))}
            </select>
            <textarea
              placeholder="Comentario (opcional)"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              rows={2}
            />
            <button type="submit">Enviar calificación</button>
          </form>
        </div>
      )}
    </div>
  );
}
