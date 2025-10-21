const express = require('express');
const puppeteer = require('puppeteer');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const { performance } = require('perf_hooks');
const { setTimeout } = require('node:timers/promises');

class BrowserPool {
    constructor(maxBrowsers = 50, maxPagesPerBrowser = 5) {
        this.maxBrowsers = maxBrowsers;
        this.maxPagesPerBrowser = maxPagesPerBrowser;
        this.browsers = [];
        this.availableBrowsers = [];
        this.stats = {
            browsersCreated: 0,
            browsersDestroyed: 0,
            screenshotsTaken: 0,
            totalErrors: 0,
            avgScreenshotTime: 0,
            concurrentOperations: 0
        };
        
        this.initializePool();
    }

    async initializePool() {
        console.log(`🚀 Initializing browser pool with ${this.maxBrowsers} browsers...`);
        
        // Create initial browsers (start with 10, scale up as needed)
        const initialBrowsers = Math.min(10, this.maxBrowsers);
        for (let i = 0; i < initialBrowsers; i++) {
            try {
                await this.createBrowser();
            } catch (error) {
                console.error(`Failed to create initial browser ${i}:`, error);
            }
        }
        
        console.log(`✅ Browser pool initialized with ${this.browsers.length} browsers`);
        
        // Start cleanup task
        this.startCleanupTask();
    }

    async createBrowser() {
        try {
            // Detect operating system and set Chrome path
            const os = require('os');
            const fs = require('fs');
            
            let executablePath;
            let launchArgs = [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                '--disable-ipc-flooding-protection',
                '--memory-pressure-off',
                '--force-device-scale-factor=1',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--hide-scrollbars',
                '--disable-logging',
                '--disable-gpu-logging',
                '--silent',
                '--no-crash-upload',
                '--window-size=1400,2000'
            ];
            
            // Platform-specific configuration
            if (os.platform() === 'darwin') {
                // macOS Chrome detection
                const chromeApps = [
                    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                    '/Applications/Chromium.app/Contents/MacOS/Chromium',
                    process.env.CHROME_PATH
                ].filter(Boolean);
                
                for (const chromePath of chromeApps) {
                    if (fs.existsSync(chromePath)) {
                        executablePath = chromePath;
                        console.log(`🔍 Using Chrome at: ${executablePath}`);
                        break;
                    }
                }
                
                // macOS-specific launch arguments for better compatibility
                launchArgs.push(
                    '--disable-features=VizDisplayCompositor',
                    '--use-gl=swiftshader',
                    '--disable-software-rasterizer',
                    '--disable-gpu-sandbox'
                );
                
            } else if (os.platform() === 'linux') {
                // Linux Chrome detection (Amazon Linux 2, Ubuntu, etc.)
                const chromeApps = [
                    '/usr/bin/google-chrome-stable',
                    '/usr/bin/google-chrome',
                    '/usr/bin/chromium-browser',
                    '/usr/bin/chromium',
                    '/opt/google/chrome/chrome',
                    process.env.CHROME_PATH
                ].filter(Boolean);
                
                for (const chromePath of chromeApps) {
                    if (fs.existsSync(chromePath)) {
                        executablePath = chromePath;
                        console.log(`🔍 Using Chrome at: ${executablePath}`);
                        break;
                    }
                }
                
                // Linux-specific optimizations
                launchArgs.push(
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-zygote',
                    '--single-process' // Helps with container environments
                );
            }
            
            const launchConfig = {
                headless: 'new',
                args: launchArgs,
                ignoreHTTPSErrors: true,
                ignoreDefaultArgs: ['--disable-extensions'],
                timeout: 30000
            };
            
            // Add executable path if found
            if (executablePath) {
                launchConfig.executablePath = executablePath;
            }
            
            console.log(`🚀 Launching browser with config:`, {
                executablePath: executablePath || 'bundled',
                headless: launchConfig.headless,
                argsCount: launchArgs.length
            });
            
            const browser = await puppeteer.launch(launchConfig);

            const browserInfo = {
                browser,
                createdAt: Date.now(),
                usageCount: 0,
                activePages: 0,
                isAvailable: true
            };

            this.browsers.push(browserInfo);
            this.availableBrowsers.push(browserInfo);
            this.stats.browsersCreated++;
            
            console.log(`📱 Created new browser (total: ${this.browsers.length})`);
            return browserInfo;
            
        } catch (error) {
            console.error('Failed to create browser:', error);
            this.stats.totalErrors++;
            throw error;
        }
    }

