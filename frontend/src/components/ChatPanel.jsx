import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Loader2 } from 'lucide-react';
import { sendChatMessage, suggestPolicies } from '../services/api';

function ChatPanel({ countryCode, currentParams, onApplyParams }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello! I'm your economic policy assistant. I can help you explore policy options for ${countryCode === 'ZAF' ? 'South Africa' : 'Tunisia'}.

Try asking me things like:
- "What if we increase tariffs on textiles by 15%?"
- "How can we create more jobs for young people?"
- "What would happen if we invest in manufacturing productivity?"`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage, countryCode, currentParams);

      let assistantMessage = '';

      if (response.understood && response.policy_params) {
        assistantMessage = `${response.explanation}\n\nI've prepared these policy parameters for you:\n`;

        const params = response.policy_params;
        if (Object.keys(params.tariff_changes || {}).length > 0) {
          assistantMessage += `\n**Tariff Changes:**\n`;
          Object.entries(params.tariff_changes).forEach(([sector, value]) => {
            assistantMessage += `- ${sector.replace('_', ' ')}: ${value > 0 ? '+' : ''}${value}%\n`;
          });
        }
        if (Object.keys(params.subsidy_changes || {}).length > 0) {
          assistantMessage += `\n**Subsidies:**\n`;
          Object.entries(params.subsidy_changes).forEach(([sector, value]) => {
            assistantMessage += `- ${sector.replace('_', ' ')}: +${value}%\n`;
          });
        }
        if (params.sme_stimulus > 0) {
          assistantMessage += `\n**SME Stimulus:** ${params.sme_stimulus}% of GDP\n`;
        }
        if (params.productivity_investment > 0) {
          assistantMessage += `\n**Productivity Investment:** ${params.productivity_investment}%\n`;
        }

        assistantMessage += `\nWould you like me to apply these parameters to the simulation?`;

        setMessages(prev => [
          ...prev,
          {
            role: 'assistant',
            content: assistantMessage,
            hasParams: true,
            params: response.policy_params,
          },
        ]);
      } else if (response.clarification_needed) {
        assistantMessage = `${response.message}\n\n${response.clarification_needed}`;
        setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }]);
      } else {
        assistantMessage = response.message || response.explanation || "I couldn't fully understand that request. Could you rephrase it?";
        setMessages(prev => [...prev, { role: 'assistant', content: assistantMessage }]);
      }
    } catch (error) {
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
          isError: true,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleApplyParams = (params) => {
    onApplyParams(params);
    setMessages(prev => [
      ...prev,
      {
        role: 'assistant',
        content: "I've applied those parameters to the simulation. Click 'Run Simulation' to see the results!",
      },
    ]);
  };

  const handleSuggestions = async () => {
    setLoading(true);
    try {
      const response = await suggestPolicies(countryCode, 'create jobs');
      setMessages(prev => [
        ...prev,
        { role: 'user', content: 'Give me some policy suggestions for job creation' },
        { role: 'assistant', content: response.suggestions },
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: `Error getting suggestions: ${error.message}`, isError: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md flex flex-col h-[500px]">
      {/* Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5 text-blue-600" />
          <h3 className="font-bold text-gray-800">Policy Assistant</h3>
        </div>
        <button
          onClick={handleSuggestions}
          disabled={loading}
          className="flex items-center space-x-1 px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200 transition-colors disabled:opacity-50"
        >
          <Sparkles className="w-4 h-4" />
          <span>Get Suggestions</span>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[85%] p-3 rounded-2xl
                ${message.role === 'user'
                  ? 'bg-blue-600 text-white rounded-br-sm'
                  : message.isError
                    ? 'bg-red-50 text-red-800 border border-red-200 rounded-bl-sm'
                    : 'bg-gray-100 text-gray-800 rounded-bl-sm'
                }
              `}
            >
              <div className="flex items-start space-x-2">
                {message.role === 'assistant' && (
                  <Bot className={`w-4 h-4 mt-1 flex-shrink-0 ${message.isError ? 'text-red-500' : 'text-blue-500'}`} />
                )}
                <div className="flex-1">
                  <div className="text-sm whitespace-pre-wrap">{message.content}</div>

                  {/* Apply params button */}
                  {message.hasParams && (
                    <button
                      onClick={() => handleApplyParams(message.params)}
                      className="mt-3 w-full py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Apply These Parameters
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-bl-sm p-3">
              <div className="flex items-center space-x-2">
                <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                <span className="text-sm text-gray-500">Thinking...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Prompt chips */}
      <div className="flex flex-wrap gap-2 px-4 pt-3 pb-1 border-t">
        {[
          "What policy would create the most jobs?",
          "What are the risks of high tariffs?",
          "How does SME stimulus compare to subsidies?",
          "Explain these results in simple terms",
        ].map(chip => (
          <button key={chip} onClick={() => setInput(chip)}
            className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 rounded-full px-3 py-1">
            {chip}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="p-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask about policy options..."
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-400 mt-2 text-center">
          Powered by Claude AI. Responses are for educational purposes.
        </p>
      </div>
    </div>
  );
}

export default ChatPanel;
