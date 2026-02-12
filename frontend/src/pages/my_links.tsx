import { useState, useEffect } from 'react'
import { useAuth } from '../context/auth_context'
import axios from 'axios'

const MyLinks = () => {
    const { user } = useAuth()
    const [links, setLinks] = useState<any[]>([])
    const [headers, setHeaders] = useState<any[]>([])
    
    useEffect(() => {
        axios.get('http://localhost:9002/urls/', { withCredentials: true })
            .then((response: any) => {
                setLinks(response.data);
                setHeaders(Object.keys(response.data[0]));
            })
            .catch((error: any) => console.error(error))
    }, [])

    return (
        <div className="m-4 max-w-7xl mx-auto">
            {links.length > 0 ? (
            <table className="table-fixed w-full mx-auto">
                <thead className="bg-gray-100">
                    <tr>
                        {headers.filter((key: any) => key !== 'id' && key !== 'user_id').map((key: any) => (
                            <th key={key}>{key.toUpperCase().replace(/_/g, ' ')}</th>
                        ))}
                        <th>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    {links.map((link: any) => (
                        <tr key={link.id}>
                        {headers
                            .filter((header: string) => header !== 'id' && header !== 'user_id')
                            .map((header: string) => 
                            // Note: No curly braces here around the ternary!
                            header.toLowerCase() === "url" ? (
                                <td key={`${header}_${link.id}`}>
                                <a className="text-blue-500 hover:underline" href={link[header]} target="_blank" rel="noopener noreferrer">
                                    {link[header]}
                                </a>
                                </td>
                            ) : (
                                <td key={`${header}_${link.id}`}>
                                {link[header]}
                                </td>
                            )
                            )}
                            <td>
                                <button className="bg-red-500 text-white p-2 rounded-md">Delete</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
            </table>
            ) : (
                <p>You haven't added any links yet</p>
            )}
        </div>
    )
}

export default MyLinks;