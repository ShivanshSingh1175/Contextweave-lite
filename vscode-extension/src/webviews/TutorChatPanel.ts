/**
 * Tutor Chat Panel - Context-aware tutoring interface
 */
import * as vscode from 'vscode';
import axios from 'axios';
import { MasteryManager } from '../storage/masteryManager';

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

export class TutorChatPanel {
    public static currentPanel: TutorChatPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];
    private messages: ChatMessage[] = [];

    private constructor(
        panel: vscode.WebviewPanel,
        extensionUri: vscode.Uri,
        private masteryManager: MasteryManager,
        private backendUrl: string
    ) {
        this._panel = panel;
        this._panel.webview.html = this._getHtmlForWebview(this._panel.webview);

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
            async message => {
                switch (message.command) {
                    case 'sendMessage':
                        await this.handleUserMessage(message.text);
                        break;
                    case 'useSelection':
                        await this.handleUseSelection();
                        break;
                    case 'explainInHindi':
                        await this.handleLanguageSwitch('hi');
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri, masteryManager: MasteryManager, backendUrl: string) {
        const column = vscode.ViewColumn.Two;

        if (TutorChatPanel.currentPanel) {
            TutorChatPanel.currentPanel._panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            'contextweaveChat',
            'ContextWeave Tutor',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        TutorChatPanel.currentPanel = new TutorChatPanel(panel, extensionUri, masteryManager, backendUrl);
    }

    private async handleUserMessage(text: string) {
        this.messages.push({ role: 'user', content: text });
        this.updateChat();

        try {
            const editor = vscode.window.activeTextEditor;
            const config = vscode.workspace.getConfiguration('contextweave');
            const examMode = config.get<boolean>('examMode', false);

            const context = {
                current_file: editor?.document.fileName,
                mastery: this.masteryManager.getProfile().topics,
                recent_concepts: this.masteryManager.getDueTopics()
            };

            const response = await axios.post(`${this.backendUrl}/v1/chat`, {
                messages: this.messages,
                context: context,
                exam_mode: examMode
            }, {
                timeout: 30000
            });

            this.messages.push({ role: 'assistant', content: response.data.message });
            this.updateChat();

        } catch (error: any) {
            vscode.window.showErrorMessage(`Chat failed: ${error.message}`);
            this.messages.push({
                role: 'assistant',
                content: 'Sorry, I encountered an error. Please try again.'
            });
            this.updateChat();
        }
    }

    private async handleUseSelection() {
        const editor = vscode.window.activeTextEditor;
        if (!editor || editor.selection.isEmpty) {
            vscode.window.showWarningMessage('No code selected');
            return;
        }

        const selectedCode = editor.document.getText(editor.selection);
        const message = `Explain this code:\n\`\`\`\n${selectedCode}\n\`\`\``;
        
        this._panel.webview.postMessage({
            command: 'insertMessage',
            text: message
        });
    }

    private async handleLanguageSwitch(lang: string) {
        const config = vscode.workspace.getConfiguration('contextweave');
        await config.update('language', lang, vscode.ConfigurationTarget.Global);
        
        vscode.window.showInformationMessage(
            lang === 'hi' ? 'Language switched to Hindi' : 'Language switched to English'
        );
    }

    private updateChat() {
        this._panel.webview.postMessage({
            command: 'updateMessages',
            messages: this.messages
        });
    }

    public dispose() {
        TutorChatPanel.currentPanel = undefined;
        this._panel.dispose();
        while (this._disposables.length) {
            const disposable = this._disposables.pop();
            if (disposable) {
                disposable.dispose();
            }
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ContextWeave Tutor</title>
    <style>
        body {
            padding: 0;
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            color: var(--vscode-foreground);
            font-family: var(--vscode-font-family);
        }
        
        .header {
            padding: 12px;
            background: var(--vscode-editor-background);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .header button {
            padding: 6px 12px;
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .header button:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
        
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        
        .message {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 6px;
            max-width: 85%;
        }
        
        .message.user {
            background: var(--vscode-input-background);
            margin-left: auto;
            text-align: right;
        }
        
        .message.assistant {
            background: var(--vscode-editor-inactiveSelectionBackground);
        }
        
        .message-role {
            font-weight: bold;
            margin-bottom: 6px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        
        .message-content {
            line-height: 1.5;
            white-space: pre-wrap;
        }
        
        .input-area {
            padding: 12px;
            background: var(--vscode-editor-background);
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 8px;
        }
        
        #messageInput {
            flex: 1;
            padding: 8px;
            background: var(--vscode-input-background);
            color: var(--vscode-input-foreground);
            border: 1px solid var(--vscode-input-border);
            border-radius: 3px;
            font-family: var(--vscode-font-family);
            font-size: 13px;
        }
        
        #sendButton {
            padding: 8px 16px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 3px;
            cursor: pointer;
            font-weight: 500;
        }
        
        #sendButton:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--vscode-descriptionForeground);
        }
        
        .empty-state h3 {
            margin-bottom: 8px;
        }
        
        code {
            background: var(--vscode-textCodeBlock-background);
            padding: 2px 6px;
            border-radius: 3px;
            font-family: var(--vscode-editor-font-family);
        }
    </style>
</head>
<body>
    <div class="header">
        <button onclick="useSelection()">📋 Use Selection</button>
        <button onclick="explainInHindi()">🇮🇳 Explain in Hindi</button>
        <button onclick="firstHintOnly()">💡 First Hint Only</button>
    </div>
    
    <div class="messages" id="messages">
        <div class="empty-state">
            <h3>👋 Hi! I'm your ContextWeave Tutor</h3>
            <p>Ask me anything about your code!</p>
            <p style="font-size: 12px; margin-top: 16px;">
                I'll guide you with hints, not full solutions.<br>
                Select code and click "Use Selection" to get started.
            </p>
        </div>
    </div>
    
    <div class="input-area">
        <input 
            type="text" 
            id="messageInput" 
            placeholder="Ask a question about your code..."
            onkeypress="handleKeyPress(event)"
        />
        <button id="sendButton" onclick="sendMessage()">Send</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        window.addEventListener('message', event => {
            const message = event.data;
            switch (message.command) {
                case 'updateMessages':
                    renderMessages(message.messages);
                    break;
                case 'insertMessage':
                    document.getElementById('messageInput').value = message.text;
                    break;
            }
        });
        
        function renderMessages(messages) {
            const container = document.getElementById('messages');
            
            if (messages.length === 0) {
                return;
            }
            
            container.innerHTML = messages.map(msg => \`
                <div class="message \${msg.role}">
                    <div class="message-role">\${msg.role === 'user' ? 'You' : '🤖 Coach'}</div>
                    <div class="message-content">\${escapeHtml(msg.content)}</div>
                </div>
            \`).join('');
            
            container.scrollTop = container.scrollHeight;
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            const text = input.value.trim();
            
            if (!text) return;
            
            vscode.postMessage({
                command: 'sendMessage',
                text: text
            });
            
            input.value = '';
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        function useSelection() {
            vscode.postMessage({ command: 'useSelection' });
        }
        
        function explainInHindi() {
            vscode.postMessage({ command: 'explainInHindi' });
        }
        
        function firstHintOnly() {
            const input = document.getElementById('messageInput');
            input.value = 'Give me just a high-level hint about this code';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>`;
    }
}
