const { BrowserWindow, app, ipcMain } = require("electron");

let win; // scoped to make varaible public
function createWindow() {
  win=new BrowserWindow({
    width: 1000,
    height: 680,
    frame: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });
  win.loadFile("index.html") // name of main .html file
  win.setMenuBarVisibility(false);
  win.on("closed", () => {
    win=null;
  });

}

let maximizeToggle=false; // toggle back to original window size if maximize is clicked again
ipcMain.on("manualMinimize", () => {
  win.minimize();
});
ipcMain.on("manualMaximize", () => {
  if (maximizeToggle) {
    win.unmaximize();
  } else {
    win.maximize();
  }
  maximizeToggle=!maximizeToggle; // flip the value of maximizeToggle
});
ipcMain.on("manualClose", () => {
  app.quit();
});

app.on("ready", createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});