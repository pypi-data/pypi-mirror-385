/**
 * External JavaScript file for Amazon Q chat client initialization.
 * Moved from inline script to comply with Content Security Policy (CSP) requirements.
 * Removes need for 'unsafe-inline' in script-src directive.
 */

const init = () => {
  const postMessage = event => {
    window.parent.postMessage(event, window.location.origin);
  };
  const api = {
    postMessage: postMessage.bind(window)
  };

  const mockQuickActions = [
    {
      commands: [
        {
          command: '/clear',
          icon: 'file',
          description: 'Clear the chat window'
        },
        {
          command: '/fix',
          icon: 'file',
          description: 'Fx an error cell selected in your notebook'
        },
        {
          command: '/explain',
          icon: 'file',
          description: 'Explains code included in a selection'
        },
        {
          command: '/optimize',
          icon: 'file',
          description: 'Optimizes code included in a selection'
        },
        {
          command: '/refactor',
          icon: 'file',
          description: 'Refactors code included in a selection'
        },
        {
          command: '/help',
          icon: 'file',
          description: 'Display this help message'
        }
      ]
    }
  ];

  // key will exist in local storage if user acknowledged the Amazon Q Developer disclaimer
  const disclaimerAcknowledged = localStorage.getItem(
    'disclaimerAcknowledged'
  );
  // key will exist in local storage if the user closed the agentic Q introduction alert
  const pairProgrammingAcknowledged = localStorage.getItem(
    'chatPromptOptionAcknowledged'
  );

  amazonQChat.createChat(api, {
    disclaimerAcknowledged,
    pairProgrammingAcknowledged,
    agenticMode: true,
    quickActionCommands: mockQuickActions
  });
};

const script = document.createElement('script');
script.type = 'application/javascript';
script.onload = () => {
  console.log('✅ Amazon Q client loaded successfully from SageMaker Distribution artifacts');
  init();
};

const baseUrl = window.location.pathname.split('/sagemaker_gen_ai_jupyterlab_extension')[0];
script.src = `${baseUrl}/sagemaker_gen_ai_jupyterlab_extension/direct/amazonq-ui.js`;

script.onerror = (message, source, lineno, colno, error) => {
  console.error('❌ Failed to load Amazon Q client from SageMaker Distribution artifacts', { message, source, lineno, colno, error });
};
document.body.appendChild(script);