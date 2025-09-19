
import React from 'react';
import { Zap } from 'lucide-react';
import Dashboard from './components/dashboard/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50">
   
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Zap className="h-8 w-8 text-green-600" />
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  EV Charging Network Optimizer
                </h1>
                <p className="text-sm text-gray-600">
                  AI-Powered Location Intelligence for Tamil Nadu
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">Tamil Nadu</div>
              <div className="text-xs text-gray-600">India</div>
            </div>
          </div>
        </div>
      </header>

      <Dashboard />


      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Zap className="h-6 w-6 text-green-600" />
                <span className="font-semibold text-gray-900">EV Optimizer</span>
              </div>
              <p className="text-sm text-gray-600">
                Smart AI-powered location optimization for EV charging infrastructure
                in Tamil Nadu using advanced agent-based analysis.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Features</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• Real-time traffic analysis</li>
                <li>• Grid capacity evaluation</li>
                <li>• Competitor mapping</li>
                <li>• ROI calculations</li>
                <li>• AI-powered recommendations</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-4">Technology</h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• LangGraph Orchestration</li>
                <li>• Gemini 1.5 Flash LLM</li>
                <li>• FastAPI Backend</li>
                <li>• React Frontend</li>
                <li>• Weaviate Vector DB</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t pt-8 mt-8">
            <div className="flex items-center justify-between">
              <p className="text-xs text-gray-500">
                © 2024 EV Charging Network Optimizer. Built for Tamil Nadu's sustainable future.
              </p>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span>Version 0.1.0</span>
                <span>•</span>
                <span>API Status: <span className="text-green-600">Online</span></span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;