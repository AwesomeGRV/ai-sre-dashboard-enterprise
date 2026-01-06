const express = require('express');
const axios = require('axios');
const app = express();
const port = 3000;

// Metrics for tracking
let requestCount = 0;
let errorCount = 0;
let responseTimeSum = 0;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  const startTime = Date.now();
  
  // Simulate occasional failures for demo
  if (Math.random() < 0.1) {
    errorCount++;
    return res.status(500).json({ status: 'unhealthy', error: 'Simulated failure' });
  }
  
  requestCount++;
  const responseTime = Date.now() - startTime;
  responseTimeSum += responseTime;
  
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    metrics: {
      requestCount,
      errorCount,
      avgResponseTime: responseTimeSum / requestCount
    }
  });
});

// API endpoints that simulate different services
app.get('/api/users', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Simulate database call
    await new Promise(resolve => setTimeout(resolve, Math.random() * 100 + 50));
    
    requestCount++;
    const responseTime = Date.now() - startTime;
    responseTimeSum += responseTime;
    
    res.json({
      users: [
        { id: 1, name: 'John Doe', email: 'john@example.com' },
        { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
      ],
      responseTime
    });
  } catch (error) {
    errorCount++;
    res.status(500).json({ error: 'Failed to fetch users' });
  }
});

app.get('/api/orders', async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Simulate external API call
    await new Promise(resolve => setTimeout(resolve, Math.random() * 200 + 100));
    
    // Simulate occasional errors
    if (Math.random() < 0.15) {
      throw new Error('External service unavailable');
    }
    
    requestCount++;
    const responseTime = Date.now() - startTime;
    responseTimeSum += responseTime;
    
    res.json({
      orders: [
        { id: 1, userId: 1, amount: 99.99, status: 'completed' },
        { id: 2, userId: 2, amount: 149.99, status: 'pending' }
      ],
      responseTime
    });
  } catch (error) {
    errorCount++;
    res.status(503).json({ error: 'Orders service temporarily unavailable' });
  }
});

// Load generation endpoint for testing
app.post('/api/load', (req, res) => {
  const { intensity = 'medium' } = req.body;
  const delays = { low: 50, medium: 150, high: 300 };
  const delay = delays[intensity] || delays.medium;
  
  setTimeout(() => {
    requestCount++;
    res.json({ message: `Load test completed with ${intensity} intensity`, delay });
  }, delay);
});

// Metrics endpoint for Prometheus
app.get('/metrics', (req, res) => {
  const metrics = [
    `# HELP http_requests_total Total number of HTTP requests`,
    `# TYPE http_requests_total counter`,
    `http_requests_total ${requestCount}`,
    '',
    `# HELP http_errors_total Total number of HTTP errors`,
    `# TYPE http_errors_total counter`,
    `http_errors_total ${errorCount}`,
    '',
    `# HELP http_response_time_avg Average HTTP response time`,
    `# TYPE http_response_time_avg gauge`,
    `http_response_time_avg ${requestCount > 0 ? responseTimeSum / requestCount : 0}`,
    '',
    `# HELP app_uptime Application uptime in seconds`,
    `# TYPE app_uptime gauge`,
    `app_uptime ${Math.floor(process.uptime())}`
  ];
  
  res.set('Content-Type', 'text/plain');
  res.send(metrics.join('\n'));
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Sample SRE app listening on port ${port}`);
  console.log(`Health check: http://localhost:${port}/health`);
  console.log(`Metrics: http://localhost:${port}/metrics`);
});
