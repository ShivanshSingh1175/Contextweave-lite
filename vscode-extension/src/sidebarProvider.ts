/**
 * Sidebar webview provider for displaying analysis results
 */
import * as vscode from 'vscode';
import { AnalysisResult } from './apiClient';

export class SidebarProvider implements vscode.WebviewViewProvider {
    private _view?: vscode.WebviewView;

    constructor(private readonly _extensionUri: vscode.Uri) {}

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getInitialHtml();

        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'openFile':
                    await this._openFile(message.path);
                    break;
            }
        });
    }

    public showLoading(filePath: string) {
        if (this._view) {
            this._view.webview.html = this._getLoadingHtml(filePath);
        }
    }

    public showResult(result: AnalysisResult) {
        if (this._view) {
            this._view.webview.html = this._getResultHtml(result);
        }
    }

    public showError(errorMessage: string) {
        if (this._view) {
            this._view.webview.html = this._getErrorHtml(errorMessage);
        }
    }

    private async _openFile(relativePath: string) {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            return;
        }

        const filePath = vscode.Uri.joinPath(workspaceFolders[0].uri, relativePath);
        
        try {
            const document = await vscode.workspace.openTextDocument(filePath);
            await vscode.window.showTextDocument(document);
        } catch (error) {
            vscode.window.showErrorMessage(`Could not open file: ${relativePath}`);
        }
    }

    private _getInitialHtml(): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContextWeave</title>
    <style>${this._getStyles()}</style>
</head>
<body>
    <div class="container">
        <div class="empty-state">
            <h2>✨ ContextWeave Lite</h2>
            <p>Open a file and run <strong>ContextWeave: Explain this file</strong> to see AI-powered insights.</p>
            <p class="hint">Use Command Palette (Ctrl+Shift+P / Cmd+Shift+P) to run the command.</p>
        </div>
    </div>
