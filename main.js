const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const { spawn, execFile } = require('child_process');
const fs = require('fs');
const https = require('https');
const os = require('os');
const log = require('electron-log');


// 🛠 Fix para entorno PATH en macOS
if (process.platform === 'darwin') {
  const fix = require('fix-path');
  fix();
}


// Configuración de electron-log
const logDir = app.getPath('logs');
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}
log.transports.file.resolvePath = () => path.join(logDir, 'main.log');
log.transports.file.level = 'info';
log.transports.console.level = false;

console.log = log.info;
console.error = log.error;
console.warn = log.warn;
console.info = log.info;

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

  // Ruta absoluta al ejecutable node embebido según SO
  const embeddedNode = isWin
    ? path.join(process.resourcesPath, 'node', 'node.exe')
    : path.join(process.resourcesPath, 'node', 'bin', 'node');

  // Ejecutable next (script JS)
  const nextScript = path.join(frontendPath, 'node_modules', 'next', 'dist', 'bin', 'next');

  nextProcess = spawn(embeddedNode, [nextScript, 'start'], {
    cwd: frontendPath,
    stdio: 'pipe',
    shell: false, // mejor false al usar ruta absoluta de node
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


function isNpcapInstalled(callback) {
  const checkCommand = 'reg query "HKLM\\SOFTWARE\\Npcap"';
  execFile('cmd', ['/c', checkCommand], (error) => {
    callback(!error);
  });
}

function downloadNpcapInstaller(destination, callback) {
  const url = 'https://npcap.com/dist/npcap-1.78.exe';
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

function promptNpcapInstallation(installerPath, callback) {
  const options = {
    type: 'info',
    buttons: ['Instalar ahora', 'Cancelar'],
    title: 'Npcap requerido',
    message: 'Npcap es necesario para capturar paquetes en Windows.',
    detail: 'Se va a abrir el instalador de Npcap. Completa la instalación manualmente y pulsa "Finalizar" en el instalador para continuar.',
  };

  dialog.showMessageBox(null, options).then((result) => {
    if (result.response === 0) {
      installNpcap(installerPath, callback);
    } else {
      console.warn('⚠️ El usuario canceló la instalación de Npcap. Continuando sin él...');
      callback();
    }
  });
}

function installNpcap(installerPath, callback) {
  const child = spawn(installerPath, [], {
    stdio: 'inherit',
    shell: true,
  });

  child.on('exit', (code) => {
    if (code === 0) {
      console.log('✅ Npcap instalado correctamente');
      callback();
    } else {
      console.error(`❌ Instalación de Npcap falló con código ${code}`);
      app.quit();
    }
  });
}

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
