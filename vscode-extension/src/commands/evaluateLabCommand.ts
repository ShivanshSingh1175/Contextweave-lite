/**
 * Evaluate Lab Command - Assesses student lab against rubric
 */
import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import axios from 'axios';
import { RubricPanel } from '../webviews/RubricPanel';

export class EvaluateLabCommand {
    constructor(
        private extensionUri: vscode.Uri,
        private backendUrl: string
    ) {}

    async execute() {
        try {
            // Get workspace folder
            const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
            if (!workspaceFolder) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }

            // Find rubric.json
            const rubricPath = await this.findRubric(workspaceFolder.uri.fsPath);
            if (!rubricPath) {
                vscode.window.showErrorMessage('rubric.json not found in workspace or demo folder');
                return;
            }

            // Load rubric
            const rubricContent = fs.readFileSync(rubricPath, 'utf8');
            const rubric = JSON.parse(rubricContent);

            // Find lab files
            const labFiles = await this.findLabFiles(workspaceFolder.uri.fsPath);
            if (labFiles.length === 0) {
                vscode.window.showErrorMessage('No lab files found. Looking for files in labs/ or demo/ folder');
                return;
            }

            // Show progress
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: 'Evaluating lab...',
                cancellable: false
            }, async () => {
                // Prepare files for API
                const files = labFiles.map(filePath => ({
                    path: path.basename(filePath),
                    content: fs.readFileSync(filePath, 'utf8')
                }));

                // Call backend
                const response = await axios.post(`${this.backendUrl}/v1/labs/evaluate`, {
                    files: files,
                    rubric: rubric.criteria || rubric,
                    rubric_descriptions: rubric.descriptions
                }, {
                    timeout: 60000
                });

                // Show results in panel
                const panel = RubricPanel.createOrShow(this.extensionUri);
                panel.showEvaluation(response.data);

                vscode.window.showInformationMessage(
                    `Lab evaluated: ${response.data.percentage}% (${response.data.overall_score}/${response.data.overall_max})`
                );
            });

        } catch (error: any) {
            vscode.window.showErrorMessage(`Lab evaluation failed: ${error.message}`);
        }
    }

    private async findRubric(workspacePath: string): Promise<string | null> {
        // Check common locations
        const locations = [
            path.join(workspacePath, 'rubric.json'),
            path.join(workspacePath, 'demo', 'rubric.json'),
            path.join(workspacePath, 'labs', 'rubric.json')
        ];

        for (const location of locations) {
            if (fs.existsSync(location)) {
                return location;
            }
        }

        return null;
    }

    private async findLabFiles(workspacePath: string): Promise<string[]> {
        const files: string[] = [];

        // Check demo folder
        const demoPath = path.join(workspacePath, 'demo');
        if (fs.existsSync(demoPath)) {
            const demoFiles = fs.readdirSync(demoPath)
                .filter(f => f.startsWith('lab') && (f.endsWith('.py') || f.endsWith('.js') || f.endsWith('.java')))
                .map(f => path.join(demoPath, f));
            files.push(...demoFiles);
        }

        // Check labs folder
        const labsPath = path.join(workspacePath, 'labs');
        if (fs.existsSync(labsPath)) {
            const labFiles = fs.readdirSync(labsPath)
                .filter(f => f.endsWith('.py') || f.endsWith('.js') || f.endsWith('.java'))
                .map(f => path.join(labsPath, f));
            files.push(...labFiles);
        }

        // If no files found, check current file
        if (files.length === 0) {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                files.push(editor.document.fileName);
            }
        }

        return files;
    }
}
