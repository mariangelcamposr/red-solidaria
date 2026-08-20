import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import client, { getApiErrorMessage } from '../api/client';

const types = ['medicamento', 'alimento', 'accesorio', 'producto de higiene', 'otro'];
const EMPTY_FORM = {
  title: '', description: '', resource_type: 'alimento', category: '', quantity: 1, condition: 'bueno',
  location: '', delivery_conditions: 'A coordinar', expiry_date: '', presentation: '', package_condition: '',
  latitude: '', longitude: '', is_urgent: false, image: null
};

export default function Donations() {
  const [items, setItems] = useState([]);
  const [mine, setMine] = useState([]);
  const [categories, setCategories] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [notice, setNotice] = useState(null);
  const [error, setError] = useState(null);
  const [fileInputKey, setFileInputKey] = useState(0);

  const categoriesByType = useMemo(() => categories.reduce((acc, item) => {
    (acc[item.resource_type] ||= []).push(item.name);
    return acc;
  }, {}), [categories]);

  const load = async () => {
    try {
      const [available, own, catalog] = await Promise.all([
        client.get('/donations'),
        client.get('/donations', { params: { mine: true } }),
        client.get('/catalogs/categories')
      ]);
      setItems(available.data);
      setMine(own.data);
      setCategories(catalog.data);
      setForm(current => {
        const options = catalog.data.filter(c => c.resource_type === current.resource_type).map(c => c.name);
        return current.category && options.includes(current.category)
          ? current
          : { ...current, category: options[0] || '' };
      });
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudieron cargar las donaciones y categorías.'));
    }
  };

  useEffect(() => { load(); }, []);

  const set = key => event => {
    const value = event.target.type === 'checkbox'
      ? event.target.checked
      : event.target.type === 'file'
        ? event.target.files[0] || null
        : event.target.value;
    setForm(current => ({ ...current, [key]: value }));
  };

  const changeType = event => {
    const resourceType = event.target.value;
    const options = categoriesByType[resourceType] || [];
    setForm(current => ({
      ...current,
      resource_type: resourceType,
      category: options[0] || '',
      ...(resourceType !== 'medicamento' ? { expiry_date: '', presentation: '', package_condition: '' } : {})
    }));
  };

  const resetForm = () => {
    const options = categoriesByType[EMPTY_FORM.resource_type] || [];
    setForm({ ...EMPTY_FORM, category: options[0] || '' });
    setFileInputKey(key => key + 1);
  };

  const submit = async event => {
    event.preventDefault();
    setError(null);
    setNotice(null);
    try {
      const fd = new FormData();
      Object.entries(form).forEach(([key, value]) => {
        if (value !== null && value !== '') fd.append(key, value);
      });
      await client.post('/donations', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
      resetForm();
      setNotice('Publicación creada, validada y enviada al matching. Los campos fueron limpiados para una nueva publicación.');
      await load();
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudo publicar'));
    }
  };

  const categoryOptions = categoriesByType[form.resource_type] || [];

  return <div className="container">
    <h2>Publicar donación</h2>
    {error && <p className="error" role="alert">{error}</p>}
    {notice && <p className="success" role="status">{notice}</p>}
    <form className="card" onSubmit={submit}>
      <div className="row">
        <input placeholder="Título" value={form.title} onChange={set('title')} required />
        <select value={form.resource_type} onChange={changeType} required>
          {types.map(type => <option key={type} value={type}>{type}</option>)}
        </select>
      </div>
      <select value={form.category} onChange={set('category')} required disabled={!categoryOptions.length}>
        {!categoryOptions.length && <option value="">Sin categorías disponibles</option>}
        {categoryOptions.map(category => <option key={category} value={category}>{category}</option>)}
      </select>
      <textarea maxLength={500} placeholder="Descripción" value={form.description} onChange={set('description')} required />
      <div className="row"><input type="number" min="0.1" step="0.1" placeholder="Cantidad" value={form.quantity} onChange={set('quantity')} required /><input placeholder="Estado de conservación" value={form.condition} onChange={set('condition')} required /></div>
      <input placeholder="Ubicación" value={form.location} onChange={set('location')} required />
      <div className="row"><input type="datetime-local" value={form.expiry_date} onChange={set('expiry_date')} /><input placeholder="Presentación" value={form.presentation} onChange={set('presentation')} /></div>
      <input placeholder="Estado del envase" value={form.package_condition} onChange={set('package_condition')} />
      <input placeholder="Condiciones de entrega" value={form.delivery_conditions} onChange={set('delivery_conditions')} required />
      <div className="row"><input type="number" step="any" placeholder="Latitud" value={form.latitude} onChange={set('latitude')} /><input type="number" step="any" placeholder="Longitud" value={form.longitude} onChange={set('longitude')} /></div>
      <label className="choice"><input type="checkbox" checked={form.is_urgent} onChange={set('is_urgent')} /> Marcar como urgente</label>
      <label>Fotografía JPG/PNG (obligatoria) <input key={fileInputKey} type="file" accept="image/jpeg,image/png" onChange={set('image')} required /></label>
      <button type="submit">Publicar</button>
    </form>

    <h3>Mis publicaciones</h3>
    {mine.map(d => <div className="card" key={d.id}><span className="badge">{d.status}</span><h3>{d.title}</h3><p>{d.description}</p><p className="muted">{d.resource_type} · {d.category} · cantidad {d.quantity} · {d.location}</p>{d.expiry_date && <p>Vence: {new Date(d.expiry_date).toLocaleDateString()}</p>}</div>)}
    <h3>Donaciones disponibles</h3>
    {items.map(d => <div className="card" key={d.id}><h3><Link to={`/donaciones/${d.id}`}>{d.title}</Link> {d.is_urgent && '🚨'}</h3><p>{d.description}</p><p className="muted">{d.category} · {d.location} · cantidad {d.quantity}</p></div>)}
  </div>;
}
