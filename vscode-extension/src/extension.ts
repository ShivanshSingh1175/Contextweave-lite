/**
 * ContextWeave Lite - VS Code Extension
 * Main extension entry point
 */
import * as vscode from 'vscode';
import { SidebarProvider } from './sidebarProvider';
import { analyzeFile } from './apiClient';

let sidebarProvider: SidebarProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('ContextWeave Lite extension activated');

    // Register sidebar provider
    sidebarProvider = new SidebarProvider(context.extensionUri);
    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            'contextweave.sidebarView',
            sidebarProvider
        )
    );

    // Register command: Explain this file
    const explainFileCommand = vscode.commands.registerCommand(
        'contextweave.explainFile',
        async () => {
            await handleExplainFile();
        }
    );

    context.subscriptions.push(explainFileCommand);
}

async function handleExplainFile() {
    const editor = vscode.window.activeTextEditor;
    
    if (!editor) {
        vscode.window.showErrorMessage('No active file to analyze');
        return;
    }

    const filePath = editor.document.uri.fsPath;
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(editor.document.uri);

    if (!workspaceFolder) {
        vscode.window.showErrorMessage('File is not in a workspace');
        return;
    }

    const repoPath = workspaceFolder.uri.fsPath;

    // Get selected code if any
    const selection = editor.selection;
    const selectedCode = !selection.isEmpty 
        ? editor.document.getText(selection) 
        : undefined;

    // Show sidebar
    await vscode.commands.executeCommand('contextweave.sidebarView.focus');

    // Show loading state
    sidebarProvider.showLoading(filePath);

    try {
        // Call backend API
        const result = await analyzeFile(repoPath, filePath, selectedCode);

        // Show results in sidebar
        sidebarProvider.showResult(result);

    } catch (error: any) {
        console.error('Error analyzing file:', error);
        
        let errorMessage = 'Failed to analyze file';
        
        if (error.code === 'ECONNREFUSED') {
            errorMessage = 'Cannot connect to backend. Make sure the backend server is running at ' + getBackendUrl();
        } else if (error.response) {
            errorMessage = `Backend error: ${error.response.data?.detail || error.response.statusText}`;
        } else if (error.message) {
            errorMessage = error.message;
        }

        vscode.window.showErrorMessage(errorMessage);
        sidebarProvider.showError(errorMessage);
    }
}

function getBackendUrl(): string {
    const config = vscode.workspace.getConfiguration('contextweave');
    return config.get('backendUrl', 'http://localhost:8000');
}

export function deactivate() {
    console.log('ContextWeave Lite extension deactivated');
}
