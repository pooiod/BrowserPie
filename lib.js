var BrowserPie = {
    installer: "https://browserpie.pages.dev/BrowserPie Installer.exe",
    port:5938
}

/** Example script (opens file explorer)
var BrowserPieScript = document.createElement("script");
BrowserPieScript.src = "https://browserpie.pages.dev/lib.js";
BrowserPieScript.onload = () => {
    BrowserPie.isInstalled().then(console.log);
    BrowserPie.run("import os; os.startfile(os.getcwd())").then(console.log);
};
document.head.appendChild(BrowserPieScript);
*/

BrowserPie.isInstalled = function() {
    return fetch('https://localhost:'+BrowserPie.port+'/')
        .then(response => {
            if (!response.ok) {
                return false;
            }
            return !!response.text();
        })
        .catch(error => {
            return false;
        });
};

BrowserPie.isAllowed = function() {
    return fetch('https://localhost:'+BrowserPie.port+'/run?py=' + encodeURIComponent('"true"'))
        .then(response => {
            if (!response.ok) {
                return false;
            }
            return !!response.text();
        })
        .catch(error => {
            return false;
        });
};

BrowserPie.run = function(code) {
    return fetch('https://localhost:'+BrowserPie.port+'/run?py=' + encodeURIComponent(code))
        .then(response => {
            if (!response.ok) {
                throw new Error('BrowserPie said ' + response.statusText);
            }
            return response.text();
        })
        .catch(error => {
            return 'Error: ' + error.message;
        });
};
