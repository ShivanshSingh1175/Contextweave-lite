/**
 * Rubric Evaluation Panel - Shows lab assessment results
 */
import * as vscode from 'vscode';

interface RubricResult {
    criterion: string;
    score: string;
    points: number;
    max_points: number;
    feedback: string;
}

interface EvaluationData {
    rubric: RubricResult[];
    overall_score: number;
    overall_max: number;
    percentage: number;
    summary: string;
}

export class RubricPanel {
    public static currentPanel: RubricPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private _disposables: vscode.Disposable[] = [];

    private constructor(panel: vscode.WebviewPanel, extensionUri: vscode.Uri) {
        this._panel = panel;
        this._panel.webview.html = this._getHtmlForWebview(this._panel.webview);

        this._panel.onDidDispose(() => this.dispose(), null, this._disposables);

        this._panel.webview.onDidReceiveMessage(
            message => {
                switch (message.command) {
                    case 'openWeakTopics':
                        vscode.commands.executeCommand('contextweave.showMastery');
                        break;
                }
            },
            null,
            this._disposables
        );
    }

    public static createOrShow(extensionUri: vscode.Uri) {
        const column = vscode.ViewColumn.Two;

        if (RubricPanel.currentPanel) {
            RubricPanel.currentPanel._panel.reveal(column);
            return RubricPanel.currentPanel;
        }

        const panel = vscode.window.createWebviewPanel(
            'contextweaveRubric',
            'Lab Evaluation',
            column,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        RubricPanel.currentPanel = new RubricPanel(panel, extensionUri);
        return RubricPanel.currentPanel;
    }

    public showEvaluation(data: EvaluationData) {
        this._panel.webview.postMessage({
            command: 'showEvaluation',
            data: data
        });
    }

    public dispose() {
        RubricPanel.currentPanel = undefined;
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
    <title>Lab Evaluation</title>
    <style>
        body {
            padding: 20px;
            color: var(--vscode-foreground);
            font-family: var(--vscode-font-family);
        }
        
        .header {
            margin-bottom: 24px;
        }
        
        h1 {
            margin: 0 0 8px 0;
            font-size: 24px;
        }
        
        .overall-score {
            display: flex;
            align-items: center;
            gap: 16px;
            padding: 16px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 6px;
            margin-bottom: 24px;
        }
        
        .score-circle {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            border: 4px solid;
        }
        
        .score-circle.high {
            border-color: #89d185;
            color: #89d185;
        }
        
        .score-circle.medium {
            border-color: #cca700;
            color: #cca700;
        }
        
        .score-circle.low {
            border-color: #f48771;
            color: #f48771;
        }
        
        .score-details {
            flex: 1;
        }
        
        .score-label {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
            margin-bottom: 4px;
        }
        
        .score-value {
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .summary {
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
        }
        
        .rubric-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 24px;
        }
        
        .rubric-table th {
            text-align: left;
            padding: 12px;
            background: var(--vscode-editor-background);
            border-bottom: 2px solid var(--vscode-panel-border);
            font-weight: 600;
            font-size: 13px;
        }
        
        .rubric-table td {
            padding: 12px;
            border-bottom: 1px solid var(--vscode-panel-border);
            vertical-align: top;
        }
        
        .criterion-name {
            font-weight: 500;
        }
        
        .score-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .score-badge.met {
            background: #89d185;
            color: #000;
        }
        
        .score-badge.partial {
            background: #cca700;
            color: #000;
        }
        
        .score-badge.not-met {
            background: #f48771;
            color: #fff;
        }
        
        .points {
            font-size: 14px;
            color: var(--vscode-descriptionForeground);
        }
        
        .feedback {
            margin-top: 4px;
            font-size: 13px;
            line-height: 1.5;
        }
        
        .actions {
            display: flex;
            gap: 12px;
        }
        
        button {
            padding: 10px 20px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }
        
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .loading {
            text-align: center;
            padding: 60px 20px;
            color: var(--vscode-descriptionForeground);
        }
    </style>
</head>
<body>
    <div id="content">
        <div class="loading">
            <h3>Evaluating your lab...</h3>
            <p>This may take a few moments.</p>
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.command === 'showEvaluation') {
                renderEvaluation(message.data);
            }
        });
        
        function renderEvaluation(data) {
            const content = document.getElementById('content');
            
            let scoreClass = 'low';
            if (data.percentage >= 80) scoreClass = 'high';
            else if (data.percentage >= 60) scoreClass = 'medium';
            
            let html = \`
                <div class="header">
                    <h1>📊 Lab Evaluation Results</h1>
                </div>
                
                <div class="overall-score">
                    <div class="score-circle \${scoreClass}">
                        \${data.percentage}%
                    </div>
                    <div class="score-details">
                        <div class="score-label">Overall Score</div>
                        <div class="score-value">\${data.overall_score} / \${data.overall_max} points</div>
                        <div class="summary">\${data.summary}</div>
                    </div>
                </div>
                
                <table class="rubric-table">
                    <thead>
                        <tr>
                            <th>Criterion</th>
                            <th>Status</th>
                            <th>Points</th>
                            <th>Feedback</th>
                        </tr>
                    </thead>
                    <tbody>
            \`;
            
            for (const item of data.rubric) {
                const badgeClass = item.score.toLowerCase().replace(' ', '-');
                
                html += \`
                    <tr>
                        <td class="criterion-name">\${formatCriterion(item.criterion)}</td>
                        <td>
                            <span class="score-badge \${badgeClass}">\${item.score}</span>
                        </td>
                        <td class="points">\${item.points} / \${item.max_points}</td>
                        <td class="feedback">\${item.feedback}</td>
                    </tr>
                \`;
            }
            
            html += \`
                    </tbody>
                </table>
                
                <div class="actions">
                    <button onclick="openWeakTopics()">📚 View Weak Topics in Mastery</button>
                </div>
            \`;
            
            content.innerHTML = html;
        }
        
        function formatCriterion(criterion) {
            return criterion.split('_').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        
        function openWeakTopics() {
            vscode.postMessage({ command: 'openWeakTopics' });
        }
    </script>
</body>
</html>`;
    }
}
