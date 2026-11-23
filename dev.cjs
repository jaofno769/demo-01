const concurrently = require('concurrently')

// Watch Python separately because Uvicorn's Windows reloader sends Ctrl+C to the shared console.
const { result } = concurrently([
  {
    name: 'api',
    command: 'node node_modules/nodemon/bin/nodemon.js --watch . --ext py --ignore frontend/ --ignore .venv/ --exec ".venv\\Scripts\\python.exe -B -m uvicorn main:app --host 127.0.0.1 --port 8000"',
  },
  {
    name: 'web',
    command: 'node node_modules/vite/bin/vite.js frontend --host 127.0.0.1 --port 5173 --strictPort',
  },
], {
  cwd: __dirname,
  prefixColors: ['blue', 'green'],
  killOthersOn: ['success', 'failure'],
})

result.catch(() => {
  process.exitCode = 1
})
