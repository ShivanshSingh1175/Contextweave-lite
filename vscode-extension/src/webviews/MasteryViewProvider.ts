/**
 * Mastery Sidebar Webview Provider
 * Shows topic mastery scores, exam readiness, and review reminders
 */
import * as vscode from 'vscode';
import { MasteryManager } from '../storage/masteryManager';

export class MasteryViewProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'contextweave.masteryView';
    private _view?: vscode.WebviewView;

    constructor(
        private readonly _extensionUri: vscode.Uri,
        private readonly masteryManager: MasteryManager
    ) {}

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

        webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);

        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(data => {
            switch (data.type) {
                case 'reviewToday':
                    vscode.commands.executeCommand('contextweave.whatToReview');
                    break;
                case 'refresh':
                    this.refresh();
                    break;
            }
        });

        // Initial render
        this.refresh();
    }

    public refresh() {
        if (this._view) {
            this._view.webview.postMessage({
                type: 'update',
                data: this.masteryManager.getProfile()
            });
        }
    }

    private _getHtmlForWebview(webview: vscode.Webview) {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mastery Tracker</title>
    <style>
        body {
            padding: 10px;
            color: var(--vscode-foreground);
            font-family: var(--vscode-font-family);
            font-size: var(--vscode-font-size);
        }
        
        .section {
            margin-bottom: 20px;
        }
        
        .section-title {
            font-weight: bold;
            margin-bottom: 10px;
            color: var(--vscode-textLink-foreground);
            font-size: 13px;
            text-transform: uppercase;
        }
        
        .topic-item {
            margin-bottom: 12px;
            padding: 8px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 4px;
        }
        
        .topic-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 4px;
        }
        
        .topic-name {
            font-weight: 500;
            flex: 1;
        }
        
        .topic-score {
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        
        .progress-bar {
            height: 6px;
            background: var(--vscode-progressBar-background);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: var(--vscode-progressBar-background);
            transition: width 0.3s ease;
        }
        
        .progress-fill.low {
            background: #f48771;
        }
        
        .progress-fill.medium {
            background: #cca700;
        }
        
        .progress-fill.high {
            background: #89d185;
        }
        
        .due-badge {
            display: inline-block;
            background: #f48771;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 8px;
        }
        
        .exam-card {
            padding: 10px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 4px;
            margin-bottom: 8px;
        }
        
        .exam-name {
            font-weight: 500;
            margin-bottom: 4px;
        }
        
        .exam-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
        }
        
        .status-badge {
            padding: 2px 8px;
            border-radius: 3px;
            font-weight: 500;
        }
        
        .status-badge.ready {
            background: #89d185;
            color: #000;
        }
        
        .status-badge.needs-work {
            background: #cca700;
            color: #000;
        }
        
        .status-badge.not-ready {
            background: #f48771;
            color: #fff;
        }
        
        button {
            width: 100%;
            padding: 8px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            margin-top: 8px;
        }
        
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        
        .empty-state {
            text-align: center;
            padding: 20px;
            color: var(--vscode-descriptionForeground);
            font-size: 12px;
        }
        
        .refresh-btn {
            background: var(--vscode-button-secondaryBackground);
            color: var(--vscode-button-secondaryForeground);
        }
        
        .refresh-btn:hover {
            background: var(--vscode-button-secondaryHoverBackground);
        }
    </style>
</head>
<body>
    <div id="content">
        <div class="empty-state">
            Loading mastery data...
        </div>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        
        window.addEventListener('message', event => {
            const message = event.data;
            if (message.type === 'update') {
                renderMastery(message.data);
            }
        });
        
        function renderMastery(profile) {
            const content = document.getElementById('content');
            
            if (!profile || Object.keys(profile.topics).length === 0) {
                content.innerHTML = \`
                    <div class="empty-state">
                        <p>No mastery data yet.</p>
                        <p>Start using hints to track your progress!</p>
                    </div>
                \`;
                return;
            }
            
            let html = '';
            
            // Topics section
            html += '<div class="section">';
            html += '<div class="section-title">📚 Topics</div>';
            
            const topics = Object.entries(profile.topics)
                .sort((a, b) => a[1].score - b[1].score);
            
            const dueToday = profile.spaced?.due_today || [];
            
            for (const [topic, data] of topics) {
                const percentage = (data.score / 5) * 100;
                let fillClass = 'low';
                if (data.score >= 4) fillClass = 'high';
                else if (data.score >= 2.5) fillClass = 'medium';
                
                const isDue = dueToday.includes(topic);
                const dueBadge = isDue ? '<span class="due-badge">⚠️ Review</span>' : '';
                
                html += \`
                    <div class="topic-item">
                        <div class="topic-header">
                            <span class="topic-name">\${formatTopicName(topic)}</span>
                            <span class="topic-score">\${data.score.toFixed(1)}/5.0\${dueBadge}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill \${fillClass}" style="width: \${percentage}%"></div>
                        </div>
                    </div>
                \`;
            }
            
            html += '</div>';
            
            // Exams section
            if (profile.exams && Object.keys(profile.exams).length > 0) {
                html += '<div class="section">';
                html += '<div class="section-title">🎯 Exam Readiness</div>';
                
                for (const [examName, exam] of Object.entries(profile.exams)) {
                    let statusClass = 'not-ready';
                    if (exam.readiness === 'Ready') statusClass = 'ready';
                    else if (exam.readiness === 'Needs Work') statusClass = 'needs-work';
                    
                    html += \`
                        <div class="exam-card">
                            <div class="exam-name">\${examName}</div>
                            <div class="exam-status">
                                <span class="status-badge \${statusClass}">\${exam.readiness}</span>
                                <span>\${exam.percentage}%</span>
                            </div>
                        </div>
                    \`;
                }
                
                html += '</div>';
            }
            
            // Actions
            html += '<div class="section">';
            html += '<button onclick="reviewToday()">📅 What to Review Today?</button>';
            html += '<button class="refresh-btn" onclick="refresh()">🔄 Refresh</button>';
            html += '</div>';
            
            content.innerHTML = html;
        }
        
        function formatTopicName(topic) {
            return topic.split('-').map(word => 
                word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ');
        }
        
        function reviewToday() {
            vscode.postMessage({ type: 'reviewToday' });
        }
        
        function refresh() {
            vscode.postMessage({ type: 'refresh' });
        }
    </script>
</body>
</html>`;
    }
}
