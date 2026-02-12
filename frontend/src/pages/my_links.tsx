import { useState, useEffect } from 'react'
import { useAuth } from '../context/auth_context'
import axios from 'axios'
import { Trash2, Plus } from 'lucide-react'
import ProgressBar from '../components/progress_bar'

const MyLinks = () => {
    const { user } = useAuth()
    const [links, setLinks] = useState<any[]>([])
    const [headers, setHeaders] = useState<any[]>([])
    const [ragYoutubeLink, setRagYoutubeLink] = useState('')
    const [showProgressBar, setShowProgressBar] = useState(false)
    const [taskId, setTaskId] = useState('')

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
                    setLinks(links.filter((link: any) => link.id !== linkId))
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
            setLinks((prevLinks) => [newObject, ...prevLinks]);
            
            // If headers are empty (first link added), set them here
            if (headers.length === 0) {
                setHeaders(Object.keys(newObject));
            }
        }
    };

    useEffect(() => {
        axios.get('http://localhost:9002/urls/', { withCredentials: true })
            .then((response: any) => {
                setLinks(response.data);
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
            {showProgressBar? ( <div className="mt-4 w-full"><ProgressBar taskId={taskId} onComplete={handleTaskComplete} /></div> ) : ( null )}
            <div className="mt-4 w-full">
                {links.length > 0 ? (
                <table className="table-fixed w-full mx-auto">
                    <thead className="bg-gray-100 border-b border-gray-200">
                        <tr>
                            {headers.filter((key: any) => key !== 'id' && key !== 'user_id').map((key: any) => (
                                <th className="px-4 py-2" key={key}>{key.toUpperCase().replace(/_/g, ' ')}</th>
                            ))}
                            <th className="px-4 py-2">
                                {/* Delete button column header */}
                            </th>
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