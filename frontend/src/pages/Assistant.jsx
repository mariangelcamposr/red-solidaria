import { useEffect, useState } from 'react';
import client, { getApiErrorMessage } from '../api/client';

export default function Assistant() {
  const [rows, setRows] = useState([]), [text, setText] = useState(''), [error, setError] = useState(null), [sending, setSending] = useState(false);
  const load = async () => { try { setRows((await client.get('/assistant/history')).data); } catch (e) { setError(getApiErrorMessage(e, 'No se pudo cargar el historial del asistente.')); } };
  useEffect(() => { load(); }, []);
  const sendMessage = async (message) => { try { setError(null); await client.post('/assistant/message', { message }); await load(); } catch (e) { setError(getApiErrorMessage(e, 'No se pudo consultar al asistente.')); } };
  const send = async (e) => { e.preventDefault(); if (!text.trim()) return; setSending(true); await sendMessage(text); setText(''); setSending(false); };
  return <div className="container" style={{ maxWidth: 760 }}><h2>🤖 Asistente virtual</h2><p className="muted">Versión académica Fase 2: respuestas predefinidas y reglas de negocio, con historial persistente.</p>{error && <div className="error" role="alert">{error}</div>}<div className="chat-box">{rows.map(m => <div key={m.id} className={`msg ${m.sender === 'user' ? 'mine' : 'theirs'}`}>{m.content}</div>)}</div><div className="row"><button onClick={() => sendMessage('¿Cómo publico una donación?')}>Publicar donación</button><button onClick={() => sendMessage('¿Cómo funciona el matching?')}>Matching</button><button onClick={() => sendMessage('Necesito ayuda de soporte')}>Soporte</button></div><form onSubmit={send} className="row" style={{ marginTop: 10 }}><input value={text} onChange={e => setText(e.target.value)} placeholder="Escribe tu consulta..."/><button disabled={sending}>{sending ? 'Enviando...' : 'Enviar'}</button></form></div>;
}