    async getBrowser() {
        // Try to get an available browser
        let browserInfo = this.availableBrowsers.find(b => 
            b.isAvailable && b.activePages < this.maxPagesPerBrowser
        );

        // If no available browser and we can create more
        if (!browserInfo && this.browsers.length < this.maxBrowsers) {
            browserInfo = await this.createBrowser();
        }

        // If still no browser, wait for one to become available
        if (!browserInfo) {
            browserInfo = await this.waitForAvailableBrowser();
        }

        browserInfo.isAvailable = false;
        browserInfo.activePages++;
        browserInfo.usageCount++;
        
        return browserInfo;
    }

    async waitForAvailableBrowser(timeout = 30000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const browserInfo = this.availableBrowsers.find(b => 
                b.isAvailable && b.activePages < this.maxPagesPerBrowser
            );
            
            if (browserInfo) {
                return browserInfo;
            }
            
            // Wait a bit before checking again
            await setTimeout(100);
        }
        
        throw new Error('Timeout waiting for available browser');
    }

    releaseBrowser(browserInfo) {
        browserInfo.activePages = Math.max(0, browserInfo.activePages - 1);
        browserInfo.isAvailable = true;
    }

    async destroyBrowser(browserInfo) {
        try {
            await browserInfo.browser.close();
            this.browsers = this.browsers.filter(b => b !== browserInfo);
            this.availableBrowsers = this.availableBrowsers.filter(b => b !== browserInfo);
            this.stats.browsersDestroyed++;
            console.log(`🗑️ Destroyed browser (remaining: ${this.browsers.length})`);
        } catch (error) {
            console.error('Error destroying browser:', error);
        }
    }

    startCleanupTask() {
        // Clean up old browsers every 5 minutes
        setInterval(async () => {
            const now = Date.now();
            const maxAge = 30 * 60 * 1000; // 30 minutes
            const maxUsage = 100;

            for (const browserInfo of this.browsers) {
                const shouldDestroy = (
                    browserInfo.isAvailable &&
                    browserInfo.activePages === 0 &&
                    (
                        now - browserInfo.createdAt > maxAge ||
                        browserInfo.usageCount > maxUsage
                    )
                );

                if (shouldDestroy) {
                    await this.destroyBrowser(browserInfo);
                }
            }
        }, 5 * 60 * 1000);
    }

    getStats() {
        return {
            ...this.stats,
            totalBrowsers: this.browsers.length,
            availableBrowsers: this.availableBrowsers.filter(b => 
                b.isAvailable && b.activePages < this.maxPagesPerBrowser
            ).length,
            maxBrowsers: this.maxBrowsers,
            maxPagesPerBrowser: this.maxPagesPerBrowser
        };
    }

    async shutdown() {
        console.log('🔄 Shutting down browser pool...');
        
        // Close all browsers
        await Promise.all(
            this.browsers.map(browserInfo => this.destroyBrowser(browserInfo))
        );
        
        console.log('✅ Browser pool shutdown complete');
    }
}

class ScreenshotService {
    constructor(maxBrowsers = 50) {
        this.browserPool = new BrowserPool(maxBrowsers);
        this.app = express();
        this.setupMiddleware();
        this.setupRoutes();
        this.setupGracefulShutdown();
    }

    setupMiddleware() {
        // Security and performance middleware
        this.app.use(helmet({
            contentSecurityPolicy: false // Allow inline styles/scripts for our HTML
        }));
        // Use compression but exclude binary endpoints
        this.app.use(compression({
            filter: (req, res) => {
                // Don't compress screenshot responses (binary data)
                if (req.path === '/screenshot') {
                    return false;
                }
                // Use default compression filter for other responses
                return compression.filter(req, res);
            }
        }));
        this.app.use(cors({
            origin: ['http://localhost:8000', 'http://127.0.0.1:8000'],
            methods: ['GET', 'POST'],
            allowedHeaders: ['Content-Type']
        }));
        this.app.use(express.json({ limit: '10mb' }));
        this.app.use(express.text({ limit: '10mb' }));
    }