</body>
</html>`;
    }

    private _getLoadingHtml(filePath: string): string {
        const fileName = filePath.split(/[\\/]/).pop() || filePath;
        
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>${this._getStyles()}</style>
</head>
<body>
    <div class="container">
        <div class="loading">
            <div class="spinner"></div>
            <h3>Analyzing ${fileName}...</h3>
            <p>Reading Git history and calling LLM...</p>
        </div>
    </div>
</body>
</html>`;
    }

    private _getErrorHtml(errorMessage: string): string {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <style>${this._getStyles()}</style>
</head>
<body>
    <div class="container">
        <div class="error">
            <h3>❌ Error</h3>
            <p>${errorMessage}</p>
            <p class="hint">Make sure the backend server is running and the file is in a Git repository.</p>
        </div>
    </div>
</body>
</html>`;
    }

    private _getResultHtml(result: AnalysisResult): string {
        const decisionsHtml = result.decisions.length > 0
            ? result.decisions.map(d => `
                <div class="decision-item">
                    <h4>${this._escapeHtml(d.title)}</h4>
                    <p>${this._escapeHtml(d.description)}</p>
                    ${d.commits.length > 0 ? `
                        <div class="commits">
                            ${d.commits.map(c => `<span class="commit-badge">${c}</span>`).join(' ')}
                        </div>
                    ` : ''}
                </div>
            `).join('')
            : '<p class="no-data">No design decisions found in commit history.</p>';

        const relatedFilesHtml = result.related_files.length > 0
            ? result.related_files.map(rf => `
                <div class="related-file-item">
                    <a href="#" class="file-link" data-path="${this._escapeHtml(rf.path)}">
                        📄 ${this._escapeHtml(rf.path)}
                    </a>
                    <p class="file-reason">${this._escapeHtml(rf.reason)}</p>
                </div>
            `).join('')
            : '<p class="no-data">No related files found.</p>';

        const weirdCodeHtml = result.weird_code_explanation
            ? `
                <div class="section">
                    <h3>🤔 Selected Code Explanation</h3>
                    <div class="explanation-box">
                        <p>${this._escapeHtml(result.weird_code_explanation)}</p>
                    </div>
                </div>
            `
            : '';

        const mockWarning = result.metadata.mock_response
            ? `
                <div class="warning-box">
                    ⚠️ <strong>Mock Response:</strong> LLM not configured. Set LLM_API_KEY in backend to get AI-powered analysis.
                </div>
            `
            : '';

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Analysis Results</title>
    <style>${this._getStyles()}</style>
</head>
<body>
    <div class="container">
        ${mockWarning}
        
        <div class="section">
            <h3>📄 What this file does</h3>
            <div class="summary-box">
                <p>${this._escapeHtml(result.summary)}</p>
            </div>
        </div>

        <div class="section">
            <h3>🔍 Key design decisions</h3>
            ${decisionsHtml}
        </div>

        <div class="section">
            <h3>📚 You should also read</h3>
            ${relatedFilesHtml}
        </div>

        ${weirdCodeHtml}

        <div class="footer">
            <p>📊 Analyzed ${result.metadata.commits_analyzed} commits</p>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        document.querySelectorAll('.file-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const path = e.target.getAttribute('data-path');
                vscode.postMessage({ type: 'openFile', path });
            });
        });
    </script>
</body>
</html>`;
    }

    private _getStyles(): string {
        return `
            body {
                font-family: var(--vscode-font-family);
                font-size: var(--vscode-font-size);
                color: var(--vscode-foreground);
                background-color: var(--vscode-sideBar-background);
                padding: 0;
                margin: 0;
            }

            .container {
                padding: 16px;
            }

            .section {
                margin-bottom: 24px;
            }

            h2, h3 {
                margin-top: 0;
                margin-bottom: 12px;
                color: var(--vscode-foreground);
            }

            h3 {
                font-size: 14px;
                font-weight: 600;
                border-bottom: 1px solid var(--vscode-panel-border);
                padding-bottom: 8px;
            }

            h4 {
                margin: 0 0 4px 0;
                font-size: 13px;
                color: var(--vscode-textLink-foreground);
            }

            p {
                margin: 8px 0;
                line-height: 1.5;
            }

            .empty-state {
                text-align: center;
                padding: 40px 20px;
            }

            .empty-state h2 {
                margin-bottom: 16px;
            }

            .hint {
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
                font-style: italic;
            }

            .loading {
                text-align: center;
                padding: 40px 20px;
            }

            .spinner {
                border: 3px solid var(--vscode-panel-border);
                border-top: 3px solid var(--vscode-progressBar-background);
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .error {
                padding: 20px;
                background-color: var(--vscode-inputValidation-errorBackground);
                border: 1px solid var(--vscode-inputValidation-errorBorder);
                border-radius: 4px;
            }

            .warning-box {
                padding: 12px;
                background-color: var(--vscode-inputValidation-warningBackground);
                border: 1px solid var(--vscode-inputValidation-warningBorder);
                border-radius: 4px;
                margin-bottom: 16px;
                font-size: 12px;
            }

            .summary-box {
                padding: 12px;
                background-color: var(--vscode-editor-background);
                border-radius: 4px;
                border-left: 3px solid var(--vscode-textLink-foreground);
            }

            .explanation-box {
                padding: 12px;
                background-color: var(--vscode-editor-background);
                border-radius: 4px;
                border-left: 3px solid var(--vscode-charts-yellow);
            }

            .decision-item {
                padding: 12px;
                background-color: var(--vscode-editor-background);
                border-radius: 4px;
                margin-bottom: 12px;
            }

            .decision-item p {
                margin: 4px 0;
                font-size: 13px;
            }

            .commits {
                margin-top: 8px;
            }

            .commit-badge {
                display: inline-block;
                padding: 2px 8px;
                background-color: var(--vscode-badge-background);
                color: var(--vscode-badge-foreground);
                border-radius: 3px;
                font-size: 11px;
                font-family: monospace;
                margin-right: 4px;
            }

            .related-file-item {
                padding: 10px;
                background-color: var(--vscode-editor-background);
                border-radius: 4px;
                margin-bottom: 8px;
            }

            .file-link {
                color: var(--vscode-textLink-foreground);
                text-decoration: none;
                font-weight: 500;
                cursor: pointer;
            }

            .file-link:hover {
                text-decoration: underline;
            }

            .file-reason {
                margin: 4px 0 0 20px;
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
            }

            .no-data {
                color: var(--vscode-descriptionForeground);
                font-style: italic;
                font-size: 13px;
            }

            .footer {
                margin-top: 24px;
                padding-top: 12px;
                border-top: 1px solid var(--vscode-panel-border);
                font-size: 12px;
                color: var(--vscode-descriptionForeground);
            }
        `;
    }

    private _escapeHtml(text: string): string {
        const map: { [key: string]: string } = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
}
