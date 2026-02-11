/**
 * ContextWeave Lite - VS Code Extension
 * Main extension entry point
 */
import * as vscode from 'vscode';
import { BackendManager } from './backendManager';
import { SidebarProvider } from './sidebarProvider';
import { analyzeFile } from './apiClient';

let sidebarProvider: SidebarProvider;
let backendManager: BackendManager;

export async function activate(context: vscode.ExtensionContext) {
    console.log('ContextWeave Lite extension activated');

    // Start backend
    backendManager = new BackendManager(context);
    // Don't await this so extension activation isn't blocked, but fire it off
    backendManager.start().catch(err => console.error(err));

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
        vscode.window.showErrorMessage('ContextWeave: No active file to analyze. Please open a file first.');
        return;
    }

    const filePath = editor.document.uri.fsPath;
    const workspaceFolder = vscode.workspace.getWorkspaceFolder(editor.document.uri);

    if (!workspaceFolder) {
        vscode.window.showErrorMessage('ContextWeave: File is not in a workspace. Please open a folder or workspace.');
        return;
    }

    const repoPath = workspaceFolder.uri.fsPath;

    // Get selected code if any
    const selection = editor.selection;
    const selectedCode = !selection.isEmpty
        ? editor.document.getText(selection)
        : undefined;

    // Show sidebar
    try {
        await vscode.commands.executeCommand('contextweave.sidebarView.focus');
    } catch (error) {
        console.error('Error focusing sidebar:', error);
        // Continue anyway - sidebar might already be visible
    }

    // Show loading state
    sidebarProvider.showLoading(filePath);

    try {
        console.log(`Analyzing file: ${filePath}`);
        console.log(`Repository: ${repoPath}`);
        console.log(`Selected code: ${selectedCode ? selectedCode.length + ' chars' : 'none'}`);

        // Call backend API
        const result = await analyzeFile(repoPath, filePath, selectedCode);

        console.log('Analysis complete:', result);

        // Show results in sidebar
        sidebarProvider.showResult(result);

    } catch (error: any) {
        console.error('Error analyzing file:', error);

        let errorMessage = 'Failed to analyze file';
        let suggestions: string[] = [];

        if (error.code === 'ECONNREFUSED') {
            errorMessage = `Cannot connect to backend server at ${getBackendUrl()}`;
            suggestions = [
                'Make sure the backend is running: cd backend && python main.py',
                'Check that the backend URL is correct in VS Code settings',
                'Verify no firewall is blocking localhost:8000'
            ];
        } else if (error.code === 'ETIMEDOUT') {
            errorMessage = 'Request timed out after 60 seconds';
            suggestions = [
                'Local LLMs can be slow on first run',
                'The file or repository might be too large',
                'Try again with a smaller file or faster model'
            ];
        } else if (error.response) {
            // Backend returned an error
            const status = error.response.status;
            const detail = error.response.data?.detail || error.response.statusText;

            if (status === 400) {
                errorMessage = `Invalid request: ${detail}`;
                suggestions = [
                    'Make sure the file is in a Git repository',
                    'Check that the file exists and is tracked by Git',
                    'Try running: git status'
                ];
            } else if (status === 503) {
                errorMessage = `Service unavailable: ${detail}`;
                suggestions = [
                    'If using Ollama: Start with "ollama serve" then "ollama pull llama3"',
                    'If using LocalAI: Start with "docker run -p 8080:8080 localai/localai"',
                    'Or switch to Groq in settings and configure LLM_API_KEY in backend/.env'
                ];
            } else if (status === 500) {
                errorMessage = `Backend error: ${detail}`;
                suggestions = [
                    'Check backend logs for details',
                    'The file might have issues (binary, too large, etc.)',
                    'Try with a different file'
                ];
            } else {
                errorMessage = `Backend error (${status}): ${detail}`;
            }
        } else if (error.message) {
            errorMessage = error.message;
        }

        // Show error in VS Code notification
        const fullMessage = suggestions.length > 0
            ? `${errorMessage}\n\nSuggestions:\n${suggestions.map(s => `• ${s}`).join('\n')}`
            : errorMessage;

        vscode.window.showErrorMessage(`ContextWeave: ${errorMessage}`);

        // Show error in sidebar with suggestions
        sidebarProvider.showError(errorMessage, suggestions);
    }
}

function getBackendUrl(): string {
    const config = vscode.workspace.getConfiguration('contextweave');
    return config.get('backendUrl', 'http://localhost:8000');
}

export function deactivate() {
    console.log('ContextWeave Lite extension deactivated');
    if (backendManager) {
        backendManager.stop();
    }
}
