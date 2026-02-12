import { useState, useEffect } from 'react';
import axios from 'axios';

interface ProgressBarProps {
  taskId: string;
  onComplete: (object: any) => void;
}

const ProgressBar = ({ taskId, onComplete }: ProgressBarProps) => {
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // idle, loading, complete, error
  const [message, setMessage] = useState('');
  const [url, setUrl] = useState('');
  const [object, setObject] = useState(null);

  useEffect(() => {
    if (!taskId) return;

    // Reset state for new taskId
    setProgress(0);
    setStatus('loading');

    const eventSource = new EventSource(`http://localhost:9002/urls/progress/${taskId}`, { withCredentials: true });

    eventSource.addEventListener("result", (event) => {
        console.log(event.data);
        const result = JSON.parse(event.data);
        setProgress(result.progress);
        setStatus(result.status);
        setMessage(result.message);
        setUrl(result.url);
        setObject(result.object);
        eventSource.close();
        onComplete(result.object);
      });
    
    eventSource.addEventListener("update", (event) => {
        console.log(event.data);
        const { progress, status, message, url, object } = JSON.parse(event.data);
        setProgress(progress);
        setStatus(status);
        setMessage(message);
        setUrl(url);
        setObject(object);
      });

    eventSource.onerror = (err) => {
        if (object) {
            return;
        }
        console.error("SSE connection closed or failed:", err);
        setStatus('error');
        eventSource.close();
    };

    // Cleanup: Close connection when component unmounts or URL changes
    return () => {
      eventSource.close();
    };
  }, [taskId]); // Dependency array ensures this runs every time 'taskId' changes

  return (
    <div className="progress-container" style={{ margin: '20px 0' }}>
      <div style={{ width: '100%', background: '#e0e0e0', borderRadius: '8px' }}>
        <div style={{ 
          width: `${progress}%`, 
          background: status === 'error' ? '#ff4d4f' : '#1890ff', 
          height: '10px', 
          borderRadius: '8px',
          transition: 'width 0.4s ease-out' 
        }} />
      </div>
      <small>Status: {status} ({progress}%)</small>
      <small>{message}</small>
    </div>
  );
};

export default ProgressBar;