const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn, exec } = require('child_process');
const fs = require('fs');
const https = require('https');
const os = require('os');

let mainWindow;
let flaskProcess;
let nextProcess;

const isWin = process.platform === 'win32';
const isMac = process.platform === 'darwin';

// Sobrescribir console.log y console.error para macOS con logger nativo
if (isMac) {
  const originalLog = console.log;
  const originalError = console.error;

  console.log = (...args) => {
    const message = args.join(' ').replace(/"/g, '\\"');
    exec(`logger "SecurAI: ${message}"`);
    originalLog(...args);
  };

  console.error = (...args) => {
    const message = args.join(' ').replace(/"/g, '\\"');
    exec(`logger "SecurAI ERROR: ${message}"`);
    originalError(...args);
  };
} else {
  // En Windows dejamos console.log y error normales pero sin más cambios
  // Si quieres evitar logs en consola Windows puedes redefinir aquí
}

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
  const execName = isWin ? 'SecurAI.exe' : 'SecurAI';
  const backendDir = path.join(process.resourcesPath, 'app', 'BackEnd', 'dist');
  const execPath = path.join(backendDir, execName);

  flaskProcess = spawn(execPath, [], {
    cwd: backendDir,
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: false,
  });

  flaskProcess.stdout.on('data', (data) => {
    console.log(`Flask: ${data.toString().trim()}`);
  });

  flaskProcess.stderr.on('data', (data) => {
    console.error(`Flask ERROR: ${data.toString().trim()}`);
  });

  flaskProcess.on('error', (err) => {
    console.error('❌ Error al lanzar el backend:', err);
  });

  flaskProcess.on('exit', (code) => {
    console.log(`ℹ️ Backend finalizó con código ${code}`);
  });
}

function startNextFrontend() {
  const frontendPath = path.join(process.resourcesPath, 'app', 'FrontEnd', 'app');
  const nextBinary = isWin
    ? path.join(frontendPath, 'node_modules', 'next', 'dist', 'bin', 'next.cmd')
    : path.join(frontendPath, 'node_modules', 'next', 'dist', 'bin', 'next');

  nextProcess = spawn(nextBinary, ['start'], {
    cwd: frontendPath,
    stdio: ['ignore', 'pipe', 'pipe'],
    shell: isWin,
  });

  nextProcess.stdout.on('data', (data) => {
    console.log(`Next.js: ${data.toString().trim()}`);
  });

  nextProcess.stderr.on('data', (data) => {
    console.error(`Next.js ERROR: ${data.toString().trim()}`);
  });

  nextProcess.on('error', (err) => {
    console.error('❌ Error al lanzar el frontend:', err);
  });

  nextProcess.on('exit', (code) => {
    console.log(`ℹ️ Frontend finalizó con código ${code}`);
  });
}

// Resto de funciones Npcap sin cambios...

// app.whenReady y demás (igual que en tu código original)

app.whenReady().then(() => {
  if (!isWin) {
    startFlaskBackend();
    setTimeout(() => {
      startNextFrontend();
      setTimeout(createWindow, 20000);
    }, 35000);
    return;
  }

  isNpcapInstalled((installed) => {
    if (installed) {
      startFlaskBackend();
      setTimeout(() => {
        startNextFrontend();
        setTimeout(createWindow, 20000);
      }, 35000);
    } else {
      console.log('⬇️ Npcap no está instalado. Descargando...');
      const installerPath = path.join(os.tmpdir(), 'npcap_installer.exe');

      downloadNpcapInstaller(installerPath, (err) => {
        if (err) {
          console.error('❌ Error al descargar Npcap:', err);
          app.quit();
          return;
        }

        promptNpcapInstallation(installerPath, () => {
          startFlaskBackend();
          setTimeout(() => {
            startNextFrontend();
            setTimeout(createWindow, 20000);
          }, 35000);
        });
      });
    }
  });
});

app.on('window-all-closed', () => {
  if (flaskProcess) flaskProcess.kill();
  if (nextProcess) nextProcess.kill();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
