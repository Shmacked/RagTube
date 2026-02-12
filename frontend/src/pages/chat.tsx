import { useState, useEffect, useRef } from 'react'
import { useAuth } from '../context/auth_context'
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid';
import ChatResponse from '../components/markdown_renderer';

const Chat = () => {
    const { user } = useAuth()
    const [input, setInput] = useState('')
    const [messages, setMessages] = useState<any[]>([])
    const [summary, setSummary] = useState('')
    const [waitingForResponse, setWaitingForResponse] = useState(false)

    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, summary]);

    useEffect(() => {
        axios.get('http://localhost:9002/chat/', { withCredentials: true })
            .then((response: any) => {
                console.log(response.data);
                setMessages(response.data.messages)
                setSummary(response.data.summary)
            })
            .catch((error: any) => console.error(error));
    }, []);

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();

        if (waitingForResponse) return;

        setWaitingForResponse(true)
    
        // 1. Add user message using functional update
        setMessages(prev => [...prev, { id: uuidv4(), type: 'human', content: input }]);
        setInput('');
    
        axios.post('http://localhost:9002/chat/', { input: input }, { withCredentials: true })
            .then((response: any) => {
                // 2. Add AI message using functional update (prev will now include the user message)
                setMessages(prev => [...prev, response.data.output]);
                setWaitingForResponse(false)
            })
            .catch((error: any) => {
                console.error(error)
                setWaitingForResponse(false)
            });
    }
    
    return (
        <div className="flex flex-col flex-1 min-h-0 w-full">
            <div className="flex flex-col w-full p-4 flex-1 min-h-0">
                <div className="flex flex-col items-stretch w-full border-2 border-gray-300 rounded-md p-0 overflow-y-auto flex-1 min-h-0">
                    {summary && <div className="bg-red-200 rounded-md p-2 m-2 text-left"><ChatResponse content={summary} /></div>}
                    {messages.map((message: any) => {
                        if (message.type === 'human') {
                            return <div key={message.id} className="bg-blue-200 rounded-lg p-2 m-2 ml-12 self-end shadow-sm text-left"><ChatResponse content={message.content} /></div>
                        } else {
                            return <div key={message.id} className="bg-gray-200 rounded-lg p-2 m-2 mr-12 self-start shadow-sm text-left"><ChatResponse content={message.content} /></div>
                        }
                    })}
                    <div ref={scrollRef} />
                </div>
            </div>
            <form onSubmit={handleSubmit} className="flex flex-row items-center justify-center w-full shrink-0 gap-2 p-4">
                <input type="text" placeholder="Message..." value={input} onChange={(e) => setInput(e.target.value)} className="border-2 border-gray-300 rounded-md p-2 w-full" />
                <button type="submit" className="bg-blue-500 text-white p-2 rounded-md" disabled={waitingForResponse}>{waitingForResponse? 'Thinking...' : 'Send'}</button>
            </form>
        </div>
    );
};

export default Chat;