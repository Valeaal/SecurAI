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
  const backendPath = path.join(__dirname, 'BackEnd');
  const venvPython = path.join(backendPath, 'venvTFG', 'bin', 'python3');

  flaskProcess = spawn(venvPython, ['run.py'], {
    cwd: backendPath,
    stdio: 'inherit',
    shell: true,
  });
}

function startNextFrontend() {
  const frontendPath = path.join(__dirname, 'FrontEnd/app');

  nextProcess = spawn('npm', ['run', 'dev'], {
    cwd: frontendPath,
    stdio: 'inherit',
    shell: true,
  });
}

app.whenReady().then(() => {
  startFlaskBackend(); // Inicia el backend silenciosamente
  setTimeout(() => {
    startNextFrontend(); // Después de 20 segundos, inicia el frontend
    createWindow(); // Después de iniciar el frontend, abre la ventana
  }, 25000); // Espera 20 segundos para el backend
});

app.on('window-all-closed', () => {
  if (flaskProcess) flaskProcess.kill();
  if (nextProcess) nextProcess.kill();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
