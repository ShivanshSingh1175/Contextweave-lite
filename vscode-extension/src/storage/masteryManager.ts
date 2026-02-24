/**
 * Mastery tracking system - stores learning progress locally
 */
import * as vscode from 'vscode';

export interface TopicMastery {
    score: number;  // 0.0 - 5.0
    attempts: number;
    hint_usage: number;
    last_review: string;  // ISO date
    last_level_used: number;  // 1, 2, or 3
}

export interface MasteryProfile {
    userId: string;
    topics: { [key: string]: TopicMastery };
    exams: { [key: string]: ExamReadiness };
    spaced: SpacedRepetition;
}

export interface ExamReadiness {
    topics: string[];
    readiness: string;  // "Ready", "Needs Work", "Not Ready"
    percentage: number;
}

export interface SpacedRepetition {
    due_today: string[];
    next_24h: string[];
    next_week: string[];
}

export class MasteryManager {
    private context: vscode.ExtensionContext;
    private profile: MasteryProfile;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.profile = this.loadProfile();
    }

    private loadProfile(): MasteryProfile {
        const stored = this.context.globalState.get<MasteryProfile>('masteryProfile');
        if (stored) {
            return stored;
        }

        // Initialize new profile
        return {
            userId: `user_${Date.now()}`,
            topics: {},
            exams: {},
            spaced: {
                due_today: [],
                next_24h: [],
                next_week: []
            }
        };
    }

    private async saveProfile() {
        await this.context.globalState.update('masteryProfile', this.profile);
    }

    /**
     * Update mastery score based on hint usage
     */
    async updateMastery(concepts: string[], hintLevel: number) {
        const today = new Date().toISOString().split('T')[0];

        for (const concept of concepts) {
            if (!this.profile.topics[concept]) {
                this.profile.topics[concept] = {
                    score: 2.5,  // Start at middle
                    attempts: 0,
                    hint_usage: 0,
                    last_review: today,
                    last_level_used: hintLevel
                };
            }

            const topic = this.profile.topics[concept];
            topic.attempts += 1;
            topic.last_review = today;
            topic.last_level_used = hintLevel;

            // Scoring rules
            if (hintLevel === 1) {
                topic.score += 0.5;  // Minimal hint
            } else if (hintLevel === 2) {
                topic.score -= 0.3;  // Moderate hint
                topic.hint_usage += 1;
            } else if (hintLevel === 3) {
                topic.score -= 0.8;  // Full explanation
                topic.hint_usage += 1;
            }

            // Clamp score between 0 and 5
            topic.score = Math.max(0, Math.min(5, topic.score));
        }

        await this.saveProfile();
        this.updateSpacedRepetition();
    }

    /**
     * Update spaced repetition schedule
     */
    private updateSpacedRepetition() {
        const today = new Date();
        const due_today: string[] = [];
        const next_24h: string[] = [];
        const next_week: string[] = [];

        for (const [concept, data] of Object.entries(this.profile.topics)) {
            const lastReview = new Date(data.last_review);
            const daysSince = Math.floor((today.getTime() - lastReview.getTime()) / (1000 * 60 * 60 * 24));

            // Scheduling logic based on score
            let reviewInterval: number;
            if (data.score <= 2) {
                reviewInterval = 1;  // Daily
            } else if (data.score <= 3.5) {
                reviewInterval = 3;  // Every 3 days
            } else {
                reviewInterval = 7;  // Weekly
            }

            if (daysSince >= reviewInterval) {
                due_today.push(concept);
            } else if (daysSince >= reviewInterval - 1) {
                next_24h.push(concept);
            } else if (daysSince >= reviewInterval - 3) {
                next_week.push(concept);
            }
        }

        this.profile.spaced = { due_today, next_24h, next_week };
    }

    /**
     * Get current mastery profile
     */
    getProfile(): MasteryProfile {
        return this.profile;
    }

    /**
     * Get topics that need review today
     */
    getDueTopics(): string[] {
        return this.profile.spaced.due_today;
    }

    /**
     * Calculate exam readiness
     */
    calculateExamReadiness(examName: string, topics: string[]): ExamReadiness {
        let totalScore = 0;
        let count = 0;

        for (const topic of topics) {
            if (this.profile.topics[topic]) {
                totalScore += this.profile.topics[topic].score;
                count++;
            }
        }

        const avgScore = count > 0 ? totalScore / count : 0;
        const percentage = (avgScore / 5) * 100;

        let readiness: string;
        if (percentage >= 80) {
            readiness = "Ready";
        } else if (percentage >= 60) {
            readiness = "Needs Work";
        } else {
            readiness = "Not Ready";
        }

        const exam: ExamReadiness = {
            topics,
            readiness,
            percentage: Math.round(percentage)
        };

        this.profile.exams[examName] = exam;
        this.saveProfile();

        return exam;
    }

    /**
     * Get weak topics (score < 3)
     */
    getWeakTopics(): Array<{ topic: string; score: number }> {
        return Object.entries(this.profile.topics)
            .filter(([_, data]) => data.score < 3)
            .map(([topic, data]) => ({ topic, score: data.score }))
            .sort((a, b) => a.score - b.score);
    }

    /**
     * Reset mastery for testing
     */
    async resetMastery() {
        this.profile = {
            userId: `user_${Date.now()}`,
            topics: {},
            exams: {},
            spaced: {
                due_today: [],
                next_24h: [],
                next_week: []
            }
        };
        await this.saveProfile();
    }
}
