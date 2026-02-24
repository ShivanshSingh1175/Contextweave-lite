/**
 * Progressive hint command - 3 levels of explanation
 */
import * as vscode from 'vscode';
import axios from 'axios';
import { MasteryManager } from '../storage/masteryManager';

export class ExplainCommand {
    private currentLevel: number = 1;
    private currentCode: string = '';
    private currentConcepts: string[] = [];

    constructor(
        private masteryManager: MasteryManager,
        private backendUrl: string
    ) {}

    async execute() {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor');
            return;
        }

        // Get selected code or current line
        const selection = editor.selection;
        let code: string;
        
        if (!selection.isEmpty) {
            code = editor.document.getText(selection);
        } else {
            // Get current function or class
            const position = editor.selection.active;
            const document = editor.document;
            code = this.getContextCode(document, position);
        }

        if (!code || code.trim().length === 0) {
            vscode.window.showErrorMessage('No code selected');
            return;
        }

        this.currentCode = code;
        this.currentLevel = 1;  // Start at level 1

        await this.showHint();
    }

    private async showHint() {
        try {
            // Get exam mode setting
            const config = vscode.workspace.getConfiguration('contextweave');
            const examMode = config.get<boolean>('examMode', false);
            const language = config.get<string>('language', 'en');

            // Show loading
            vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: `Getting Level ${this.currentLevel} hint...`,
                cancellable: false
            }, async () => {
                // Call backend
                const response = await axios.post(`${this.backendUrl}/v1/explain`, {
                    code: this.currentCode,
                    level: this.currentLevel,
                    lang: language,
                    exam_mode: examMode
                }, {
                    timeout: 30000
                });

                const data = response.data;
                this.currentConcepts = data.concepts || [];

                // Update mastery
                await this.masteryManager.updateMastery(this.currentConcepts, this.currentLevel);

                // Show hint in webview
                await this.showHintPanel(data);
            });

        } catch (error: any) {
            vscode.window.showErrorMessage(`Failed to get hint: ${error.message}`);
        }
    }

    private async showHintPanel(data: any) {
        const panel = vscode.window.createWebviewPanel(
            'contextweaveHint',
            `Level ${this.currentLevel} Hint`,
            vscode.ViewColumn.Beside,
            {
                enableScripts: true
            }
        );

        const nextLevelButton = data.next_level_available
            ? `<button onclick="nextLevel()">Next Level Hint →</button>`
            : '';

        const conceptTags = this.currentConcepts
            .map(c => `<span class="concept-tag">${c}</span>`)
            .join(' ');

        panel.webview.html = this.getHintHtml(data.hint, conceptTags, nextLevelButton);

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(async message => {
            if (message.command === 'nextLevel') {
                if (this.currentLevel < 3) {
                    this.currentLevel++;
                    await this.showHint();
                }
            } else if (message.command === 'gotIt') {
                // User understood - give bonus points
                await this.masteryManager.updateMastery(this.currentConcepts, 0);
                vscode.window.showInformationMessage('Great! Keep practicing! 🎉');
                panel.dispose();
            }
        });
    }

    private getHintHtml(hint: string, concepts: string, nextButton: string): string {
        return `<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: var(--vscode-font-family);
            padding: 20px;
            color: var(--vscode-foreground);
            background: var(--vscode-editor-background);
        }
        .hint-box {
            background: var(--vscode-editor-inactiveSelectionBackground);
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid var(--vscode-activityBarBadge-background);
        }
        .concept-tag {
            display: inline-block;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 12px;
            border-radius: 12px;
            margin: 4px;
            font-size: 12px;
        }
        button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 10px 5px;
            font-size: 14px;
        }
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .actions {
            margin-top: 20px;
            display: flex;
            gap: 10px;
        }
        h2 {
            color: var(--vscode-activityBarBadge-background);
        }
    </style>
</head>
<body>
    <h2>💡 Level ${this.currentLevel} Hint</h2>
    
    <div class="hint-box">
        ${hint.replace(/\n/g, '<br>')}
    </div>

    <div>
        <strong>Concepts:</strong><br>
        ${concepts}
    </div>

    <div class="actions">
        ${nextButton}
        <button onclick="gotIt()">I've Got It! ✓</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        function nextLevel() {
            vscode.postMessage({ command: 'nextLevel' });
        }
        
        function gotIt() {
            vscode.postMessage({ command: 'gotIt' });
        }
    </script>
</body>
</html>`;
    }

    private getContextCode(document: vscode.TextDocument, position: vscode.Position): string {
        // Simple heuristic: get surrounding 20 lines
        const startLine = Math.max(0, position.line - 10);
        const endLine = Math.min(document.lineCount - 1, position.line + 10);
        
        const range = new vscode.Range(startLine, 0, endLine, document.lineAt(endLine).text.length);
        return document.getText(range);
    }
}
