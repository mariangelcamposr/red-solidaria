import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import client, { getApiErrorMessage } from '../api/client';

const types = ['', 'medicamento', 'alimento', 'accesorio', 'producto de higiene', 'otro'];

export default function Search() {
  const [f, setF] = useState({ category: '', resource_type: '', location: '', max_distance_km: '', sort_by: 'relevance' });
  const [rows, setRows] = useState([]);
  const [name, setName] = useState('');
  const [error, setError] = useState(null);
  const [notice, setNotice] = useState(null);
  const [searched, setSearched] = useState(false);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    client.get('/catalogs/categories')
      .then(({ data }) => setCategories(data))
      .catch((e) => setError(getApiErrorMessage(e, 'No se pudieron cargar las categorías.')));
  }, []);

  const categoriesByType = useMemo(() => categories.reduce((acc, item) => {
    (acc[item.resource_type] ||= []).push(item.name);
    return acc;
  }, {}), [categories]);

  const categoryOptions = f.resource_type ? (categoriesByType[f.resource_type] || []) : categories.map(item => item.name).filter((name, index, all) => all.indexOf(name) === index);

  const set = key => e => setF(current => ({ ...current, [key]: e.target.value }));

  const changeType = e => {
    const resourceType = e.target.value;
    const options = categoriesByType[resourceType] || [];
    setF(current => ({ ...current, resource_type: resourceType, category: resourceType && !options.includes(current.category) ? (options[0] || '') : current.category }));
  };

  const search = async () => {
    try {
      setError(null);
      setNotice(null);
      const data = (await client.get('/search/donations', { params: { ...f, max_distance_km: f.max_distance_km || undefined } })).data;
      setRows(data);
      setSearched(true);
      if (!data.length) setNotice('No se encontraron donaciones con los criterios seleccionados. Prueba modificando los filtros.');
    } catch (e) {
      setRows([]);
      setSearched(true);
      setError(getApiErrorMessage(e, 'No se pudo realizar la búsqueda.'));
    }
  };

  const save = async () => {
    try {
      setError(null);
      await client.post('/notifications/search-favorites', { name, filters: f, alerts_enabled: true });
      setName('');
      setNotice('Búsqueda guardada correctamente.');
    } catch (e) {
      setError(getApiErrorMessage(e, 'No se pudo guardar la búsqueda.'));
    }
  };

  return <div className="container">
    <h2>Búsqueda de donaciones</h2>
    {error && <div className="error" role="alert">{error}</div>}
    {notice && <div className="success" role="status">{notice}</div>}
    <div className="card">
      <div className="row">
        <select value={f.resource_type} onChange={changeType}>
          <option value="">Todos los tipos</option>
          {types.slice(1).map(type => <option key={type} value={type}>{type}</option>)}
        </select>
        <select value={f.category} onChange={set('category')} disabled={!categoryOptions.length}>
          <option value="">Todas las categorías</option>
          {categoryOptions.map(category => <option key={category} value={category}>{category}</option>)}
        </select>
      </div>
      <div className="row"><input placeholder="Ubicación" value={f.location} onChange={set('location')} /><input type="number" min="0" placeholder="Distancia máxima km" value={f.max_distance_km} onChange={set('max_distance_km')} /></div>
      <select value={f.sort_by} onChange={set('sort_by')}><option value="relevance">Relevancia</option><option value="distance">Cercanía</option><option value="date">Fecha</option><option value="expiry">Vencimiento</option><option value="quantity">Cantidad</option></select>
      <div className="row"><button type="button" onClick={search}>Buscar</button><input placeholder="Nombre de búsqueda favorita" value={name} onChange={e => setName(e.target.value)} /><button type="button" className="secondary" disabled={!name} onClick={save}>Guardar búsqueda</button></div>
    </div>
    {searched && !rows.length && !error && <div className="card"><p className="muted">No hay resultados para los filtros actuales.</p></div>}
    {rows.map(d => <div className="card" key={d.id}><h3><Link to={`/donaciones/${d.id}`}>{d.title}</Link></h3><p>{d.description}</p><p className="muted">{d.category} · {d.location} · {d.quantity}</p></div>)}
  </div>;
}
