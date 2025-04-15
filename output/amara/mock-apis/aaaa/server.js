const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const app = express();
const port = 8080;
const serviceName = 'aaaa';

// Middleware
app.use(cors());
app.use(express.json());
app.use(morgan('combined'));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', service: serviceName });
});

// Information endpoint
app.get('/info', (req, res) => {
  res.status(200).json({
    name: serviceName,
    version: '1.0.0',
    description: 'Mock API for ' + serviceName
  });
});

// Echo endpoint
app.all('/echo', (req, res) => {
  res.status(200).json({
    method: req.method,
    url: req.url,
    headers: req.headers,
    query: req.query,
    body: req.body
  });
});

// Generic CRUD endpoints
const items = [
  { id: 1, name: 'Item 1', description: 'This is item 1' },
  { id: 2, name: 'Item 2', description: 'This is item 2' }
];

// List items
app.get('/items', (req, res) => {
  res.status(200).json(items);
});

// Get a specific item
app.get('/items/:id', (req, res) => {
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (item) {
    res.status(200).json(item);
  } else {
    res.status(404).json({ error: 'Item not found' });
  }
});

// Create an item
app.post('/items', (req, res) => {
  const newId = items.length > 0 ? Math.max(...items.map(i => i.id)) + 1 : 1;
  const newItem = { id: newId, ...req.body };
  items.push(newItem);
  res.status(201).json(newItem);
});

// Update an item
app.put('/items/:id', (req, res) => {
  const itemIndex = items.findIndex(i => i.id === parseInt(req.params.id));
  if (itemIndex >= 0) {
    items[itemIndex] = { ...items[itemIndex], ...req.body };
    res.status(200).json(items[itemIndex]);
  } else {
    res.status(404).json({ error: 'Item not found' });
  }
});

// Delete an item
app.delete('/items/:id', (req, res) => {
  const itemIndex = items.findIndex(i => i.id === parseInt(req.params.id));
  if (itemIndex >= 0) {
    const deleted = items.splice(itemIndex, 1);
    res.status(200).json(deleted[0]);
  } else {
    res.status(404).json({ error: 'Item not found' });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`${serviceName} mock API listening at http://localhost:${port}`);
});
