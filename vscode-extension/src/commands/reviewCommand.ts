/**
 * Review Command - Shows topics due for spaced repetition
 */
import * as vscode from 'vscode';
import { MasteryManager } from '../storage/masteryManager';

export class ReviewCommand {
    constructor(private masteryManager: MasteryManager) {}

    async execute() {
        const profile = this.masteryManager.getProfile();
        const dueToday = profile.spaced.due_today;
        const next24h = profile.spaced.next_24h;

        if (dueToday.length === 0 && next24h.length === 0) {
            vscode.window.showInformationMessage(
                '✅ All caught up! No topics need review today.',
                'Great!'
            );
            return;
        }

        // Build message
        let message = '📅 Topics to Review:\n\n';

        if (dueToday.length > 0) {
            message += '⚠️ Due Today:\n';
            for (const topic of dueToday) {
                const score = profile.topics[topic]?.score || 0;
                message += `  • ${this.formatTopic(topic)} (${score.toFixed(1)}/5.0)\n`;
            }
            message += '\n';
        }

        if (next24h.length > 0) {
            message += '📌 Due in 24 hours:\n';
            for (const topic of next24h) {
                const score = profile.topics[topic]?.score || 0;
                message += `  • ${this.formatTopic(topic)} (${score.toFixed(1)}/5.0)\n`;
            }
        }

        // Show in quick pick
        const items = [
            ...dueToday.map(topic => ({
                label: `⚠️ ${this.formatTopic(topic)}`,
                description: `Score: ${profile.topics[topic]?.score.toFixed(1)}/5.0`,
                detail: 'Due today - Review recommended',
                topic: topic
            })),
            ...next24h.map(topic => ({
                label: `📌 ${this.formatTopic(topic)}`,
                description: `Score: ${profile.topics[topic]?.score.toFixed(1)}/5.0`,
                detail: 'Due in 24 hours',
                topic: topic
            }))
        ];

        const selected = await vscode.window.showQuickPick(items, {
            placeHolder: 'Select a topic to review',
            title: 'Topics to Review'
        });

        if (selected) {
            // Open chat with review prompt
            vscode.commands.executeCommand('contextweave.openTutorChat');
            
            // Wait a bit for chat to open, then send message
            setTimeout(() => {
                vscode.window.showInformationMessage(
                    `Ready to review ${this.formatTopic(selected.topic)}! Ask the tutor for practice problems or explanations.`
                );
            }, 500);
        }
    }

    private formatTopic(topic: string): string {
        return topic.split('-').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
}
