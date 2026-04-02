const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');
const scriptMatch = html.match(/<script>([\s\S]*?)<\/script>/);

if (scriptMatch) {
    const script = scriptMatch[1];
    try {
        new Function(script);
        console.log('Script is syntactically correct');
    } catch (e) {
        console.error('Syntax error found:');
        console.error(e.message);
        // Find line number
        const lines = script.split('\n');
        const errLine = e.lineNumber || (e.stack && e.stack.match(/:(\d+):(\d+)/) ? e.stack.match(/:(\d+):(\d+)/)[1] : 'unknown');
        console.error('Near line: ' + errLine);
    }
} else {
    console.error('No script tag found');
}
