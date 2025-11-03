import React, { useState, useEffect } from 'react';

const TestComponent = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const testFetch = async () => {
      try {
        console.log('Testing API connection...');
        console.log('Base URL:', import.meta.env.VITE_BASE_URL);
        
        const response = await fetch(`${import.meta.env.VITE_BASE_URL}/customers`);
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (response.ok) {
          const result = await response.json();
          console.log('Data received:', result);
          setData(result);
        } else {
          setError(`HTTP ${response.status}: ${response.statusText}`);
        }
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    testFetch();
  }, []);

  if (loading) {
    return <div className="p-4">Loading test...</div>;
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded">
        <h2 className="text-red-800 font-bold">Error:</h2>
        <p className="text-red-600">{error}</p>
        <p className="text-sm text-gray-600 mt-2">
          Base URL: {import.meta.env.VITE_BASE_URL}
        </p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-green-50 border border-green-200 rounded">
      <h2 className="text-green-800 font-bold">Success!</h2>
      <p className="text-green-600">API connection working</p>
      <p className="text-sm text-gray-600">
        Received {data?.customers?.length || 0} customers
      </p>
    </div>
  );
};

export default TestComponent;