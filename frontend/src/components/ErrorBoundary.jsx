import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error('Error no controlado en la interfaz:', error, info);
  }

  handleReload = () => {
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <main className="container">
        <div className="card error-card">
          <h2>Ocurrió un problema en la aplicación</h2>
          <p>
            La pantalla encontró un error inesperado. Tus datos no se pierden por este mensaje.
          </p>
          <p className="muted">
            Puedes intentar recargar la página. Si el problema continúa, revisa el mensaje de la consola.
          </p>
          <button onClick={this.handleReload}>Recargar aplicación</button>
          {this.state.error?.message && (
            <details className="error-details">
              <summary>Detalle técnico</summary>
              <pre>{this.state.error.message}</pre>
            </details>
          )}
        </div>
      </main>
    );
  }
}
