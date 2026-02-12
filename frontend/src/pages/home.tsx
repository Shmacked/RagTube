import React from 'react'
import logo from '../assets/rag_tube.png'

const Home = () => {
    return (
        <div className="flex flex-col items-center justify-center h-full">
            <img src={logo} alt="RagTube" className="h-1/2" />
        </div>
    );
};

export default Home;