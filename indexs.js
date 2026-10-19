const { spawn, execSync } = require('child_process');
function run(c){ try{ execSync(c,{stdio:'inherit'}); return true;}catch{ console.log("[Skip] "+c); return false; } }

console.log("[System] Mencoba download pip manual...");

// download get-pip.py
run('curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py || wget -q https://bootstrap.pypa.io/get-pip.py -O /tmp/get-pip.py');
run('python3 /tmp/get-pip.py --break-system-packages');
run('python3 -m pip install --break-system-packages -r requirements.txt');
run('python3 -m pip install --break-system-packages discord.py aiohttp requests');

console.log("[System] Menjalankan Jekkie V15 pakai Python...");
let py = spawn('python3', ['main.py'], {stdio:'inherit'});
py.on('close', c => process.exit(c));
py.on('error', () => {
  let py2 = spawn('python', ['main.py'], {stdio:'inherit'});
  py2.on('close', c => process.exit(c));
});
