/**
 * Exam Mode Toggle Command - Restricts hints for fair assessment
 */
import * as vscode from 'vscode';

export class ExamModeCommand {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'contextweave.toggleExamMode';
        this.updateStatusBar();
    }

    async execute() {
        const config = vscode.workspace.getConfiguration('contextweave');
        const currentMode = config.get<boolean>('examMode', false);
        const newMode = !currentMode;

        await config.update('examMode', newMode, vscode.ConfigurationTarget.Global);

        this.updateStatusBar();

        if (newMode) {
            vscode.window.showWarningMessage(
                '🔒 Exam Mode ON – Only high-level hints will be provided. Good luck!',
                'Got it'
            );
        } else {
            vscode.window.showInformationMessage(
                '✅ Exam Mode OFF – Normal learning mode restored.',
                'Got it'
            );
        }
    }

    private updateStatusBar() {
        const config = vscode.workspace.getConfiguration('contextweave');
        const examMode = config.get<boolean>('examMode', false);

        if (examMode) {
            this.statusBarItem.text = '$(lock) Exam Mode';
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            this.statusBarItem.tooltip = 'Exam Mode is ON - Click to disable';
        } else {
            this.statusBarItem.text = '$(unlock) Learning Mode';
            this.statusBarItem.backgroundColor = undefined;
            this.statusBarItem.tooltip = 'Learning Mode - Click to enable Exam Mode';
        }

        this.statusBarItem.show();
    }

    public dispose() {
        this.statusBarItem.dispose();
    }
}
