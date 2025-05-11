const { app, BrowserWindow } = require('electron');
const path = require('path');
const { spawn, execFile } = require('child_process');
const fs = require('fs');
const https = require('https');
const os = require('os');

let mainWindow;
let flaskProcess;
let nextProcess;

const isWin = process.platform === 'win32';

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

// Verifica si Npcap está instalado usando el Registro de Windows
function isNpcapInstalled(callback) {
  const checkCommand = 'reg query "HKLM\\SOFTWARE\\Npcap"';
  execFile('cmd', ['/c', checkCommand], (error) => {
    callback(!error); // instalado si no hay error
  });
}

// Descarga el instalador de Npcap
function downloadNpcapInstaller(destination, callback) {
  const url = 'https://npcap.com/dist/npcap-1.78.exe'; // actualiza a la versión estable si cambia
  const file = fs.createWriteStream(destination);

  https.get(url, (response) => {
    if (response.statusCode !== 200) {
      callback(new Error(`Fallo en la descarga: ${response.statusCode}`));
      return;
    }

    response.pipe(file);
    file.on('finish', () => {
      file.close(callback);
    });
  }).on('error', (err) => {
    fs.unlink(destination, () => callback(err));
  });
}

// Instala Npcap de forma silenciosa
function installNpcap(installerPath, callback) {
  const child = spawn(installerPath, args, {
    stdio: 'inherit',
    shell: true
  });

  child.on('exit', (code) => {
    if (code === 0) {
      console.log('✅ Npcap instalado correctamente');
      callback();
    } else {
      console.error(`❌ Npcap falló con código ${code}`);
      app.quit();
    }
  });
}

app.whenReady().then(() => {
  if (!isWin) {
    // macOS o Linux: arranque directo
    startFlaskBackend();
    setTimeout(() => {
      startNextFrontend();
      setTimeout(createWindow, 20000);
    }, 35000);
    return;
  }

  // Windows: comprobar Npcap
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

        installNpcap(installerPath, () => {
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
