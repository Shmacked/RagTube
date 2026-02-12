import { useState, useEffect } from 'react'
import { useAuth } from '../context/auth_context'
import axios from 'axios'
import { Trash2, Plus, ArrowUp, ArrowDown } from 'lucide-react'
import ProgressBar from '../components/progress_bar'

const MyLinks = () => {
    const { user } = useAuth()
    const [links, setLinks] = useState<any[]>([])
    const [headers, setHeaders] = useState<any[]>([])
    const [ragYoutubeLink, setRagYoutubeLink] = useState('')
    const [showProgressBar, setShowProgressBar] = useState(false)
    const [taskId, setTaskId] = useState('')
    const [sortBy, setSortBy] = useState('newest')

    // Helper function to sort links oldest -> newest
    const sortLinks = (data: any[], sortBy: string) => {
        return [...data].sort((a, b) => {
            // Priority 1: Use created_at date
            // Priority 2: Fallback to ID if date is missing
            const dateA = a.created_at ? new Date(a.created_at).getTime() : a.id;
            const dateB = b.created_at ? new Date(b.created_at).getTime() : b.id;
            return sortBy === 'newest' ? dateB - dateA : dateA - dateB;
        });
    }

    const handleAddRagYoutubeLink = () => {
        setShowProgressBar(true)
        axios.post(`http://localhost:9002/urls/?url=${ragYoutubeLink}`, {}, { withCredentials: true })
            .then((response: any) => {
                setRagYoutubeLink('')
                // setShowProgressBar(false)
                setTaskId(response.data.task_id)
                localStorage.setItem('active_task_id', response.data.task_id);
            })
            .catch((error: any) => {
                console.error(error)
                alert('Failed to add link')
                setShowProgressBar(false)
                setTaskId('')
                localStorage.removeItem('active_task_id');
            })
    }

    const handleDeleteLink = (e: React.MouseEvent<HTMLButtonElement>, linkId: number) => {
        e.preventDefault()
        axios.delete(`http://localhost:9002/urls/?linkId=${linkId}`, { withCredentials: true })
            .then((response: any) => {
                if (response.status === 200) {
                    setLinks(sortLinks(links.filter((link: any) => link.id !== linkId), sortBy))
                } else {
                    alert('Failed to delete link')
                }
            })
            .catch((error: any) => {
                console.error(error)
                alert('Failed to delete link')
            })
    }

    const handleTaskComplete = (newObject: any) => {
        // 1. Hide the progress bar
        setShowProgressBar(false);
        setTaskId('');
        localStorage.removeItem('active_task_id');

        // 2. Update the links list immediately so the user sees the new item
        if (newObject) {
            setLinks((prevLinks) => sortLinks([newObject, ...prevLinks], sortBy));
            
            // If headers are empty (first link added), set them here
            if (headers.length === 0) {
                setHeaders(Object.keys(newObject));
            }
        }
    };

    useEffect(() => {
        axios.get('http://localhost:9002/urls/', { withCredentials: true })
            .then((response: any) => {
                if (response.data.length == 0) {
                    return;
                }
                setLinks(sortLinks(response.data, sortBy));
                setHeaders(Object.keys(response.data[0]));
            })
            .catch((error: any) => console.error(error))
    }, [])

    useEffect(() => {
        const savedTaskId = localStorage.getItem('active_task_id');
        if (savedTaskId) {
            setTaskId(savedTaskId);
            setShowProgressBar(true);
        }
    }, [])

    return (
        <div className="m-4 max-w-7xl mx-auto">
            {showProgressBar? ( <div className="mt-4 w-full"><ProgressBar taskId={taskId} onComplete={handleTaskComplete} /></div> ) : (
                <div className="flex flex-row items-center justify-center gap-2">
                    <input type="text" placeholder="Rag Youtube Link" className="w-full max-w-md px-4 py-2 rounded-lg border-2 border-gray-300" value={ragYoutubeLink} onChange={(e) => setRagYoutubeLink(e.target.value)} />
                    <button className="bg-blue-500 text-white px-6 py-2 rounded-lg shadow-lg 
                        transition-all duration-150 
                        hover:shadow-md hover:translate-y-0.5 
                        active:shadow-none active:translate-y-1 cursor-pointer"
                        onClick={() => handleAddRagYoutubeLink()}>
                            <Plus className="w-6 h-6" />
                    </button>
                </div>
            )}
            <div className="mt-4 w-full">
                {links.length > 0 ? (
                <table className="table-fixed w-full mx-auto">
                    <thead className="bg-gray-100 border-b border-gray-200">
                        <tr>
                            {headers.filter((key: any) => key !== 'id' && key !== 'user_id').map((key: any) => (
                                <th className="px-4 py-2 text-center" key={key}>
                                    {key === 'created_at' ? (
                                        /* inline-flex + justify-center keeps the pair centered as one unit */
                                        <div 
                                            className="inline-flex items-center justify-center gap-2 cursor-pointer select-none hover:text-blue-600 transition-colors" 
                                            onClick={() => {
                                                const nextSort = sortBy === 'newest' ? 'oldest' : 'newest';
                                                setSortBy(nextSort);
                                                setLinks(sortLinks(links, nextSort));
                                            }}
                                        >
                                            <span>{key.toUpperCase().replace(/_/g, ' ')}</span>
                                            {sortBy === 'newest' ? (
                                                <ArrowUp className="w-4 h-4" />
                                            ) : (
                                                <ArrowDown className="w-4 h-4" />
                                            )}
                                        </div>
                                    ) : (
                                        key.toUpperCase().replace(/_/g, ' ')
                                    )}
                                </th>
                            ))}
                            <th className="px-4 py-2"></th>
                        </tr>
                    </thead>
                    <tbody>
                        {links.map((link: any) => (
                            <tr className="border-b border-gray-200" key={link.id}>
                            {headers
                                .filter((header: string) => header !== 'id' && header !== 'user_id')
                                .map((header: string) => 
                                // Note: No curly braces here around the ternary!
                                header.toLowerCase() === "url" ? (
                                    <td className="px-4 py-2" key={`${header}_${link.id}`}>
                                    <a className="text-blue-500 hover:underline" href={link[header]} target="_blank" rel="noopener noreferrer">
                                        {link[header]}
                                    </a>
                                    </td>
                                ) : (
                                    <td className="px-4 py-2" key={`${header}_${link.id}`}>
                                    {link[header]}
                                    </td>
                                )
                                )}
                                <td className="px-4 py-2">
                                    <button className="bg-red-500 text-white px-6 py-2 rounded-lg shadow-lg 
                                        transition-all duration-150 
                                        hover:shadow-md hover:translate-y-0.5 
                                        active:shadow-none active:translate-y-1"
                                        onClick={(e: React.MouseEvent<HTMLButtonElement>) => handleDeleteLink(e, link.id)}>
                                            <Trash2 className="w-6 h-6" />
                                        </button>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                </table>
                ) : (
                    <p>You haven't added any links yet</p>
                )}
            </div>
        </div>
    )
}

export default MyLinks;