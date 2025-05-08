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
    // icon: path.join(__dirname, 'icon.icns'),
    webPreferences: {
      contextIsolation: true,
    },
  });

  // Da tiempo a que Next.js levante el servidor
  setTimeout(() => {
    mainWindow.loadURL('http://localhost:3000');
  }, 15000); // Espera 15 segundos después de iniciar el frontend
}

function startFlaskBackend() {
  const isWin = process.platform === 'win32';
  const execName = isWin ? 'SecurAI.exe' : 'SecurAI';

  const backendDir = path.join(__dirname, 'BackEnd/dist');
  const execPath = path.join(backendDir, execName);

  flaskProcess = spawn(execPath, [], {
    cwd: backendDir,
    stdio: 'pipe',  // Cambiar a 'pipe' para poder capturar la salida
    shell: true,
  });

  // Captura los logs del proceso de Flask
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
  const frontendPath = path.join(__dirname, 'FrontEnd/app');

  nextProcess = spawn('npm', ['start'], {
    cwd: frontendPath,
    stdio: 'pipe',  // Cambiar a 'pipe' para poder capturar la salida
    shell: true,
  });

  // Captura los logs del proceso de Next.js
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
