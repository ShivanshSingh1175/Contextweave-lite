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

    console.log(`API Request to ${backendUrl}/context/file:`, {
        repo_path: repoPath,
        file_path: filePath,
        has_selected_code: !!selectedCode,
        commit_limit: commitLimit
    });

    try {
        const response = await axios.post<AnalysisResult>(
            `${backendUrl}/context/file`,
            requestBody,
            {
                timeout: 30000, // 30 second timeout
                headers: {
                    'Content-Type': 'application/json'
                },
                validateStatus: (status) => status < 600 // Don't throw on 4xx/5xx, handle manually
            }
        );

        if (response.status >= 400) {
            // Backend returned an error
            const errorDetail = response.data as any;
            throw {
                response: {
                    status: response.status,
                    statusText: response.statusText,
                    data: errorDetail
                }
            };
        }

        console.log('API Response received:', {
            status: response.status,
            commits_analyzed: response.data.metadata.commits_analyzed,
            has_decisions: response.data.decisions.length > 0,
            has_related_files: response.data.related_files.length > 0
        });

        return response.data;

    } catch (error: any) {
        console.error('API call failed:', {
            message: error.message,
            code: error.code,
            response: error.response ? {
                status: error.response.status,
                data: error.response.data
            } : undefined
        });
        throw error;
    }
}
