import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import client, { getApiErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function MatchDetail() {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");
  const [deliveryDetails, setDeliveryDetails] = useState("");
  const [transaction, setTransaction] = useState(null);
  const [error, setError] = useState(null);
  const bottomRef = useRef(null);

  const loadMessages = async () => {
    try {
      const { data } = await client.get(`/matches/${matchId}/messages`);
      setMessages(data);
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudieron cargar los mensajes.'));
    }
  };

  useEffect(() => {
    loadMessages();
    const interval = setInterval(loadMessages, 4000); // polling simple para el chat
    return () => clearInterval(interval);
  }, [matchId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    try {
      setError(null);
      await client.post(`/matches/${matchId}/messages`, { content: text });
      setText('');
      await loadMessages();
    } catch (err) {
      setError(getApiErrorMessage(err, 'No se pudo enviar el mensaje.'));
    }
  };

  const coordinate = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const { data } = await client.post(`/transactions/${matchId}/coordinate`, {
        delivery_details: deliveryDetails,
      });
      setTransaction(data);
    } catch (err) {
      setError(getApiErrorMessage(err, "No se pudo coordinar la entrega"));
    }
  };

  const markDelivered = async () => {
    setError(null);
    try {
      const { data } = await client.post(`/transactions/${matchId}/deliver`);
      setTransaction(data);
      navigate(`/transacciones/${data.id}`);
    } catch (err) {
      setError(getApiErrorMessage(err, "No se pudo registrar la entrega"));
    }
  };

  return (
    <div className="container">
      <h2>Conversación</h2>
      {error && <p className="error">{error}</p>}

      <div className="chat-box">
        {messages.map((m) => (
          <div key={m.id} className={`msg ${m.sender_id === user?.id ? "mine" : "theirs"}`}>
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={sendMessage} className="row">
        <input
          placeholder="Escribí un mensaje..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <button type="submit" style={{ flex: "0 0 auto" }}>
          Enviar
        </button>
      </form>

      <div className="card" style={{ marginTop: 20 }}>
        <h3>Coordinar entrega</h3>
        <form onSubmit={coordinate}>
          <textarea
            placeholder="Fecha, hora, lugar y condiciones acordadas"
            value={deliveryDetails}
            onChange={(e) => setDeliveryDetails(e.target.value)}
            rows={2}
            required
          />
          <button type="submit">Guardar acuerdo</button>
        </form>
        {transaction && <p className="muted">Detalles guardados: {transaction.delivery_details}</p>}
        <button className="secondary" style={{ marginTop: 10 }} onClick={markDelivered}>
          Marcar entrega como realizada
        </button>
      </div>
    </div>
  );
}
