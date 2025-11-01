import * as vscode from 'vscode';
// We need to import the specific types from axios to help TypeScript
import axios, { AxiosError } from 'axios';

export function activate(context: vscode.ExtensionContext) {

    console.log('Congratulations, your extension "slicer-script-runner" is now active!');

    let disposable = vscode.commands.registerCommand('slicer-script-runner.execute', async () => {
        
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showWarningMessage('No active editor found. Please open a script file.');
            return;
        }

        const scriptText = editor.document.getText();
        if (!scriptText.trim()) {
            vscode.window.showWarningMessage('The editor is empty. Please write a script to execute.');
            return;
        }

        const configuration = vscode.workspace.getConfiguration('slicer-script-runner');
        const serverUrl = configuration.get<string>('serverUrl');

        if (!serverUrl) {
            vscode.window.showErrorMessage('Slicer server URL is not configured. Please set it in your settings.');
            return;
        }

        try {
            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: "Sending script to Slicer...",
                cancellable: false
            }, async (progress) => {
                
                const response = await axios.post(serverUrl, scriptText, {
                    headers: { 'Content-Type': 'text/plain' }
                });

                vscode.window.showInformationMessage('Script executed successfully in Slicer!');
                
                // --- FIX START ---
                // Check if there is data in the response before creating the channel
                if (response.data) {
                    const outputChannel = vscode.window.createOutputChannel("Slicer Response");
                    // Ensure the data is a string before appending
                    const responseText = typeof response.data === 'string' ? response.data : JSON.stringify(response.data, null, 2);
                    outputChannel.appendLine(responseText);
                    outputChannel.show();
                }
                // --- FIX END ---
            });

        } catch (error) {
            console.error('Error executing script in Slicer:', error);
            
            // --- FIX START ---
            // Type-safe error handling
            if (axios.isAxiosError(error)) {
                // Now TypeScript knows 'error' is an AxiosError
                const axiosError = error as AxiosError;
                let errorMessage = `Failed to connect to Slicer: ${axiosError.message}.`;
                // Provide more detail if the server responded with an error
                if (axiosError.response) {
                    errorMessage += ` Server responded with status ${axiosError.response.status}.`;
                }
                vscode.window.showErrorMessage(errorMessage);
            } else if (error instanceof Error) {
                // Handle generic JavaScript errors
                vscode.window.showErrorMessage(`An error occurred: ${error.message}`);
            } else {
                // Handle other unknown throwables
                vscode.window.showErrorMessage('An unexpected error occurred while sending the script.');
            }
            // --- FIX END ---
        }
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}
