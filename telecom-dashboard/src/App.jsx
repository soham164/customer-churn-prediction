import React from 'react';
import { useState } from 'react'
import './index.css';
import Telecom from './Telecom';
import TestComponent from './TestComponent';

function App() {
  const [showTest, setShowTest] = useState(false);

  return (
    <>
      {showTest ? (
        <div className="p-4">
          <button 
            onClick={() => setShowTest(false)}
            className="mb-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Back to Dashboard
          </button>
          <TestComponent />
        </div>
      ) : (
        <div>
          <button 
            onClick={() => setShowTest(true)}
            className="fixed top-4 right-4 z-50 px-3 py-1 bg-gray-500 text-white text-sm rounded hover:bg-gray-600"
          >
            Test API
          </button>
          <Telecom />
        </div>
      )}
    </>
  )
}

export default App
