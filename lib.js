var BrowserPie = {
    installer: "https://browserpie.pages.dev/BrowserPie Installer.exe",
    port:5938
}

// import os; os.startfile(os.getcwd())

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
                throw new Error('Network response was not ok ' + response.statusText);
            }
            return response.text();
        })
        .catch(error => {
            return 'Error: ' + error.message;
        });
};