    setupRoutes() {
        // Health check endpoint
        this.app.get('/health', (req, res) => {
            const stats = this.browserPool.getStats();
            res.json({
                status: 'healthy',
                timestamp: new Date().toISOString(),
                stats
            });
        });

        // Main screenshot endpoint
        this.app.post('/screenshot', async (req, res) => {
            const startTime = performance.now();
            let browserInfo = null;
            
            try {
                const { html, width = 1400, height = 2000, timeout = 10000 } = req.body;
                
                if (!html) {
                    return res.status(400).json({ error: 'HTML content is required' });
                }

                this.browserPool.stats.concurrentOperations++;
                
                // Get browser from pool
                browserInfo = await this.browserPool.getBrowser();
                
                // Create new page
                const page = await browserInfo.browser.newPage();
                
                try {
                    // Set viewport
                    await page.setViewport({ width, height });
                    
                    // Set timeouts
                    page.setDefaultTimeout(timeout);
                    page.setDefaultNavigationTimeout(timeout);
                    
                    // Set content with optimized loading
                    await page.setContent(html, {
                        waitUntil: 'domcontentloaded',
                        timeout: timeout
                    });
                    
                    // Wait for any dynamic content (MathJax, images)
                    try {
                        await page.waitForFunction(
                            () => {
                                // Check if MathJax is done rendering
                                if (window.MathJax && window.MathJax.startup) {
                                    return window.MathJax.startup.document.state() >= 8; // STATE.RENDERED
                                }
                                // Check if images are loaded
                                const images = document.querySelectorAll('img');
                                return Array.from(images).every(img => img.complete);
                            },
                            { timeout: 5000 }
                        );
                    } catch (waitError) {
                        // Continue even if wait fails - don't block on MathJax
                        console.warn('Wait for content failed, proceeding:', waitError.message);
                    }
                    
                    // Small delay for final rendering
                    await setTimeout(500);
                    
                    // Take screenshot
                    const screenshot = await page.screenshot({
                        type: 'png',
                        fullPage: true,
                        optimizeForSpeed: true
                    });
                    
                    // Update stats
                    const duration = performance.now() - startTime;
                    this.browserPool.stats.screenshotsTaken++;
                    this.browserPool.stats.avgScreenshotTime = 
                        (this.browserPool.stats.avgScreenshotTime + duration) / 2;
                    
                    console.log(`📸 Screenshot completed in ${duration.toFixed(0)}ms`);
                    
                    // Return binary PNG data - use res.end() for proper binary handling
                    res.set('Content-Type', 'image/png');
                    res.set('Content-Length', screenshot.length.toString());
                    res.end(screenshot, 'binary');
                    
                } finally {
                    // Always close the page
                    await page.close();
                }
                
            } catch (error) {
                console.error('Screenshot error:', error);
                this.browserPool.stats.totalErrors++;
                
                res.status(500).json({
                    error: 'Screenshot failed',
                    message: error.message
                });
                
            } finally {
                // Always release browser back to pool
                if (browserInfo) {
                    this.browserPool.releaseBrowser(browserInfo);
                }
                this.browserPool.stats.concurrentOperations--;
            }
        });

        // Stats endpoint
        this.app.get('/stats', (req, res) => {
            res.json(this.browserPool.getStats());
        });
    }

    setupGracefulShutdown() {
        const shutdown = async (signal) => {
            console.log(`\n🔄 Received ${signal}, shutting down gracefully...`);
            
            // Stop accepting new requests
            this.server.close(() => {
                console.log('✅ HTTP server closed');
            });
            
            // Shutdown browser pool
            await this.browserPool.shutdown();
            
            console.log('✅ Screenshot service shutdown complete');
            process.exit(0);
        };

        process.on('SIGTERM', () => shutdown('SIGTERM'));
        process.on('SIGINT', () => shutdown('SIGINT'));
    }

    start(port = 8001) {
        this.server = this.app.listen(port, '127.0.0.1', () => {
            console.log(`🚀 Screenshot service listening on http://127.0.0.1:${port}`);
            console.log(`📊 Browser pool configured for ${this.browserPool.maxBrowsers} browsers`);
        });
        
        return this.server;
    }
}

// Start the service
if (require.main === module) {
    // Configure browser pool size based on available memory
    // Assuming ~400MB per browser, with 25GB allocated = ~60 browsers max
    const maxBrowsers = process.env.MAX_BROWSERS ? 
        parseInt(process.env.MAX_BROWSERS) : 50;
    
    const service = new ScreenshotService(maxBrowsers);
    service.start();
}

module.exports = ScreenshotService;
