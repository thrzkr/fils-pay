import { Link } from "react-router-dom";
import "../../dashboard.css";

/**
 * Shown for any path the router doesn't know, instead of React Router's
 * default "Unexpected Application Error" screen. Payment links live under
 * /pay/:token, so a customer who lands here most likely has a mistyped or
 * truncated link.
 */
export function NotFoundPage() {
  return (
    <main className="dash-centered">
      <h1>Page not found</h1>
      <p className="dash-muted">
        This address doesn't match any FilsPay page. If you were paying, check
        that you opened the full payment link you were sent.
      </p>
      <p>
        <Link to="/dashboard/login">Merchant sign-in</Link>
      </p>
    </main>
  );
}
