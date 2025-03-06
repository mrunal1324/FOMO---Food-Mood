import React, { useState, useRef, useEffect } from 'react';

const MoodFoodChat = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [weatherEnabled, setWeatherEnabled] = useState(true);
    const [location, setLocation] = useState('London');
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input.trim();
        setInput('');
        setMessages(prev => [...prev, { type: 'user', content: userMessage }]);
        setIsLoading(true);

        try {
            const response = await simulateApiCall(userMessage);
            setMessages(prev => [...prev, { type: 'bot', content: response }]);
        } catch (error) {
            setMessages(prev => [...prev, { 
                type: 'error', 
                content: 'Sorry, I encountered an error. Please try again.' 
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const simulateApiCall = async (message) => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return {
            mood: 'happy',
            recommendations: [
                'Colorful Mediterranean salad with feta and olives',
                'Fresh fruit smoothie bowl with granola',
                'Light pasta primavera with fresh vegetables'
            ],
            weather: {
                temperature: 72,
                condition: 'sunny'
            }
        };
    };

    const renderMessage = (message, index) => {
        if (message.type === 'user') {
            return (
                <div key={index} className="flex items-start gap-4 justify-end animate-fade-in">
                    <div className="bg-food-primary text-white px-4 py-3 rounded-2xl shadow-soft hover:shadow-hover transition-all duration-300 max-w-[80%]">
                        {message.content}
                    </div>
                    <div className="w-10 h-10 bg-food-accent rounded-full flex items-center justify-center text-food-text flex-shrink-0 shadow-soft">
                        👤
                    </div>
                </div>
            );
        } else if (message.type === 'bot') {
            return (
                <div key={index} className="flex items-start gap-4 animate-fade-in">
                    <div className="w-10 h-10 bg-food-secondary rounded-full flex items-center justify-center text-white flex-shrink-0 shadow-soft animate-float">
                        🍽️
                    </div>
                    <div className="bg-white px-4 py-3 rounded-2xl shadow-soft max-w-[80%] hover:shadow-hover transition-all duration-300">
                        <div className="mb-4">
                            <h3 className="text-lg font-semibold text-food-text mb-2">
                                Detected Mood: {message.content.mood}
                            </h3>
                            {message.content.weather && (
                                <p className="text-food-neutral-600">
                                    Weather: {message.content.weather.temperature}°F, {message.content.weather.condition}
                                </p>
                            )}
                        </div>
                        <div>
                            <h4 className="text-lg font-semibold text-food-text mb-2">
                                Recommended Foods:
                            </h4>
                            <ul className="list-none space-y-2">
                                {message.content.recommendations.map((rec, idx) => (
                                    <li key={idx} className="flex items-center gap-2 text-food-neutral-700">
                                        <span className="text-food-accent">•</span>
                                        {rec}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>
                </div>
            );
        } else {
            return (
                <div key={index} className="flex justify-center animate-fade-in">
                    <div className="bg-food-error/10 text-food-error px-4 py-3 rounded-2xl shadow-soft">
                        {message.content}
                    </div>
                </div>
            );
        }
    };

    return (
        <div className="min-h-screen bg-food-background p-4">
            <div className="max-w-4xl mx-auto h-[80vh] bg-white rounded-2xl shadow-lg flex flex-col overflow-hidden">
                <div className="bg-gradient-food p-6 text-white relative overflow-hidden">
                    <div className="absolute inset-0 bg-white/10 backdrop-blur-sm"></div>
                    <div className="relative z-10">
                        <h1 className="text-3xl font-bold mb-4 flex items-center gap-2">
                            <span className="text-food-accent">🍽️</span>
                            FeelFood
                        </h1>
                        <div className="flex flex-wrap gap-4">
                            <button 
                                onClick={() => setWeatherEnabled(!weatherEnabled)}
                                className={`px-4 py-2 rounded-full transition-all duration-300 ${
                                    weatherEnabled 
                                        ? 'bg-white/20 font-semibold' 
                                        : 'bg-white/10 hover:bg-white/15'
                                }`}
                            >
                                {weatherEnabled ? '🌤️ Weather On' : '🌤️ Weather Off'}
                            </button>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={location}
                                    onChange={(e) => setLocation(e.target.value)}
                                    placeholder="Enter location"
                                    className="bg-white/20 border-none px-4 py-2 rounded-full text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white/30"
                                />
                                <button 
                                    onClick={() => setLocation(location)}
                                    className="bg-white/20 hover:bg-white/30 px-4 py-2 rounded-full transition-all duration-300"
                                >
                                    📍
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-food-neutral-50">
                    {messages.map((message, index) => renderMessage(message, index))}
                    {isLoading && (
                        <div className="flex items-start gap-4 animate-fade-in">
                            <div className="w-10 h-10 bg-food-secondary rounded-full flex items-center justify-center text-white flex-shrink-0 shadow-soft">
                                🍽️
                            </div>
                            <div className="bg-white px-4 py-3 rounded-2xl shadow-soft">
                                <div className="flex space-x-2">
                                    <span className="w-2 h-2 bg-food-primary rounded-full animate-bounce"></span>
                                    <span className="w-2 h-2 bg-food-primary rounded-full animate-bounce delay-100"></span>
                                    <span className="w-2 h-2 bg-food-primary rounded-full animate-bounce delay-200"></span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                <form onSubmit={handleSubmit} className="p-6 border-t border-food-neutral-200 bg-white">
                    <div className="flex gap-4">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Tell me how you're feeling..."
                            disabled={isLoading}
                            className="flex-1 px-4 py-3 rounded-xl border border-food-neutral-200 focus:outline-none focus:ring-2 focus:ring-food-primary focus:border-transparent transition-all duration-300 disabled:bg-food-neutral-50 disabled:cursor-not-allowed"
                        />
                        <button 
                            type="submit" 
                            disabled={isLoading}
                            className="px-6 py-3 bg-food-primary text-white rounded-xl font-semibold hover:bg-food-primary/90 focus:outline-none focus:ring-2 focus:ring-food-primary focus:ring-offset-2 transition-all duration-300 disabled:bg-food-neutral-400 disabled:cursor-not-allowed"
                        >
                            {isLoading ? '...' : 'Send'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default MoodFoodChat; 