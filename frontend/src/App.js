import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaDocker } from 'react-icons/fa';
import { FaFileZipper } from 'react-icons/fa6';
import { IoMdDownload } from 'react-icons/io';
import { GoogleGenerativeAI } from '@google/generative-ai';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { solarizedlight } from 'react-syntax-highlighter/dist/esm/styles/prism';

const genAI = new GoogleGenerativeAI('<Gemini API key>'); // Replace with your actual API key

const App = () => {
  const [zipFile, setZipFile] = useState(null);
  const [dockerFile, setDockerFile] = useState(null);
  const [imageName, setImageName] = useState('');
  const [endpoint, setEndpoint] = useState('');
  const [loading, setLoading] = useState(false);
  const [output, setOutput] = useState(null);
  const [error, setError] = useState('');
  const [fileError, setFileError] = useState('');
  const [renderLog, setRenderLog] = useState(false);
  const [dockerFileError, setDockerFileError] = useState('');
  const [logs, setLogs] = useState([]);
  const [solution, setSolution] = useState('');
  const [generatingSolution, setGeneratingSolution] = useState(false);


  const handleFileChange = (e) => {
    setZipFile(e.target.files[0]);
    setFileError('');
  };

  const handleDockerFileChange = (e) => {
    setDockerFile(e.target.files[0]);
    setDockerFileError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!zipFile && !dockerFile) {
      setFileError("Please upload a Zip file!");
      setDockerFileError("Please upload a Docker file!");
      return;
    } else if (!zipFile) {
      setFileError("Please upload a Zip file!");
      return;
    } else if (!dockerFile) {
      setDockerFileError("Please upload a Docker file!");
      return;
    } else if (dockerFile && dockerFile.name !== 'Dockerfile') {
      setDockerFileError("Please upload a valid Docker file!");
      return;
    }

    setLoading(true);
    setError('');
    setOutput(null);
    setLogs([]); // Clear previous logs
    setRenderLog(true);
    setSolution('');
    const formData = new FormData();
    formData.append('Dockerfile', dockerFile);
    formData.append('zip_file', zipFile);
    formData.append('image_name', imageName);
    formData.append('endpoint', endpoint);

    try {
      const response = await axios.post("http://localhost:5000/api/v1/build_and_run", formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setOutput(response.data.urls);
    } catch (err) {
      console.error('API Error:', err);
      if (err.response) {
        setError(err.response.data.error || 'An error occurred while processing your request.');
      } else if (err.request) {
        setError('No response received from the server. Please try again later.');
      } else {
        setError('An error occurred while sending the request. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Listen to log events from the server
  useEffect(() => {
    const eventSource = new EventSource('http://localhost:5000/api/v1/logs');

    eventSource.onmessage = (event) => {
      if(!event.data.includes('Heartbeat')){
        console.log('Log received:', event.data); // Debug log
        setLogs((prevLogs) => [...prevLogs, event.data]);
      }
    };

    eventSource.onerror = (error) => {
      console.error('EventSource error:', error);
    };

    return () => {
      eventSource.close(); // Cleanup on component unmount
    };
  }, []);

  // Function to download logs as a .txt file
  const downloadLogs = () => {
    const logText = logs.join("\n");  // Join logs with newline characters
    const element = document.createElement("a");
    const file = new Blob([logText], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "logs.txt";
    document.body.appendChild(element); // Append to body
    element.click(); // Trigger the download
    document.body.removeChild(element); // Clean up
  };

  const generateSolution = async () => {
    setGeneratingSolution(true);
    try {
      const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });
      const prompt = `Given the following error and build logs, suggest a solution:
      
      Error: ${error}
      
      Build Logs:
      ${logs.join('\n')}
      
      Provide a step-by-step solution to resolve this issue. Use markdown formatting for better readability, including code blocks where appropriate:`;

      const result = await model.generateContent(prompt);
      setSolution(result.response.text());
    } catch (err) {
      console.error('Error generating solution:', err);
      setSolution('Failed to generate a solution. Please try again.');
    } finally {
      setGeneratingSolution(false);
    }
  };

  const renderOutput = () => {
    if (!output || !Array.isArray(output)) return null;

    return (
      <div className="mt-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative overflow-hidden break-words">
        <h2 className="text-xl font-semibold mb-2">Success!</h2>
        <p>Your Image has been created and Containerized successfully.</p>
        {output.map((item, index) => (
          <div key={index} className="mt-4">
            {item && (
              <p className="mt-2">
                Docker Image URL: <a href={item} className="text-blue-500 hover:underline" target="_blank" rel="noopener noreferrer">{item}</a>
              </p>
            )}
          </div>
        ))}
      </div>
    );
  };

  const renderLogs = () => (
    <div className="mt-4 bg-gray-100 border border-gray-400 text-gray-800 px-4 py-3 rounded relative max-h-60">
      {/* Container for the title and button */}
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-xl font-semibold">Logs</h2>
        {/* Download Logs button with centered icon and fixed positioning for responsiveness */}
        <button
          className="bg-blue-500 h-10 w-10 flex items-center justify-center text-white rounded hover:bg-blue-600 transition duration-300 sticky top-0 right-0 z-10"
          onClick={downloadLogs}
        >
          <IoMdDownload className="h-6 w-6" />
        </button>
      </div>

      {/* Scrollable logs */}
      <div className="overflow-y-auto max-h-40 pr-2">
        {logs.map((log, index) => (
          <p key={index} className="break-words">{log}</p>
        ))}
      </div>
    </div>
  );
  const renderError = () => (
    <div className="mt-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 sm:px-6 sm:py-4 lg:px-8 lg:py-5 rounded relative">
      <strong>Error:</strong> {error}
      <br />
      <button
        onClick={generateSolution}
        disabled={generatingSolution}
         flex items-center justify-center
        className="mt-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300 text-white font-bold py-2 px-4 sm:px-6 sm:py-2 lg:px-8 lg:py-3 rounded"
      >
        {generatingSolution ? 'Generating Solution...' : 'Generate Solution'}
      </button>
      {solution && (
        <div className="mt-4 bg-white border border-gray-300 text-gray-800 px-4 py-3 sm:px-6 sm:py-4 lg:px-8 lg:py-5 rounded relative">
          <strong className="block mb-2 text-sm sm:text-base lg:text-lg">
            Suggested Solution:
          </strong>
          <ReactMarkdown
            children={solution}
            components={{
              code({ node, inline, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    children={String(children).replace(/\n$/, '')}
                    style={solarizedlight}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  />
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              },
            }}
          />
        </div>
      )}
    </div>
  );  

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 break-words">
      <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-2xl">
        <h1 className="text-2xl font-bold mb-4 text-center">AI Driven Automated Docker Image Creation</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Image Name Input */}
          <div>
            <label className="block text-gray-700">Image Name</label>
            <input
              type="text"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              value={imageName}
              onChange={(e) => setImageName(e.target.value)}
              required
            />
          </div>
          {/* API Endpoint Input */}
          <div>
            <label className="block text-gray-700">API Endpoint</label>
            <input
              type="number"
              className="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              required
            />
          </div>

          {/* File upload section for Dockerfile and Zip file */}
          <div className='flex flex-col md:flex-row items-center justify-center space-y-4 md:space-y-0 md:space-x-3'>
            {/* Dockerfile upload */}
            <div className="relative flex justify-center items-center w-full md:w-1/2 h-36 bg-gray-100 rounded-lg border-2 border-dashed border-gray-400 p-4 cursor-pointer hover:bg-gray-200 transition duration-300">
              <input
                type="file"
                className="absolute inset-0 opacity-0 cursor-pointer"
                id="dockerFileInput"
                onChange={handleDockerFileChange}
                accept="Dockerfile"
              />
              <label htmlFor="dockerFileInput" className="flex flex-col items-center justify-center w-full h-full cursor-pointer">
                <FaDocker className="w-10 h-10 text-blue-500"/>
                <span className="mt-2 text-gray-600">Upload Dockerfile</span>
                {dockerFile && (
                  <span className="mt-1 text-blue-500">{dockerFile.name}</span>
                )}
              </label>
            </div>

            {/* Zip file upload */}
            <div className="relative flex justify-center items-center w-full md:w-1/2 h-36 bg-gray-100 rounded-lg border-2 border-dashed border-gray-400 p-4 cursor-pointer hover:bg-gray-200 transition duration-300">
              <input
                type="file"
                className="absolute inset-0 opacity-0 cursor-pointer"
                id="zipFileInput"
                onChange={handleFileChange}
                accept=".zip"
              />
              <label htmlFor="zipFileInput" className="flex flex-col items-center justify-center w-full h-full cursor-pointer">
                <FaFileZipper className="w-10 h-10 text-green-500"/>
                <span className="mt-2 text-gray-600">Upload Zip file</span>
                {zipFile && (
                  <span className="mt-1 text-blue-500">{zipFile.name}</span>
                )}
              </label>
            </div>
          </div>

          {/* Display file errors, if any */}
          {dockerFileError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{dockerFileError}</span>
            </div>
          )}
          {fileError && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
              <span className="block sm:inline">{fileError}</span>
            </div>
          )}

          {/* Submit button */}
          <div className="flex justify-center">
            <button
              type="submit"
              className="w-full py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition duration-300 flex items-center justify-center"
              disabled={loading}
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 mr-3 border-t-2 border-b-2 border-white rounded-full" viewBox="0 0 24 24"></svg>
                  Processing...
                </>
              ) : (
                "Submit"
              )}
            </button>
          </div>
        </form>

        {/* Display error if any */}
        {error && renderError()}

        {/* Render the output if available */}
        {output && renderOutput()}
        {/* Render the output if available */}
        {renderLog && renderLogs()}
      </div>
    </div>
  );
};

export default App;