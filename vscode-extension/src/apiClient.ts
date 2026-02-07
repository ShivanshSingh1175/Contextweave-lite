/**
 * API client for communicating with ContextWeave backend
 */
import axios from 'axios';
import * as vscode from 'vscode';

export interface AnalysisResult {
    summary: string;
    decisions: DesignDecision[];
    related_files: RelatedFile[];
    weird_code_explanation?: string;
    metadata: {
        commits_analyzed: number;
        llm_configured?: boolean;
        mock_response?: boolean;
    };
}

export interface DesignDecision {
    title: string;
    description: string;
    commits: string[];
}

export interface RelatedFile {
    path: string;
    reason: string;
}

export async function analyzeFile(
    repoPath: string,
    filePath: string,
    selectedCode?: string
): Promise<AnalysisResult> {
    const config = vscode.workspace.getConfiguration('contextweave');
    const backendUrl = config.get<string>('backendUrl', 'http://localhost:8000');
    const commitLimit = config.get<number>('commitLimit', 50);

    const requestBody = {
        repo_path: repoPath,
        file_path: filePath,
        selected_code: selectedCode || null,
        commit_limit: commitLimit
    };

    try {
        const response = await axios.post<AnalysisResult>(
            `${backendUrl}/context/file`,
            requestBody,
            {
                timeout: 30000, // 30 second timeout
                headers: {
                    'Content-Type': 'application/json'
                }
            }
        );

        return response.data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}
