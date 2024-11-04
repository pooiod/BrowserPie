// BrowserPie - run python from the browser

(function(Scratch) {
    'use strict';
  
    if (!Scratch.extensions.unsandboxed) {
        throw new Error('This extension must run unsandboxed');
    }

    class BrowserPie {
        constructor() {
            this.port = 5938;
        }
    
        getInfo() {
            return {
                id: 'BrowserPie',
                name: 'Python',
                color1: "#3a709f",
                color2: '#ffd344',
                blocks: [
                    {
                        opcode: 'isInstalled',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'Is BrowserPie installed',
                        disableMonitor: true
                    },
                    {
                        opcode: 'isAllowed',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'Can run python',
                        disableMonitor: true
                    },
                    {
                        opcode: 'run2',
                        blockType: Scratch.BlockType.REPORTER,
                        text: 'Run python [CODE]',
                        disableMonitor: true,
                        arguments: {
                            CODE: {
                                type: Scratch.ArgumentType.STRING,
                                defaultValue: '9 + 10',
                            },
                        }
                    },
                    {
                        opcode: 'run',
                        blockType: Scratch.BlockType.COMMAND,
                        text: 'Run python [CODE]',
                        arguments: {
                            CODE: {
                            type: Scratch.ArgumentType.STRING,
                            defaultValue: 'import ctypes; ctypes.windll.user32.MessageBoxW(0, "Hello, World!", "Alert", 1)',
                            },
                        }
                    },
                    {
                        opcode: 'downloadBrowserPie',
                        blockType: Scratch.BlockType.COMMAND,
                        text: 'Download BrowserPie'
                    }
                ]
            };
        }

        async isInstalled() {
            return Scratch.fetch('https://localhost:'+this.port+'/')
            .then(response => {
                if (!response.ok) {
                    return false;
                }
                return !!response.text();
            })
            .catch(_ => {
                return false;
            });
        }

        async isAllowed() {
            return Scratch.fetch('https://localhost:'+this.port+'/run?py=' + encodeURIComponent('"true"'))
                .then(response => {
                    if (!response.ok) {
                        return false;
                    }
                    return !!response.text();
                })
                .catch(_ => {
                    return false;
                });
        }
      
        async run2(args) {this.run(args)}
        async run({CODE}) {
            return Scratch.fetch('https://localhost:'+this.port+'/run?py=' + encodeURIComponent(CODE))
            .then(response => {
                if (!response.ok) {
                    throw new Error('Script not allowed: ' + response.statusText);
                }
                return Scratch.Cast.toString(response.text());
            })
            .catch(error => {
                return 'Error executing code: ' + error.message;
            });
        }

        setPort({PORT}) {
            this.port = PORT;
        }

        downloadBrowserPie() {
            window.open("https://browserpie.pages.dev/BrowserPie Installer.exe");
        }
    }
    Scratch.extensions.register(new BrowserPie());
})(Scratch);
  