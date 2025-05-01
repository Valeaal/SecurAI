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
    //icon: path.join(__dirname, 'icon.icns'),
    webPreferences: {
      contextIsolation: true,
    },
  });

  // Da tiempo a que Next.js levante el servidor
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:3000');
  }, 15000); // Espera 10 segundos después de iniciar el frontend
}

function startFlaskBackend() {
  const isWin = process.platform === 'win32';
  const execName = isWin ? 'SecurAI.exe' : './SecurAI';

  const backendExecutableDir = path.join(__dirname, 'BackEnd', 'dist', 'run', '_internal');
  const execPath = path.join(backendExecutableDir, execName);

  flaskProcess = spawn(execPath, [], {
    cwd: backendExecutableDir,
    stdio: 'inherit',
    shell: true
  });
}

function startNextFrontend() {
  const frontendPath = path.join(__dirname, 'FrontEnd/app');

  nextProcess = spawn('npm', ['start'], {
    cwd: frontendPath,
    stdio: 'inherit',
    shell: true,
  });
}

app.whenReady().then(() => {
  // Paso 1: Inicia backend
  startFlaskBackend();

  // Paso 2: Espera 35 segundos
  setTimeout(() => {
    // Paso 3: Inicia frontend
    startNextFrontend();

    // Paso 4: Espera 20 segundos más
    setTimeout(() => {
      // Paso 5: Crea la ventana
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
