const { useState, useEffect } = React;

const DataTable = ({ data, columns }) => (
  <table><tbody>{((data || []).map((row, i) => {
    const isObj = row && typeof row === 'object' && !Array.isArray(row);
    const cols = columns || (isObj ? Object.keys(row) : ['value']);
    return <tr key={i}>{cols.map(c => <td key={c}>{isObj ? row[c] : String(row)}</td>)}</tr>;
  }))}</tbody></table>
);

const DataForm = ({ name, fields, onSubmit }) => (
  <form onSubmit={e => { e.preventDefault(); onSubmit(new FormData(e.target)); }}>
    { (fields || []).map(f => <label key={f}>{f}<input name={f} /></label>) }
    <button type="submit">Submit</button>
  </form>
);

const App = () => {
  const [path, setPath] = useState(() => (window.location.hash || '#/').slice(1) || '/');
  useEffect(() => { const onHash = () => setPath((window.location.hash || '#/').slice(1) || '/'); window.addEventListener('hashchange', onHash); onHash(); return () => window.removeEventListener('hashchange', onHash); }, []);
  const R = {"/": "Dashboard"};
  const Comps = {  };
  const Page = Comps[R[path]] || Dashboard;
  const nav = ["/"].map(p => <a key={p} href={'#'+p}>{p}</a>);
  return <div><nav>{nav}</nav><Page /></div>;
};

ReactDOM.render(<App />, document.getElementById('root'));
