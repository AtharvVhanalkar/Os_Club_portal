// Validates contributor files so mistakes are caught in CI, not in review.
// Run with: npm run check:contributors
import { readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'

const dir = new URL('../src/contributors/', import.meta.url).pathname
const errors = []

for (const file of readdirSync(dir)) {
  if (!file.endsWith('.json') || file.startsWith('_')) continue
  const path = join(dir, file)
  let data
  try {
    data = JSON.parse(readFileSync(path, 'utf8'))
  } catch (err) {
    errors.push(`${file}: is not valid JSON (${err.message})`)
    continue
  }
  if (!data.name?.trim()) errors.push(`${file}: "name" is required`)
  if (!data.github?.trim()) errors.push(`${file}: "github" is required`)
  if (data.github && file !== `${data.github.toLowerCase()}.json` && file !== 'osc-maintainers.json') {
    errors.push(`${file}: file name must match your GitHub username, e.g. ${data.github.toLowerCase()}.json`)
  }
  if (data.interests && !Array.isArray(data.interests)) errors.push(`${file}: "interests" must be a list`)
}

if (errors.length) {
  console.error('Contributor file problems:\n' + errors.map((e) => `  - ${e}`).join('\n'))
  process.exit(1)
}
console.log('All contributor files look good.')
