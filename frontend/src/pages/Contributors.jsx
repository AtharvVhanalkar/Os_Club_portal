// Vite reads every JSON file in src/contributors at build time.
const files = import.meta.glob('../contributors/*.json', { eager: true, import: 'default' })

const contributors = Object.entries(files)
  .filter(([path]) => !path.split('/').pop().startsWith('_'))
  .map(([, data]) => data)
  .filter((person) => person?.name && person?.github)
  .sort((a, b) => a.name.localeCompare(b.name))

export default function Contributors() {
  return (
    <section className="page">
      <h1>Contributors</h1>
      <p className="muted">
        Anyone who has merged a pull request into this project. Want to be here? Add a file to{' '}
        <code>frontend/src/contributors/</code> and open a pull request.
      </p>

      <ul className="contributors">
        {contributors.map((person) => (
          <li key={person.github} className="contributor">
            <img
              className="contributor__avatar"
              src={`https://github.com/${person.github}.png?size=96`}
              alt=""
              width="48"
              height="48"
              loading="lazy"
            />
            <div>
              <p className="contributor__name">{person.name}</p>
              <p className="contributor__handle">
                <a href={`https://github.com/${person.github}`} target="_blank" rel="noreferrer">
                  @{person.github}
                </a>
                {person.year && <span className="muted">, {person.year}</span>}
              </p>
              {person.message && <p className="contributor__message">{person.message}</p>}
              {person.interests?.length > 0 && (
                <ul className="interests" aria-label="Interests">
                  {person.interests.map((interest) => (
                    <li key={interest}>{interest}</li>
                  ))}
                </ul>
              )}
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
