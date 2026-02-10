import * as vscode from 'vscode';
import * as cp from 'child_process';
import * as path from 'path';
import axios from 'axios';
import * as fs from 'fs';

export class BackendManager {
    private process: cp.ChildProcess | undefined;
    private outputChannel: vscode.OutputChannel;
    private isRunning: boolean = false;
    private backendUrl: string = 'http://localhost:8000';

    constructor(private context: vscode.ExtensionContext) {
        this.outputChannel = vscode.window.createOutputChannel('ContextWeave Backend');
    }

    async start(): Promise<void> {
        if (await this.checkHealth()) {
            this.outputChannel.appendLine('Backend already running.');
            this.isRunning = true;
            return;
        }

        this.outputChannel.appendLine('Starting ContextWeave backend...');
        
        // Assume backend is sibling to vscode-extension in dev environment
        // In production, you might bundle the backend or download it
        let backendPath = path.join(this.context.extensionUri.fsPath, '..', 'backend');
        
        // If that doesn't exist, try resolving from workspace root if available
        if (!fs.existsSync(backendPath)) {
            // Check if we are in the monorepo root
            if (vscode.workspace.workspaceFolders && vscode.workspace.workspaceFolders.length > 0) {
                const root = vscode.workspace.workspaceFolders[0].uri.fsPath;
                if (fs.existsSync(path.join(root, 'backend'))) {
                    backendPath = path.join(root, 'backend');
                }
            }
        }

        if (!fs.existsSync(backendPath)) {
             this.outputChannel.appendLine(`Could not find backend directory at ${backendPath}`);
             return;
        }

        const mainPyPath = path.join(backendPath, 'main.py');
        
        // Find python
        let pythonPath = 'python'; // Default fallback
        const venvPath = process.platform === 'win32' 
            ? path.join(backendPath, 'venv', 'Scripts', 'python.exe')
            : path.join(backendPath, 'venv', 'bin', 'python');
            
        if (fs.existsSync(venvPath)) {
            pythonPath = venvPath;
            this.outputChannel.appendLine(`Using venv python: ${pythonPath}`);
        } else {
             this.outputChannel.appendLine(`Using system python: ${pythonPath}`);
        }

        try {
            this.process = cp.spawn(pythonPath, [mainPyPath], {
                cwd: backendPath,
                env: { ...process.env, PYTHONUNBUFFERED: '1' }
            });

            this.process.stdout?.on('data', (data) => {
                this.outputChannel.append(`[Backend]: ${data}`);
            });

            this.process.stderr?.on('data', (data) => {
                this.outputChannel.append(`[Backend Error]: ${data}`);
            });
            
            this.process.on('error', (err) => {
                 this.outputChannel.appendLine(`Failed to start backend: ${err.message}`);
                 vscode.window.showErrorMessage(`ContextWeave: Failed to start backend. ${err.message}`);
            });

            // Wait for it to be ready
            let retries = 0;
            while (retries < 15) {
                await new Promise(r => setTimeout(r, 1000));
                if (await this.checkHealth()) {
                    this.isRunning = true;
                    this.outputChannel.appendLine('Backend started successfully.');
                    vscode.window.setStatusBarMessage('ContextWeave Backend: Running', 3000);
                    return;
                }
                retries++;
            }
            
            this.outputChannel.appendLine('Backend failed to respond after startup.');

        } catch (error: any) {
            this.outputChannel.appendLine(`Error spawning backend: ${error.message}`);
        }
    }

    async stop() {
        if (this.process) {
            this.process.kill();
            this.process = undefined;
            this.isRunning = false;
            this.outputChannel.appendLine('Backend stopped.');
        }
    }

    private async checkHealth(): Promise<boolean> {
        try {
            await axios.get(this.backendUrl);
            return true;
        } catch (e) {
            return false;
        }
    }
}
