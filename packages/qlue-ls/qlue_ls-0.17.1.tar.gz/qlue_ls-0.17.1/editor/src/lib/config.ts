import { configureDefaultWorkerFactory } from 'monaco-editor-wrapper/workers/workerLoaders';
import type { WrapperConfig } from 'monaco-editor-wrapper';
import { LogLevel, Uri } from 'vscode';

import sparqlTextmateGrammar from './sparql.tmLanguage.json?raw';
import sparqlLanguageConfig from './sparql.configuration.json?raw';
import sparqlTheme from './sparql.theme.json?raw';
import languageServerWorker from './languageServer.worker?worker';

export async function buildWrapperConfig(
    container: HTMLElement,
    initial: string
): Promise<WrapperConfig> {
    const workerPromise: Promise<Worker> = new Promise((resolve) => {
        const instance: Worker = new languageServerWorker({ name: 'Language Server' });
        instance.onmessage = (event) => {
            if (event.data.type === 'ready') {
                resolve(instance);
            }
        };
    });
    const worker = await workerPromise;

    const extensionFilesOrContents = new Map<string, string | URL>();
    extensionFilesOrContents.set('/sparql-configuration.json', sparqlLanguageConfig);
    extensionFilesOrContents.set('/sparql-grammar.json', sparqlTextmateGrammar);
    extensionFilesOrContents.set('/sparql-theme.json', sparqlTheme);

    const wrapperConfig: WrapperConfig = {
        $type: 'extended',
        htmlContainer: container,
        logLevel: LogLevel.Info,
        languageClientConfigs: {
            configs: {
                sparql: {
                    name: 'Qlue-ls',
                    clientOptions: {
                        documentSelector: [{ language: 'sparql' }],
                        workspaceFolder: {
                            index: 0,
                            name: 'workspace',
                            uri: Uri.file('/')
                        },
                        progressOnInitialization: true,
                        diagnosticPullOptions: {
                            onChange: true,
                            onSave: false
                        }
                    },
                    connection: {
                        options: {
                            $type: 'WorkerDirect',
                            worker: worker
                        }
                    },
                    restartOptions: {
                        retries: 5,
                        timeout: 1000,
                        keepWorker: true
                    }
                }
            }
        },
        editorAppConfig: {
            codeResources: {
                modified: {
                    uri: 'query.rq',
                    text: initial
                }
            },
            monacoWorkerFactory: configureDefaultWorkerFactory,
            editorOptions: {
                tabCompletion: 'on',
                suggestOnTriggerCharacters: true,
                theme: 'vs-dark',
                fontSize: 16,
                fontFamily: 'Source Code Pro',
                links: false,
                minimap: {
                    enabled: false
                },
                overviewRulerLanes: 0,
                scrollBeyondLastLine: false,
                padding: {
                    top: 10,
                    bottom: 10
                },
                folding: true,
                foldingImportsByDefault: true
            }
        },
        vscodeApiConfig: {
            userConfiguration: {
                json: JSON.stringify({
                    'workbench.colorTheme': 'custom',
                    'editor.guides.bracketPairsHorizontal': 'active',
                    'editor.lightbulb.enabled': 'On',
                    'editor.wordBasedSuggestions': 'off',
                    'editor.experimental.asyncTokenization': true,
                    'editor.tabSize': 2,
                    'editor.insertSpaces': true,
                    'editor.detectIndentation': false,
                    'files.eol': '\n'
                })
            }
        },

        extensions: [
            {
                config: {
                    name: 'langium-sparql',
                    publisher: 'Ioannis Nezis',
                    version: '1.0.0',
                    engines: {
                        vscode: '*'
                    },
                    contributes: {
                        languages: [
                            {
                                id: 'sparql',
                                extensions: ['.rq'],
                                aliases: ['sparql', 'SPARQL'],
                                configuration: '/sparql-configuration.json'
                            }
                        ],
                        themes: [
                            {
                                id: 'custom',
                                label: 'SPARQL Custom Theme',
                                uiTheme: 'vs-dark',
                                path: './sparql-theme.json'
                            }
                        ],
                        grammars: [
                            {
                                language: 'sparql',
                                scopeName: 'source.sparql',
                                path: '/sparql-grammar.json'
                            }
                        ]
                    }
                },
                filesOrContents: extensionFilesOrContents
            }
        ]
    };
    return wrapperConfig;
}
