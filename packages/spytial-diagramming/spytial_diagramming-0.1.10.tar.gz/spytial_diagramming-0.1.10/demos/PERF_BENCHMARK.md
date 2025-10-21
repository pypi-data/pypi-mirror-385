# sPyTial Performance Benchmarking Demo

This demo showcases sPyTial's performance benchmarking capabilities by rendering trees of increasing complexity and recording metrics.

## What It Does

The demo creates and visualizes 100 binary trees with 1 to 100 nodes each, measuring:
- **Parse Spec**: Time to parse the CnD specification
- **Generate Layout**: Time to compute the spatial layout
- **Render Layout**: Time to render the visualization
- **Total Time**: End-to-end time

## Usage

### Sequential Benchmark (100 trees, 1-100 nodes)
```bash
python perf-example.py --mode sequential --iterations 100
```

This creates 100 diagrams of increasing complexity. Each one is rendered once, and metrics appear in the browser console.

### Aggregated Benchmark (One tree, 50 iterations)
```bash
python perf-example.py --mode aggregated
```

This creates a single tree (50 nodes) and renders it 50 times, aggregating min/max/avg metrics. The results are automatically saved.

### Both Benchmarks
```bash
python perf-example.py --mode both
```

### With Server-Side Collection
```bash
python perf-example.py --mode aggregated --perf-path http://localhost:5000/api/metrics
```

Metrics will be POSTed to your endpoint instead of downloaded locally.

## Understanding the Output

### Single Render (Sequential Mode)
Each diagram shows timing in the browser console:
```
=== Performance Metrics ===
Parse Spec: 2.45ms
Generate Layout: 125.32ms
Render Layout: 48.90ms
Total Time: 176.67ms
Timestamp: 2025-10-20T14:32:45.123Z
==========================
```

### Multiple Iterations (Aggregated Mode)
After 50 renders, you see aggregated statistics:
```
=== Aggregated Performance Metrics ===
Parse Spec: 2.45ms (min: 2.30, max: 2.67)
Generate Layout: 125.32ms (min: 120.15, max: 132.42)
Render Layout: 48.90ms (min: 47.21, max: 51.33)
Total Time: 176.67ms (min: 170.25, max: 185.91)
=====================================
```

## Browser Console Access

From the browser developer console (F12), access metrics:

```javascript
// Get all stored metrics and statistics
window.spytialPerformance.getHistory()

// Download current metrics as JSON
window.spytialPerformance.downloadMetrics()

// Export all stored metrics as CSV
window.spytialPerformance.exportAsCSV()

// Clear metrics history
window.spytialPerformance.clearHistory()
```

## Key Features

✅ **Automatic metric collection** - No manual instrumentation needed  
✅ **Sequential mode** - Test scaling with increasing complexity  
✅ **Aggregated mode** - Get statistical analysis with min/max/avg  
✅ **Server integration** - POST metrics to your backend  
✅ **CSV export** - Analyze results in Excel/Python  
✅ **Zero overhead** - Only saves metrics when benchmarking

## Performance Expectations

For a balanced binary tree on typical hardware:

| Nodes | Parse (ms) | Layout (ms) | Render (ms) | Total (ms) |
|-------|-----------|-----------|-----------|-----------|
| 10    | 2-3       | 15-25     | 10-15     | 30-50     |
| 50    | 2-3       | 80-120    | 40-60     | 130-180   |
| 100   | 2-3       | 180-250   | 80-120    | 270-380   |

## Tips for Analysis

1. **First run warmup**: First render may be slower due to JIT compilation
2. **Use aggregated mode**: Multiple iterations give more reliable statistics
3. **Compare across commits**: Run benchmarks after code changes to measure impact
4. **CSV export**: Use `exportAsCSV()` for detailed time-series analysis
5. **Server collection**: Integrate with your CI/CD to track performance over time

## Next Steps

- Modify `create_balanced_tree()` to test different data structures
- Add custom relationalizers to see their performance impact
- Integrate metrics collection with your build pipeline
- Compare performance across different Python/browser versions
