#!/usr/bin/env node

const ScreenshotService = require('./server');

// Simple test script
async function test() {
    console.log('🧪 Starting screenshot service test...');
    
    const service = new ScreenshotService(5); // Small pool for testing
    const server = service.start(8002); // Use different port for testing
    
    // Wait for service to start
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    try {
        const fetch = require('node:fetch');
        
        // Test HTML content
        const testHtml = `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; }
                .test-box { 
                    background: #f0f0f0; 
                    padding: 20px; 
                    border-radius: 8px;
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <h1>Screenshot Test</h1>
            <div class="test-box">
                <p>This is a test of the screenshot service.</p>
                <p>If you can see this text clearly in a PNG image, the service is working!</p>
            </div>
        </body>
        </html>
        `;
        
        console.log('📡 Testing screenshot endpoint...');
        const response = await fetch('http://127.0.0.1:8002/screenshot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ html: testHtml })
        });
        
        if (response.ok) {
            const imageData = await response.arrayBuffer();
            console.log(`✅ Screenshot successful! Received ${imageData.byteLength} bytes`);
        } else {
            console.error('❌ Screenshot failed:', response.status, response.statusText);
        }
        
        // Test health endpoint
        console.log('🏥 Testing health endpoint...');
        const healthResponse = await fetch('http://127.0.0.1:8002/health');
        const healthData = await healthResponse.json();
        console.log('✅ Health check:', healthData.status);
        console.log('📊 Stats:', healthData.stats);
        
    } catch (error) {
        console.error('❌ Test failed:', error);
    } finally {
        server.close();
        process.exit(0);
    }
}

if (require.main === module) {
    test();
}
