import Bulldog from './Bulldog'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-brand">
          <span className="footer-mark">
            <Bulldog size={34} accent="var(--gold-bright)" />
          </span>
          <span>
            <span className="footer-name">CAMPUS CUSTOMS</span>
            <span className="footer-line">Bulldog pride, wherever you are.</span>
          </span>
        </div>

        <div className="footer-haven">
          <strong>Made for New Haven</strong>
          Two blocks off the Green, under the elms.
          <br />
          Shipping Yale blue to every corner of the world.
          <span className="footer-coords">41.3163&deg; N &middot; 72.9223&deg; W</span>
        </div>
      </div>

      <div className="container footer-legal">
        <span>&copy; {new Date().getFullYear()} Campus Customs &middot; New Haven, Connecticut</span>
        <span>Official Yale apparel for students, alumni, and families.</span>
      </div>
    </footer>
  )
}
