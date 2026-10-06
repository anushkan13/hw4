/**
 * "Handsome Dan" — the Campus Customs bulldog.
 *
 * An original drawing built from plain geometry: a rounded head, two folded ears,
 * a wrinkled brow, a wide muzzle and an off-centre grin. Deliberately not modelled
 * on any real university's mascot or wordmark. He appears as the chat assistant's
 * avatar, in the nav bar, in the hero, and in the footer, so one small character
 * carries the brand across the whole site.
 *
 * Colors come from currentColor and the `accent` prop, so the same drawing works on
 * navy, on cream, and at 20px or 200px.
 */
export default function Bulldog({
  size = 40,
  accent = 'var(--gold)',
  className,
  title = 'Handsome Dan, the Campus Customs bulldog',
}: {
  size?: number
  accent?: string
  className?: string
  title?: string
}) {
  // The body is currentColor, so on a light surface he is navy and on a dark one he
  // is white. The face is outlined in navy either way, so the eyes and muzzle never
  // disappear into the body.
  const outline = '#0a1b2e'

  return (
    <svg
      className={className}
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      role="img"
      aria-label={title}
    >
      {/* collar, behind the head */}
      <path
        d="M19 47c4 3.2 8.3 4.8 13 4.8S41 50.2 45 47l1.6 4.6c-4.6 3.6-9.5 5.4-14.6 5.4s-10-1.8-14.6-5.4L19 47z"
        fill={accent}
      />
      <circle cx="32" cy="55.4" r="2.6" fill={accent} stroke="currentColor" strokeWidth="1.6" />

      {/* ears, folded forward */}
      <path
        d="M14.5 17.5c-3.4-.6-5.8 1.5-6.2 5-.5 4.2 1.3 8.6 4.6 11.6 1.9 1.7 4 2.3 5.3 1.4 1.4-1 1.5-3 .6-5.8-1-3.1-1.4-6-1.1-8.6.2-2.1-1-3.3-3.2-3.6z"
        fill="currentColor"
      />
      <path
        d="M49.5 17.5c3.4-.6 5.8 1.5 6.2 5 .5 4.2-1.3 8.6-4.6 11.6-1.9 1.7-4 2.3-5.3 1.4-1.4-1-1.5-3-.6-5.8 1-3.1 1.4-6 1.1-8.6-.2-2.1 1-3.3 3.2-3.6z"
        fill="currentColor"
      />

      {/* head */}
      <path
        d="M32 8c-9.6 0-16.2 4.6-18 12.4-.8 3.4-.8 7 .1 11.2C15.9 41.2 22.6 47 32 47s16.1-5.8 17.9-15.4c.9-4.2.9-7.8.1-11.2C48.2 12.6 41.6 8 32 8z"
        fill="currentColor"
      />

      {/* brow wrinkles — what makes him read as a bulldog rather than any dog */}
      <path
        d="M24 19.5c1.6-1.1 3.4-1.6 5.4-1.5M40 19.5c-1.6-1.1-3.4-1.6-5.4-1.5M27 14.8c1.7-.7 3.4-1 5-1s3.3.3 5 1"
        stroke={accent}
        strokeWidth="1.8"
        strokeLinecap="round"
        opacity="0.75"
      />

      {/* eyes */}
      <circle cx="25" cy="25.5" r="3.3" fill="#ffffff" stroke={outline} strokeWidth="0.9" />
      <circle cx="39" cy="25.5" r="3.3" fill="#ffffff" stroke={outline} strokeWidth="0.9" />
      <circle cx="25.8" cy="26" r="1.7" fill={outline} />
      <circle cx="39.8" cy="26" r="1.7" fill={outline} />
      <circle cx="26.5" cy="25.2" r="0.6" fill="#ffffff" />
      <circle cx="40.5" cy="25.2" r="0.6" fill="#ffffff" />

      {/* muzzle */}
      <path
        d="M32 30.5c6.4 0 10.4 2.6 10.4 6.6S38 44.5 32 44.5s-10.4-3.4-10.4-7.4 4-6.6 10.4-6.6z"
        fill="#ffffff"
        stroke={outline}
        strokeWidth="1.1"
      />
      {/* nose */}
      <path
        d="M32 32.4c2 0 3.4 1.1 3.4 2.5s-1.5 2.4-3.4 2.4-3.4-1-3.4-2.4 1.4-2.5 3.4-2.5z"
        fill={outline}
      />
      {/* grin, slightly off-centre so he looks friendly rather than stern */}
      <path
        d="M32 37.3v2.1M32 39.4c-1.5 1.7-3.6 1.8-5.1.3M32 39.4c1.7 1.9 4 1.8 5.5-.2"
        stroke={outline}
        strokeWidth="1.7"
        strokeLinecap="round"
      />
      {/* one tooth */}
      <path d="M28.6 40.8h2.2v2a1.1 1.1 0 0 1-2.2 0v-2z" fill="#ffffff" stroke={outline} strokeWidth="0.7" />
    </svg>
  )
}
