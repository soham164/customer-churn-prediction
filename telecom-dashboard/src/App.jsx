import React from 'react';
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './index.css';
import Telecom from './Telecom';

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <Telecom />
    </>
  )
}

export default App
