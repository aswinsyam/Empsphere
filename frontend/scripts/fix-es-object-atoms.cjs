const fs = require('fs');
const path = require('path');

const target = path.join(__dirname, '..', 'node_modules', 'es-object-atoms', 'tsconfig.json');

if (!fs.existsSync(target)) {
  process.exit(0);
}

let content = fs.readFileSync(target, 'utf8');

if (content.includes('"ignoreDeprecations": "6.0"')) {
  content = content.replace(/\s*"ignoreDeprecations":\s*"6\.0"\s*,?\s*\n?/, '');
  content = content.replace(/,(\s*\n?\s*[}\]])/, '$1');
  fs.writeFileSync(target, content);
}
