const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let flaskProcess;
let nextProcess;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      contextIsolation: true,
    },
  });

  setTimeout(() => {
    mainWindow.loadURL('http://localhost:3000');
  }, 15000);
}

function startFlaskBackend() {
  const isWin = process.platform === 'win32';
  const execName = isWin ? 'SecurAI.exe' : 'SecurAI';

  // Usar process.resourcesPath para aplicaciones empaquetadas
  const backendDir = path.join(process.resourcesPath, 'app', 'BackEnd', 'dist');
  const execPath = path.join(backendDir, execName);

  flaskProcess = spawn(execPath, [], {
    cwd: backendDir, // IMPORTANTE: especificar cwd explícitamente
    stdio: 'pipe',
    shell: false,
  });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask ERROR: ${data}`);
  });

  flaskProcess.on('error', (err) => {
    console.error('❌ Error al lanzar el backend:', err);
  });

  flaskProcess.on('exit', (code) => {
    console.log(`ℹ️ Backend finalizó con código ${code}`);
  });
}

function startNextFrontend() {
  const isWin = process.platform === 'win32';
  const frontendPath = path.join(process.resourcesPath, 'app', 'FrontEnd', 'app');
  const nextBinary = isWin
    ? path.join(frontendPath, 'node_modules', '.bin', 'next.cmd')
    : path.join(frontendPath, 'node_modules', '.bin', 'next');

  nextProcess = spawn(nextBinary, ['start'], {
    cwd: frontendPath,
    stdio: 'pipe',
    shell: true
  });

  nextProcess.stdout.on('data', (data) => {
    console.log(`Next.js: ${data}`);
  });

  nextProcess.stderr.on('data', (data) => {
    console.error(`Next.js ERROR: ${data}`);
  });

  nextProcess.on('error', (err) => {
    console.error('❌ Error al lanzar el frontend:', err);
  });

  nextProcess.on('exit', (code) => {
    console.log(`ℹ️ Frontend finalizó con código ${code}`);
  });
}


app.whenReady().then(() => {
  startFlaskBackend();

  setTimeout(() => {
    startNextFrontend();

    setTimeout(() => {
      createWindow();
    }, 20000);
  }, 35000);
});

app.on('window-all-closed', () => {
  if (flaskProcess) flaskProcess.kill();
  if (nextProcess) nextProcess.kill();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
