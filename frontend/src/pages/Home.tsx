import { Link } from 'react-router-dom'
import Bulldog from '../components/Bulldog'

export default function Home() {
  return (
    <>
      <section className="hero">
        <div className="container">
          <div className="hero-copy">
          <p className="eyebrow">New Haven · Est. for Bulldogs</p>
          <h1>Yale Bulldog Pride</h1>
          <h2>
            Official Yale apparel and gear for students, alumni, and families.
          </h2>
          <p>
            Campus Customs brings Yale spirit to you with merchandise you can't wait to
            wear, from game-day hoodies, to every-day tees. Whether you're showing your
            school spirit from campus or from across the world, we help you show your
            pride.
          </p>
          <div className="hero-actions">
            <Link to="/products" className="btn btn-primary">
              Shop the Collection <span className="btn-arrow" aria-hidden="true">→</span>
            </Link>
            <Link to="/about" className="btn btn-outline">
              About Us
            </Link>
          </div>
          </div>

          {/* Handsome Dan, the shop's mascot, as the hero's brand figure. */}
          <div className="hero-mascot" aria-hidden="true">
            <span className="hero-mascot-ring" />
            <span className="hero-mascot-disc">
              <Bulldog size={132} accent="var(--gold-bright)" title="" />
            </span>
            <span className="hero-mascot-name">Handsome Dan</span>
          </div>
        </div>
      </section>

      <section className="pillars">
        <div className="container">
          <div className="pillar-grid">
            <article className="pillar">
              <h3>Game-Day Ready</h3>
              <p>
                Hoodies, crewnecks, and quarter-zips built for the Bowl in November and
                every tailgate in between.
              </p>
            </article>
            <article className="pillar">
              <h3>Everyday Blue</h3>
              <p>
                Soft tees and classic layers in Yale navy and white that look right on
                Old Campus or anywhere else.
              </p>
            </article>
            <article className="pillar">
              <h3>Made to Last</h3>
              <p>
                Heavyweight fabrics and stitched detailing, so your Yale piece outlasts
                the four years.
              </p>
            </article>
          </div>
        </div>
      </section>
    </>
  )
}
